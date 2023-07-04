import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime
from query_opencollective import QueryOpenCollective
from query_github import QueryGithub
from github_bot import GithubBot


region = os.getenv("REGION")
dynamodb = boto3.resource("dynamodb", region)
payment_table = dynamodb.Table("Payments")
pr_table = dynamodb.Table("PullRequests")
user_table = dynamodb.Table("UserSettings")

ssm = boto3.client("ssm", region)
open_collective_token = None
github_token = None


def lambda_handler(event, context):
    print(event)
    path, method = get_path_method(event)
    try:
        username = event["requestContext"]["authorizer"]["lambda"]["username"]
    except:
        return {"message": "Unauthorized"}

    if path == "/api/admin/finance" and method == "GET":

        oc_balance = get_oc_balance()
        outstanding_payments = get_outstanding_payments()
        effective_balance = oc_balance - outstanding_payments
        return {"oc_balance": "${:.2f}".format(oc_balance), "outstanding": "${:.2f}".format(outstanding_payments), "effective_balance": "${:.2f}".format(effective_balance)}

    if path == "/api/admin/contributors" and method == "GET":
        return get_contributors()

    if path == "/api/admin/contributor" and method == "GET":
        contributor = event["rawQueryString"].split("=")[-1]
        return get_contributor_info(contributor)

    if path == "/api/admin/invite" and method == "POST":
        # Store details in DB
        details = json.loads(event["body"])
        details["updatedBy"] = username
        details["date_created"] = datetime.now().strftime("%Y%m%d%H%M%S")
        payment_table.put_item(Item=details)
        # Notify user
        if details.get("pr_notification"):
            GithubBot.notify_user(pr_number=details["pr_notification"], notification_text=details["pr_text"])
        return {}

    return {"message": "Unknown"}


def get_outstanding_payments() -> str:
    items = payment_table.scan(
        ProjectionExpression="amount",
        FilterExpression="attribute_not_exists(#processed)",
        ExpressionAttributeNames={"#processed": "processed"}
    )["Items"]
    amount = 0.0
    for item in items:
        try:
            amount += float(item["amount"][1:])
        except:
            pass
    return amount


def get_oc_balance():
    global open_collective_token
    if open_collective_token is None:
        open_collective_token = ssm.get_parameter(Name="/moto/payments/tokens/open_collective", WithDecryption=True)["Parameter"]["Value"]
    return QueryOpenCollective.get_balance(open_collective_token)


def get_contributors():
    global github_token
    if github_token is None:
        github_token = ssm.get_parameter(Name="/moto/payments/tokens/github", WithDecryption=True)["Parameter"]["Value"]
    recent_prs = QueryGithub.get_recent_approved_prs(github_token)
    resp = {}
    for pr in recent_prs:
        author = pr["author"]["login"]
        if author in resp:
            resp[author].append({"number": pr["number"], "title": pr["title"]})
        else:
            resp[author] = [{"number": pr["number"], "title": pr["title"]}]
    return resp


def get_contributor_info(contributor):
    global github_token
    if github_token is None:
        github_token = ssm.get_parameter(Name="/moto/payments/tokens/github", WithDecryption=True)["Parameter"]["Value"]
    payments = payment_table.query(
        ScanIndexForward=False,
        KeyConditionExpression=Key("username").eq(contributor)
    )["Items"]
    prs = QueryGithub.get_prs_for(github_token, contributor)
    return {"prs": prs, "payments": payments}


def get_path_method(event):
    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
