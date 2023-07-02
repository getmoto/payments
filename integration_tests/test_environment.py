import boto3


def test_dynamodb():
    ddb = boto3.client("dynamodb", "us-east-1", endpoint_url="http://localhost:5000")
    table_names = ddb.list_tables()["TableNames"]
    assert len(table_names) == 5
    assert "PullRequests" in table_names
    assert "UserSettings" in table_names
    assert "OAuthState" in table_names
    assert "Payments" in table_names
    assert "ScriptExecutionInfo" in table_names


def test_dynamodb__different_region():
    ddb = boto3.client("dynamodb", "us-west-1", endpoint_url="http://localhost:5000")
    assert ddb.list_tables()["TableNames"] == []


def test_apigateway():
    apigw = boto3.client("apigatewayv2", "us-east-1", endpoint_url="http://localhost:5000")
    apis = apigw.get_apis()["Items"]
    api_names = [api["Name"] for api in apis]
    assert api_names == ["payments-api"]


def test_cloudfront():
    cf = boto3.client("cloudfront", "us-east-1", endpoint_url="http://localhost:5000")
    distributions = cf.list_distributions()["DistributionList"]["Items"]
    assert len(distributions) == 1

    # S3 and APIGateway
    assert len(distributions[0]["Origins"]["Items"]) == 2


def test_lambda():
    awslambda = boto3.client("lambda", "us-east-1", endpoint_url="http://localhost:5000")
    functions = awslambda.list_functions()["Functions"]
    function_names = [fn["FunctionName"] for fn in functions]

    assert len(function_names) == 5
    assert "Auth" in function_names
    assert "UserArea" in function_names
    assert "AdminArea" in function_names
    assert "LoadPullRequestInfo" in function_names
    assert "PaymentsTableBackup" in function_names
