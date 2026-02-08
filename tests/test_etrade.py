import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etrade_auth import get_request_token, get_access_token
from etrade_client import ETradeClient

class TestETradeApp(unittest.TestCase):

    @patch('etrade_auth.OAuth1Session')
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

    @patch('etrade_auth.OAuth1Session')
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

    @patch('etrade_client.requests.get')
    def test_list_accounts(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'AccountListResponse': {'Accounts': {'Account': []}}}
        mock_get.return_value = mock_response

        client = ETradeClient('key', 'secret', 'at', 'ats', 'https://api.com')
        accounts = client.list_accounts()

        self.assertEqual(accounts['AccountListResponse']['Accounts']['Account'], [])
        mock_get.assert_called_once()

    @patch('etrade_client.requests.get')
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
        # Verify params
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['instType'], 'BROKERAGE')
        self.assertEqual(kwargs['params']['realTimeNAV'], 'true')

if __name__ == '__main__':
    unittest.main()
