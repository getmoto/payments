get_payment_info = {
    "version": "2.0",
    "routeKey": "GET /payment_info",
    "rawPath": "/api/payment_info",
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "GET",
            "path": "/api/payment_info",
        },
    },
}

admin_get_finance = {
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "GET",
            "path": "/api/admin/finance",
        },
    },
}

admin_get_contributors = {
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "GET",
            "path": "/api/admin/contributors",
        },
    },
}

admin_get_contributor = {
    "rawQueryString": "author=user_name",
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "GET",
            "path": "/api/admin/contributor",
        },
    },
}

admin_invite = {
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "POST",
            "path": "/api/admin/invite",
        },
    },
    "body": '{"username":"user_name","amount":"22","title":"Development Moto","details":"Development of ...", "pr_notification": "1", "pr_text": "some text"}',
}

post_username = {
    "version": "2.0",
    "routeKey": "POST /settings",
    "rawPath": "/api/settings",
    "rawQueryString": "",
    "requestContext": {
        "authorizer": {"lambda": {"username": "bblommers"}},
        "http": {
            "method": "POST",
            "path": "/api/settings",
        },
    },
    "body": '{"oc_username":"bblommers"}',
}
