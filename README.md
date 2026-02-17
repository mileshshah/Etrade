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

## Running Tests

To run the unit tests and verify the logic:

```bash
python3 -m unittest tests/test_etrade.py
```

## File Structure

- `main.py`: The entry point that orchestrates the OAuth flow, API calls, and Gemini analysis.
- `etrade_auth.py`: Contains functions for handling the OAuth 1.0a handshake.
- `etrade_client.py`: A client class for making signed requests to E*TRADE API endpoints.
- `gemini_client.py`: A client class for interacting with the Google Gemini API.
- `config_sandbox.json` / `config_prod.json`: Configuration files for API keys and URLs.
- `tests/test_etrade.py`: Unit tests for the authentication, E*TRADE client, and Gemini client logic.

## Running the API Server

You can also run the application as a RESTful API using FastAPI:

1. Start the server:

   ```bash
   uvicorn api:app --reload
   ```

2. The API will be available at `http://localhost:8000`. You can access the interactive documentation (Swagger UI) at `http://localhost:8000/docs`.

### API Endpoints

- `POST /auth/initialize`: Get the E*TRADE authorization URL.
  - Body: `{"env": "sandbox"}`
- `POST /auth/verify`: Exchange the verifier code for an access token.
  - Body: `{"verifier": "CODE"}`
- `GET /accounts`: List all brokerage accounts.
- `GET /portfolio/{account_id_key}`: View the portfolio for a specific account.
- `POST /order/preview`: Preview an equity order.
  - Body: `{"accountIdKey": "...", "symbol": "AAPL", "orderAction": "BUY", "quantity": 10}`
- `POST /order/place`: Place a previously previewed order.
  - Body: `{"accountIdKey": "...", "previewId": 123456, ...}`
- `POST /gemini/chat`: Ask Gemini questions about your portfolio.
  - Body: `{"accountIdKey": "...", "message": "Explain my risk exposure."}`
