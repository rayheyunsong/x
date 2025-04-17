from pydantic import BaseSettings

class Settings(BaseSettings):
    data_source: str = "yfinance"
    start_cash: float = 1_000_000

settings = Settings()
