import requests
from requests_oauthlib import OAuth1

class ETradeClient:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, base_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = base_url
        # OAuth1 object for signing requests
        self.auth = OAuth1(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
            signature_type='auth_header'
        )

    def list_accounts(self):
        """
        Fetch the list of accounts for the authenticated user.
        """
        url = f"{self.base_url}/v1/accounts/list.json"
        response = requests.get(url, auth=self.auth)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return {"AccountListResponse": {"Accounts": {"Account": []}}}
        else:
            print(f"Error listing accounts: {response.status_code} - {response.text}")
            response.raise_for_status()

    def get_account_balances(self, account_id_key, inst_type="BROKERAGE", real_time_nav=True):
        """
        Fetch balances for a specific account.
        """
        url = f"{self.base_url}/v1/accounts/{account_id_key}/balance.json"
        params = {
            "instType": inst_type,
            "realTimeNAV": "true" if real_time_nav else "false"
        }
        response = requests.get(url, auth=self.auth, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching balances: {response.status_code} - {response.text}")
            response.raise_for_status()