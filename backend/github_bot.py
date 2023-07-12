import boto3
import jwt
import os
import time
from expiring_dict import ExpiringDict
from typing import Tuple
from query_github import QueryGithub


class GithubBot:

    _storage = ExpiringDict(max_len=5, max_age_seconds=60 * 30)  # store things for 30 minutes
    region = os.getenv("REGION")

    ssm = boto3.client("ssm", region)

    @staticmethod
    def notify_user(pr_number: str, notification_text: str) -> None:
        app_id, installation_id, private_key = GithubBot.get_bot_details()
        jwt_token = GithubBot.get_jwt_token(private_key, app_id)
        access_token = GithubBot.get_access_token(installation_id, jwt_token)
        # use REST api to make comment
        QueryGithub.create_comment(access_token, pr_number, notification_text)

    @staticmethod
    def get_jwt_token(private_key, app_id):
        signing_key = jwt.jwk_from_pem(private_key)

        payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + 600,
            'iss': app_id,
        }

        # Create JWT
        jwt_instance = jwt.JWT()
        encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

        return encoded_jwt

    @staticmethod
    def get_bot_details() -> Tuple[str, str, str]:
        if "bot_details" not in GithubBot._storage:
            params = GithubBot.ssm.get_parameters_by_path(Path="/moto/payments/github/bot", WithDecryption=True)["Parameters"]
            app_id = [prm for prm in params if prm["Name"] == "/moto/payments/github/bot/app_id"][0]["Value"]
            installation_id = [prm for prm in params if prm["Name"] == "/moto/payments/github/bot/installation_id"][0]["Value"]
            private_token = [prm for prm in params if prm["Name"] == "/moto/payments/github/bot/private_key"][0]["Value"].encode("utf-8")
            GithubBot._storage["bot_details"] = (app_id, installation_id, private_token)
        return GithubBot._storage["bot_details"]

    @staticmethod
    def get_access_token(installation_id, jwt_token):
        if "access_token" not in GithubBot._storage:
            GithubBot._storage["access_token"] = QueryGithub.get_access_token(installation_id, jwt_token)
        return GithubBot._storage["access_token"]
