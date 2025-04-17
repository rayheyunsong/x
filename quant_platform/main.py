from typer import Typer
from quant_platform.backtest.engine import BacktestEngine

app = Typer(help="CLI for your personal quantitative trading platform")

@app.command()
def backtest(
        symbol: str,
        strategy: str = "ma_crossover",
        start: str = "2020-01-01",
        end: str = "2024-12-31"):
    """Run a simple backtest with the chosen strategy"""
    engine = BacktestEngine(symbol, strategy, start, end)
    engine.run()
    engine.report()

if __name__ == "__main__":
    app()
