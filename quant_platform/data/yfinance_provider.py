import yfinance as yf
import pandas as pd
from .data_provider import DataProvider

class YFinanceProvider(DataProvider):
    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        df = yf.download(symbol, start=start, end=end, progress=False)
        df = df.reset_index()
        return df
