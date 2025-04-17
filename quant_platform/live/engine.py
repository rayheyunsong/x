from quant_platform.strategy import get_strategy
from quant_platform.data.yfinance_provider import YFinanceProvider
from quant_platform.broker.base_broker import Order
from quant_platform.utils.logger import logger

class LiveEngine:
    """Run strategy in live trading mode in a simple polling loop"""
    def __init__(self, symbol: str, strategy_name: str, broker, strategy_kwargs=None):
        self.symbol = symbol
        self.strategy_cls = get_strategy(strategy_name)
        self.strategy_kwargs = strategy_kwargs or {}
        self.data_provider = YFinanceProvider()
        self.broker = broker

    def run_cycle(self):
        df = self.data_provider.fetch(self.symbol, start="2023-01-01", end=None)
        signal = self.strategy_cls(**self.strategy_kwargs).generate_signals(df).iloc[-1]['signal']
        pos = self.broker.positions().get(self.symbol, 0)
        if signal == 1 and pos <= 0:
            logger.info("LiveEngine BUY 100 %s", self.symbol)
            self.broker.submit(Order(self.symbol, 100, "buy"))
        elif signal == -1 and pos >= 0:
            logger.info("LiveEngine SELL 100 %s", self.symbol)
            self.broker.submit(Order(self.symbol, 100, "sell"))
