# scheduled action

# get known prs from DynamoDB
# check when this script was last run
# Get list of all PR's updated since
# Update DynamoDB accordingly

import boto3
import os
from query_github import QueryGithub


dynamodb = boto3.client("dynamodb", "us-east-1")
pr_table_name = os.getenv("PR_TABLE_NAME")
script_info_table_name = os.getenv("SCRIPT_INFO_TABLE_NAME")


def lambda_handler(event, context):
    # Get from SecretsManager? that way we can keep the value permanently
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise Exception("Please supply a Github Token")

    existing_items = dynamodb.scan(
        TableName=pr_table_name,
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="pr_nr",
    )["Items"]
    existing_prs = [item["pr_nr"]["N"] for item in existing_items]
    print(f"Found {len(existing_prs)} existing PR's...")

    script_info = dynamodb.get_item(
        TableName=script_info_table_name,
        Key={
            "script_name": {"S": "LOAD_PR_INFO"}
        }
    )["Item"]
    get_prs_since = script_info["earliest_modify_date"]["S"]
    if script_info.get("latest_date_processed", {}).get("S"):
        get_prs_since = script_info["latest_date_processed"]["S"]

    list_of_prs = QueryGithub.get_prs(token=github_token, since=get_prs_since)
    print(f"Processing {len(list_of_prs)} PRs")
    # we have a sorted list
    # but we can only create transactions of 25 at the time
    sublists = [list_of_prs[x:x + 25] for x in range(0, len(list_of_prs), 25)]

    for sublist in sublists:
        transact_items = []
        for pr in sublist:
            user_name = pr["author"]["login"]
            pr_nr = str(pr["number"])
            review = pr["reviewDecision"] or ""
            updated_at = pr["updatedAt"]
            if pr_nr in existing_items:
                # A field has been updated - we don't know which one, so just re-set everything
                dynamodb.update_item(
                    TableName=pr_table_name,
                    Key={
                        "username": {"S": user_name},
                        "pr_nr": {"S": pr_nr},
                    },
                    UpdateExpression="SET last_updated=:upd, merged = :mrgd, title=:title, state=:state, isDraft=:draft, closed=:closed, review=:review",
                    ExpressionAttributeValues={
                        ":upd": {"S": updated_at},
                        ":mrgd": {"BOOL": pr["merged"]},
                        ":title": {"S": pr["title"]},
                        ":state": {"S": pr["state"]},
                        ":draft": {"BOOL": pr["isDraft"]},
                        ":closed": {"BOOL": pr["closed"]},
                        ":review": {"S": review},
                    },
                )
            else:
                transact_items.append({
                    "PutRequest": {
                        "Item": {
                            "username": {"S": user_name},
                            "pr_nr": {"N": pr_nr},
                            "last_updated": {"S": updated_at},
                            "id": {"S": pr["id"]},
                            "merged": {"BOOL": pr["merged"]},
                            "title": {"S": pr["title"]},
                            "state": {"S": pr["state"]},
                            "isDraft": {"BOOL": pr["isDraft"]},
                            "closed": {"BOOL": pr["closed"]},
                            "review": {"S": review}
                        }
                    }
                })
        dynamodb.batch_write_item(
            RequestItems={
                pr_table_name: transact_items
            }
        )
        # Quick status update so that we don't have to deal with these items again next time
        dynamodb.update_item(
            TableName=script_info_table_name,
            Key={
                "script_name": {"S": "LOAD_PR_INFO"},
            },
            UpdateExpression="SET #attr = :val",
            ExpressionAttributeNames={"#attr": "latest_date_processed"},
            ExpressionAttributeValues={":val": {"S": pr["updatedAt"]}},
        )
        print(f"set latest date to {pr['updatedAt']}")

    return None
