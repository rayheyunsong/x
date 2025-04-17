import pandas as pd
import matplotlib.pyplot as plt
from quant_platform.data.yfinance_provider import YFinanceProvider
from quant_platform.strategy import get_strategy

class BacktestEngine:
    def __init__(self, symbol: str, strategy_name: str, start: str, end: str, *, strategy_kwargs=None):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.strategy_class = get_strategy(strategy_name)
        self.strategy_kwargs = strategy_kwargs or {}
        self.data_provider = YFinanceProvider()
        self.results: pd.DataFrame | None = None

    def run(self):
        data = self.data_provider.fetch(self.symbol, self.start, self.end)
        strategy = self.strategy_class(**self.strategy_kwargs)
        df = strategy.generate_signals(data)

        df['returns'] = df['Close'].pct_change()
        df['strategy'] = df['signal'].shift(1) * df['returns']
        df['equity_curve'] = (1 + df['strategy'].fillna(0)).cumprod()
        self.results = df

    def report(self):
        if self.results is None:
            raise RuntimeError("Run backtest first!")
        tail = self.results[['Date', 'equity_curve']].tail()
        print(tail.to_string(index=False))
        self.results.set_index('Date')['equity_curve'].plot(
            title=f"{self.symbol} equity curve ({self.strategy_class.__name__})"
        )
        plt.show()
