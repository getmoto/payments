# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
# https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow
import base64

import boto3
import json
import urllib3
from time import time
from uuid import uuid4

tokens_table_name = "UserTokens"
state_table_name = "OAuthState"

ssm = boto3.client("ssm", "us-east-1")
github_client_id = ssm.get_parameter(Name="/moto/payments/github/oauth/client")["Parameter"]["Value"]
github_client_secret = ssm.get_parameter(Name="/moto/payments/github/oauth/secret", WithDecryption=True)["Parameter"]["Value"]
domain_name = ssm.get_parameter(Name="/moto/payments/domain_name", WithDecryption=False)["Parameter"]["Value"]

dynamodb = boto3.client("dynamodb", "us-east-1")

http = urllib3.PoolManager()
redirect_uri = f"https://{domain_name}/api/logged_in"


def lambda_handler(event, context):
    path, method = get_path_method(event)
    if path == "/login.html" and method == "GET":
        cf_record = event["Records"][0]["cf"]
        request_id = cf_record["config"]["requestId"]

        state = base64.b64encode((request_id + str(uuid4())).encode("utf-8")).decode("utf-8")
        expires = str(int(time() + (60 * 60)))  # one hour from now
        dynamodb.put_item(
            TableName=state_table_name,
            Item={
                "state": {
                    "S": state,
                },
                "expiration": {"N": expires}
            }
        )

        return {
            "status": "302",
            "statusDescription": "Found",
            "headers": {
                "location": [{
                    "key": 'Location',
                    "value": f'https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_uri}&login=false&state={state}&allow_signup=false',
                }],
            }
        }

    if path == "/api/logged_in" and method == "GET":
        code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]

        assert dynamodb.get_item(TableName=state_table_name, Key={"state": {"S": state}})["Item"]["state"]["S"] == state

        body = {
            "client_id": github_client_id,
            "client_secret": github_client_secret,
            "code": code
        }
        resp = http.request(
            "POST",
            "https://github.com/login/oauth/access_token",
            body=json.dumps(body),
            headers={"Accept": "application/json",
                     "Content-Type": "application/json"}
        )
        access_token = json.loads(resp.data.decode('utf-8'))["access_token"]
        # TODO: store access token against username?

        expiry = "Fri, 13-Feb-2032 13:27:44 GMT"
        return {
            "statusCode": "302",
            "headers": {
                "location": f"https://{domain_name}/payments.html",
                "Set-Cookie": f"token={access_token}; path=/; expires={expiry}; secure; HttpOnly; SameSite=None",
            }
        }

    if path == "/api/pr_info" and method == "GET":
        # AUTHORIZE access
        token = event["identitySource"][0].split("token=")[-1]
        resp = http.request(
            "GET",
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"}
        )

        username = json.loads(resp.data.decode('utf-8'))["login"]
        return {
          "isAuthorized": True,
          "context": {
            "username": username
          }
        }

    # Nothing matched
    return {
        "statusCode": "400"
    }

def get_path_method(event):
    try:
        # Lambda@Edge - CloudFront event
        cf_record = event["Records"][0]["cf"]

        path = cf_record["request"]["uri"]
        method = cf_record["request"]["method"]
        return path, method
    except:
        pass

    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
