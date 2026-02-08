import json
import os
import sys
from etrade_auth import get_request_token, get_authorization_url, get_access_token
from etrade_client import ETradeClient

def load_config():
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found. Please create it from the template.")
        sys.exit(1)

def main():
    config = load_config()
    consumer_key = config.get('consumer_key')
    consumer_secret = config.get('consumer_secret')
    base_url = config.get('base_url', 'https://apisb.etrade.com')
    auth_base_url = config.get('auth_url', 'https://us.etrade.com/e/t/etws/authorize')

    if not consumer_key or consumer_key == "YOUR_CONSUMER_KEY":
        print("Please update config.json with your E*TRADE consumer key and secret.")
        return

    try:
        # Step 1: Get Request Token
        print("Step 1: Fetching request token...")
        rt, rts = get_request_token(consumer_key, consumer_secret, base_url)

        # Step 2: Authorize
        auth_url = get_authorization_url(consumer_key, rt, auth_base_url)
        print(f"\nStep 2: Please visit the following URL in your browser to authorize the application:")
        print(f"---")
        print(f"{auth_url}")
        print(f"---\n")

        verifier = input("Enter the verification code provided by E*TRADE: ").strip()
        if not verifier:
            print("Verification code is required.")
            return

        # Step 3: Get Access Token
        print("\nStep 3: Fetching access token...")
        at, ats = get_access_token(consumer_key, consumer_secret, rt, rts, verifier, base_url)
        print("Access token obtained successfully.")

        # Step 4: Call E*TRADE API
        client = ETradeClient(consumer_key, consumer_secret, at, ats, base_url)

        print("\nStep 4: Fetching account list...")
        accounts_data = client.list_accounts()
        print("\nAccount List Response:")
        print(json.dumps(accounts_data, indent=2))

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
