import boto3
import os
from query_opencollective import QueryOpenCollective


region = os.getenv("REGION")
dynamodb = boto3.resource("dynamodb", region)
payment_table = dynamodb.Table("Payments")
pr_table = dynamodb.Table("PullRequests")
user_table = dynamodb.Table("UserSettings")

ssm = boto3.client("ssm", region)
open_collective_token = None


def lambda_handler(event, context):
    print(event)
    path, method = get_path_method(event)
    if path == "/api/admin/finance" and method == "GET":

        oc_balance = get_oc_balance()
        outstanding_payments = get_outstanding_payments()
        effective_balance = oc_balance - outstanding_payments
        return {"oc_balance": "${:.2f}".format(oc_balance), "outstanding": "${:.2f}".format(outstanding_payments), "effective_balance": "${:.2f}".format(effective_balance)}

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
    return amount


def get_oc_balance():
    global open_collective_token
    if open_collective_token is None:
        open_collective_token = ssm.get_parameter(Name="/moto/payments/tokens/open_collective", WithDecryption=True)["Parameter"]["Value"]
    return QueryOpenCollective.get_balance(open_collective_token)


def get_path_method(event):
    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
