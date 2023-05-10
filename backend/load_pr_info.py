# scheduled action

# get known prs from DynamoDB
# Get list of all PR's in the last 6 months
# Update DynamoDB accordingly

import os
from query_github import QueryGithub


def lambda_handler(event, context):
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token is None:
        raise Exception("Please supply a Github Token")

    existing_prs = ...

    list_of_prs = QueryGithub.get_prs(token=github_token)

    transact_items = []
    for pr in list_of_prs:
        print(pr)

    return None
