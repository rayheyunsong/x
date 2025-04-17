from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Annotate data with trading signals"""
