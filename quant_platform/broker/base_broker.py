from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Order:
    symbol: str
    qty: int
    side: str  # 'buy' or 'sell'
    type: str = "market"

class BaseBroker(ABC):
    @abstractmethod
    def submit(self, order: Order) -> dict: ...

    @abstractmethod
    def positions(self) -> dict: ...
