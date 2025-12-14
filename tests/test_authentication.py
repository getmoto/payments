import boto3
import copy
import json
from base64 import b64decode

from moto import mock_aws
from unittest.mock import patch, Mock
from .api_events import api_login_event, api_pr_info_event, github_user_response
from .api_events import api_status_event
from .api_events import github_bad_credentials


@mock_aws
class TestAuthentication:

    @patch.dict("os.environ", {"REGION": "us-east-1"})
    def setup_method(self, *args):
        ssm = boto3.client("ssm", "us-east-1")
        ssm.put_parameter(
            Name="/moto/payments/github/oauth/client",
            Value="my_client_id",
            Type="String",
        )
        ssm.put_parameter(
            Name="/moto/payments/github/oauth/secret",
            Value="my_client_secret",
            Type="SecureString",
        )
        from backend.authentication import state_table_name, valid_access_tokens
        valid_access_tokens.clear()

        self.ddb = boto3.client("dynamodb", region_name="us-east-1")
        self.ddb.create_table(
            TableName=state_table_name,
            KeySchema=[{"AttributeName": "state", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "state", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    def test_redirect_to_github(self):
        from backend.authentication import lambda_handler, state_table_name
        # Invoke a LOGIN event
        resp = lambda_handler(api_login_event, context=None)

        # We should redirect to GitHub, to authenticate the user
        assert resp["statusCode"] == "302"
        assert resp["headers"]["location"].startswith("https://github.com/login/oauth/authorize?client_id=my_client_id")

        # Ensure the state is persisted in the database
        items = self.ddb.scan(TableName=state_table_name)["Items"]
        assert len(items) == 1
        assert "state" in items[0]
        assert "expiration" in items[0]
        state = items[0]["state"]["S"]
        assert api_login_event["requestContext"]["requestId"] in b64decode(state).decode("utf-8")

    def test_auth_for_pr_info(self):
        from backend import authentication

        token_value = "gho_cAHumzvdbT"
        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_user_response).encode("utf-8")

            # Verify user is logged in
            resp = authentication.lambda_handler(api_pr_info_event, context=None)
            assert resp == {"isAuthorized": True, "context": {"username": "my_user_name"}}

            # Verify the correct token was passed
            request_args = list(mock_http.call_args)
            assert ('GET', "https://api.github.com/user") in request_args
            assert {'headers': {"Authorization": f"Bearer {token_value}"}} in request_args

        # Verify that the access token is temporarily cached
        resp = authentication.lambda_handler(api_pr_info_event, context=None)
        assert resp == {"isAuthorized": True, "context": {"username": "my_user_name"}}

        assert token_value in authentication.valid_access_tokens
        assert authentication.valid_access_tokens[token_value] == "my_user_name"

    def test_auth_for_pr_info__no_cookies(self):
        from backend import authentication

        event = copy.deepcopy(api_pr_info_event)
        event["identitySource"] = []

        # Verify we get the correct response
        # Note that we don't have to mock any URL requests, as we won't get that far
        resp = authentication.lambda_handler(event, context=None)
        assert resp == {"isAuthorized": False}

    def test_auth_for_pr_info__missing_cookies(self):
        from backend import authentication

        event = copy.deepcopy(api_pr_info_event)
        event["identitySource"] = ["cookie=yum; second_cooke=too_much"]

        # Verify we get the correct response
        # Note that we don't have to mock any URL requests, as we won't get that far
        resp = authentication.lambda_handler(event, context=None)
        assert resp == {"isAuthorized": False}

    def test_auth_for_pr_info__cookies_in_different_order(self):
        from backend import authentication

        # Re-arrange the cookies, so that the desired cookie is in the middle
        token_value = "my_unique_token"
        event = copy.deepcopy(api_pr_info_event)
        event["identitySource"] = [f"cookie=yum; __Host-token={token_value}; second_cookie=too_much"]

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_user_response).encode("utf-8")

            # Verify user is logged in
            resp = authentication.lambda_handler(event, context=None)
            assert resp == {"isAuthorized": True, "context": {"username": "my_user_name"}}

            # Verify the correct token was passed
            request_args = list(mock_http.call_args)
            assert ('GET', "https://api.github.com/user") in request_args
            assert {'headers': {"Authorization": f"Bearer {token_value}"}} in request_args

    def test_auth_for_status(self):
        from backend import authentication

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_user_response).encode("utf-8")

            # Verify user is logged in
            resp = authentication.lambda_handler(api_status_event, context=None)
            assert resp["statusCode"] == '200'
            assert resp["headers"] == {'Content-Type': 'application/json'}
            assert resp["body"] == json.dumps({"admin": False})

            # Verify the correct token was passed
            request_args = list(mock_http.call_args)
            assert ('GET', "https://api.github.com/user") in request_args
            assert {'headers': {"Authorization": f"Bearer gho_cAHumzvdbT"}} in request_args

    def test_auth_status__missing_cookie(self):
        from backend import authentication

        event = copy.deepcopy(api_status_event)
        event["cookies"] = []

        # Verify this fails without cookies
        resp = authentication.lambda_handler(event, context=None)
        assert resp == {'statusCode': '403'}

    def test_auth_status__invalid_cookie(self):
        from backend import authentication

        event = copy.deepcopy(api_pr_info_event)
        event["cookies"] = []

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_bad_credentials).encode("utf-8")

            # Verify GH says no
            resp = authentication.lambda_handler(api_status_event, context=None)
            assert resp == {'statusCode': '403'}

    def test_auth_for_unknown_path(self):
        from backend import authentication

        resp = authentication.lambda_handler(event={}, context=None)
        assert resp == {'statusCode': '400'}
