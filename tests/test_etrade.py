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
    def test_get_request_token(self, mock_oauth):
        mock_session = mock_oauth.return_value
        mock_session.fetch_request_token.return_value = {
            'oauth_token': 'fake_rt',
            'oauth_token_secret': 'fake_rts'
        }

        rt, rts = get_request_token('key', 'secret', 'https://api.com')

        self.assertEqual(rt, 'fake_rt')
        self.assertEqual(rts, 'fake_rts')
        mock_session.fetch_request_token.assert_called_once()

    @patch('api.etrade_auth.OAuth1Session')
    def test_get_access_token(self, mock_oauth):
        mock_session = mock_oauth.return_value
        mock_session.fetch_access_token.return_value = {
            'oauth_token': 'fake_at',
            'oauth_token_secret': 'fake_ats'
        }

        at, ats = get_access_token('key', 'secret', 'rt', 'rts', '123', 'https://api.com')

        self.assertEqual(at, 'fake_at')
        self.assertEqual(ats, 'fake_ats')
        mock_session.fetch_access_token.assert_called_once()

    @patch('api.etrade_client.requests.get')
    def test_list_accounts(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'AccountListResponse': {'Accounts': {'Account': []}}}
        mock_get.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        accounts = client.list_accounts()

        self.assertEqual(accounts['AccountListResponse']['Accounts']['Account'], [])
        mock_get.assert_called_once()

    @patch('api.etrade_client.requests.get')
    def test_get_account_balances(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'BalanceResponse': {
                'Computed': {
                    'cashBalance': 1000.50,
                    'cashAvailableForInvestment': 800.00,
                    'realTimeValues': {
                        'totalAccountValue': 5000.00
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        balance = client.get_account_balances('acc_key')

        self.assertEqual(balance['BalanceResponse']['Computed']['cashBalance'], 1000.50)
        self.assertEqual(balance['BalanceResponse']['Computed']['realTimeValues']['totalAccountValue'], 5000.00)
        mock_get.assert_called_once()

    @patch('api.etrade_client.requests.get')
    def test_view_portfolio(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'PortfolioResponse': {
                'AccountPortfolio': [
                    {
                        'Position': [
                            {
                                'Product': {'symbol': 'AAPL', 'securityType': 'EQ'},
                                'symbolDescription': 'APPLE INC COM',
                                'quantity': 10,
                                'pricePaid': 145.50,
                                'price': 150.00,
                                'marketValue': 1500.00
                            }
                        ]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        portfolio = client.view_portfolio('acc_key')

        pos = portfolio['PortfolioResponse']['AccountPortfolio'][0]['Position'][0]
        self.assertEqual(pos['Product']['symbol'], 'AAPL')
        self.assertEqual(pos['symbolDescription'], 'APPLE INC COM')
        self.assertEqual(pos['pricePaid'], 145.50)
        self.assertEqual(pos['marketValue'], 1500.00)
        mock_get.assert_called_once()

    @patch('api.etrade_client.requests.post')
    def test_preview_order(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'PreviewOrderResponse': {
                'Order': [{'Instrument': [{'orderAction': 'BUY'}]}],
                'PreviewIds': [{'previewId': 12345}]
            }
        }
        mock_post.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        preview = client.preview_order('acc_key', 'AAPL', 'BUY', 10)

        self.assertEqual(preview['PreviewOrderResponse']['PreviewIds'][0]['previewId'], 12345)
        mock_post.assert_called_once()

    @patch('api.etrade_client.requests.post')
    def test_place_order(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'PlaceOrderResponse': {
                'OrderIds': [{'orderId': 67890}]
            }
        }
        mock_post.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        place = client.place_order('acc_key', 12345, 'AAPL', 'BUY', 10)

        self.assertEqual(place['PlaceOrderResponse']['OrderIds'][0]['orderId'], 67890)
        mock_post.assert_called_once()

class TestGeminiClient(unittest.TestCase):

    @patch('google.genai.Client')
    def test_analyze_portfolio(self, mock_genai_client):
        mock_client_instance = mock_genai_client.return_value
        mock_response = MagicMock()
        mock_response.text = "Analysis result"
        mock_client_instance.models.generate_content.return_value = mock_response

        client = GeminiClient('fake_api_key')
        # Only symbol, company, and quantity should be present
        result = client.analyze_portfolio([{'symbol': 'AAPL', 'company': 'Apple Inc', 'quantity': 10}])

        self.assertEqual(result, "Analysis result")
        mock_client_instance.models.generate_content.assert_called_once()

    @patch('google.genai.Client')
    def test_chat(self, mock_genai_client):
        mock_client_instance = mock_genai_client.return_value
        mock_response = MagicMock()
        mock_response.text = "Chat result"
        mock_client_instance.models.generate_content.return_value = mock_response

        client = GeminiClient('fake_api_key')
        # Only symbol, company, and quantity should be present
        result = client.chat([{'symbol': 'AAPL', 'company': 'Apple Inc', 'quantity': 10}], "Is Apple a good buy?")

        self.assertEqual(result, "Chat result")
        mock_client_instance.models.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
