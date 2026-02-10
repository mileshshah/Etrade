import json
import os
from gemini_client import GeminiClient

def load_gemini_key():
    """Attempt to load Gemini key from any available config file."""
    for filename in ['config_sandbox.json', 'config_prod.json']:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                    key = config.get('gemini_api_key')
                    if key and "YOUR" not in key:
                        return key
            except:
                continue
    return None

def main():
    print("=== E*TRADE Application Manual Test ===")
    print("This script simulates the portfolio display and Gemini analysis using sample data.\n")

    # Sample Data
    sample_portfolio = [
        {"symbol": "AAPL", "company": "Apple Inc", "quantity": 10, "marketValue": 1800.50, "pricePaid": 150.00},
        {"symbol": "TSLA", "company": "Tesla Inc", "quantity": 5, "marketValue": 1200.00, "pricePaid": 210.00},
        {"symbol": "NVDA", "company": "NVIDIA Corporation", "quantity": 2, "marketValue": 1600.00, "pricePaid": 450.00}
    ]

    # Display Simulation
    print("Simulated Portfolio Display:")
    print(f"{'Company':<25} {'Symbol':<10} {'Qty':<8} {'Price Paid':<15} {'Market Value':<15}")
    print("-" * 80)
    for pos in sample_portfolio:
        company = pos['company']
        if len(company) > 22:
            company = company[:20] + ".."
        print(f"{company:<25} {pos['symbol']:<10} {pos['quantity']:<8} ${pos['pricePaid']:<14.2f} ${pos['marketValue']:<14.2f}")
    print("-" * 80)

    # Gemini Integration Test
    gemini_key = load_gemini_key()
    if gemini_key:
        print("\nGemini API Key found. Performing analysis...")
        gemini = GeminiClient(gemini_key)
        # Reformat for the client as main.py does: Restrict to symbol, company, and quantity
        analysis_input = [{"symbol": p["symbol"], "company": p["company"], "quantity": p["quantity"]} for p in sample_portfolio]
        analysis = gemini.analyze_portfolio(analysis_input)
        print("\n" + "="*60)
        print("GEMINI PORTFOLIO INSIGHTS (SIMULATED)")
        print("="*60)
        print(analysis)
        print("="*60)
    else:
        print("\nNote: Gemini API key not found or still set to default in config files.")
        print("To test the AI integration, add your key to config_sandbox.json or config_prod.json.")

if __name__ == "__main__":
    main()
