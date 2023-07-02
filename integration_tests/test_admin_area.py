import boto3
import json
from backend import admin_area
from unittest.mock import patch, Mock
from .lambda_events import admin_get_finance


OPEN_COLLECTIVE_RESPONSE = {
    "data": {
        "collective": {
            "name": "Moto",
            "stats": {
                "balance": {
                    "value": 50.00,
                    "currency": "USD"
                }
            }
        }
    }
}


class TestUserArea:
    def setup_method(self):
        self.ddb = boto3.client(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )
        ddb_resource = boto3.resource(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )
        ssm = boto3.client(
            "ssm", "us-east-1", endpoint_url="http://localhost:5000"
        )

        admin_area.dynamodb = ddb_resource
        admin_area.payment_table = ddb_resource.Table(admin_area.payment_table.name)
        admin_area.user_table = ddb_resource.Table(admin_area.user_table.name)
        admin_area.ssm = ssm

        # Clean tables to make sure we don't have any shared data between tests
        for item in admin_area.payment_table.scan()["Items"]:
            key = {"username": item["username"], "date_created": item["date_created"]}
            admin_area.payment_table.delete_item(Key=key)

    def test_get_finance_data__no_prs(self):
        with patch("query_opencollective.http.request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(OPEN_COLLECTIVE_RESPONSE).encode("utf-8")

            resp = admin_area.lambda_handler(admin_get_finance, context=None)
            assert resp == {'effective_balance': '$50.00', 'oc_balance': "$50.00", 'outstanding': '$0.00'}

    def test_get_finance_data(self):
        self.ddb.put_item(
            TableName="Payments",
            Item={
                "username": {"S": "a1"},
                "date_created": {"S": "b1"},
                "amount": {"S": "$25.00"},
            },
        )
        self.ddb.put_item(
            TableName="Payments",
            Item={
                "username": {"S": "a2"},
                "date_created": {"S": "b2"},
                "amount": {"S": "$100.00"},
                # This item should be skipped, as the 'processed' attribute indicate it is not outstanding
                # PROD values will have a dict with details, but that's irrelevant
                "processed": {"S": "yes"},
            },
        )
        self.ddb.put_item(
            TableName="Payments",
            Item={
                "username": {"S": "a2"},
                "date_created": {"S": "b2"},
                "amount": {"S": "$5.00"},
            },
        )
        with patch("query_opencollective.http.request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(OPEN_COLLECTIVE_RESPONSE).encode("utf-8")

            resp = admin_area.lambda_handler(admin_get_finance, context=None)
            assert resp == {'effective_balance': '$20.00', 'oc_balance': "$50.00", 'outstanding': '$30.00'}

    def test_unknown_path(self):
        resp = admin_area.lambda_handler(event={}, context=None)
        assert resp == {'message': 'Unauthorized'}
