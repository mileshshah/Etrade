import json
import os
import sys
from etrade_auth import get_request_token, get_authorization_url, get_access_token
from etrade_client import ETradeClient
from gemini_client import GeminiClient

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
    gemini_api_key = config.get('gemini_api_key')

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

        portfolio_summary = []

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
                            print(f"{'Company':<25} {'Symbol':<10} {'Qty':<8} {'Price Paid':<15} {'Market Value':<15}")
                            print("-" * 60)
                            for pos in positions:
                                symbol = pos.get("Product", {}).get("symbol", "N/A")
                                company = pos.get("symbolDescription", "N/A")
                                qty = pos.get("quantity", 0)
                                price_paid = pos.get("pricePaid", 0)
                                mkt_val = pos.get("marketValue", 0)

                                portfolio_summary.append({
                                    "symbol": symbol,
                                    "company": company,
                                    "quantity": qty,
                                    "marketValue": mkt_val
                                })

                                # Limit company name length for display
                                display_company = company
                                if len(display_company) > 22:
                                    display_company = display_company[:20] + ".."

                                print(f"{display_company:<25} {symbol:<10} {qty:<8} ${price_paid:<14.2f} ${mkt_val:<14.2f}")

                    if not positions_found:
                        print("No positions found in this account.")
                except Exception as e:
                    print(f"Could not fetch portfolio: {e}")
            else:
                print("Skipping details for inactive account.")
            print("="*60)

        # Step 5: Gemini Analysis
        if gemini_api_key and gemini_api_key != "YOUR_GEMINI_API_KEY" and portfolio_summary:
            print("\nStep 5: Performing Gemini Analysis on Portfolio...")
            gemini = GeminiClient(gemini_api_key)
            analysis = gemini.analyze_portfolio(portfolio_summary)
            print("\n" + "="*60)
            print("GEMINI PORTFOLIO INSIGHTS")
            print("="*60)
            print(analysis)
            print("="*60)
        elif not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY":
            print("\nNote: Gemini API key not configured. Skipping portfolio analysis.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
