from abc import ABC, abstractmethod
import pandas as pd

class DataProvider(ABC):
    @abstractmethod
    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Return price data for the symbol between start and end dates"""
