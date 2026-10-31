import os
import re
import time
import sqlite3
from typing import Dict, Any, Set
from prometheus_client import start_http_server, Gauge, Counter

HERMES_DIR = os.environ.get("HERMES_DIR", os.path.expanduser("~/.hermes"))
PROFILES = [p.strip() for p in os.environ.get("PROFILES", "default,coder").split(",")]
SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL_SECONDS", "5"))
PORT = int(os.environ.get("EXPORTER_PORT", "9100"))

# --- Sub-Agent & Delegation Metrics ---
ACTIVE_DELEGATIONS = Gauge("hermes_subagent_active_count", "Currently active sub-agents", ["profile", "state"])
TOTAL_DELEGATIONS = Counter("hermes_subagent_total", "Total sub-agent delegations dispatched", ["profile"])
FAILED_DELEGATIONS = Counter("hermes_subagent_failed_total", "Total sub-agent delegations failed", ["profile"])

# --- Security & Anomaly Metrics ---
SECURITY_ALERTS = Counter("hermes_security_scan_alerts_total", "Security alerts flagged by Tirith/scanner", ["profile", "severity"])
TOOL_CALL_ERRORS = Counter("hermes_tool_call_errors_total", "Tool call executions returned error", ["profile", "tool"])
INBOUND_MESSAGES = Counter("hermes_inbound_messages_total", "Inbound messages received", ["profile", "source"])

# --- MCP (Model Context Protocol) Metrics ---
MCP_SERVER_STATUS = Gauge("hermes_mcp_server_status", "MCP server connection status (1=connected, 0=disconnected)", ["profile", "server"])
MCP_SERVER_TOOLS = Gauge("hermes_mcp_server_tools_count", "Number of tools registered by MCP server", ["profile", "server"])

# --- Token & Cost Economics Metrics ---
LLM_INPUT_TOKENS = Gauge("hermes_llm_input_tokens_total", "Total LLM prompt input tokens", ["profile", "model", "provider"])
LLM_OUTPUT_TOKENS = Gauge("hermes_llm_output_tokens_total", "Total LLM completion output tokens", ["profile", "model", "provider"])
LLM_CACHE_READ_TOKENS = Gauge("hermes_llm_cache_read_tokens_total", "Total LLM prompt cache hit/read tokens", ["profile", "model", "provider"])
LLM_ESTIMATED_COST_USD = Gauge("hermes_llm_cost_usd_total", "Estimated LLM API cost in USD", ["profile", "model", "provider"])
LLM_API_CALLS = Gauge("hermes_llm_api_calls_total", "Total LLM API calls executed", ["profile", "model", "provider"])

# Internal tracking
_seen_delegation_ids: Set[str] = set()
_log_file_offsets: Dict[str, int] = {}
_known_mcp_servers: Dict[str, Set[str]] = {}

def get_state_db_path(profile: str) -> str:
    if profile == "default":
        return os.path.join(HERMES_DIR, "state.db")
    return os.path.join(HERMES_DIR, "profiles", profile, "state.db")

def get_agent_log_path(profile: str) -> str:
    if profile == "default":
        return os.path.join(HERMES_DIR, "logs", "agent.log")
    return os.path.join(HERMES_DIR, "profiles", profile, "logs", "agent.log")

def get_gateway_log_path(profile: str) -> str:
    if profile == "default":
        return os.path.join(HERMES_DIR, "logs", "gateway.log")
    return os.path.join(HERMES_DIR, "profiles", profile, "logs", "gateway.log")

