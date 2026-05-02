import boto3
from dotenv import load_dotenv
import os

load_dotenv()
REQUIRED_TAGS = ["Environment", "Owner", "Project"]

def check_ec2_tags():
    ec2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
    instances = ec2.describe_instances()
    untagged = []

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            if instance["State"]["Name"] == "terminated":
                continue
            tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
            missing = [t for t in REQUIRED_TAGS if t not in tags]
            if missing:
                untagged.append({
                    "resource_type": "EC2",
                    "resource_id": instance["InstanceId"],
                    "missing_tags": missing
                })
    return untagged

def check_s3_tags():
    s3 = boto3.client("s3")
    untagged = []
    buckets = s3.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]
        try:
            tags_resp = s3.get_bucket_tagging(Bucket=name)
            tags = {t["Key"]: t["Value"] for t in tags_resp.get("TagSet", [])}
        except s3.exceptions.ClientError:
            tags = {}
        missing = [t for t in REQUIRED_TAGS if t not in tags]
        if missing:
            untagged.append({"resource_type": "S3", "resource_id": name, "missing_tags": missing})

    return untagged

def get_all_untagged():
    return check_ec2_tags() + check_s3_tags()

if __name__ == "__main__":
    results = get_all_untagged()
    for r in results:
        print(r)