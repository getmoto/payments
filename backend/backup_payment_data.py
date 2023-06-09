import boto3
import json
import time
import os
import uuid


s3 = boto3.client("s3", "us-east-1")
bucket_name = os.getenv("BACKUP_BUCKET_NAME")


def handler(event, context):
    records = event["Records"]
    for record in records:
        record.pop("eventID")
        record.pop("eventVersion")
        record.pop("eventSource")
        record.pop("awsRegion")
        record.pop("eventSourceARN")
        record["dynamodb"].pop("SequenceNumber")
        record["dynamodb"].pop("SizeBytes")
        record["dynamodb"].pop("StreamViewType")

    short_form = json.dumps(records, separators=(",", ":"))

    unique_key = f"{time.time()}-{str(uuid.uuid4())[0:6]}"

    s3.put_object(
        Body=short_form,
        Bucket=bucket_name,
        Key=unique_key
    )

    return event
