# FinOps AWS Cost Monitor

> A production-grade AWS cost monitoring and anomaly detection pipeline built with Python, Prometheus, Grafana, and GitHub Actions.

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Youngyz1/finops-dashboard/daily_run.yml?label=Daily%20Pipeline&logo=github)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![AWS](https://img.shields.io/badge/AWS-Cost%20Explorer-orange?logo=amazon-aws)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-red?logo=prometheus)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-yellow?logo=grafana)

---

## What This Project Does

This pipeline runs every day at 08:00 UTC and:

1. **Pulls daily AWS spend** from Cost Explorer API, broken down by service
2. **Checks tag compliance** — finds EC2, RDS, and S3 resources missing required tags (`Environment`, `Owner`, `Project`)
3. **Detects cost anomalies** — flags any service with a >20% spend increase day-over-day
4. **Fires Slack alerts** when anomalies are found
5. **Auto-creates Jira tickets** for each anomaly with full context
6. **Exposes 8 Prometheus metrics** via a custom HTTP exporter
7. **Visualises everything** in a live Grafana dashboard

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (cron)                     │
│                    Runs daily at 08:00 UTC                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────▼───────────────┐
           │         Python Pipeline        │
           │                               │
           │  cost_collector.py            │──► AWS Cost Explorer API
           │  tag_checker.py               │──► AWS EC2 / S3 / RDS API
           │  anomaly_detector.py          │──► Slack Webhook
           │  jira_reporter.py             │──► Jira REST API
           │  metrics_exporter.py          │
           └───────────────┬───────────────┘
                           │ :8000/metrics
           ┌───────────────▼───────────────┐
           │          Prometheus            │
           │     Scrapes every 60s          │
           └───────────────┬───────────────┘
                           │
           ┌───────────────▼───────────────┐
           │           Grafana              │
           │   localhost:3000               │
           │                               │
           │  • Daily cost by service       │
           │  • Untagged resource count     │
           │  • Active anomaly count        │
           └───────────────────────────────┘
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core automation and scripting |
| boto3 | AWS SDK — Cost Explorer, EC2, S3, RDS APIs |
| prometheus-client | Custom metrics HTTP exporter |
| Prometheus | Metrics scraping and storage |
| Grafana | Dashboard visualisation |
| Docker Compose | Local Prometheus + Grafana stack |
| GitHub Actions | Scheduled CI/CD pipeline (cron) |
| Jira REST API | Automated ticket creation |
| Slack Webhooks | Real-time alerting |

---

## Project Structure

```
finops-dashboard/
├── collector/
│   ├── cost_collector.py       # Pull daily AWS spend by service
│   ├── tag_checker.py          # Find untagged EC2, S3, RDS resources
│   ├── anomaly_detector.py     # Detect spend spikes, fire Slack alerts
│   ├── jira_reporter.py        # Auto-create Jira tickets on anomaly
│   ├── metrics_exporter.py     # Expose Prometheus metrics on :8000
│   └── mock_data.py            # Realistic mock data for demo/dev
├── infra/
│   ├── docker-compose.yml      # Prometheus + Grafana stack
│   └── prometheus.yml          # Scrape config
├── .github/
│   └── workflows/
│       └── daily_run.yml       # GitHub Actions cron pipeline
├── .env.example                # Environment variable template
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Docker Desktop
- AWS account with Cost Explorer enabled
- AWS CLI configured (`aws configure`)
- Jira Cloud account
- Slack workspace with incoming webhook

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Youngyz1/finops-dashboard.git
cd finops-dashboard
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```dotenv
AWS_REGION=us-east-1
COST_SPIKE_THRESHOLD=20
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_PROJECT_KEY=OPS
```

### 4. Verify AWS credentials

```bash
aws configure
aws sts get-caller-identity
```

You should see your AWS account ID returned. If not, run `aws configure` and enter your Access Key ID and Secret Access Key.

> **Enable Cost Explorer:** Go to AWS Console → Cost Explorer → Launch Cost Explorer. Allow up to 24 hours for data to populate on a new account.

### 5. Start Prometheus and Grafana

```bash
cd infra
docker compose up -d
```

Verify both containers are running:

```bash
docker compose ps
```

Expected output:
```
NAME                    STATUS
infra-prometheus-1      running
infra-grafana-1         running
```

### 6. Start the metrics exporter

Open a new terminal and run:

```bash
cd finops-dashboard
python -m collector.metrics_exporter
```

Expected output:
```
✓ Metrics server running on http://localhost:8000/metrics
Collecting costs...
  ✓ Costs collected
Checking tags...
  ✓ Tag check done — N untagged resources
Detecting anomalies...
  ✓ No anomalies detected
Sleeping 1 hour...
```

Verify metrics are being served:

```bash
curl http://localhost:8000/metrics
```

You should see output like:
```
aws_service_cost_usd{service="Amazon EC2"} 45.2
aws_untagged_resources{resource_type="S3"} 1.0
aws_cost_anomaly_count 0.0
```

### 7. (Optional) Run mock data for demo dashboard

If your AWS account is on free tier with no meaningful charges, run the mock exporter alongside the real one for a populated dashboard:

```bash
# In a separate terminal
python -m collector.mock_data
```

This serves realistic demo data on port 8001. Add it to `infra/prometheus.yml`:

```yaml
  - job_name: "finops-demo"
    static_configs:
      - targets: ["YOUR_LOCAL_IP:8001"]
```

---

## Grafana Dashboard Setup

### 1. Open Grafana

Go to `http://localhost:3000` — login with `admin` / `admin`.

### 2. Add Prometheus data source

- Click ☰ → **Connections → Data sources → Add new data source**
- Select **Prometheus**
- URL: `http://prometheus:9090`
- Click **Save & test**

### 3. Create dashboard panels

**Panel 1 — Daily AWS Cost by Service (Bar chart)**
```promql
aws_service_cost_usd{job="finops-demo"}
```
- Visualization: **Bar chart**
- Unit: **Dollars ($)**
- Legend format: `{{service}}`

**Panel 2 — Untagged Resources (Stat)**
```promql
sum(aws_untagged_resources)
```
- Visualization: **Stat**
- Color mode: **Background**
- Graph mode: **None**

**Panel 3 — Cost Anomalies Detected (Stat)**
```promql
max(aws_cost_anomaly_count)
```
- Visualization: **Stat**
- Thresholds: green at 0, red at 1
- Color mode: **Background**

Save the dashboard as **FinOps — AWS Cost Monitor**.

---

## GitHub Actions Setup

The pipeline runs automatically every day at 08:00 UTC. To set it up:

### 1. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add each of these:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `AWS_REGION` | `us-east-1` |
| `SLACK_WEBHOOK_URL` | Your Slack webhook URL |
| `JIRA_BASE_URL` | `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Your Jira email |
| `JIRA_API_TOKEN` | Your Jira API token |
| `JIRA_PROJECT_KEY` | e.g. `OPS` or `SCRUM` |

### 2. Get a Jira API token

Go to `https://id.atlassian.com/manage-profile/security/api-tokens` → **Create API token** → copy the value.

### 3. Trigger a manual run to test

Go to your repo → **Actions → FinOps Daily Run → Run workflow → Run workflow**

Expected result: all steps green, logs showing `Found 0 anomalies`.

---

## Running Individual Scripts

```bash
# Pull and print last 30 days of AWS costs
python -m collector.cost_collector

# Find all untagged resources
python -m collector.tag_checker

# Run anomaly detection and fire Slack alert if triggered
python -m collector.anomaly_detector

# Create Jira tickets for any detected anomalies
python -m collector.jira_reporter

# Start the Prometheus metrics HTTP server (keeps running)
python -m collector.metrics_exporter
```

---

## Prometheus Metrics Reference

| Metric | Type | Labels | Description |
|---|---|---|---|
| `aws_service_cost_usd` | Gauge | `service` | Daily spend per AWS service in USD |
| `aws_untagged_resources` | Gauge | `resource_type` | Count of resources missing required tags |
| `aws_cost_anomaly_count` | Gauge | — | Number of services with >20% spend spike |

---

## Stopping the Stack

```bash
# Stop Prometheus and Grafana
cd infra
docker compose down

# Stop the metrics exporter
# Press Ctrl+C in the terminal running python -m collector.metrics_exporter
```

---

## Skills Demonstrated

- **Python automation** — boto3 API integration, threading, HTTP servers
- **AWS** — Cost Explorer, EC2, S3, RDS APIs, IAM, CLI
- **Prometheus** — custom metrics exporter, scrape config, PromQL
- **Grafana** — dashboard creation, data sources, stat panels, bar charts
- **Docker Compose** — multi-container local stack
- **GitHub Actions** — cron scheduling, secrets management, CI pipeline
- **FinOps** — cost visibility, tag compliance, anomaly detection, chargeback
- **Jira API** — programmatic ticket creation with labels and priority
- **Slack API** — incoming webhook alerting

---

## Author

**Ohia Uche Godwill**
Cloud & DevOps Engineer
[GitHub](https://github.com/Youngyz1) · [LinkedIn](https://linkedin.com/in/yourprofile) · godwillyoungyz@gmail.com