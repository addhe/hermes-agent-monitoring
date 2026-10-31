# 🛡️ Hermes Agent & Sub-Agent Monitoring Stack

Production-ready observability stack for **Hermes Agent**, its **Sub-Agents**, and **Host Hardware Metrics (CPU, Memory, Disk, Network)**, using **VictoriaMetrics** (Prometheus TSDB) and **Grafana**.

Designed to track:
- 💻 **Host Hardware Utilization**: Real-time CPU %, RAM %, Root Disk %, and Network I/O throughput of the machine running the agent.
- 🔌 **Model Context Protocol (MCP)**: Active connection status and registered tools per MCP server.
- 🧠 **LLM Token & Cost Economics**: In/Out tokens, API calls, and prompt cache hit savings per model.
- 🚨 **Security Alerts & Anomalies**: Tirith security scan flags, prompt injection attempts, unauthorized terminal execution.
- 🤖 **Multi-Agent Orchestration**: Real-time sub-agent states (`running`, `pending`, `completed`, `failed`), spawn rates, and stuck tasks.
- 🛠️ **Tool Failures**: Terminal command errors, tool crashes.
- 📨 **Gateway Activity**: Inbound message traffic (Telegram).

---

## 🔍 How to Read the Dashboard: Detecting Rogue Agents & Hacks

A common question in autonomous AI agents: **"How do I know if my agent is secretly talking to other agents, caught in an infinite loop, or compromised via prompt injection?"**

Here are the key symptoms and corresponding panels to watch on your Grafana dashboard:

### 1. 🪙 Anomaly in Token Consumption ("The Silent Spender")
- **Symptom**: Tokens ticking up steadily when you are away from the keyboard or asleep.
- **Look at**: `🧠 LLM Tokens & Cost Economics` -> **Total Tokens by Model** & **API Calls**.
- **What it means**: An autonomous background job, rogue multi-agent conversation, or prompt-injection jailbreak running reconnaissance tasks without your consent.

### 2. 🤖 Unintended Sub-Agent Swarms
- **Symptom**: The number of running sub-agents increases unexpectedly or tasks remain in `running` status for >15–30 minutes.
- **Look at**: `🤖 Multi-Agent / Sub-Agent Orchestration` -> **Running Sub-Agents** & **Status Breakdown Over Time**.
- **What it means**: An agent delegating recursive tasks without termination criteria, or communicating with external agent nodes.

### 3. 🚨 Spike in Security Scan Alerts & Tool Errors
- **Symptom**: Sudden increment in security alerts (red threshold) or repeated tool failures.
- **Look at**: `🚨 Security & Anomaly Detection` -> **Security Scan Alerts (Total)** & **Tool Execution Errors**.
- **What it means**: The agent encountered prompt injection attempts trying to force reading sensitive files (`.env`, `id_rsa`, keychains) or executing unauthorized shell commands (e.g. reverse shells). Repeated tool errors indicate trial-and-error privilege escalation or sandbox probing.

### 4. 🌐 Suspicious Hardware & Network Activity
- **Symptom**: Network upload bandwidth (`Network I/O Throughput`) spikes significantly, or CPU stays pinned at 80–100% when no compilation or tests are running.
- **Look at**: `💻 Laptop Host System Resources` -> **Network I/O (Upload)** & **CPU Usage**.
- **What it means**: Potential data exfiltration (large dumps or repositories uploaded outward) or hidden unauthorized background processes.

---

### 📊 Quick Incident Triage Matrix

| Observed Symptom | Primary Panel to Inspect | Threat Category | Immediate Action |
|---|---|---|---|
| Token count rising at night | **Total Tokens by Model** | Rogue agent / rogue cron | Check recent sessions (`state.db`) & kill agent process |
| Multiple sub-agents stuck in `running` | **Running Sub-Agents** | Orphaned delegation loop | Inspect `async_delegations` and cancel tasks |
| High security scan count (Red) | **Security Scan Alerts** | Prompt injection / exploit | Review `agent.log` for malicious tool commands |
| Sudden outbound network upload surge | **Network I/O Throughput** | Data exfiltration | Check open sockets, network connections, and firewall |
| MCP Server status flips Red | **MCP Server Status** | MCP bridge crash / auth expiry | Inspect MCP server logs and refresh credentials |

---

## 🤖 Prompt for Your AI Agent (One-Click Setup)

If you are using **Hermes Agent**, **Claude Code**, **Codex**, or any autonomous AI coding assistant, copy and paste this prompt directly to your agent to have it set up and run this monitoring stack automatically:

```markdown
Please clone and run the Hermes Agent monitoring stack on my machine from https://github.com/addhe/hermes-agent-monitoring:

1. Clone repo to `~/Workspaces/hermes-agent-monitoring` (or current workspace).
2. Check that Docker and Docker Compose are running.
3. Start the host hardware metrics exporter in the background:
   uv run --with psutil --with prometheus_client python exporter/host_exporter.py
4. Start the monitoring stack:
   docker compose up -d --build
5. Verify health:
   - Exporter: curl -s http://localhost:9100/metrics | grep hermes_
   - VictoriaMetrics: curl -s http://localhost:8428/api/v1/targets
   - Grafana: curl -sI http://localhost:3000
6. Give me the summary and Grafana dashboard link (default login: admin / admin2026login).
```

---

## 🚀 Manual Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed and running.
- Hermes Agent configured (`~/.hermes`).

### 2. Start Host Hardware Exporter (Optional but Recommended)
Untuk membaca CPU/RAM/Disk/Network dari host (macOS/Linux) tanpa batasan isolasi container:

```bash
uv run --with psutil --with prometheus_client python exporter/host_exporter.py
```
*(Di macOS, ini juga bisa dipasang sebagai background agent via LaunchAgent)*

### 3. Run the Monitoring Stack
Clone repo dan jalankan Docker Compose:

```bash
git clone https://github.com/addhe/hermes-agent-monitoring.git
cd hermes-agent-monitoring

docker compose up -d
```

### 4. Open Dashboards
- **Grafana**: [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin2026login`)
- **VictoriaMetrics Web UI / Metrics**: [http://localhost:8428](http://localhost:8428)
- **Hermes Metrics Exporter**: [http://localhost:9100/metrics](http://localhost:9100/metrics)
- **Host Metrics Exporter**: [http://localhost:9105/metrics](http://localhost:9105/metrics)

Grafana otomatis ter-provision dengan datasource VictoriaMetrics dan dashboard **"Hermes Agent & Sub-Agent Ops"** yang menyajikan metrik sistem host, MCP status, token usage, keamanan agent, dan status orkestrasi sub-agent!

---

## 🤝 Contributing

We love community contributions! Whether you want to add new dashboard panels, support additional LLM provider token formats, improve anomaly detection, or enhance cross-platform host metrics:

Please read our [Contributing Guide](CONTRIBUTING.md) for local dev setup, guidelines, and PR workflow.
