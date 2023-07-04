import os
from datetime import datetime, timedelta
from string import Template
from typing import Dict
import json
import urllib3


http = urllib3.PoolManager()
repo_owner_name = os.environ.get("REPO_OWNER_NAME")


class QueryGithub:

    class Queries:
        GET_USER = """
        query {
          viewer {
            login
          }
        }
    """

        GET_PULL_REQUESTS = Template("""
            {
              search(query: "repo:$REPO_OWNER_NAME is:pr updated:>$SINCE" type: ISSUE last: 25 $PAGE) {
                edges {
                  node {
                    ... on PullRequest {
                      id
                      merged
                      reviewDecision
                      number
                      title
                      updatedAt
                      state
                      isDraft
                      closed
                      author {
                        login
                      }
                    }
                  }
                }
                pageInfo {
                  endCursor
                  hasNextPage
                  startCursor
                }
              }
            }
            """)

        GET_APPROVED_PRS = Template("""
            {
              search(query: "repo:$REPO_OWNER_NAME is:pr review:approved updated:>$SINCE" type:ISSUE last:25) {
                edges {
                  node {
                    ... on PullRequest {
                      number
                      title
                      author {
                        login
                      }
                    }
                  }
                }
              }
            }
            """)

        GET_PRS_OF_AUTHOR = Template("""
            {
              search(
                query: "repo:$REPO_OWNER_NAME is:pr review:approved author:$author" type:ISSUE first: 5
              ) {
                edges {
                  node {
                    ... on PullRequest {
                      merged
                      number
                      title
                      updatedAt
                      state
                      isDraft
                      closed
                      labels(first: 10) {
                        edges {
                          node {
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """)

    URL = "https://api.github.com/graphql"

    @classmethod
    def get_current_user(cls, token: str) -> str:
        query = {"query": QueryGithub.Queries.GET_USER}
        body = cls._execute(query, token)
        return body["data"]["viewer"]["login"]

    @classmethod
    def get_prs(cls, token: str, since: str):
        nodes, page = cls._get_pr_page("", since, token)
        while page:
            new_nodes, page = cls._get_pr_page(page, since, token)
            nodes.extend(new_nodes)
        return sorted(nodes, key=lambda y: y["updatedAt"])

    @classmethod
    def get_recent_approved_prs(cls, token: str):
        """
        Returns the 25 most recent Approved PR's from the last 4 weeks
        """
        now = datetime.now()
        four_weeks = now - timedelta(weeks=4)
        query = {"query": QueryGithub.Queries.GET_APPROVED_PRS.substitute(REPO_OWNER_NAME=repo_owner_name, SINCE=four_weeks.strftime("%Y-%m-%d"))}
        result = cls._execute(query, token)["data"]["search"]["edges"]
        return [res["node"] for res in result]

    @classmethod
    def get_prs_for(cls, token: str, author: str):
        query = {"query": QueryGithub.Queries.GET_PRS_OF_AUTHOR.substitute(REPO_OWNER_NAME=repo_owner_name, author=author)}
        resp = cls._execute(query, token)["data"]["search"]["edges"]
        return [n["node"] for n in resp]

    @classmethod
    def create_comment(cls, access_token: str, pr_number: str, notification_text) -> None:
        resp = http.request(
            "POST",
            f"https://api.github.com/repos/{repo_owner_name}/issues/{pr_number}/comments",
            body=json.dumps({"body": notification_text}),
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(resp)
        print(resp.__dict__)

    @classmethod
    def get_access_token(cls, installation_id, jwt_token) -> str:
        resp = http.request(
            "POST",
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        return json.loads(resp.data.decode('utf-8'))["token"]

    @classmethod
    def _get_pr_page(cls, page, since, token):
        page_ = f"after: \"{page}\"" if page else ""
        query = {"query": QueryGithub.Queries.GET_PULL_REQUESTS.substitute(REPO_OWNER_NAME=repo_owner_name, SINCE=since, PAGE=page_)}
        result = cls._execute(query, token)
        if "data" in result:
            new_nodes = [edge["node"] for edge in result["data"]["search"]["edges"]]
            page = result["data"]["search"]["pageInfo"]["endCursor"]
        else:
            new_nodes = []
            page = None
        return new_nodes, page

    @classmethod
    def _execute(cls, query: Dict[str, str], token: str):
        resp = http.request(
            "POST",
            QueryGithub.URL,
            body=json.dumps(query),
            headers={"Authorization": f"Bearer {token}"}
        )
        return json.loads(resp.data.decode('utf-8'))
