import boto3
from backend import user_area
from .lambda_events import get_payment_info, post_username


class TestUserArea:
    def setup_method(self):
        self.ddb = boto3.client(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )
        ddb_resource = boto3.resource(
            "dynamodb", "us-east-1", endpoint_url="http://localhost:5000"
        )

        user_area.dynamodb = ddb_resource
        user_area.payment_table = ddb_resource.Table(user_area.payment_table.name)
        user_area.user_table = ddb_resource.Table(user_area.user_table.name)

        # Clean tables to make sure we don't have any shared data between tests
        for item in user_area.user_table.scan()["Items"]:
            user_area.user_table.delete_item(Key={"username": item["username"]})

        for item in user_area.payment_table.scan()["Items"]:
            key = {"username": item["username"], "date_created": item["date_created"]}
            user_area.payment_table.delete_item(Key=key)

    def test_user_without_any_data(self):
        resp = user_area.lambda_handler(get_payment_info, context=None)
        assert resp == {"payments": [], "oc": None}

    def test_user_with_oc_setting(self):
        self.ddb.put_item(
            TableName="UserSettings",
            Item={"username": {"S": "bblommers"}, "oc_username": {"S": "bblommers_oc"}},
        )

        resp = user_area.lambda_handler(get_payment_info, context=None)
        assert resp == {"payments": [], "oc": "bblommers_oc"}

    def test_user_with_payment_info(self):
        self.ddb.put_item(
            TableName="Payments",
            Item={
                "username": {"S": "bblommers"},
                "date_created": {"S": "20230524215900"},
                "amount": {"S": "$25.00"},
                "details": {"S": "test details"},
                "title": {"S": "Development Moto"},
            },
        )

        resp = user_area.lambda_handler(get_payment_info, context=None)
        assert resp == {
            "payments": [
                {
                    "amount": "$25.00",
                    "date_created": "20230524215900",
                    "details": "test details",
                    "title": "Development Moto",
                    "username": "bblommers",
                }
            ],
            "oc": None,
        }

    def test_post_opencollective_username(self):
        resp = user_area.lambda_handler(post_username, context=None)
        assert resp == {}

        resp = user_area.lambda_handler(get_payment_info, context=None)
        assert resp == {"payments": [], "oc": "bblommers"}
