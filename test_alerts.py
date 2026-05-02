from dotenv import load_dotenv
load_dotenv()

from collector.jira_reporter import report_anomalies_to_jira
from collector.anomaly_detector import send_slack_alert

# Fake a realistic anomaly
test_anomalies = [
    {
        "service": "Amazon EC2",
        "yesterday": 10.50,
        "today": 45.20,
        "pct_change": 330.5
    },
    {
        "service": "Amazon RDS",
        "yesterday": 5.00,
        "today": 28.50,
        "pct_change": 470.0
    }
]

print("Sending Slack alert...")
send_slack_alert(test_anomalies)
print("✓ Slack alert sent")

print("Creating Jira tickets...")
report_anomalies_to_jira(test_anomalies)
print("✓ Jira tickets created")