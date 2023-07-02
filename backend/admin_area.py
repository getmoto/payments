import boto3
import json
import os
from boto3.dynamodb.conditions import Key


region = os.getenv("REGION")
dynamodb = boto3.resource("dynamodb", region)
payment_table = dynamodb.Table("Payments")
pr_table = dynamodb.Table("PullRequests")
user_table = dynamodb.Table("UserSettings")


def lambda_handler(event, context):
    print(event)
    path, method = get_path_method(event)
    if path == "/api/admin/finance" and method == "GET":

        return {"oc_balance": "TODO", "outstanding": get_outstanding_payments(), "effective_balance": "TODO"}

    return {"message": "Unauthorized"}


def get_outstanding_payments() -> str:
    items = payment_table.scan(
        ProjectionExpression="amount",
        FilterExpression="attribute_not_exists(#processed)",
        ExpressionAttributeNames={"#processed": "processed"}
    )["Items"]
    amount = 0.0
    for item in items:
        amount += float(item["amount"][1:])
    return "${:.2f}".format(amount)


def get_path_method(event):
    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
