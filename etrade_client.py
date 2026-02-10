import requests
from requests_oauthlib import OAuth1
import json
import time
import random
import string

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

    def view_portfolio(self, account_id_key, count=50, view="QUICK"):
        """
        Fetch portfolio positions for a specific account.
        """
        url = f"{self.base_url}/v1/accounts/{account_id_key}/portfolio.json"
        params = {
            "count": count,
            "view": view
        }
        response = requests.get(url, auth=self.auth, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return {"PortfolioResponse": {"AccountPortfolio": []}}
        else:
            print(f"Error fetching portfolio: {response.status_code} - {response.text}")
            response.raise_for_status()

    def preview_order(self, account_id_key, symbol, action, quantity, price_type="MARKET", limit_price=None):
        """
        Preview an equity order.
        """
        url = f"{self.base_url}/v1/accounts/{account_id_key}/orders/preview.json"

        client_order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        order_detail = {
            "allOrNone": "false",
            "priceType": price_type,
            "orderTerm": "GOOD_FOR_DAY",
            "marketSession": "REGULAR",
            "Instrument": [
                {
                    "Product": {
                        "securityType": "EQ",
                        "symbol": symbol
                    },
                    "orderAction": action,
                    "quantityType": "QUANTITY",
                    "quantity": quantity
                }
            ]
        }

        if price_type == "LIMIT" and limit_price:
            order_detail["limitPrice"] = limit_price

        payload = {
            "PreviewOrderRequest": {
                "orderType": "EQ",
                "clientOrderId": client_order_id,
                "Order": [order_detail]
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, auth=self.auth, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error previewing order: {response.status_code} - {response.text}")
            response.raise_for_status()

    def place_order(self, account_id_key, preview_id, symbol, action, quantity, price_type="MARKET", limit_price=None, client_order_id=None):
        """
        Place an equity order after it has been previewed.
        """
        url = f"{self.base_url}/v1/accounts/{account_id_key}/orders/place.json"

        if not client_order_id:
            client_order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        order_detail = {
            "allOrNone": "false",
            "priceType": price_type,
            "orderTerm": "GOOD_FOR_DAY",
            "marketSession": "REGULAR",
            "Instrument": [
                {
                    "Product": {
                        "securityType": "EQ",
                        "symbol": symbol
                    },
                    "orderAction": action,
                    "quantityType": "QUANTITY",
                    "quantity": quantity
                }
            ]
        }

        if price_type == "LIMIT" and limit_price:
            order_detail["limitPrice"] = limit_price

        payload = {
            "PlaceOrderRequest": {
                "orderType": "EQ",
                "clientOrderId": client_order_id,
                "PreviewIds": [
                    {
                        "previewId": preview_id
                    }
                ],
                "Order": [order_detail]
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, auth=self.auth, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error placing order: {response.status_code} - {response.text}")
            response.raise_for_status()
