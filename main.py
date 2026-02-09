import json
import os
import sys
from etrade_auth import get_request_token, get_authorization_url, get_access_token
from etrade_client import ETradeClient

def load_config(env):
    """Load configuration for the specified environment."""
    filename = f'config_{env}.json'
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{filename} not found. Please create it from the template.")
        sys.exit(1)

def main():
    # Default to sandbox if no argument is provided
    env = 'sandbox'
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['sandbox', 'prod']:
            env = arg
        else:
            print(f"Unknown environment: {arg}. Using 'sandbox' as default.")

    print(f"Starting E*TRADE application in {env.upper()} mode...")

    config = load_config(env)
    consumer_key = config.get('consumer_key')
    consumer_secret = config.get('consumer_secret')
    base_url = config.get('base_url')
    auth_base_url = config.get('auth_url')

    if not consumer_key or "YOUR" in consumer_key:
        print(f"Please update config_{env}.json with your E*TRADE consumer key and secret.")
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

        accounts = accounts_data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])

        if not accounts:
            print("No accounts found.")
            return

        print(f"\nFound {len(accounts)} account(s):")
        for acc in accounts:
            acc_id = acc.get("accountId")
            acc_key = acc.get("accountIdKey")
            acc_name = acc.get("accountName", acc.get("accountDesc", "Unknown"))
            acc_status = acc.get("accountStatus", "Unknown")

            print(f"\n" + "="*60)
            print(f"Account: {acc_name} (ID: {acc_id})")
            print(f"Status:  {acc_status}")
            print("-" * 60)

            if acc_status.upper() == "ACTIVE":
                # Fetch Balance
                try:
                    balance_data = client.get_account_balances(acc_key)
                    balance = balance_data.get("BalanceResponse", {})
                    computed = balance.get("Computed", {})
                    real_time = computed.get("realTimeValues", {})

                    total_value = real_time.get("totalAccountValue", "N/A")
                    cash_balance = computed.get("cashBalance", "N/A")

                    print(f"Total Value: ${total_value} | Cash: ${cash_balance}")
                except Exception as e:
                    print(f"Could not fetch balance: {e}")

                # Fetch Portfolio
                print("-" * 60)
                print("Portfolio Positions:")
                try:
                    portfolio_data = client.view_portfolio(acc_key)
                    portfolios = portfolio_data.get("PortfolioResponse", {}).get("AccountPortfolio", [])

                    positions_found = False
                    for port in portfolios:
                        positions = port.get("Position", [])
                        if positions:
                            positions_found = True
                            print(f"{'Symbol':<10} {'Type':<10} {'Qty':<10} {'Last Price':<12} {'Market Value':<15}")
                            for pos in positions:
                                symbol = pos.get("Product", {}).get("symbol", "N/A")
                                sec_type = pos.get("Product", {}).get("securityType", "N/A")
                                qty = pos.get("quantity", 0)
                                price = pos.get("price", 0)
                                mkt_val = pos.get("marketValue", 0)
                                print(f"{symbol:<10} {sec_type:<10} {qty:<10} ${price:<11.2f} ${mkt_val:<14.2f}")

                    if not positions_found:
                        print("No positions found in this account.")
                except Exception as e:
                    print(f"Could not fetch portfolio: {e}")
            else:
                print("Skipping details for inactive account.")
            print("="*60)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
