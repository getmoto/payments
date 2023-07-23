prep_test_env:
	aws route53 create-hosted-zone --name getmoto.org --caller-ref x --endpoint-url http://localhost:5000
	aws ssm put-parameter --name "/moto/payments/tokens/open_collective" --value test --type SecureString --endpoint-url http://localhost:5000
	aws ssm put-parameter --name "/moto/payments/tokens/github" --value gh_token --type SecureString --endpoint-url http://localhost:5000
	aws ssm put-parameter --name "/moto/payments/github/bot/private_key" --value stuff --type SecureString --endpoint-url http://localhost:5000
	aws ssm put-parameter --name "/moto/payments/github/bot/app_id" --value a235 --type SecureString --endpoint-url http://localhost:5000
	aws ssm put-parameter --name "/moto/payments/github/bot/installation_id" --value i789 --type SecureString --endpoint-url http://localhost:5000