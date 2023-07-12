import boto3
import jwt
import json
from moto import mock_ssm
from unittest.mock import patch, Mock
from uuid import uuid4

import cryptography.x509
import cryptography.hazmat.primitives.asymmetric.rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


@mock_ssm
class TestAuthentication:

    @patch.dict("os.environ", {"REGION": "us-east-1", "REPO_OWNER_NAME": "owner/repo"})
    def setup_method(self, *args):
        # Generate Key
        private_key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        self.private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_key_string = self.private_key_bytes.decode("utf-8")
        self.signing_key = jwt.jwk_from_pem(self.private_key_bytes)
        self.ssm = boto3.client("ssm", "us-east-1")
        self.ssm.put_parameter(
            Name="/moto/payments/github/bot/private_key",
            Value=private_key_string,
            Type="SecureString",
        )
        self.app_id = str(uuid4())
        self.ssm.put_parameter(
            Name="/moto/payments/github/bot/app_id",
            Value=self.app_id,
            Type="String",
        )
        self.installation_id = str(uuid4())
        self.ssm.put_parameter(
            Name="/moto/payments/github/bot/installation_id",
            Value=self.installation_id,
            Type="String",
        )

        from backend.github_bot import GithubBot
        self.bot = GithubBot
        self.bot._storage.clear()

    def test_get_jwt_token(self):
        token = self.bot.get_jwt_token(self.private_key_bytes, self.app_id)
        token = jwt.JWT().decode(token, self.signing_key)
        assert "iat" in token
        assert "exp" in token
        assert token["iss"] == self.app_id

    def test_invite_user(self):
        with patch("query_github.http.request", return_value=Mock()) as github_http:
            github_http.return_value.data = json.dumps({"token": "some access token"}).encode("utf-8")
            self.bot.notify_user(pr_number="42", notification_text="some text")

            access_token_url, _ = github_http.call_args_list[0]
            assert access_token_url == ("POST", f"https://api.github.com/app/installations/{self.installation_id}/access_tokens")

            comment_url, comment_details = github_http.call_args_list[1]
            assert comment_url == ("POST", "https://api.github.com/repos/owner/repo/issues/42/comments")
            assert comment_details == {'body': '{"body": "some text"}', 'headers': {'Authorization': 'Bearer some access token'}}

    def test_get_bot_details(self):
        assert self.bot.get_bot_details() == (self.app_id, self.installation_id, self.private_key_bytes)
