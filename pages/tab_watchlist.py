# pages/tab_watchlist.py
import streamlit as st
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

    # 大盘指数
    indices, _ = get_market_index()
    render_market_index_simple(indices)

    st.markdown("---")

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

    st.markdown("---")

    # 自选股列表
    st.markdown("### 自选股")

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

    # 添加自选股
    st.markdown("---")
    st.markdown("#### ➕ 添加自选股")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("搜索股票", key="watchlist_search", placeholder="输入代码或名称")

    with col2:
        selected = None
        if search.strip():
            results, _ = search_stock(search.strip(), st.session_state.all_stocks)
            if results:
                options = [f"{r['代码']} - {r['名称']}" for r in results]
                selected = st.selectbox("选择股票", options, key="watchlist_select")

    with col3:
        if st.button("添加", type="primary", use_container_width=True):
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