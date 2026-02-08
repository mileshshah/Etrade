import json
import os
import sys
from etrade_auth import get_request_token, get_authorization_url, get_access_token
from etrade_client import ETradeClient

# Hardcoded Sandbox URLs to ensure the application only works in the Sandbox environment.
SANDBOX_BASE_URL = "https://apisb.etrade.com"
SANDBOX_AUTH_URL = "https://us.etrade.com/e/t/etws/authorize"

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

    if not consumer_key or consumer_key == "YOUR_CONSUMER_KEY":
        print("Please update config.json with your E*TRADE Sandbox consumer key and secret.")
        return

    try:
        # Step 1: Get Request Token
        print("Step 1: Fetching request token from Sandbox...")
        rt, rts = get_request_token(consumer_key, consumer_secret, SANDBOX_BASE_URL)

        # Step 2: Authorize
        auth_url = get_authorization_url(consumer_key, rt, SANDBOX_AUTH_URL)
        print(f"\nStep 2: Please visit the following URL in your browser to authorize the application:")
        print(f"---")
        print(f"{auth_url}")
        print(f"---\n")

        verifier = input("Enter the verification code provided by E*TRADE: ").strip()
        if not verifier:
            print("Verification code is required.")
            return

        # Step 3: Get Access Token
        print("\nStep 3: Fetching access token from Sandbox...")
        at, ats = get_access_token(consumer_key, consumer_secret, rt, rts, verifier, SANDBOX_BASE_URL)
        print("Access token obtained successfully.")

        # Step 4: Call E*TRADE API
        client = ETradeClient(consumer_key, consumer_secret, at, ats, SANDBOX_BASE_URL)

        print("\nStep 4: Fetching account list from Sandbox...")
        accounts_data = client.list_accounts()

        accounts = accounts_data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])

        if not accounts:
            print("No accounts found in Sandbox.")
            return

        print(f"\nFound {len(accounts)} account(s) in Sandbox:")
        for acc in accounts:
            acc_id = acc.get("accountId")
            acc_key = acc.get("accountIdKey")
            acc_name = acc.get("accountName", acc.get("accountDesc", "Unknown"))
            acc_status = acc.get("accountStatus", "Unknown")

            print(f"\n" + "="*40)
            print(f"Account: {acc_name}")
            print(f"ID:      {acc_id}")
            print(f"Status:  {acc_status}")
            print("-" * 40)

            if acc_status.upper() == "ACTIVE":
                try:
                    balance_data = client.get_account_balances(acc_key)
                    balance = balance_data.get("BalanceResponse", {})

                    computed = balance.get("Computed", {})
                    real_time = computed.get("realTimeValues", {})

                    total_value = real_time.get("totalAccountValue", "N/A")
                    cash_balance = computed.get("cashBalance", "N/A")
                    cash_available = computed.get("cashAvailableForInvestment", "N/A")

                    print(f"Total Account Value:        ${total_value}")
                    print(f"Net Cash Balance:           ${cash_balance}")
                    print(f"Cash Available for Invest:  ${cash_available}")

                    # Check for money market in Cash section
                    cash_section = balance.get("Cash", {})
                    if "moneyMktBalance" in cash_section:
                        print(f"Money Market Balance:       ${cash_section.get('moneyMktBalance')}")

                except Exception as e:
                    print(f"Could not fetch balance for account {acc_id}: {e}")
            else:
                print("Skipping balance fetch for inactive account.")
            print("="*40)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
