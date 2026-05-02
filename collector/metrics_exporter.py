from prometheus_client import start_http_server, Gauge
from dotenv import load_dotenv
import threading
import time
import os

load_dotenv()

cost_gauge     = Gauge("aws_service_cost_usd",   "Daily AWS cost per service",      ["service"])
untagged_gauge = Gauge("aws_untagged_resources",  "Count of untagged resources",     ["resource_type"])
anomaly_gauge  = Gauge("aws_cost_anomaly_count",  "Number of cost anomalies detected")

def collect_and_expose():
    while True:
        try:
            print("Collecting costs...")
            from collector.cost_collector import get_daily_costs
            for row in get_daily_costs():
                cost_gauge.labels(service=row["service"]).set(row["cost"])
            print("  ✓ Costs collected")
        except Exception as e:
            print(f"  ✗ Cost collection failed: {e}")

        try:
            print("Checking tags...")
            from collector.tag_checker import get_all_untagged
            from collections import Counter
            untagged = get_all_untagged()
            counts = Counter(r["resource_type"] for r in untagged)
            for rtype, count in counts.items():
                untagged_gauge.labels(resource_type=rtype).set(count)
            print(f"  ✓ Tag check done — {len(untagged)} untagged resources")
        except Exception as e:
            print(f"  ✗ Tag check failed: {e}")

        try:
            print("Detecting anomalies...")
            from collector.anomaly_detector import detect_anomalies, send_slack_alert
            from collector.jira_reporter import report_anomalies_to_jira
            anomalies = detect_anomalies()
            anomaly_gauge.set(len(anomalies))
            if anomalies:
                print(f"  ! {len(anomalies)} anomalies found — alerting")
                send_slack_alert(anomalies)
                report_anomalies_to_jira(anomalies)
            else:
                print("  ✓ No anomalies detected")
        except Exception as e:
            print(f"  ✗ Anomaly detection failed: {e}")

        print("Sleeping 1 hour...\n")
        time.sleep(3600)

if __name__ == "__main__":
    # Start HTTP server FIRST on main thread
    start_http_server(8000)
    print("✓ Metrics server running on http://localhost:8000/metrics")

    # Run collection in background so HTTP stays responsive
    t = threading.Thread(target=collect_and_expose, daemon=True)
    t.start()

    # Keep main thread alive
    while True:
        time.sleep(10)