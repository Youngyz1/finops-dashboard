import requests, os
from dotenv import load_dotenv
from collector.cost_collector import get_daily_costs
from collections import defaultdict

load_dotenv()

def detect_anomalies(threshold_pct=None):
    threshold = float(os.getenv("COST_SPIKE_THRESHOLD", 20))
    if threshold_pct:
        threshold = threshold_pct

    costs = get_daily_costs()
    by_service = defaultdict(list)
    for row in costs:
        by_service[row["service"]].append(row)

    anomalies = []
    for service, records in by_service.items():
        records.sort(key=lambda x: x["date"])
        if len(records) < 2:
            continue
        yesterday = records[-2]["cost"]
        today     = records[-1]["cost"]
        if yesterday == 0:
            continue
        pct_change = ((today - yesterday) / yesterday) * 100
        if pct_change > threshold:
            anomalies.append({
                "service": service,
                "yesterday": round(yesterday, 2),
                "today": round(today, 2),
                "pct_change": round(pct_change, 1)
            })
    return anomalies

def send_slack_alert(anomalies):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook or not anomalies:
        return
    lines = [f"*AWS Cost Anomaly Detected*\n"]
    for a in anomalies:
        lines.append(f"• *{a['service']}*: ${a['yesterday']} → ${a['today']} (+{a['pct_change']}%)")
    payload = {"text": "\n".join(lines)}
    requests.post(webhook, json=payload)

if __name__ == "__main__":
    anomalies = detect_anomalies()
    print(f"Found {len(anomalies)} anomalies")
    send_slack_alert(anomalies)