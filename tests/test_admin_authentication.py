import boto3
import copy
import json

from moto import mock_aws
from unittest.mock import patch, Mock
from .api_events import github_user_response
from .api_events import api_admin_finance_event, api_status_event


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

    def test_auth_for_finance__valid(self):
        from backend import authentication

        token_value = "gho_cAHumzvdbT"
        github_response = copy.deepcopy(github_user_response)
        github_response["login"] = "bblommers"

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_response).encode("utf-8")

            # Verify user is logged in
            resp = authentication.lambda_handler(api_admin_finance_event, context=None)
            assert resp == {"isAuthorized": True, "context": {"username": "bblommers"}}

            # User can call Status endpoint
            resp = authentication.lambda_handler(api_status_event, context=None)
            assert resp["statusCode"] == '200'
            assert resp["headers"] == {'Content-Type': 'application/json'}
            assert resp["body"] == json.dumps({"admin": True})

        # Verify that the access token is temporarily cached
        resp = authentication.lambda_handler(api_admin_finance_event, context=None)
        assert resp == {"isAuthorized": True, "context": {"username": "bblommers"}}

        assert token_value in authentication.valid_access_tokens
        assert authentication.valid_access_tokens[token_value] == "bblommers"

    def test_auth_for_finance__invalid(self):
        from backend import authentication

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_user_response).encode("utf-8")

            # Verify random user is not authorized
            resp = authentication.lambda_handler(api_admin_finance_event, context=None)
            assert resp == {"isAuthorized": False}

        # User is valid, even if we can't access Finance
        assert authentication.valid_access_tokens["gho_cAHumzvdbT"] == "my_user_name"

    def test_valid_user_cant_access_finance(self):
        from backend import authentication

        token_value = "gho_cAHumzvdbT"

        with patch.object(authentication.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_user_response).encode("utf-8")

            # User can call Status endpoint
            resp = authentication.lambda_handler(api_status_event, context=None)
            assert resp["statusCode"] == '200'
            assert resp["headers"] == {'Content-Type': 'application/json'}
            assert resp["body"] == json.dumps({"admin": False})

        # Verify that the access token is temporarily cached
        assert token_value in authentication.valid_access_tokens

        # But user can't access /admin section
        resp = authentication.lambda_handler(api_admin_finance_event, context=None)
        assert resp == {'isAuthorized': False}
