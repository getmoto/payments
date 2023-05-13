# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
# https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow


import boto3
import json
import os
import urllib3
pr_table_name = os.getenv("TOKENS_TABLE_NAME")

ssm = boto3.client("ssm", "us-east-1")
github_client_id = ssm.get_parameter(Name="/moto/payments/github/oauth/client")["Parameter"]["Value"]
github_client_secret = ssm.get_parameter(Name="/moto/payments/github/oauth/secret", WithDecryption=True)["Parameter"]["Value"]
# TODO: can we pass this as a environment variable?
redirect_uri = "https://d12yfygy3qt5g4.cloudfront.net/api/logged_in"


http = urllib3.PoolManager()


def lambda_handler(event, context):
    print(event)
    try:
        cf_record = event["Records"][0]["cf"]
        request_id = cf_record["config"]["requestId"]
        print(request_id)

        path = cf_record["request"]["uri"]
        method = cf_record["request"]["method"]
        print(f"{method} :: {path}")
        if path == "/login.html" and method == "GET":
            print("login - send 302 to github")
            # LOGIN
            # create state
            # redirect to GET https://github.com/login/oauth/authorize

            return {
                "status": "302",
                "statusDescription": "Found",
                "headers": {
                    "location": [{
                        "key": 'Location',
                        "value": f'https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_uri}&login=false&state=sth&allow_signup=false',
                    }],
                }
            }
        else:
            print("returning 200")
            return {
                "status": "200"
            }
    except:
        print("except")
        # This was not a CF event - which means it was invoked otherwise
        pass


    # LOGGED IN
    print("try logged_in")
    if event.get("requestContext", {}).get("http", {}).get("path") == "/api/logged_in" and event.get("requestContext", {}).get("http", {}).get("method") == "GET":
        print(event.get("queryStringParameters"))
        code = event["queryStringParameters"]["code"]
        state = event["queryStringParameters"]["state"]
        # TODO: verify state is correct
        body = {
            "client_id": github_client_id,
            "client_secret": github_client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        print(body)
        resp = http.request(
            "POST",
            "https://github.com/login/oauth/access_token",
            body=json.dumps(body),
            headers={"Accept": f"application/json"}
        )
        print(resp.data)
        print(resp.status)
        print(resp.headers)
        return {
            "statusCode": "302",
            "headers": {
                "location": "https://d12yfygy3qt5g4.cloudfront.net/payments.html",
                "Set-Cookie": "token=ab; path=/; expires=Fri, 13-Feb-2032 13:27:44 GMT; secure; HttpOnly; SameSite=None",
            }
        }
    # extract state from request
    # validate state
    # extract token from request
    # POST
    # Accept: application/json
    # client_id = ?
    # client_secret = ?
    # code = ?
    # redirect_uri = ?

    print("nothing matched")
    pass

