## FinOps AWS Cost Monitor

Real-time AWS cost monitoring pipeline built with Python, Prometheus, and Grafana.

**What it does:**
- Pulls daily spend data from AWS Cost Explorer API by service
- Checks EC2, RDS, and S3 resources for missing required tags
- Detects cost spikes >20% and fires Slack alerts + creates Jira tickets automatically
- Exposes 8 custom Prometheus metrics via threaded HTTP exporter
- Scheduled daily via GitHub Actions cron (08:00 UTC)

**Stack:** Python · boto3 · Prometheus · Grafana · Docker Compose · GitHub Actions · AWS Cost Explorer · Jira API · Slack Webhooks