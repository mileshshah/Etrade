from typing import Optional, Dict, Any

class TradingTools:
    def __init__(self, etrade_client):
        self.client = etrade_client

    def preview_etrade_trade(self, accountIdKey: str, symbol: str, orderAction: str, quantity: int, priceType: str = "MARKET") -> str:
        """
        Preview an equity trade (BUY or SELL) using the E*TRADE API to get an estimated total and previewId.

        Args:
            accountIdKey: The key identifier for the user's account.
            symbol: The stock symbol (e.g., 'AAPL', 'TSLA').
            orderAction: Either 'BUY' or 'SELL'.
            quantity: The number of shares.
            priceType: Either 'MARKET' (default) or 'LIMIT'.

        Returns:
            A string summary of the trade preview including total estimate and previewId.
        """
        try:
            preview = self.client.preview_order(accountIdKey, symbol, orderAction.upper(), quantity, priceType.upper())
            if preview:
                order_resp = preview.get('PreviewOrderResponse', {})
                instr = order_resp.get('Order', [{}])[0].get('Instrument', [{}])[0]
                preview_id = order_resp.get('PreviewIds', [{}])[0].get('previewId')
                total = order_resp.get('Order', [{}])[0].get('estimatedTotalAmount', 'N/A')

                return f"PREVIEW SUCCESSFUL:\nAction: {instr.get('orderAction')}\nSymbol: {instr.get('Product', {}).get('symbol')}\nQty: {instr.get('quantity')}\nEst. Total: ${total}\nPreview ID: {preview_id}"
            return "Preview failed: No response from E*TRADE."
        except Exception as e:
            return f"Preview failed error: {str(e)}"

    def place_etrade_trade(self, accountIdKey: str, previewId: int, symbol: str, orderAction: str, quantity: int, priceType: str = "MARKET") -> str:
        """
        Execute/Place a trade that has been previously previewed and has a valid previewId.

        Args:
            accountIdKey: The key identifier for the user's account.
            previewId: The previewId obtained from a preview_etrade_trade call.
            symbol: The stock symbol (e.g., 'AAPL').
            orderAction: Either 'BUY' or 'SELL'.
            quantity: The number of shares.
            priceType: Either 'MARKET' or 'LIMIT'.

        Returns:
            A string summary of the order placement status and the orderId.
        """
        try:
            result = self.client.place_order(accountIdKey, previewId, symbol.upper(), orderAction.upper(), quantity, priceType.upper())
            if result:
                order_id = result.get('PlaceOrderResponse', {}).get('OrderIds', [{}])[0].get('orderId')
                return f"ORDER PLACED SUCCESSFULLY:\nOrder ID: {order_id}"
            return "Order placement failed: No response from E*TRADE."
        except Exception as e:
            return f"Order placement error: {str(e)}"
