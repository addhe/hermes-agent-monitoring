# Contributing to Hermes Agent Monitoring Stack

Thank you for your interest in improving the **Hermes Agent Monitoring Stack**! We welcome contributions from the community to help make agent observability, security alerting, and multi-agent coordination better for everyone running [Hermes Agent](https://github.com/NousResearch/hermes-agent).

---

## 🌟 Areas We Welcome Contributions In

1. **New Dashboard Panels & Visualizations**:
   - Better metrics representations (e.g. sub-agent tree views, cost burn-rate predictions, memory leak detectors).
2. **Provider & Tool Adapters**:
   - Enhancing token/cost tracking for custom providers, local Ollama/vLLM endpoints, or cloud APIs.
3. **Security Anomaly Rules**:
   - Adding finer-grained regex patterns or parsing rules for security scanner outputs and unexpected tool calls.
4. **Cross-Platform Support**:
   - Improving host metrics collection across Linux, Windows (WSL2), and different container engines (Podman).
5. **Documentation & Recipes**:
   - Guides on integrating with alert managers (Slack/Telegram webhooks), long-term cold storage, or cloud deployments.

---

## 🛠️ Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/hermes-agent-monitoring.git
cd hermes-agent-monitoring
```

### 2. Local Environment Setup
The stack uses standard Python and Docker:
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- Docker & Docker Compose

To test the exporter locally without Docker:
```bash
# Run Hermes agent metrics exporter
uv run --with prometheus_client python exporter/exporter.py

# Run host hardware metrics exporter
uv run --with psutil --with prometheus_client python exporter/host_exporter.py
```

### 3. Running Stack with Changes
When modifying configs or exporter scripts:
```bash
docker compose up -d --build
```
Check endpoints:
- Exporter Metrics: `http://localhost:9100/metrics`
- Host Exporter: `http://localhost:9105/metrics`
- VictoriaMetrics Targets: `http://localhost:8428/api/v1/targets`
- Grafana: `http://localhost:3000`

---

## 📋 Pull Request (PR) Guidelines

1. **Keep it Minimal & Robust (KISS/DRY)**:
   - Prefer stdlib or already included dependencies (`psutil`, `prometheus_client`). Avoid adding heavy frameworks unless strictly necessary.
2. **Sanitize Secrets**:
   - Never commit API keys, personal paths, or environment files.
3. **Test Your Changes**:
   - Ensure `docker compose up -d` starts cleanly without port conflicts or syntax errors in YAML/JSON.
   - Verify Grafana panel UIDs and field configurations.
4. **Commit Messages**:
   - Follow standard conventional commits format:
     - `feat: add token cost prediction panel`
     - `fix: correct panel type for Grafana v11+`
     - `docs: improve quickstart instructions`

---

## 💬 Community & Feedback

- Open an [Issue](https://github.com/addhe/hermes-agent-monitoring/issues) for bug reports, metric proposals, or discussion.
- Submit a [Pull Request](https://github.com/addhe/hermes-agent-monitoring/pulls) with your enhancements!
