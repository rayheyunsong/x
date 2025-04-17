from .base_broker import BaseBroker, Order
try:
    from alpaca_trade_api import REST
except ImportError:
    REST = None  # Will raise at runtime

class AlpacaBroker(BaseBroker):
    """Thin wrapper around Alpaca Trade API (v2)"""
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        if REST is None:
            raise ImportError("alpaca-trade-api not installed")
        url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.api = REST(api_key, api_secret, base_url=url, api_version="v2")

    def submit(self, order: Order) -> dict:
        o = self.api.submit_order(order.symbol, order.qty, order.side, order.type, "day")
        return o._raw

    def positions(self) -> dict:
        return {p.symbol: float(p.qty) for p in self.api.list_positions()}
