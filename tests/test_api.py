import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api import app, state

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Reset state before each test
        state.auth = None
        state.client = None
        state.gemini = None
        state.env = "sandbox"
        state.gemini_api_key = None

    @patch('api.ETradeAuth')
    @patch('os.path.exists')
    def test_initialize_auth(self, mock_exists, mock_auth):
        mock_exists.return_value = True
        mock_auth_instance = mock_auth.return_value
        mock_auth_instance.get_authorization_url.return_value = "https://auth.url"

        response = self.client.post("/auth/initialize", json={"env": "sandbox"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authorization_url": "https://auth.url"})
        self.assertEqual(state.env, "sandbox")
        self.assertIsNotNone(state.auth)

    @patch('api.ETradeClient')
    def test_verify_auth(self, mock_client):
        state.auth = MagicMock()
        state.auth.get_access_token.return_value = {"gemini_api_key": "fake_gemini_key"}

        response = self.client.post("/auth/verify", json={"verifier": "1234"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIsNotNone(state.client)
        self.assertEqual(state.gemini_api_key, "fake_gemini_key")

    def test_list_accounts_unauthorized(self):
        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, 401)

    def test_list_accounts_success(self):
        state.client = MagicMock()
        state.client.list_accounts.return_value = [{"accountId": "1"}]

        response = self.client.get("/accounts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"accounts": [{"accountId": "1"}]})

    def test_get_balance_success(self):
        state.client = MagicMock()
        state.client.get_account_balances.return_value = {"BalanceResponse": {}}

        response = self.client.get("/accounts/key1/balance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"balance": {"BalanceResponse": {}}})

    def test_get_portfolio_success(self):
        state.client = MagicMock()
        state.client.view_portfolio.return_value = {"Position": []}

        response = self.client.get("/portfolio/key1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"portfolio": {"Position": []}})

    def test_preview_order_success(self):
        state.client = MagicMock()
        state.client.preview_order.return_value = {"previewId": 123}

        payload = {
            "accountIdKey": "key1",
            "symbol": "AAPL",
            "orderAction": "BUY",
            "quantity": 1
        }
        response = self.client.post("/order/preview", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"previewId": 123})

    @patch('api.GeminiClient')
    def test_gemini_chat(self, mock_gemini):
        state.client = MagicMock()
        # Mocking the portfolio structure returned by ETradeClient
        state.client.view_portfolio.return_value = {
            "PortfolioResponse": {
                "AccountPortfolio": [
                    {
                        "Position": [
                            {
                                "Product": {"symbol": "AAPL"},
                                "symbolDescription": "Apple Inc.",
                                "quantity": 10
                            }
                        ]
                    }
                ]
            }
        }
        state.gemini_api_key = "fake_key"
        state.gemini = mock_gemini.return_value
        state.gemini.chat.return_value = "Nice portfolio!"

        payload = {"accountIdKey": "key1", "message": "hello"}
        response = self.client.post("/gemini/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Nice portfolio!"})

        # Verify filtering: Gemini should be called with filtered data
        expected_data = [{"symbol": "AAPL", "company": "Apple Inc.", "quantity": 10}]
        state.gemini.chat.assert_called_with(expected_data, "hello")

if __name__ == '__main__':
    unittest.main()
