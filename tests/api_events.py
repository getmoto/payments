api_gw_event = {
    "version": "2.0",
    "type": "REQUEST",
    "routeArn": "arn:aws:execute-api:us-east-1:193347341732:iaq4obbxnd/api/GET/pr_info",
    "identitySource": ["token=at"],
    "routeKey": "GET /pr_info",
    "rawPath": "/api/pr_info",
    "rawQueryString": "",
    "cookies": ["token=at"],
    "headers": {
        "accept-encoding": "gzip",
        "content-length": "0",
        "cookie": "token=at",
        "host": "iaq4obbxnd.execute-api.us-east-1.amazonaws.com",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Amazon CloudFront",
        "via": "2.0 9b77256cb4a2caf313b1650e5e0805f8.cloudfront.net (CloudFront)",
        "x-amz-cf-id": "JFcl6VOiYYuYKkLx5PbdGGtE6IunL9R6AgVqKt1Rt1zp22mciTsnKA==",
        "x-amzn-trace-id": "Root=1-6461524b-36aae9f52033a6a24b43859e",
        "x-forwarded-for": "87.196.72.103, 64.252.170.145",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https",
    },
    "requestContext": {
        "accountId": "193347341732",
        "apiId": "iaq4obbxnd",
        "domainName": "iaq4obbxnd.execute-api.us-east-1.amazonaws.com",
        "domainPrefix": "iaq4obbxnd",
        "http": {
            "method": "GET",
            "path": "/api/pr_info",
            "protocol": "HTTP/1.1",
            "sourceIp": "87.196.72.103",
            "userAgent": "Amazon CloudFront",
        },
        "requestId": "E7nLxggGoAMEYyA=",
        "routeKey": "GET /pr_info",
        "stage": "api",
        "time": "14/May/2023:21:27:39 +0000",
        "timeEpoch": 1684099659054,
    },
}

github_oauth_event = {
    "version": "2.0",
    "routeKey": "GET /logged_in",
    "rawPath": "/api/logged_in",
    "rawQueryString": "code=405b3178b880b1999d64&state=Ui01T1l1a3VxeGJRZ2RxNldKNGVHNExWanNCdTFYa2kybHlwM19FMkhQZWNzLUVnOHJQUk5BPT0yYWY0M2U1NS04MGQzLTRjY2YtYTBmOC00OGFiM2I2NzQyYmY%3D",
    "cookies": ["token=at"],
    "headers": {
        "accept-encoding": "gzip",
        "content-length": "0",
        "host": "iaq4obbxnd.execute-api.us-east-1.amazonaws.com",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "upgrade-insecure-requests": "1",
        "user-agent": "Amazon CloudFront",
        "via": "2.0 5dacd17e64f61e2e81d7dae8a2cf2a9a.cloudfront.net (CloudFront)",
        "x-amz-cf-id": "3G9NruN75Wo2tbHUR76ohq8mQ6XNdmGsAU9mUXQ0srwuiBqigrO-ew==",
        "x-amzn-trace-id": "Root=1-646157d3-402e017215fe83b746872538",
        "x-forwarded-for": "87.196.72.103, 64.252.170.145",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https",
    },
    "queryStringParameters": {
        "code": "405b3178b880b1999d64",
        "state": "Ui01T1l1a3VxeGJRZ2RxNldKNGVHNExWanNCdTFYa2kybHlwM19FMkhQZWNzLUVnOHJQUk5BPT0yYWY0M2U1NS04MGQzLTRjY2YtYTBmOC00OGFiM2I2NzQyYmY=",
    },
    "requestContext": {
        "accountId": "193347341732",
        "apiId": "iaq4obbxnd",
        "domainName": "iaq4obbxnd.execute-api.us-east-1.amazonaws.com",
        "domainPrefix": "iaq4obbxnd",
        "http": {
            "method": "GET",
            "path": "/api/logged_in",
            "protocol": "HTTP/1.1",
            "sourceIp": "87.196.72.103",
            "userAgent": "Amazon CloudFront",
        },
        "requestId": "E7qpIjXloAMEYVw=",
        "routeKey": "GET /logged_in",
        "stage": "api",
        "time": "14/May/2023:21:51:15 +0000",
        "timeEpoch": 1684101075772,
    },
    "isBase64Encoded": False,
}

cf_viewer_request_event = {
    "Records": [
        {
            "cf": {
                "config": {
                    "distributionDomainName": "d1cti9sh1yd63l.cloudfront.net",
                    "distributionId": "E2YANEH09EVOZA",
                    "eventType": "viewer-request",
                    "requestId": "0ea7-_A2MJ89ejWx9a8MPgvVXPl8YuPe9LIW5Sngw389HZ58lf0MlA==",
                },
                "request": {
                    "clientIp": "87.196.72.103",
                    "headers": {
                        "host": [
                            {"key": "Host", "value": "d1cti9sh1yd63l.cloudfront.net"}
                        ],
                        "user-agent": [
                            {
                                "key": "User-Agent",
                                "value": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
                            }
                        ],
                        "accept": [
                            {
                                "key": "accept",
                                "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                            }
                        ],
                        "accept-language": [
                            {"key": "accept-language", "value": "en-GB,en;q=0.5"}
                        ],
                        "accept-encoding": [
                            {"key": "accept-encoding", "value": "gzip, deflate, br"}
                        ],
                        "referer": [
                            {
                                "key": "referer",
                                "value": "https://d1cti9sh1yd63l.cloudfront.net/",
                            }
                        ],
                        "upgrade-insecure-requests": [
                            {"key": "upgrade-insecure-requests", "value": "1"}
                        ],
                        "sec-fetch-dest": [
                            {"key": "sec-fetch-dest", "value": "document"}
                        ],
                        "sec-fetch-mode": [
                            {"key": "sec-fetch-mode", "value": "navigate"}
                        ],
                        "sec-fetch-site": [
                            {"key": "sec-fetch-site", "value": "same-origin"}
                        ],
                        "sec-fetch-user": [{"key": "sec-fetch-user", "value": "?1"}],
                        "te": [{"key": "te", "value": "trailers"}],
                    },
                    "method": "GET",
                    "querystring": "",
                    "uri": "/login.html",
                },
            }
        }
    ]
}
