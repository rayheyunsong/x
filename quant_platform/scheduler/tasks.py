from apscheduler.schedulers.background import BackgroundScheduler
from quant_platform.data.yfinance_provider import YFinanceProvider
from quant_platform.utils.logger import logger
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

provider = YFinanceProvider()
_latest_cache: dict[str, pd.DataFrame] = {}

def fetch_latest(symbol: str):
    # Use 7-day lookback to ensure data exists
    df = yf.download(symbol, period="7d", interval="1d", progress=False)
    _latest_cache[symbol] = df.tail(1).copy()
    logger.info(f"Fetched latest data for {symbol} rows={len(df)}")

def start_scheduler(symbols: list[str]):
    sched = BackgroundScheduler()
    for sym in symbols:
        sched.add_job(fetch_latest, "interval", minutes=5, args=[sym.strip()], next_run_time=datetime.utcnow())
    sched.start()
    logger.info("BackgroundScheduler started for symbols %s", symbols)
    return sched, _latest_cache
