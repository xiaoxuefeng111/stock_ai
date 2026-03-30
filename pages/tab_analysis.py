# pages/tab_analysis.py
import streamlit as st
import json
from services.data_service import *
from services.ai_service import ai_analyze
from utils.helpers import add_to_watchlist, load_watchlist
from components.news_timeline import render_news_timeline
from components.chart import render_simple_chart

def render_tab_analysis():
    """渲染个股分析Tab"""

    # 股票选择 - 紧凑布局
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        search = st.text_input("🔍 搜索股票", key="analysis_search", placeholder="输入代码或名称")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
        if st.button("分析此股票", key="analyze_btn", type="primary", use_container_width=True):
            if st.session_state.get('analysis_select'):
                st.session_state.selected_symbol = st.session_state.analysis_select.split(" - ")[0]
                st.rerun()

    symbol = st.session_state.get('selected_symbol')

    if search.strip() and st.session_state.stocks_loaded:
        results, _ = search_stock(search.strip(), st.session_state.all_stocks)
        if results:
            options = [f"{r['代码']} - {r['名称']}" for r in results]
            with col2:
                selected = st.selectbox("选择", options, key="analysis_select", label_visibility="collapsed")

    if not symbol:
        st.info("👆 请选择或搜索股票进行分析")
        return

    if not st.session_state.stocks_loaded:
        st.warning("⚠️ 请先在自选股Tab初始化数据")
        return

    # 获取数据
    quote, _ = get_quote_from_cache(symbol, st.session_state.all_stocks)
    if not quote:
        st.error("未找到股票")
        return

    # 行情概览 - 加入自选股按钮放这里
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader(f"{quote['name']} ({symbol})")
    with col_btn:
        if not any(s['symbol'] == symbol for s in st.session_state.watchlist):
            if st.button("⭐ 加自选", key="add_to_watchlist_btn"):
                add_to_watchlist(symbol, quote['name'])
                st.session_state.watchlist = load_watchlist()
                st.success("已添加")
                st.rerun()

    cols = st.columns(4)
    pct = quote['change_pct']
    arrow = "📈" if pct >= 0 else "📉"
    cols[0].metric("当前价", f"{quote['price']:.2f}", f"{arrow} {pct:.2f}%")
    cols[1].metric("最高", f"{quote['high']:.2f}")
    cols[2].metric("最低", f"{quote['low']:.2f}")
    cols[3].metric("成交额", f"{quote['amount']/1e8:.1f}亿")

    st.markdown("---")

    # 简洁图表
    with st.expander("📈 技术图表", expanded=True):
        df, _ = get_history(symbol, 60)
        if df is not None:
            render_simple_chart(df, quote['name'], symbol)

            # 基础指标
            latest = df.iloc[-1]
            cols = st.columns(4)
            cols[0].metric("MA5", f"{latest['MA5']:.2f}")
            cols[1].metric("MA10", f"{latest['MA10']:.2f}")
            cols[2].metric("RSI", f"{latest['RSI']:.1f}")
            macd_status = "金叉" if latest['MACD'] > 0 else "死叉"
            cols[3].metric("MACD", f"{latest['MACD']:.3f}", macd_status)

    st.markdown("---")

    # 资讯时间线
    with st.expander("📰 资讯时间线", expanded=True):
        news, _ = get_news(symbol, 10)
        render_news_timeline(news)

    st.markdown("---")

    # AI简要分析
    with st.expander("🤖 AI简要分析"):
        if st.button("开始分析"):
            with st.spinner("分析中..."):
                ctx = {
                    "quote": quote,
                    "indicators": {"MA5": float(latest['MA5']), "RSI": float(latest['RSI'])}
                }
                result = ai_analyze(json.dumps(ctx), f"简要分析{quote['name']}投资价值")
                st.markdown(result)