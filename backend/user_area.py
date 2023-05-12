# if not username:
#     query username
#     store username + token
# query DynamoDB for PR's
# return pr's

def lambda_handler(event, context):
    if event["http"]["path"] == "/pr_info" and event["http"]["method"] == "GET":
        pass
    return {"message": "Hi!"}
