# pages/tab_watchlist.py
import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh
from services.data_service import *
from services.sentiment_service import calculate_market_sentiment, calculate_stock_sentiment
from utils.helpers import *
from components.market_index import render_market_index_simple
from components.sentiment_panel import render_sentiment_panel
from components.stock_card import render_stock_card

def render_tab_watchlist():
    """渲染自选股Tab"""

    if not st.session_state.stocks_loaded:
        st.info("👆 请先点击顶部'初始化数据'按钮加载数据")
        return

    # 自动刷新配置
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### ⭐ 自选股")
    with col2:
        auto_refresh = st.checkbox("自动刷新", value=True, key="auto_refresh_check")
    with col3:
        if auto_refresh:
            refresh_interval = st.selectbox("间隔(秒)", [30, 60, 120, 300], key="refresh_interval", index=1)
        else:
            if st.button("🔄 刷新", key="manual_refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

    # 自动刷新逻辑
    if auto_refresh:
        refresh_interval = st.session_state.get('refresh_interval', 60)
        # 使用 streamlit-autorefresh 组件
        count = st_autorefresh(interval=refresh_interval * 1000, key="watchlist_autorefresh")
        st.markdown(f"<span style='font-size:0.8rem; color:#666;'>⏱️ 每 {refresh_interval} 秒自动刷新 (已刷新 {count} 次)</span>", unsafe_allow_html=True)

    # 大盘指数
    indices, _ = get_market_index()
    render_market_index_simple(indices)

    # 市场情绪
    limit_up_df, _ = get_limit_up_pool()
    limit_down_df, _ = get_limit_down_pool()
    sentiment = calculate_market_sentiment(st.session_state.all_stocks, limit_up_df)

    # 统计涨停跌停数
    limit_up = len(limit_up_df) if limit_up_df is not None else 0
    limit_down = len(limit_down_df) if limit_down_df is not None else 0

    # 如果跌停池API失败，从全市场数据统计
    if limit_down == 0 and st.session_state.all_stocks is not None:
        limit_down = len(st.session_state.all_stocks[st.session_state.all_stocks['涨跌幅'] <= -9.5])

    render_sentiment_panel(sentiment, limit_down)

    # 自选股列表 - 添加功能在上方
    col_title, col1, col2, col3 = st.columns([2, 2, 2, 1])
    with col_title:
        st.markdown("#### 📋 自选股列表")
    with col1:
        search = st.text_input("搜索", key="watchlist_search", placeholder="输入代码或名称", label_visibility="collapsed")
    with col2:
        selected = None
        if search.strip():
            results, _ = search_stock(search.strip(), st.session_state.all_stocks)
            if results:
                options = [f"{r['代码']} - {r['名称']}" for r in results]
                selected = st.selectbox("选择", options, key="watchlist_select", label_visibility="collapsed")
    with col3:
        if st.button("➕ 添加", type="primary", use_container_width=True, key="add_watchlist_btn"):
            if selected:
                symbol = selected.split(" - ")[0]
                name = selected.split(" - ")[1]
                success, msg = add_to_watchlist(symbol, name)
                st.session_state.watchlist = load_watchlist()
                if success:
                    st.success(msg)
                else:
                    st.warning(msg)
                st.rerun()

    # 显示自选股卡片
    if st.session_state.watchlist:
        quotes = get_watchlist_quotes(st.session_state.watchlist, st.session_state.all_stocks)

        for q in quotes:
            ma_data = get_ma_data(q['symbol'], st.session_state.all_stocks)
            sentiment_tags = calculate_stock_sentiment(q, ma_data).get('tags', [])
            industry = q.get('industry', '')

            def on_analyze(symbol):
                st.session_state.selected_symbol = symbol

            def on_remove(symbol):
                remove_from_watchlist(symbol)
                st.session_state.watchlist = load_watchlist()

            render_stock_card(q, ma_data, sentiment_tags, on_analyze, on_remove, industry)
    else:
        st.info("暂无自选股，请在上方搜索添加")