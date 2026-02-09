# E*TRADE Python Application

A basic Python application that demonstrates how to authenticate with the E*TRADE API using OAuth 1.0a, fetch account information, and analyze your portfolio using Google Gemini.

## Prerequisites

- Python 3.6 or higher
- An E*TRADE account with API keys (Sandbox or Production)
- A Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/))

## Installation

1. Clone this repository (or copy the files).
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Locate the configuration files: `config_sandbox.json` and `config_prod.json`.
2. Update the appropriate file with your E*TRADE Consumer Key, Consumer Secret, and Gemini API Key:

   ```json
   {
       "consumer_key": "YOUR_CONSUMER_KEY",
       "consumer_secret": "YOUR_CONSUMER_SECRET",
       "base_url": "https://apisb.etrade.com",
       "auth_url": "https://us.etrade.com/e/t/etws/authorize",
       "gemini_api_key": "YOUR_GEMINI_API_KEY"
   }
   ```

## Running the Application

1. Run the main script (defaults to sandbox):

   ```bash
   python main.py
   ```

   To run in production mode:

   ```bash
   python main.py prod
   ```

2. Follow the on-screen instructions:
   - Step 1: The application will fetch a request token.
   - Step 2: It will provide a URL. Copy and paste this URL into your browser.
   - Step 3: Log in to E*TRADE and authorize the application.
   - Step 4: Copy the verification code provided by E*TRADE and paste it back into the terminal.
   - Step 5: The application will fetch the access token, display your account details, and perform a Gemini analysis of your portfolio.

## Testing and Verification

### Automated Tests
To run the suite of unit tests which mock the E*TRADE and Gemini APIs:

```bash
python3 -m unittest tests/test_etrade.py
```

### Manual Verification of Gemini Integration
If you want to verify that the Gemini client is working without using real E*TRADE keys:
1. Ensure your `config_sandbox.json` has a valid `gemini_api_key`.
2. You can temporarily modify `main.py` to bypass Step 1-4 and call `GeminiClient.analyze_portfolio()` with sample data.

### Expected Output
When running successfully, you should see:
- A formatted table of your accounts.
- A detailed list of portfolio holdings (Company, Symbol, Qty, Price, Value).
- A section titled "GEMINI PORTFOLIO INSIGHTS" containing AI-generated analysis of your holdings.

## File Structure

- `main.py`: The entry point that orchestrates the OAuth flow, API calls, and Gemini analysis.
- `etrade_auth.py`: Contains functions for handling the OAuth 1.0a handshake.
- `etrade_client.py`: A client class for making signed requests to E*TRADE API endpoints.
- `gemini_client.py`: A client class for interacting with the Google Gemini API.
- `config_sandbox.json` / `config_prod.json`: Configuration files for API keys and URLs.
- `tests/test_etrade.py`: Unit tests for the authentication, E*TRADE client, and Gemini client logic.
