# pages/tab_indicators.py
import streamlit as st
from services.data_service import get_history, search_stock
from utils.indicators import calc_ma, calc_macd, calc_rsi, calc_kdj, calc_boll
from components.chart import render_simple_chart

def render_tab_indicators():
    """渲染技术指标Tab"""
    st.markdown("### 📊 技术指标分析")

    # 股票选择
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("搜索股票", key="indicators_search", placeholder="输入代码或名称")
    with col2:
        period = st.selectbox("周期", ["日线", "周线", "月线"], key="indicators_period")

    symbol = st.session_state.get('selected_symbol')

    if search.strip() and st.session_state.stocks_loaded:
        results, _ = search_stock(search.strip(), st.session_state.all_stocks)
        if results:
            options = [f"{r['代码']} - {r['名称']}" for r in results]
            selected = st.selectbox("选择股票", options, key="indicators_select")
            if st.button("确认选择"):
                st.session_state.selected_symbol = selected.split(" - ")[0]
                st.rerun()

    if not symbol:
        st.info("👆 请先在自选股或个股分析Tab选择股票，或在此搜索股票")
        return

    if not st.session_state.stocks_loaded:
        st.warning("⚠️ 请先在自选股Tab初始化数据")
        return

    # 指标选择器
    st.markdown("#### 指标选择")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_ma = st.checkbox("均线 (MA)", value=True)
        ma_periods = st.multiselect("均线周期", [5, 10, 20, 60], default=[5, 10, 20])
    with col2:
        show_macd = st.checkbox("MACD", value=True)
    with col3:
        show_rsi = st.checkbox("RSI", value=True)
        rsi_period = st.number_input("RSI周期", min_value=5, max_value=30, value=14)
    with col4:
        show_kdj = st.checkbox("KDJ", value=False)
        show_boll = st.checkbox("布林带", value=False)

    # 参数调整
    with st.expander("⚙️ 高级参数"):
        if show_macd:
            col1, col2, col3 = st.columns(3)
            macd_fast = col1.number_input("MACD快线", min_value=5, max_value=20, value=12)
            macd_slow = col2.number_input("MACD慢线", min_value=15, max_value=40, value=26)
            macd_signal = col3.number_input("MACD信号线", min_value=5, max_value=15, value=9)
        if show_boll:
            boll_period = st.number_input("布林带周期", min_value=10, max_value=30, value=20)
            boll_std = st.number_input("标准差倍数", min_value=1.0, max_value=3.0, value=2.0, step=0.1)

    # 获取数据并计算指标
    df, _ = get_history(symbol, 120)
    if df is not None:
        # 计算指标
        if show_ma and ma_periods:
            df = calc_ma(df, ma_periods)
        if show_macd:
            df = calc_macd(df, macd_fast if show_macd else 12, macd_slow if show_macd else 26, macd_signal if show_macd else 9)
        if show_rsi:
            df = calc_rsi(df, rsi_period)
        if show_kdj:
            df = calc_kdj(df)
        if show_boll:
            df = calc_boll(df, boll_period if show_boll else 20, boll_std if show_boll else 2.0)

        # 显示图表
        stock_name = st.session_state.get('stock_name', symbol)
        render_simple_chart(df, stock_name, symbol)

        # 显示指标数值
        st.markdown("#### 最新指标值")
        latest = df.iloc[-1]
        cols = st.columns(6)

        if show_ma and ma_periods:
            for i, p in enumerate(ma_periods[:3]):
                cols[i].metric(f"MA{p}", f"{latest.get(f'MA{p}', 0):.2f}")

        if show_macd:
            cols[3].metric("MACD", f"{latest.get('MACD', 0):.3f}")
            macd_signal_val = "金叉" if latest.get('MACD', 0) > latest.get('MACD_Signal', 0) else "死叉"
            cols[3].metric("信号", macd_signal_val)

        if show_rsi:
            rsi_val = latest.get('RSI', 50)
            rsi_status = "超买" if rsi_val > 70 else "超卖" if rsi_val < 30 else "正常"
            cols[4].metric("RSI", f"{rsi_val:.1f}", rsi_status)

        if show_kdj:
            cols[5].metric("KDJ-K", f"{latest.get('KDJ_K', 0):.1f}")

        # 策略提示
        st.markdown("#### 📊 策略信号")
        signals = []

        if show_macd:
            if latest.get('MACD', 0) > latest.get('MACD_Signal', 0):
                signals.append("🟢 MACD金叉")
            else:
                signals.append("🔴 MACD死叉")

        if show_rsi:
            rsi_val = latest.get('RSI', 50)
            if rsi_val < 30:
                signals.append("🟢 RSI超卖区，可能反弹")
            elif rsi_val > 70:
                signals.append("🔴 RSI超买区，可能回调")

        if show_ma and len(ma_periods) >= 2:
            if latest.get(f'MA{ma_periods[0]}', 0) > latest.get(f'MA{ma_periods[-1]}', 0):
                signals.append("🟢 均线多头排列")
            else:
                signals.append("🔴 均线空头排列")

        for s in signals:
            st.write(s)