import json
from unittest.mock import patch, Mock
from .api_events import github_approved_prs_result


class TestGithubQueries:

    def test_get_approved_prs(self):
        from backend import query_github

        with patch.object(query_github.http, "request", return_value=Mock()) as mock_http:
            mock_http.return_value.data = json.dumps(github_approved_prs_result).encode("utf-8")

            # Verify user is logged in
            prs = query_github.QueryGithub.get_approved_prs("some token")
            assert len(prs) == 2
            assert {'author': {'login': 'author1'}, 'number': 6460, 'title': 'Title 1'} in prs
            assert {'author': {'login': 'author2'}, 'number': 6449, 'title': 'Title 2'} in prs

            # Verify the correct token was passed
            url, details = mock_http.call_args
            assert ('POST', "https://api.github.com/graphql") == url
            assert details['headers'] == {"Authorization": "bearer some token"}
