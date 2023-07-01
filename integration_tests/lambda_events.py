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
