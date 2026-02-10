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

def authenticate(config):
    """Orchestrate the OAuth flow."""
    consumer_key = config.get('consumer_key')
    consumer_secret = config.get('consumer_secret')
    base_url = config.get('base_url')
    auth_base_url = config.get('auth_url')

    if not consumer_key or "YOUR" in consumer_key:
        print("Please update config files with your E*TRADE consumer key and secret.")
        sys.exit(1)

    try:
        # Step 1: Get Request Token
        print("Fetching request token...")
        rt, rts = get_request_token(consumer_key, consumer_secret, base_url)

        # Step 2: Authorize
        auth_url = get_authorization_url(consumer_key, rt, auth_base_url)
        print(f"\nPlease visit the following URL in your browser to authorize the application:")
        print(f"---")
        print(f"{auth_url}")
        print(f"---\n")

        verifier = input("Enter the verification code provided by E*TRADE: ").strip()
        if not verifier:
            print("Verification code is required.")
            sys.exit(1)

        # Step 3: Get Access Token
        print("\nFetching access token...")
        at, ats = get_access_token(consumer_key, consumer_secret, rt, rts, verifier, base_url)
        print("Access token obtained successfully.")

        return ETradeClient(consumer_key, consumer_secret, at, ats, base_url)
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)

def list_accounts(client):
    """Fetch and display the account list."""
    print("\nFetching account list...")
    try:
        accounts_data = client.list_accounts()
        accounts = accounts_data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])

        if not accounts:
            print("No accounts found.")
            return []

        print(f"\nFound {len(accounts)} account(s):")
        print(f"{'Name':<25} {'ID':<15} {'Status':<10}")
        print("-" * 50)
        for acc in accounts:
            acc_id = acc.get("accountId")
            acc_name = acc.get("accountName", acc.get("accountDesc", "Unknown"))
            acc_status = acc.get("accountStatus", "Unknown")
            print(f"{acc_name:<25} {acc_id:<15} {acc_status:<10}")
        return accounts
    except Exception as e:
        print(f"Error listing accounts: {e}")
        return []

def view_portfolio(client, accounts):
    """Fetch and display the portfolio for active accounts."""
    portfolio_summary = []
    active_accounts = [a for a in accounts if a.get("accountStatus", "").upper() == "ACTIVE"]

    if not active_accounts:
        print("No active accounts to show portfolio for.")
        return []

    for acc in active_accounts:
        acc_id = acc.get("accountId")
        acc_key = acc.get("accountIdKey")
        acc_name = acc.get("accountName", acc.get("accountDesc", "Unknown"))

        print(f"\n" + "="*80)
        print(f"Portfolio for: {acc_name} (ID: {acc_id})")
        print("-" * 80)

        try:
            portfolio_data = client.view_portfolio(acc_key)
            portfolios = portfolio_data.get("PortfolioResponse", {}).get("AccountPortfolio", [])

            positions_found = False
            for port in portfolios:
                positions = port.get("Position", [])
                if positions:
                    positions_found = True
                    print(f"{'Company':<25} {'Symbol':<10} {'Qty':<8} {'Price Paid':<15} {'Market Value':<15}")
                    print("-" * 80)
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
                            "marketValue": mkt_val,
                            "pricePaid": price_paid
                        })

                        display_company = company
                        if len(display_company) > 22:
                            display_company = display_company[:20] + ".."
                        print(f"{display_company:<25} {symbol:<10} {qty:<8} ${price_paid:<14.2f} ${mkt_val:<14.2f}")

            if not positions_found:
                print("No positions found in this account.")
        except Exception as e:
            print(f"Could not fetch portfolio: {e}")
        print("="*80)

    return portfolio_summary

def chat_with_gemini(gemini, portfolio):
    """Interactive chat with Gemini about the portfolio."""
    if not gemini:
        print("Gemini API key not configured. Cannot chat.")
        return

    if not portfolio:
        print("No portfolio data available to chat about. Please view your portfolio first.")
        return

    print("\n" + "*"*60)
    print("Welcome to Gemini Portfolio Chat!")
    print("Ask Gemini anything about your holdings (or type 'back' to return to menu).")
    print("*"*60)

    while True:
        question = input("\nYou: ").strip()
        if question.lower() == 'back':
            break
        if not question:
            continue

        print("\nGemini is thinking...")
        answer = gemini.chat(portfolio, question)
        print(f"\nGemini: {answer}")

def main_menu():
    # Setup environment
    env = 'sandbox'
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['sandbox', 'prod']:
            env = arg

    config = load_config(env)
    print(f"\n=== E*TRADE {env.upper()} CLI Application ===")

    # Authenticate
    client = authenticate(config)

    # Setup Gemini
    gemini_key = config.get('gemini_api_key')
    gemini = None
    if gemini_key and "YOUR" not in gemini_key:
        gemini = GeminiClient(gemini_key)

    cached_accounts = []
    cached_portfolio = []

    while True:
        print("\n--- Main Menu ---")
        print("1. View Accounts")
        print("2. View Portfolio")
        print("3. Chat with Gemini about Portfolio")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == '1':
            cached_accounts = list_accounts(client)
        elif choice == '2':
            if not cached_accounts:
                cached_accounts = list_accounts(client)
            cached_portfolio = view_portfolio(client, cached_accounts)
        elif choice == '3':
            if not cached_portfolio:
                print("Fetching your portfolio data first for Gemini...")
                if not cached_accounts:
                    cached_accounts = list_accounts(client)
                cached_portfolio = view_portfolio(client, cached_accounts)
            chat_with_gemini(gemini, cached_portfolio)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main_menu()
