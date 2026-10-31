# 🛡️ Hermes Agent & Sub-Agent Monitoring Stack

Production-ready observability stack for **Hermes Agent**, its **Sub-Agents**, and **Host Hardware Metrics (CPU, Memory, Disk, Network)**, using **VictoriaMetrics** (Prometheus TSDB) and **Grafana**.

Designed to track:
- 💻 **Host Hardware Utilization**: Real-time CPU %, RAM %, Root Disk %, and Network I/O throughput of the machine running the agent.
- 🚨 **Security Alerts & Anomalies**: Tirith security scan flags, prompt injection attempts, unauthorized terminal execution.
- 🤖 **Multi-Agent Orchestration**: Real-time sub-agent states (`running`, `pending`, `completed`, `failed`), spawn rates, and stuck tasks.
- 🛠️ **Tool Failures**: Terminal command errors, tool crashes.
- 📨 **Gateway Activity**: Inbound message traffic (Telegram).

---

## 🚀 Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed and running.
- Hermes Agent configured (`~/.hermes`).

### 2. Start Host Hardware Exporter (Optional but Recommended)
Untuk membaca CPU/RAM/Disk/Network dari host (macOS/Linux) tanpa batasan container isolasi:

```bash
# Menggunakan uv (atau python3 biasa dengan psutil dan prometheus_client)
uv run --with psutil --with prometheus_client python exporter/host_exporter.py
```
*(Di macOS, ini juga sudah otomatis dipasang sebagai background agent `ai.hermes.host-exporter`)*

### 3. Run the Monitoring Stack
Clone repo dan jalankan Docker Compose:

```bash
git clone https://github.com/addhe/hermes-agent-monitoring.git
cd hermes-agent-monitoring

docker-compose up -d
```

### 4. Open Dashboards
- **Grafana**: [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin2026login`)
- **VictoriaMetrics Web UI / Metrics**: [http://localhost:8428](http://localhost:8428)
- **Hermes Metrics Exporter**: [http://localhost:9100/metrics](http://localhost:9100/metrics)
- **Host Metrics Exporter**: [http://localhost:9105/metrics](http://localhost:9105/metrics)

Grafana otomatis ter-provision dengan datasource VictoriaMetrics dan dashboard **"Hermes Agent & Sub-Agent Ops"** yang menyajikan metrik sistem host, keamanan agent, dan status orkestrasi sub-agent!

---

## 🤝 Contributing

We love community contributions! Whether you want to add new dashboard panels, support additional LLM provider token formats, improve anomaly detection, or enhance cross-platform host metrics:

Please read our [Contributing Guide](CONTRIBUTING.md) for local dev setup, guidelines, and PR workflow.

