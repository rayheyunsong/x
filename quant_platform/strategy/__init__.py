from importlib import import_module

STRATEGIES = {
    "ma_crossover": "quant_platform.strategy.ma_crossover:MovingAverageCrossover",
}

def get_strategy(name: str):
    if name not in STRATEGIES:
        raise ValueError(f"Strategy '{name}' not found. Available: {list(STRATEGIES.keys())}")
    module_path, class_name = STRATEGIES[name].split(":")
    module = import_module(module_path)
    return getattr(module, class_name)

STRATEGIES.update({
    "rsi_mean_reversion": "quant_platform.strategy.rsi_mean_reversion:RSIMeanReversion",
    "bb_breakout": "quant_platform.strategy.bb_breakout:BollingerBreakout",
})
