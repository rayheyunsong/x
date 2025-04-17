import asyncio, nest_asyncio
asyncio.set_event_loop(asyncio.new_event_loop())   # 给 ScriptRunner 线程建 loop
nest_asyncio.apply()                               # 允许嵌套事件循环  (ib_insync 需要)

import streamlit as st
try:
    from quant_platform.broker.ibkr_broker import IBKRBroker
except ModuleNotFoundError:
    IBKRBroker = None      # Cloud 环境没有此模块也能运行

if IBKRBroker is None:
    st.warning("IBKR functions unavailable in this build.")
from quant_platform.broker.ibkr_broker import IBKRBroker
import inspect
def render_param_inputs(strategy_cls):
    params = {}
    sig = inspect.signature(strategy_cls.__init__)
    for name, p in sig.parameters.items():
        if name == "self": continue
        default = p.default if p.default is not inspect._empty else 0
        if isinstance(default, int):
            params[name] = st.number_input(name, value=int(default))
        elif isinstance(default, float):
            params[name] = st.number_input(name, value=float(default), step=0.1, format="%.2f")
        else:
            params[name] = st.text_input(name, value=str(default))
    return params

import pandas as pd
from quant_platform.backtest.engine import BacktestEngine
from quant_platform.scheduler.tasks import start_scheduler
from quant_platform.database.models import init_db, BacktestRun
from quant_platform.strategy import STRATEGIES,get_strategy
import inspect, json

Session = init_db()

st.set_page_config(page_title="Quant Platform Web", layout="wide", page_icon="🪙")
st.title("🪙 Personal Quant Trading Platform")

tabs = st.tabs(["Backtest", "Historical Runs", "Live Data"])

# --- Backtest Tab ---
with tabs[0]:
    st.header("Run Backtest")
    symbol = st.text_input("Symbol", "AAPL")
    strategy_name = st.selectbox("Strategy", list(STRATEGIES.keys()))

    # 动态渲染策略参数
    def render_param_inputs(cls):
        params = {}
        for name, p in inspect.signature(cls.__init__).parameters.items():
            if name == "self": continue
            default = p.default if p.default is not inspect._empty else 0
            if isinstance(default, int):
                params[name] = st.number_input(name, value=int(default))
            elif isinstance(default, float):
                params[name] = st.number_input(name, value=float(default), step=0.1)
            else:
                params[name] = st.text_input(name, value=str(default))
        return params

    strategy_cls = get_strategy(strategy_name)
    strategy_params = render_param_inputs(strategy_cls)

    col1, col2 = st.columns(2)
    start = col1.date_input("Start", pd.to_datetime("2022-01-01"))
    end   = col2.date_input("End",   pd.to_datetime("2024-12-31"))
    run_button = st.button("🚀 Run")

    if run_button:
        engine = BacktestEngine(
            symbol, strategy_name, str(start), str(end),
            strategy_kwargs=strategy_params
        )
        engine.run()
        df = engine.results

        # ---- 只保留下面 3 行，绝对不要再有 to_dict 行 ----
        df_flat = df.copy()
        df_flat.columns = ["_".join(map(str, c)).strip("_") if isinstance(c, tuple) else str(c) for c in df_flat.columns]
        results_json = json.loads(df_flat.to_json(orient="records", date_format="iso"))
        # --------------------------------------------------------------------

        st.success("Backtest Done")
        st.line_chart(df.set_index("Date")["equity_curve"])
        st.dataframe(df.tail(10))

        Session.add(
            BacktestRun(
                symbol=symbol,
                strategy=strategy_name,
                start=str(start),
                end=str(end),
                equity_final=float(df["equity_curve"].iloc[-1]),
                results_json=results_json
            )
        )
        Session.commit()
# ---------------------------------------------------------------------------

# --- Historical Runs ---
with tabs[1]:
    st.header("Historical Backtests")
    runs = Session.query(BacktestRun).order_by(BacktestRun.created_at.desc()).all()
    data = [{
        "id": r.id, "symbol": r.symbol, "strategy": r.strategy,
        "start": r.start, "end": r.end, "equity_final": r.equity_final,
        "date": r.created_at
    } for r in runs]
    if data:
        st.dataframe(pd.DataFrame(data))
    else:
        st.info("No runs yet.")

# ---- Live Data / Trading Tab ------------------------------------------------
with tabs[2]:
    st.header("Live Quotes / Live Trade")

    # ===== 输入区域 =====
    symbols_input = st.text_input("Symbols (comma‑separated)", "")
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    colA, colB = st.columns(2)
    with colA:
        # 行情按钮
        if st.button("Start Stream"):
            # 0) 关闭旧定时器
            if st.session_state.get("sched"):
                st.session_state["sched"].shutdown(wait=False)

            # 1) 清空后台 & 前端缓存
            from quant_platform.scheduler import tasks
            tasks._latest_cache.clear()
            st.session_state["latest_cache"] = {}

            # 2) 同步抓一次，立刻有数据
            for sym in symbols:
                tasks.fetch_latest(sym)

            # 3) 新定时器，每 5 min 更新
            sched, latest_cache = start_scheduler(symbols)
            st.session_state["sched"] = sched
            st.session_state["latest_cache"] = latest_cache

            # 4) 刷新
            (st.rerun() if hasattr(st, "rerun") else st.experimental_rerun())

    with colB:
        # ======= 实盘交易按钮 =======
        qty = st.number_input("Qty / trade", 100, step=100)
        strategy_trade = st.selectbox("Trade Strategy", list(STRATEGIES.keys()))
        if st.button("Start Live Trade"):
            # 初始化 IBKR 连接（只建一次）
            if "ibkr" not in st.session_state:
                st.session_state["ibkr"] = IBKRBroker(port=7497)

            # 关闭旧交易调度
            if st.session_state.get("trade_sched"):
                st.session_state["trade_sched"].shutdown(wait=False)

            # 为每只股票建实时引擎
            from apscheduler.schedulers.background import BackgroundScheduler
            trade_sched = BackgroundScheduler()
            for sym in symbols:
                eng = RealTimeEngine(sym, strategy_trade, st.session_state["ibkr"], qty=qty)
                trade_sched.add_job(eng.run_once, "interval",
                                    seconds=60, next_run_time=datetime.utcnow())
            trade_sched.start()
            st.session_state["trade_sched"] = trade_sched
            st.success("Live trading started!")

    # ===== 渲染行情表格 =====
    cache = st.session_state.get("latest_cache", {})
    for sym in symbols:
        df = cache.get(sym)
        if df is not None and not df.empty:
            st.subheader(sym)
            st.dataframe(df.tail(5))
