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
    if path == "/api/pr_info" and method == "GET":
        username = event["requestContext"]["authorizer"]["lambda"]["username"]
        # Appropriate error when not logged in
        # FE Redirect when not logged in
        items = pr_table.query(
            IndexName="query_on_date",
            ScanIndexForward=False,
            KeyConditionExpression=Key("username").eq(username)
        )["Items"]
        return {"prs": items}

    if path == "/api/payment_info" and method == "GET":
        username = event["requestContext"]["authorizer"]["lambda"]["username"]
        items = payment_table.query(
            ScanIndexForward=False,
            KeyConditionExpression=Key("username").eq(username)
        )["Items"]
        # Get OpenCollective username
        resp = user_table.get_item(Key={"username": username}, ProjectionExpression="oc_username")
        oc_user = resp.get("Item", {}).get("oc_username")
        return {"payments": items, "oc": oc_user}

    if path == "/api/settings" and method == "POST":
        username = event["requestContext"]["authorizer"]["lambda"]["username"]
        oc_username = json.loads(event["body"])["oc_username"]
        user_table.put_item(
            Item={"username": username, "oc_username": oc_username}
        )
        return {}

    return {"message": "Hi!"}

def get_path_method(event):
    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
