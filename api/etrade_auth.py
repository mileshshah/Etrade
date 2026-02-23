import json
from requests_oauthlib import OAuth1Session

class ETradeAuth:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)

        self.consumer_key = config['consumer_key']
        self.consumer_secret = config['consumer_secret']
        self.base_url = config['base_url']
        self.auth_base_url = config['auth_url']
        self.gemini_api_key = config.get('gemini_api_key')

        self.oauth_token = None
        self.oauth_token_secret = None

    def get_authorization_url(self):
        """
        Step 1 & 2: Get request token and return authorization URL.
        """
        request_token_url = f"{self.base_url}/oauth/request_token"
        oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret, callback_uri='oob')

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
            self.oauth_token = fetch_response['oauth_token']
            self.oauth_token_secret = fetch_response['oauth_token_secret']

            return f"{self.auth_base_url}?key={self.consumer_key}&token={self.oauth_token}"
        except Exception as e:
            print(f"Error fetching request token: {e}")
            raise

    def get_access_token(self, verifier):
        """
        Step 3: Exchange request token and verifier for access token.
        Returns a dictionary of credentials for ETradeClient and GeminiClient.
        """
        access_token_url = f"{self.base_url}/oauth/access_token"
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret,
            verifier=verifier
        )

        try:
            tokens = oauth.fetch_access_token(access_token_url)
            return {
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret,
                "access_token": tokens['oauth_token'],
                "access_token_secret": tokens['oauth_token_secret'],
                "base_url": self.base_url,
                "gemini_api_key": self.gemini_api_key
            }
        except Exception as e:
            print(f"Error fetching access token: {e}")
            raise

# Legacy function support
def get_request_token(consumer_key, consumer_secret, base_url):
    request_token_url = f"{base_url}/oauth/request_token"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')
    fetch_response = oauth.fetch_request_token(request_token_url)
    return fetch_response['oauth_token'], fetch_response['oauth_token_secret']

def get_authorization_url(consumer_key, oauth_token, auth_base_url):
    return f"{auth_base_url}?key={consumer_key}&token={oauth_token}"

def get_access_token(consumer_key, consumer_secret, oauth_token, oauth_token_secret, verifier, base_url):
    access_token_url = f"{base_url}/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=verifier
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    return oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret']
