# if not username:
#     query username
#     store username + token
# query DynamoDB for PR's
# return pr's

def lambda_handler(event, context):
    print(event)
    if event["requestContext"]["http"]["path"] == "/api/pr_info" and event["requestContext"]["http"]["method"] == "GET":
        return {"pr": "info"}
    return {"message": "Hi!"}
