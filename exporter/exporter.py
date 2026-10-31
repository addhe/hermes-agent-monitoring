import os
import re
import time
import sqlite3
from typing import Dict, Any
from prometheus_client import start_http_server, Gauge, Counter

HERMES_DIR = os.environ.get("HERMES_DIR", os.path.expanduser("~/.hermes"))
PROFILES = [p.strip() for p in os.environ.get("PROFILES", "default,coder").split(",")]
SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL_SECONDS", "5"))
PORT = int(os.environ.get("EXPORTER_PORT", "9100"))

# Metrics
ACTIVE_DELEGATIONS = Gauge("hermes_subagent_active_count", "Currently active sub-agents", ["profile", "state"])
TOTAL_DELEGATIONS = Counter("hermes_subagent_total", "Total sub-agent delegations dispatched", ["profile"])
FAILED_DELEGATIONS = Counter("hermes_subagent_failed_total", "Total sub-agent delegations failed", ["profile"])
SECURITY_ALERTS = Counter("hermes_security_scan_alerts_total", "Security alerts flagged by Tirith/scanner", ["profile", "severity"])
TOOL_CALL_ERRORS = Counter("hermes_tool_call_errors_total", "Tool call executions returned error", ["profile", "tool"])
INBOUND_MESSAGES = Counter("hermes_inbound_messages_total", "Inbound messages received", ["profile", "source"])

# Track state for incrementals
_seen_delegation_ids = set()
_log_file_offsets: Dict[str, int] = {}

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

        conn.close()
    except Exception as e:
        pass

def scrape_logs(profile: str):
    agent_log = get_agent_log_path(profile)
    if os.path.exists(agent_log):
        offset = _log_file_offsets.get(agent_log, 0)
        file_size = os.path.getsize(agent_log)
        
        # If file rotated/truncated
        if file_size < offset:
            offset = 0

        if file_size > offset:
            try:
                with open(agent_log, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(offset)
                    for line in f:
                        # Tirith / Security scan alerts
                        if "Security scan" in line:
                            sev = "UNKNOWN"
                            if "[HIGH]" in line:
                                sev = "HIGH"
                            elif "[MEDIUM]" in line:
                                sev = "MEDIUM"
                            elif "[LOW]" in line:
                                sev = "LOW"
                            SECURITY_ALERTS.labels(profile=profile, severity=sev).inc()

                        # Tool errors
                        if "Tool" in line and "returned error" in line:
                            match = re.search(r"Tool\s+(\w+)\s+returned error", line)
                            tool_name = match.group(1) if match else "unknown"
                            TOOL_CALL_ERRORS.labels(profile=profile, tool=tool_name).inc()

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
