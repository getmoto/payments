# Moto Payments

https://payments.getmoto.org/

Companion website that helps us distribute donations, made to Moto, to contributors that have submitted PR's to Moto.


### For maintainers:


To update the infrastructure:
```commandline
cd terraform/envs/prod
terraform init
terraform apply
```


Setting up a new infrastructure:
 - Create a Github OAuth app
 - Create an S3 bucket for the Terraform state, and store the bucket-name in `terraform/envs/NAME/main.tf`
 - Create a HostedZone, and configure the name as the `root_domain`-variable of the `infrastructure`-module
 - Decide on a subdomain, and configure that as the `domain`-variable for the `infrastructure`-module
 - If you run multiple environments in the same AWS account, make sure that the `s3-prefix`-variable is different for each environment
 - Create a Github OAuth token<sup>*1</sup>
 - Create a OpenCollective 'Personal Token' <sup>*2</sup>
 - Create the following SSM parameters in the appropriate region:
   - `/moto/payments/github/oauth/client`
   - `/moto/payments/github/oauth/secret` (SecureString)
   - `/moto/payments/tokens/github` (SecureString)
   - `/moto/payments/tokens/open_collective` (SecureString)

<sup>*1</sup>The GitHub token is required to pull the latest PR's into our own database.
Because all PR info is public, the token does not need any permissions.

<sup>*2</sup>The OpenCollective token is required to fetch the current balance.
Because this information is public, the token does not need any permissions.