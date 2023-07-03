api_login_event = {
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/login",
        },
        "requestId": "GX96jiqcDoEEJ8Q=",
    },
}

api_pr_info_event = {
    "identitySource": ["__Host-token=gho_cAHumzvdbT; cookie2=yum; cookie3=ugh"],
    "cookies": ["cookie2=yum", "__Host-token=gho_cAHumzvdbT", "cookie3=ugh"],
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/pr_info",
        },
    },
}

api_status_event = {
    "identitySource": ["__Host-token=gho_cAHumzvdbT; cookie2=yum; cookie3=ugh"],
    "cookies": ["cookie2=yum", "__Host-token=gho_cAHumzvdbT", "cookie3=ugh"],
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/status",
        },
    },
}

api_admin_finance_event = {
    "identitySource": ["__Host-token=gho_cAHumzvdbT; cookie2=yum; cookie3=ugh"],
    "cookies": ["cookie2=yum", "__Host-token=gho_cAHumzvdbT", "cookie3=ugh"],
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/admin/finance",
        },
    },
}

github_oauth_event = {
    "version": "2.0",
    "routeKey": "GET /logged_in",
    "rawPath": "/api/logged_in",
    "rawQueryString": "code=405b3178b880b1999d64&state=Ui01T1l1a3VxeGJRZ2RxNldKNGVHNExWanNCdTFYa2kybHlwM19FMkhQZWNzLUVnOHJQUk5BPT0yYWY0M2U1NS04MGQzLTRjY2YtYTBmOC00OGFiM2I2NzQyYmY%3D",
    "cookies": ["token=at"],
    "queryStringParameters": {
        "code": "405b3178b880b1999d64",
        "state": "Ui01T1l1a3VxeGJRZ2RxNldKNGVHNExWanNCdTFYa2kybHlwM19FMkhQZWNzLUVnOHJQUk5BPT0yYWY0M2U1NS04MGQzLTRjY2YtYTBmOC00OGFiM2I2NzQyYmY=",
    },
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/logged_in",
        },
    },
    "isBase64Encoded": False,
}

dynamodb_records = {
    "Records": [
        {
            "eventID": "0e35235fa66bef9ff61f1c22293c81f0",
            "eventName": "MODIFY",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "ApproximateCreationDateTime": 1684532421.0,
                "Keys": {"pr_nr": {"N": "6312"}, "username": {"S": "bblommers"}},
                "NewImage": {
                    "st": {"S": "uff"},
                    "last_updated": {"S": "2023-05-11T23:12:00Z"},
                    "review": {"S": ""},
                    "isDraft": {"BOOL": False},
                    "merged": {"BOOL": True},
                    "closed": {"BOOL": True},
                    "id": {"S": "PR_kwDOAH5NfM5QORGr"},
                    "state": {"S": "MERGED"},
                    "title": {
                        "S": "SNS: Allow Topic without properties to be deleted using CF"
                    },
                    "pr_nr": {"N": "6312"},
                    "username": {"S": "bblommers"},
                },
                "OldImage": {
                    "last_updated": {"S": "2023-05-11T23:12:00Z"},
                    "review": {"S": ""},
                    "isDraft": {"BOOL": False},
                    "merged": {"BOOL": True},
                    "closed": {"BOOL": True},
                    "id": {"S": "PR_kwDOAH5NfM5QORGr"},
                    "state": {"S": "MERGED"},
                    "title": {
                        "S": "SNS: Allow Topic without properties to be deleted using CF"
                    },
                    "pr_nr": {"N": "6312"},
                    "username": {"S": "bblommers"},
                },
                "SequenceNumber": "22283300000000009849036471",
                "SizeBytes": 390,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
            "eventSourceARN": "arn:aws:dynamodb:us-east-1:193347341732:table/PullRequests/stream/2023-05-19T21:35:03.095",
        }
    ]
}

github_user_response = {
    "login": "my_user_name",
    "id": 60585,
    "node_id": "M=",
    "avatar_url": "https://avatars.githubusercontent.com/u/60585?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/my_user_name",
    "html_url": "https://github.com/my_user_name",
}

github_bad_credentials = {
    "message": "Bad credentials",
    "documentation_url": "https://docs.github.com/rest",
}


github_approved_prs_result = {
    "data": {
        "search": {
            "edges": [
                {
                    "node": {
                        "number": 6460,
                        "title": "Title 1",
                        "author": {"login": "author1"},
                    }
                },
                {
                    "node": {
                        "number": 6449,
                        "title": "Title 2",
                        "author": {"login": "author2"},
                    }
                }
            ]
        }
    }
}
