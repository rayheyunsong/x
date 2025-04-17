import pandas as pd
from datetime import datetime
from quant_platform.strategy import get_strategy
from quant_platform.data.yfinance_provider import YFinanceProvider
from quant_platform.utils.logger import logger
from quant_platform.broker.base_broker import Order

class RealTimeEngine:
    def __init__(self, symbol, strategy_name, broker, cash=1_000_000, qty=100, **strategy_kwargs):
        self.symbol, self.qty = symbol, qty
        self.strategy_cls = get_strategy(strategy_name)
        self.broker = broker
        self.data = YFinanceProvider()
        self.kw = strategy_kwargs

    def run_once(self):
        # 取近 N 天数据做信号
        df = self.data.fetch(self.symbol, start="2024-01-01", end=None)
        signal = self.strategy_cls(**self.kw).generate_signals(df).iloc[-1]["signal"]
        pos = self.broker.positions().get(self.symbol, 0)

        # === 简单方向判定 ===
        if signal == 1 and pos <= 0:
            logger.info("%s %s BUY %s", datetime.now(), self.symbol, self.qty)
            self.broker.submit(Order(self.symbol, self.qty, "buy"))
        elif signal == -1 and pos >= 0:
            logger.info("%s %s SELL %s", datetime.now(), self.symbol, self.qty)
            self.broker.submit(Order(self.symbol, self.qty, "sell"))
        else:
            logger.info("%s Hold (signal=%s, pos=%s)", self.symbol, signal, pos)