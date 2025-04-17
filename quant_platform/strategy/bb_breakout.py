import pandas as pd
from .base_strategy import BaseStrategy

class BollingerBreakout(BaseStrategy):
    """Bollinger band breakout strategy"""
    def __init__(self, window: int = 20, num_std: float = 2.0):
        self.window, self.num_std = window, num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        ma = df['Close'].rolling(self.window).mean()
        std = df['Close'].rolling(self.window).std()
        upper = ma + self.num_std * std
        lower = ma - self.num_std * std
        df['signal'] = 0
        df.loc[df['Close'] > upper, 'signal'] = 1
        df.loc[df['Close'] < lower, 'signal'] = -1
        return df
