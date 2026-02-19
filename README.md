# E*TRADE Python Application

A robust Python application providing both a Command Line Interface (CLI) and a RESTful API to interact with E*TRADE and analyze portfolios using Google Gemini.

## Features

- **OAuth 1.0a Authentication**: Secure handshake with E*TRADE.
- **Account Management**: List accounts and view real-time balances/cash.
- **Portfolio Insights**: View holdings with original cost and current market value.
- **AI Analysis**: Chat with Google Gemini about your portfolio (with strict data privacy).
- **Order Execution**: Preview and place equity orders (Buy/Sell).
- **REST API**: Full-featured FastAPI service with Swagger UI.

## Prerequisites

- Python 3.6 or higher
- E*TRADE API keys (Sandbox or Production)
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/))

## Installation

1. Clone the repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Update `config_sandbox.json` and `config_prod.json` with your keys:

```json
{
    "consumer_key": "YOUR_KEY",
    "consumer_secret": "YOUR_SECRET",
    "base_url": "https://apisb.etrade.com",
    "auth_url": "https://us.etrade.com/e/t/etws/authorize",
    "gemini_api_key": "YOUR_GEMINI_KEY"
}
```

## Running via CLI

The CLI provides an interactive menu for all features.

1. Start the CLI (defaults to sandbox):

   ```bash
   python main.py
   ```

   For production: `python main.py prod`

2. Follow the prompts to authorize via browser and enter the verifier code.

## Running the API Server

The API server allows other applications to interact with your E*TRADE account.

1. Start the server:

   ```bash
   uvicorn api.server:app --reload
   ```

2. **Swagger UI**: Once the server is running, access the interactive documentation and test endpoints at:
   [http://localhost:8000/docs](http://localhost:8000/docs)

### API Endpoints

- `POST /auth/initialize`: Start OAuth flow.
- `POST /auth/verify`: Complete authentication with verifier code.
- `GET /accounts`: List accounts.
- `GET /accounts/{id}/balance`: Get cash/balances.
- `GET /portfolio/{id}`: View holdings.
- `POST /order/preview`: Preview an order.
- `POST /order/place`: Execute an order.
- `POST /gemini/chat`: Chat with AI about your holdings.

## Testing

Run the automated test suite:

```bash
python3 -m unittest discover tests
```

Run the manual UI/AI simulation:

```bash
python manual_test.py
```
