# Quant Platform

A minimal, extensible quantitative trading platform scaffold.

## Quick Start

```bash
# Clone / extract this project
cd quant_platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run a sample backtest
quant-platform backtest --symbol AAPL --start 2022-01-01 --end 2024-12-31
```

## Packaging

```bash
pip install build
python -m build  # Generates wheel in dist/
```

## Adding new strategies

1. Create a new file in `quant_platform/strategy/`.
2. Inherit from `BaseStrategy` and implement `generate_signals`.
3. Register your strategy in `quant_platform/strategy/__init__.py`.
