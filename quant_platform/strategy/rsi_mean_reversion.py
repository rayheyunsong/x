import pandas as pd
from .base_strategy import BaseStrategy

class RSIMeanReversion(BaseStrategy):
    """RSI mean‑reversion strategy: buy when RSI < low, sell when RSI > high"""
    def __init__(self, period: int = 14, low: int = 30, high: int = 70):
        self.period, self.low, self.high = period, low, high

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(self.period).mean()
        loss = -delta.clip(upper=0).rolling(self.period).mean().replace(0, 1e-9)
        rs = gain / loss
        df['rsi'] = 100 - 100 / (1 + rs)
        df['signal'] = 0
        df.loc[df['rsi'] < self.low, 'signal'] = 1
        df.loc[df['rsi'] > self.high, 'signal'] = -1
        return df
