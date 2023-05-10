# scheduled action

# get known prs from DynamoDB
# Get list of all PR's in the last 6 months
# Update DynamoDB accordingly

import os
from .query_github import QueryGithub


def handler_name(event, context):
    if os.getenv("GITHUB_TOKEN") is None:
        raise Exception("Please supply a Github Token")

    existing_prs = ...

    list_of_prs = QueryGithub.get_prs(os.getenv("GITHUB_TOKEN"))

    transact_items = []
    for pr in list_of_prs:
        print(pr)

    return None
