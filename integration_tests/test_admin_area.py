import boto3
from backend import admin_area
from .lambda_events import admin_get_finance


class TestUserArea:
    def setup_method(self):
        self.ddb = boto3.client(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )
        ddb_resource = boto3.resource(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )

        admin_area.dynamodb = ddb_resource
        admin_area.payment_table = ddb_resource.Table(admin_area.payment_table.name)
        admin_area.user_table = ddb_resource.Table(admin_area.user_table.name)

        # Clean tables to make sure we don't have any shared data between tests
        for item in admin_area.payment_table.scan()["Items"]:
            key = {"username": item["username"], "date_created": item["date_created"]}
            admin_area.payment_table.delete_item(Key=key)

    def test_get_finance_data__no_prs(self):
        resp = admin_area.lambda_handler(admin_get_finance, context=None)
        assert resp == {'effective_balance': 'TODO', 'oc_balance': 'TODO', 'outstanding': '$0.00'}

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
                "amount": {"S": "$25.00"},
            },
        )
        resp = admin_area.lambda_handler(admin_get_finance, context=None)
        assert resp == {'effective_balance': 'TODO', 'oc_balance': 'TODO', 'outstanding': '$50.00'}

    def test_unknown_path(self):
        resp = admin_area.lambda_handler(event={}, context=None)
        assert resp == {'message': 'Unauthorized'}