def scrape_state_db(profile: str):
    db_path = get_state_db_path(profile)
    if not os.path.exists(db_path):
        return

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        # 1. Active Delegations
        cursor.execute("SELECT state, count(*) FROM async_delegations GROUP BY state")
        states = {"running": 0, "pending": 0, "completed": 0, "failed": 0}
        for state, count in cursor.fetchall():
            states[state] = count
            ACTIVE_DELEGATIONS.labels(profile=profile, state=state).set(count)

        # 2. Track new delegations
        cursor.execute("SELECT delegation_id, state FROM async_delegations")
        for d_id, state in cursor.fetchall():
            if d_id not in _seen_delegation_ids:
                _seen_delegation_ids.add(d_id)
                TOTAL_DELEGATIONS.labels(profile=profile).inc()
                if state == "failed":
                    FAILED_DELEGATIONS.labels(profile=profile).inc()

        # 3. Model Token & Cost Usage
        cursor.execute("""
            SELECT model, billing_provider, 
                   SUM(api_call_count), SUM(input_tokens), SUM(output_tokens), 
                   SUM(cache_read_tokens), SUM(estimated_cost_usd)
            FROM session_model_usage
            GROUP BY model, billing_provider
        """)
        for model, provider, calls, in_tok, out_tok, cache_tok, cost in cursor.fetchall():
            provider_label = provider if provider else "default"
            LLM_API_CALLS.labels(profile=profile, model=model, provider=provider_label).set(calls or 0)
            LLM_INPUT_TOKENS.labels(profile=profile, model=model, provider=provider_label).set(in_tok or 0)
            LLM_OUTPUT_TOKENS.labels(profile=profile, model=model, provider=provider_label).set(out_tok or 0)
            LLM_CACHE_READ_TOKENS.labels(profile=profile, model=model, provider=provider_label).set(cache_tok or 0)
            LLM_ESTIMATED_COST_USD.labels(profile=profile, model=model, provider=provider_label).set(cost or 0.0)

        conn.close()
    except Exception:
        pass

def scrape_logs(profile: str):
    agent_log = get_agent_log_path(profile)
    if os.path.exists(agent_log):
        offset = _log_file_offsets.get(agent_log, 0)
        file_size = os.path.getsize(agent_log)
        
        if file_size < offset:
            offset = 0

        # Read whole or tail
        try:
            with open(agent_log, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(offset)
                for line in f:
                    # Security alerts
                    if "Security scan" in line:
                        sev = "UNKNOWN"
                        if "[HIGH]" in line:
                            sev = "HIGH"
                        elif "[MEDIUM]" in line:
                            sev = "MEDIUM"
                        elif "[LOW]" in line:
                            sev = "LOW"
                        SECURITY_ALERTS.labels(profile=profile, severity=sev).inc()

                    # Tool execution errors
                    if "Tool" in line and "returned error" in line:
                        match = re.search(r"Tool\s+(\w+)\s+returned error", line)
                        tool_name = match.group(1) if match else "unknown"
                        TOOL_CALL_ERRORS.labels(profile=profile, tool=tool_name).inc()

                    # MCP server registration & tools count
                    # e.g.: MCP server 'notebooklm-memory' (stdio): registered 57 tool(s)
                    if "MCP server" in line and "registered" in line:
                        mcp_match = re.search(r"MCP server '([^']+)'[^:]*:\s+registered\s+(\d+)\s+tool", line)
                        if mcp_match:
                            s_name = mcp_match.group(1)
                            t_count = int(mcp_match.group(2))
                            if profile not in _known_mcp_servers:
                                _known_mcp_servers[profile] = set()
                            _known_mcp_servers[profile].add(s_name)
                            MCP_SERVER_STATUS.labels(profile=profile, server=s_name).set(1)
                            MCP_SERVER_TOOLS.labels(profile=profile, server=s_name).set(t_count)

                    # MCP disconnection or error
                    if "MCP" in line and ("failed" in line or "closed" in line or "disconnected" in line):
                        for s_name in _known_mcp_servers.get(profile, []):
                            if s_name in line:
                                MCP_SERVER_STATUS.labels(profile=profile, server=s_name).set(0)

                _log_file_offsets[agent_log] = f.tell()
        except Exception:
            pass

    # Gateway log for inbound messages
    gw_log = get_gateway_log_path(profile)
    if os.path.exists(gw_log):
        offset = _log_file_offsets.get(gw_log, 0)
        file_size = os.path.getsize(gw_log)
        if file_size < offset:
            offset = 0
        if file_size > offset:
            try:
                with open(gw_log, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(offset)
                    for line in f:
                        if "inbound message" in line:
                            INBOUND_MESSAGES.labels(profile=profile, source="telegram").inc()
                    _log_file_offsets[gw_log] = f.tell()
            except Exception:
                pass

def main():
    print(f"Starting Hermes Metrics Exporter on port {PORT}...")
    start_http_server(PORT)
    while True:
        for profile in PROFILES:
            scrape_state_db(profile)
            scrape_logs(profile)
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main()
