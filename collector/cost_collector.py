import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os, json

load_dotenv()

def get_daily_costs():
    client = boto3.client("ce", region_name=os.getenv("AWS_REGION", "us-east-1"))
    end   = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    results = []
    for day in response["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        for group in day["Groups"]:
            service = group["Keys"][0]
            amount  = float(group["Metrics"]["UnblendedCost"]["Amount"])
            results.append({"date": date, "service": service, "cost": amount})

    return results

if __name__ == "__main__":
    data = get_daily_costs()
    print(json.dumps(data[:10], indent=2))