# 🛡️ Hermes Agent & Sub-Agent Monitoring Stack

Production-ready observability stack for **Hermes Agent** and its **Sub-Agents**, using **VictoriaMetrics** (Prometheus TSDB) and **Grafana**.

Designed to track:
- 🚨 **Security Alerts & Anomalies**: Tirith security scan flags, prompt injection attempts, unauthorized terminal execution.
- 🤖 **Multi-Agent Orchestration**: Real-time sub-agent states (`running`, `pending`, `completed`, `failed`), spawn rates, and stuck tasks.
- 🛠️ **Tool Failures**: Terminal command errors, tool crashes.
- 📨 **Gateway Activity**: Inbound message traffic (Telegram).

---

## 🚀 Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed and running.
- Hermes Agent configured (`~/.hermes`).

### 2. Run the Stack
Clone this repo and spin up the containers:

```bash
git clone https://github.com/<your-username>/hermes-agent-monitoring.git
cd hermes-agent-monitoring

docker-compose up -d
```

### 3. Open Dashboards
- **Grafana**: [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`)
- **VictoriaMetrics Web UI / Metrics**: [http://localhost:8428](http://localhost:8428)
- **Hermes Metrics Exporter**: [http://localhost:9100/metrics](http://localhost:9100/metrics)

Grafana is pre-provisioned with the datasource and the **"Hermes Agent & Sub-Agent Ops"** dashboard automatically!

---

## 📂 Architecture

```
[ Hermes Agent & Sub-Agents ]
  │  (writes ~/.hermes/profiles/*/state.db & logs/*.log)
  ▼
[ hermes-exporter (:9100) ]  (Read-Only mount of ~/.hermes)
  │  - Scrapes active delegations from SQLite
  │  - Tails agent & gateway logs for Security scan flags and errors
  ▼
[ VictoriaMetrics (:8428) ] (Ultra-lightweight Prometheus TSDB)
  ▲
[ Grafana (:3000) ] (Pre-configured Dashboards & Visualizations)
```

## 🔒 Security
- The Hermes state folder `~/.hermes` is mounted into the exporter container as **READ-ONLY (`:ro`)**.
- No tokens or API keys are exposed to Prometheus metrics.
