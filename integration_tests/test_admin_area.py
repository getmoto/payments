import copy

import boto3
import json
from backend import admin_area, github_bot
from unittest.mock import patch, Mock
from .lambda_events import admin_get_finance, admin_get_contributors, admin_get_contributor
from .lambda_events import admin_invite


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

GITHUB_CONTRIBUTOR_RESPONSE = {
  "data": {
    "search": {
      "edges": [
        {
          "node": {
            "merged": True,
            "number": 6479,
            "title": "Title of PR 1",
            "updatedAt": "2023-07-04T16:59:28Z",
            "state": "MERGED",
            "isDraft": False,
            "closed": True,
            "labels": {
              "edges": []
            }
          }
        }
        ]
    }
  }
}

GITHUB_CONTRIBUTORS_RESPONSE = {
  "data": {
    "search": {
      "edges": [
        {
          "node": {
            "number": 6475,
            "title": "Title of PR 1",
            "author": {"login": "author_1"}
          }},{
          "node": {
            "number": 6476,
            "title": "Title of PR 2",
            "author": {"login": "author_1"}
          }},{
          "node": {
            "number": 6477,
            "title": "Title of PR 3",
            "author": {"login": "author_2"}
          }},{
          "node": {
            "number": 6478,
            "title": "Title of PR 4",
            "author": {"login": "author_3"}
          }
        }
      ]
    }
  }
}


class TestAdminArea:
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
        github_bot.GithubBot.ssm = ssm

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

    def test_get_contributors(self):
        assert admin_area.github_token is None
        with patch("query_github.QueryGithub._execute", return_value=Mock()) as mock_gh:
            mock_gh.return_value = GITHUB_CONTRIBUTORS_RESPONSE

            resp = admin_area.lambda_handler(admin_get_contributors, context=None)
            assert resp == {'author_1': [{'number': 6475, 'title': 'Title of PR 1'},
                                         {'number': 6476, 'title': 'Title of PR 2'}],
                            'author_2': [{'number': 6477, 'title': 'Title of PR 3'}],
                            'author_3': [{'number': 6478, 'title': 'Title of PR 4'}]}

            assert admin_area.github_token == "gh_token"

    def test_get_contributor(self):
        with patch("query_github.QueryGithub._execute", return_value=Mock()) as mock_gh:
            mock_gh.return_value = GITHUB_CONTRIBUTOR_RESPONSE

            resp = admin_area.lambda_handler(admin_get_contributor, context=None)
            assert resp == {'prs': [{'closed': True,
                                      'isDraft': False,
                                      'labels': {'edges': []},
                                      'merged': True,
                                      'number': 6479,
                                      'state': 'MERGED',
                                      'title': 'Title of PR 1',
                                      'updatedAt': '2023-07-04T16:59:28Z'}],
                            "payments": []}

    def test_invite(self):
        with patch("github_bot.GithubBot.notify_user", return_value=Mock()) as github_notifier:
            resp = admin_area.lambda_handler(admin_invite, context=None)
            _, kwargs = github_notifier.call_args
            assert kwargs == {"notification_text": "some text", "pr_number": "1"}
        assert resp == {}

        database_items = admin_area.payment_table.scan()["Items"]
        assert len(database_items) == 1
        assert database_items[0]["username"] == "user_name"
        assert database_items[0]["amount"] == "22"
        assert database_items[0]["title"] == "Development Moto"
        assert database_items[0]["details"] == "Development of ..."
        assert database_items[0]["updatedBy"] == "bblommers"
        assert "date_created" in database_items[0]

        with patch("query_github.QueryGithub._execute", return_value=Mock()) as mock_gh:
            mock_gh.return_value = GITHUB_CONTRIBUTOR_RESPONSE

            resp = admin_area.lambda_handler(admin_get_contributor, context=None)
            assert len(resp["payments"]) == 1
            assert resp["payments"][0]["amount"] == "22"
            assert resp["payments"][0]["details"] == "Development of ..."
            assert resp["payments"][0]["title"] == "Development Moto"

    def test_invite_without_notification(self):
        event = copy.deepcopy(admin_invite)
        body = json.loads(event["body"])
        del body["pr_notification"]
        event["body"] = json.dumps(body)
        resp = admin_area.lambda_handler(event, context=None)
        assert resp == {}

        database_items = admin_area.payment_table.scan()["Items"]
        assert len(database_items) == 1

    def test_unknown_caller(self):
        resp = admin_area.lambda_handler(event={}, context=None)
        assert resp == {'message': 'Unauthorized'}

    def test_unknown_path(self):
        resp = admin_area.lambda_handler(event={"requestContext": {"authorizer": {"lambda": {"username": "asd"}}}}, context=None)
        assert resp == {'message': 'Unknown'}
