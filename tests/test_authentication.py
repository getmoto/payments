import boto3
from base64 import b64decode
from moto import mock_dynamodb, mock_ssm
from unittest.mock import patch
from .api_events import api_login_event


@mock_dynamodb
@mock_ssm
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
        from backend.authentication import state_table_name
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
