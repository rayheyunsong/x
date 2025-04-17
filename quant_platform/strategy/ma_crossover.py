import pandas as pd
from .base_strategy import BaseStrategy

class MovingAverageCrossover(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['short_ma'] = df['Close'].rolling(self.short_window).mean()
        df['long_ma'] = df['Close'].rolling(self.long_window).mean()
        df['signal'] = 0
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
        df.loc[df['short_ma'] <= df['long_ma'], 'signal'] = -1
        return df
