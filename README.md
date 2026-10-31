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
