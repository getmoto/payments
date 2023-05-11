from string import Template
from typing import Dict
import json
import urllib3


http = urllib3.PoolManager()


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
              search(query: "repo:getmoto/moto is:pr updated:>$SINCE" type: ISSUE last: 25 $PAGE) {
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
    def _get_pr_page(cls, page, since, token):
        page_ = f"after: \"{page}\"" if page else ""
        query = {"query": QueryGithub.Queries.GET_PULL_REQUESTS.substitute(SINCE=since, PAGE=page_)}
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
            headers={"Authorization": f"bearer {token}"}
        )
        return json.loads(resp.data.decode('utf-8'))
