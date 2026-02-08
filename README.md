# E*TRADE Python Application

A basic Python application that demonstrates how to authenticate with the E*TRADE API using OAuth 1.0a and fetch account information.

## Prerequisites

- Python 3.6 or higher
- An E*TRADE account with Sandbox API keys (Consumer Key and Consumer Secret)

## Installation

1. Clone this repository (or copy the files).
2. Install the required dependencies:

   ```bash
   pip install requests requests-oauthlib
   ```

## Configuration

1. Locate the `config.json` file in the root directory.
2. Update the file with your E*TRADE Sandbox Consumer Key and Consumer Secret:

   ```json
   {
       "consumer_key": "YOUR_CONSUMER_KEY",
       "consumer_secret": "YOUR_CONSUMER_SECRET",
       "base_url": "https://apisb.etrade.com",
       "auth_url": "https://us.etrade.com/e/t/etws/authorize"
   }
   ```

## Running the Application

1. Run the main script:

   ```bash
   python main.py
   ```

2. Follow the on-screen instructions:
   - Step 1: The application will fetch a request token.
   - Step 2: It will provide a URL. Copy and paste this URL into your browser.
   - Step 3: Log in to E*TRADE (Sandbox environment) and authorize the application.
   - Step 4: Copy the verification code provided by E*TRADE and paste it back into the terminal.
   - Step 5: The application will fetch the access token and display your account list.

## Running Tests

To run the unit tests and verify the logic:

```bash
python3 -m unittest tests/test_etrade.py
```

## File Structure

- `main.py`: The entry point that orchestrates the OAuth flow and API calls.
- `etrade_auth.py`: Contains functions for handling the OAuth 1.0a handshake.
- `etrade_client.py`: A client class for making signed requests to E*TRADE API endpoints.
- `config.json`: Configuration file for API keys and URLs.
- `tests/test_etrade.py`: Unit tests for the authentication and client logic.
