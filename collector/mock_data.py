from prometheus_client import start_http_server, Gauge
import time
import math
import random

cost_gauge     = Gauge("aws_service_cost_usd",   "Daily AWS cost per service",  ["service"])
untagged_gauge = Gauge("aws_untagged_resources",  "Count of untagged resources", ["resource_type"])
anomaly_gauge  = Gauge("aws_cost_anomaly_count",  "Number of cost anomalies detected")

# Realistic AWS service costs (monthly ~$200 account)
BASE_COSTS = {
    "Amazon EC2":                      45.20,
    "Amazon RDS":                      28.50,
    "Amazon S3":                        8.30,
    "AWS Lambda":                       3.10,
    "Amazon CloudFront":                5.80,
    "AmazonCloudWatch":                 2.40,
    "AWS Key Management Service":       1.20,
    "Amazon Route 53":                  0.90,
    "AWS Secrets Manager":              0.80,
    "Amazon Simple Notification Service": 0.40,
}

def generate_costs():
    """Add small daily fluctuation to base costs to simulate real usage"""
    for service, base in BASE_COSTS.items():
        # +/- 5% random daily variation
        variation = base * random.uniform(-0.05, 0.05)
        cost_gauge.labels(service=service).set(round(base + variation, 4))

def generate_tags():
    untagged_gauge.labels(resource_type="EC2").set(3)
    untagged_gauge.labels(resource_type="S3").set(1)
    untagged_gauge.labels(resource_type="RDS").set(2)

def generate_anomaly():
    """Simulate a spike every ~5 minutes for demo purposes"""
    minute = int(time.time() / 60) % 10
    anomaly_gauge.set(1 if minute < 2 else 0)

if __name__ == "__main__":
    start_http_server(8001)   # port 8001 so it doesn't conflict
    print("✓ Mock metrics server running on http://localhost:8001/metrics")

    while True:
        generate_costs()
        generate_tags()
        generate_anomaly()
        print("  Mock data refreshed")
        time.sleep(30)