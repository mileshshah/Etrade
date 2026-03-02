import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.etrade_auth import get_request_token, get_access_token
from api.etrade_client import ETradeClient
from api.gemini_client import GeminiClient

class TestETradeApp(unittest.TestCase):

    @patch('api.etrade_auth.OAuth1Session')
    def test_get_request_token(self, mock_session):
        mock_instance = mock_session.return_value
        mock_instance.fetch_request_token.return_value = {
            'oauth_token': 'test_token',
            'oauth_token_secret': 'test_secret'
        }

        token, secret = get_request_token('key', 'secret', 'https://api.com')
        self.assertEqual(token, 'test_token')
        self.assertEqual(secret, 'test_secret')

    @patch('api.etrade_auth.OAuth1Session')
    def test_get_access_token(self, mock_session):
        mock_instance = mock_session.return_value
        mock_instance.fetch_access_token.return_value = {
            'oauth_token': 'access_token',
            'oauth_token_secret': 'access_secret'
        }

        token, secret = get_access_token('key', 'secret', 'rt', 'rts', '1234', 'https://api.com')
        self.assertEqual(token, 'access_token')
        self.assertEqual(secret, 'access_secret')

class TestETradeClient(unittest.TestCase):

    @patch('requests.get')
    def test_list_accounts(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"AccountListResponse": {"Accounts": {"Account": []}}}

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        result = client.list_accounts()
        self.assertIn('AccountListResponse', result)

    @patch('requests.get')
    def test_get_account_balances(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"BalanceResponse": {}}

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        result = client.get_account_balances('key1')
        self.assertIn('BalanceResponse', result)

    @patch('requests.get')
    def test_view_portfolio(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"PortfolioResponse": {}}

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        result = client.view_portfolio('key1')
        self.assertIn('PortfolioResponse', result)

    @patch('requests.post')
    def test_preview_order(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"PreviewOrderResponse": {}}

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        result = client.preview_order('key1', 'AAPL', 'BUY', 10)
        self.assertIn('PreviewOrderResponse', result)

    @patch('requests.post')
    def test_place_order(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"PlaceOrderResponse": {}}

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        result = client.place_order('key1', 12345, 'AAPL', 'BUY', 10)
        self.assertIn('PlaceOrderResponse', result)

class TestGeminiClient(unittest.TestCase):

    @patch('api.gemini_client.genai.Client')
    def test_chat(self, mock_genai_client):
        mock_client_instance = mock_genai_client.return_value
        mock_chat = mock_client_instance.chats.create.return_value
        mock_chat.send_message.return_value.text = "Chat result"

        client = GeminiClient('fake_key')
        result = client.chat([{'symbol': 'AAPL'}], 'hello')
        self.assertEqual(result, "Chat result")

if __name__ == '__main__':
    unittest.main()
