from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    start = Column(String)
    end = Column(String)
    equity_final = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    results_json = Column(JSON)

def get_engine(db_url="sqlite:///quant.db"):
    return create_engine(db_url, echo=False, future=True)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
