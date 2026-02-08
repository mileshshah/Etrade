import json
from requests_oauthlib import OAuth1Session

def get_request_token(consumer_key, consumer_secret, base_url):
    """
    Step 1: Get a request token from E*TRADE.
    """
    request_token_url = f"{base_url}/oauth/request_token"
    # E*TRADE requires oauth_callback="oob" for manual verification
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
        return fetch_response['oauth_token'], fetch_response['oauth_token_secret']
    except Exception as e:
        print(f"Error fetching request token: {e}")
        raise

def get_authorization_url(consumer_key, oauth_token, auth_base_url):
    """
    Step 2: Build the authorization URL for the user to visit.
    """
    return f"{auth_base_url}?key={consumer_key}&token={oauth_token}"

def get_access_token(consumer_key, consumer_secret, oauth_token, oauth_token_secret, verifier, base_url):
    """
    Step 3: Exchange the request token and verifier for an access token.
    """
    access_token_url = f"{base_url}/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=verifier
    )

    try:
        oauth_tokens = oauth.fetch_access_token(access_token_url)
        return oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret']
    except Exception as e:
        print(f"Error fetching access token: {e}")
        raise
