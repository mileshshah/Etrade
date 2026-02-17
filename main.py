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
    """Fetch and display the account list with balances."""
    print("\nFetching account list...")
    try:
        accounts_data = client.list_accounts()
        accounts = accounts_data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])

        if not accounts:
            print("No accounts found.")
            return []

        print(f"\nFound {len(accounts)} account(s):")
        print(f"{'Name':<25} {'ID':<15} {'Status':<10} {'Cash / Net Value':<25}")
        print("-" * 80)
        for acc in accounts:
            acc_id = acc.get("accountId")
            acc_key = acc.get("accountIdKey")
            acc_name = acc.get("accountName", acc.get("accountDesc", "Unknown"))
            acc_status = acc.get("accountStatus", "Unknown")

            balance_display = "N/A"
            try:
                bal_data = client.get_account_balances(acc_key)
                bal_resp = bal_data.get("BalanceResponse", {})
                computed = bal_resp.get("Computed", {})
                cash = computed.get("cashAvailableForInvestment", 0)
                net_val = computed.get("netAccountValue", 0)
                balance_display = f"${cash:,.2f} / ${net_val:,.2f}"
            except Exception:
                pass

            print(f"{acc_name:<25} {acc_id:<15} {acc_status:<10} {balance_display:<25}")
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

                        # Restrict data for Gemini to only symbol, company name and quantity
                        portfolio_summary.append({
                            "symbol": symbol,
                            "company": company,
                            "quantity": qty
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

def place_order(client, accounts):
    """Place an order for a stock."""
    active_accounts = [a for a in accounts if a.get("accountStatus", "").upper() == "ACTIVE"]
    if not active_accounts:
        print("No active accounts available for trading.")
        return

    # If multiple accounts, let user choose. For simplicity, use the first one if only one.
    if len(active_accounts) > 1:
        print("\nSelect an account for the order:")
        for i, acc in enumerate(active_accounts):
            print(f"{i+1}. {acc.get('accountName')} ({acc.get('accountId')})")
        acc_choice = int(input("Choice (1-{0}): ".format(len(active_accounts))).strip()) - 1
        selected_account = active_accounts[acc_choice]
    else:
        selected_account = active_accounts[0]

    acc_key = selected_account.get("accountIdKey")
    print(f"\nPlacing order for account: {selected_account.get('accountName')} ({selected_account.get('accountId')})")

    symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
    action = input("Enter action (BUY or SELL): ").strip().upper()
    if action not in ["BUY", "SELL"]:
        print("Invalid action. Use BUY or SELL.")
        return

    try:
        quantity = int(input("Enter quantity: ").strip())
    except ValueError:
        print("Invalid quantity.")
        return

    price_type = input("Enter price type (MARKET or LIMIT): ").strip().upper()
    limit_price = None
    if price_type == "LIMIT":
        try:
            limit_price = float(input("Enter limit price: ").strip())
        except ValueError:
            print("Invalid limit price.")
            return
    elif price_type != "MARKET":
        print("Invalid price type. Use MARKET or LIMIT.")
        return

    # Step 1: Preview Order
    print("\nPreviewing order...")
    try:
        preview_data = client.preview_order(acc_key, symbol, action, quantity, price_type, limit_price)
        preview_response = preview_data.get("PreviewOrderResponse", {})

        # Display preview details
        order_preview = preview_response.get("Order", [{}])[0]
        instr = order_preview.get("Instrument", [{}])[0]
        est_amount = order_preview.get("estimatedTotalAmount", "N/A")
        preview_id = preview_response.get("PreviewIds", [{}])[0].get("previewId")

        print("\n" + "="*40)
        print("ORDER PREVIEW")
        print("-" * 40)
        print(f"Symbol:         {instr.get('Product', {}).get('symbol')}")
        print(f"Action:         {instr.get('orderAction')}")
        print(f"Quantity:       {instr.get('quantity')}")
        print(f"Price Type:     {order_preview.get('priceType')}")
        if limit_price:
            print(f"Limit Price:    ${order_preview.get('limitPrice')}")
        print(f"Est. Total:     ${est_amount}")
        print("="*40)

        confirm = input("\nConfirm order? (yes/no): ").strip().lower()
        if confirm == 'yes':
            # Step 2: Place Order
            print("Placing order...")
            place_data = client.place_order(acc_key, preview_id, symbol, action, quantity, price_type, limit_price)
            order_id = place_data.get("PlaceOrderResponse", {}).get("OrderIds", [{}])[0].get("orderId")
            print(f"Order placed successfully! Order ID: {order_id}")
        else:
            print("Order cancelled.")

    except Exception as e:
        print(f"Error during order process: {e}")

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
        print("1. View Accounts & Balances")
        print("2. View Portfolio")
        print("3. Place Order (Buy/Sell)")
        print("4. Chat with Gemini about Portfolio")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()

        if choice == '1':
            cached_accounts = list_accounts(client)
        elif choice == '2':
            if not cached_accounts:
                cached_accounts = list_accounts(client)
            cached_portfolio = view_portfolio(client, cached_accounts)
        elif choice == '3':
            if not cached_accounts:
                cached_accounts = list_accounts(client)
            place_order(client, cached_accounts)
            # Clear portfolio cache since it might change
            cached_portfolio = []
        elif choice == '4':
            if not cached_portfolio:
                print("Fetching your portfolio data first for Gemini...")
                if not cached_accounts:
                    cached_accounts = list_accounts(client)
                cached_portfolio = view_portfolio(client, cached_accounts)
            chat_with_gemini(gemini, cached_portfolio)
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main_menu()
