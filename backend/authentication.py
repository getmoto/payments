# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
# https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow
import base64
import boto3
import json
import os
import urllib3
from expiring_dict import ExpiringDict
from datetime import datetime, timedelta
from time import time
from uuid import uuid4

state_table_name = "OAuthState"
domain_name = os.getenv("DOMAIN_NAME")
region = os.getenv("REGION")

ssm = boto3.client("ssm", region)
github_client_id = ssm.get_parameter(Name="/moto/payments/github/oauth/client")["Parameter"]["Value"]
github_client_secret = ssm.get_parameter(Name="/moto/payments/github/oauth/secret", WithDecryption=True)["Parameter"]["Value"]

dynamodb = boto3.client("dynamodb", region)

http = urllib3.PoolManager()
redirect_uri = f"https://{domain_name}/api/logged_in"

# Format for the Expiry-attribute in our cookie
RFC1123 = "%a, %d %b %Y %H:%M:%S GMT"
TOKEN_NAME = "__Host-token"

ADMIN_USERS = ["bblommers", "spulec"]


valid_access_tokens = ExpiringDict(max_len=100, max_age_seconds=60)


def lambda_handler(event, context):
    print(event)
    path, method = get_path_method(event)
    if path == "/api/login" and method == "GET":
        request_id = event["requestContext"]["requestId"]

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
            "statusCode": "302",
            "headers": {
                "location": f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_uri}&login=false&state={state}&allow_signup=false",
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

        now = datetime.now()
        later = now + timedelta(days=7)
        return {
            "statusCode": "302",
            "headers": {
                "location": f"https://{domain_name}/payments.html",
                "Set-Cookie": f"{TOKEN_NAME}={access_token}; path=/; expires={later.strftime(RFC1123)}; Secure; HttpOnly; SameSite=Strict"
            }
        }

    if (path in ["/api/pr_info", "/api/payment_info"] and method == "GET") or (path == "/api/settings" and method == "POST"):
        # AUTHORIZER
        #
        # The actual logic is handled by user_area.py - here we just verify whether the user has access
        try:
            token = None
            for cookie in event["identitySource"][0].split(";"):
                if cookie.strip().startswith(f"{TOKEN_NAME}="):
                    token = cookie.split(f"{TOKEN_NAME}=")[-1]
            if not token:
                raise Exception("no")
            if token in valid_access_tokens:
                username = valid_access_tokens[token]
            else:
                resp = http.request(
                    "GET",
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token}"}
                )

                username = json.loads(resp.data.decode('utf-8'))["login"]
                valid_access_tokens[token] = username
            return {
                "isAuthorized": True,
                "context": {
                    "username": username
                }
            }
        except Exception as e:
            print(e)
            return {"isAuthorized": False}

    get_paths = ["/api/admin/finance", "/api/admin/contributors", "/api/admin/contributor"]
    post_paths = ["/api/admin/payment", "/api/admin/payment/retract", "/api/admin/payment/approve"]
    if (path in get_paths and method == "GET") or (path in post_paths and method == "POST"):
        # ADMIN AUTHORIZER
        try:
            token = None
            for cookie in event["identitySource"][0].split(";"):
                if cookie.strip().startswith(f"{TOKEN_NAME}="):
                    token = cookie.split(f"{TOKEN_NAME}=")[-1]
            if not token:
                raise Exception("no token provided")
            if token in valid_access_tokens:
                username = valid_access_tokens[token]
            else:
                resp = http.request(
                    "GET",
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token}"}
                )

                username = json.loads(resp.data.decode('utf-8'))["login"]
                valid_access_tokens[token] = username

            if username not in ADMIN_USERS:
                raise Exception("user not in admin-list")

            return {
                "isAuthorized": True,
                "context": {
                    "username": username
                }
            }
        except Exception as e:
            print(e)
            return {"isAuthorized": False}

    if path in ["/api/status"] and method == "GET":
        try:
            token = None
            for cookie in event["cookies"]:
                if cookie.startswith(f"{TOKEN_NAME}="):
                    token = cookie.split(f"{TOKEN_NAME}=")[-1]
            if not token:
                raise Exception("no")
            if token not in valid_access_tokens:
                resp = http.request(
                    "GET",
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token}"}
                )

                username = json.loads(resp.data.decode('utf-8'))["login"]
                valid_access_tokens[token] = username

            return {"statusCode": "200"}
        except Exception as e:
            return {"statusCode": "403"}

    # Nothing matched
    return {
        "statusCode": "400"
    }

def get_path_method(event):
    try:
        # API Gateway request
        path = event["requestContext"]["http"]["path"]
        method = event["requestContext"]["http"]["method"]
        return path, method
    except:
        pass

    return None, None
