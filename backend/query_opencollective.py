from typing import Dict
import json
import urllib3


http = urllib3.PoolManager()


class QueryOpenCollective:

    class Queries:
        GET_BALANCE = """
        query {
          collective(slug: "moto") {
            stats {
              balance {
                value
                currency
              }
            }
          }
        }
    """

    URL = "https://api.opencollective.com/graphql/v2"

    @classmethod
    def get_balance(cls, token: str) -> str:
        query = {"query": QueryOpenCollective.Queries.GET_BALANCE}
        body = cls._execute(query, token)
        value = body["data"]["collective"]["stats"]["balance"]["value"]
        return float(value)

    @classmethod
    def _execute(cls, query: Dict[str, str], token: str):
        resp = http.request(
            "POST",
            QueryOpenCollective.URL,
            body=json.dumps(query),
            headers={"Personal-Token": token, "content-type": "application/json"}
        )
        print(resp.data)
        return json.loads(resp.data.decode('utf-8'))
