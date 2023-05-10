from string import Template
import json
import urllib3


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
              search(query: "repo:getmoto/moto is:pr created:2022-12-01..2023-06-01" type: ISSUE last: 10) {
                edges {
                  node {
                    ... on PullRequest {
                      id
                      merged
                      reviewDecision
                      number
                      title
                      updatedAt
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
        resp = urllib3.request(
            "POST",
            QueryGithub.URL,
            body=json.dumps(query),
            headers={"Authorization": f"bearer {token}"}
        )
        return resp.json()["data"]["viewer"]["login"]

    @classmethod
    def get_prs(cls, token: str):
        query = {"query": QueryGithub.Queries.GET_PULL_REQUESTS.substitute()}
        resp = urllib3.request(
            "POST",
            QueryGithub.URL,
            body=json.dumps(query),
            headers={"Authorization": f"bearer {token}"}
        )
        # TODO: add date logic
        return resp.json()["data"]["search"]["edges"]
