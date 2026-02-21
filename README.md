# E*TRADE API Service

A RESTful API service for interacting with E*TRADE and analyzing portfolios using Google Gemini. This project provides a robust backend to manage accounts, view portfolios, place orders, and get AI-driven insights via a REST API.

## Features

- **OAuth 1.0a Authentication**: Secure handshake with E*TRADE via API endpoints.
- **Account Management**: Retrieve account lists and real-time balances/cash.
- **Portfolio Insights**: Access holdings with cost basis and current market value.
- **AI Integration**: Chat with Google Gemini about portfolio data with strict privacy filtering.
- **Order Execution**: Preview and place equity orders (Buy/Sell) through a secure two-step workflow.
- **Interactive Documentation**: Built-in Swagger UI for easy endpoint exploration and testing.

## Prerequisites

- Python 3.6 or higher
- E*TRADE API keys (Sandbox or Production)
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/))

## Installation

1. Clone the repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Update `config_sandbox.json` or `config_prod.json` with your respective API keys:

```json
{
    "consumer_key": "YOUR_ETRADE_CONSUMER_KEY",
    "consumer_secret": "YOUR_ETRADE_CONSUMER_SECRET",
    "base_url": "https://apisb.etrade.com",
    "auth_url": "https://us.etrade.com/e/t/etws/authorize",
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
}
```

## Running the API Server

Start the FastAPI server using uvicorn:

```bash
uvicorn api.server:app --reload
```

The server will be available at `http://localhost:8000`.

## API Documentation (Swagger UI)

Once the server is running, you can access the interactive Swagger UI to view all available endpoints, see request/response schemas, and test the API directly from your browser:

**[http://localhost:8000/docs](http://localhost:8000/docs)**

### Key Endpoints

- `POST /auth/initialize`: Initiates the OAuth flow and returns the authorization URL.
- `POST /auth/verify`: Completes the authentication using the verifier code from E*TRADE.
- `GET /accounts`: Lists all brokerage accounts.
- `GET /accounts/{id}/balance`: Retrieves real-time balances and cash available.
- `GET /portfolio/{id}`: Returns the current holdings for an account.
- `POST /order/preview`: Previews an equity order.
- `POST /order/place`: Places an order using a `previewId`.
- `POST /gemini/chat`: Sends filtered portfolio data to Gemini for analysis or chat.

## Testing

Run the automated test suite to verify the API and E*TRADE client logic:

```bash
python3 -m unittest discover tests
```

## Data Privacy

This project is designed with financial data privacy in mind. When using the Gemini AI integration, only the `symbol`, `company description`, and `quantity` of your holdings are shared with the AI model. Sensitive metrics like account balances, market values, and prices paid are filtered out before being sent to the AI.
