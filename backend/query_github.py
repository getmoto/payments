from string import Template
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


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
              search(
                query: "repo:getmoto/moto is:pr author:$AUTHOR created:2022-12-01..2023-06-01"
                type: ISSUE
                last: 100
              ) {
                edges {
                  node {
                    ... on PullRequest {
                      id
                      merged
                      reviewDecision
                      number
                      title
                    }
                  }
                }
              }
              }
            """)

    URL = "https://api.github.com/graphql"

    def get_current_user(self, token: str) -> str:
        transport = RequestsHTTPTransport(
            url=QueryGithub.URL,
            headers={"Authorization": f"bearer {token}"}
        )

        client = Client(transport=transport)
        return client.execute(gql(QueryGithub.Queries.GET_USER))["viewer"]["login"]

    def get_prs(self, username: str, token: str):
        # TODO: add date logic
        query = gql(
            QueryGithub.Queries.GET_PULL_REQUESTS.substitute(AUTHOR=username)
        )
        transport = RequestsHTTPTransport(
            url=QueryGithub.URL,
            headers={"Authorization": f"bearer {token}"}
        )

        client = Client(transport=transport)
        return client.execute(gql(query))["search"]["edges"]
