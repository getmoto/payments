import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb", "us-east-1")
table = dynamodb.Table("PullRequests")



def lambda_handler(event, context):
    print(event)
    if event["requestContext"]["http"]["path"] == "/api/pr_info" and event["requestContext"]["http"]["method"] == "GET":
        username = event["requestContext"]["authorizer"]["lambda"]["username"]
        # Appropriate error when not logged in
        # FE Redirect when not logged in
        items = table.query(
            IndexName="query_on_date",
            ScanIndexForward=False,
            KeyConditionExpression=Key("username").eq(username)
        )["Items"]
        return items
    return {"message": "Hi!"}
