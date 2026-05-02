import requests, os, base64
from dotenv import load_dotenv

load_dotenv()

def create_jira_ticket(summary, description):
    url   = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue"
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    auth  = base64.b64encode(f"{email}:{token}".encode()).decode()

    payload = {
        "fields": {
            "project":     {"key": os.getenv("JIRA_PROJECT_KEY", "OPS")},
            "summary":     summary,
            "description": {
                "type":    "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype":   {"name": "Task"},
            "priority":    {"name": "High"},
            "labels":      ["finops", "cost-anomaly"]
        }
    }

    resp = requests.post(url, json=payload, headers={
        "Authorization": f"Basic {auth}",
        "Content-Type":  "application/json"
    })
    resp.raise_for_status()
    key = resp.json().get("key")
    print(f"Created Jira ticket: {key}")
    return key

def report_anomalies_to_jira(anomalies):
    for a in anomalies:
        summary = f"Cost spike: {a['service']} +{a['pct_change']}%"
        desc    = (f"Service: {a['service']}\n"
                   f"Yesterday: ${a['yesterday']}\n"
                   f"Today:     ${a['today']}\n"
                   f"Change:    +{a['pct_change']}%\n\n"
                   f"Please investigate and tag responsible team.")
        create_jira_ticket(summary, desc)