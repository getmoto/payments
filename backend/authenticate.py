# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
# https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow

# extract state from request
# validate state
# extract token from request
# POST https://github.com/login/oauth/access_token
# Accept: application/json
# client_id = ?
# client_secret = ?
# code = ?
# redirect_uri = ?