# pages/tab_news.py
import streamlit as st
from typing import List, Dict
from services.news_crawler_service import (
    get_cls_news_crawl, get_eastmoney_news_crawl,
    get_ths_news_crawl, get_thshy_news_crawl
)

def render_news_item(news: Dict):
    """渲染单条新闻"""
    source = news.get('source', '')
    title = news.get('title', '无标题')
    content = news.get('content', '')
    time = news.get('time', '')
    url = news.get('url', '')

    # 来源颜色（根据来源名称匹配）
    if '财联社' in source:
        color = '#e74c3c'
    elif '东方财富' in source:
        color = '#3498db'
    elif '同花顺' in source or '热门个股' in source:
        color = '#9b59b6'
    else:
        color = '#666'

    st.markdown(f"""
    <div style="background:#fff; border-radius:6px; padding:10px 12px; margin:6px 0; border-left:3px solid {color}; box-shadow:0 1px 2px rgba(0,0,0,0.08);">
        <div style="display:flex; align-items:center; margin-bottom:6px;">
            <span style="background:{color}; color:#fff; font-size:0.7rem; padding:2px 6px; border-radius:3px; font-weight:bold;">{source}</span>
            <span style="font-size:0.75rem; color:#999; margin-left:8px;">{time}</span>
        </div>
        <div style="font-size:0.95rem; color:#333; font-weight:500; margin-bottom:4px;">{title}</div>
        <div style="font-size:0.85rem; color:#666; line-height:1.4;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_source_section(source_name: str, fetch_func, icon: str):
    """渲染单个新闻源板块"""
    st.markdown(f"### {icon} {source_name}")

    with st.spinner(f"正在加载{source_name}..."):
        news_list, error = fetch_func()

    if error:
        st.warning(error)
        return

    if not news_list:
        st.info(f"暂无{source_name}数据")
        return

    for news in news_list:
        render_news_item(news)


def render_tab_news():
    """渲染热点资讯Tab"""
    st.markdown("## 🔥 热点资讯")
    st.markdown("实时财经快讯，多渠道信息聚合")

    # 刷新按钮
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 刷新", key="refresh_news", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # 财联社电报快讯
    with st.expander("📢 财联社电报", expanded=True):
        news_list, error = get_cls_news_crawl()
        if error:
            st.warning(error)
        elif news_list:
            for news in news_list[:15]:
                render_news_item(news)
        else:
            st.info("暂无数据")

    # 东方财富快讯
    with st.expander("📊 东方财富快讯", expanded=True):
        news_list, error = get_eastmoney_news_crawl()
        if error:
            st.warning(error)
        elif news_list:
            for news in news_list[:15]:
                render_news_item(news)
        else:
            st.info("暂无数据")

    # 同花顺快讯
    with st.expander("📈 同花顺快讯", expanded=False):
        news_list, error = get_ths_news_crawl()
        if error:
            st.warning(error)
        elif news_list:
            for news in news_list[:15]:
                render_news_item(news)
        else:
            st.info("暂无数据")

    # 热门个股快讯
    with st.expander("🔥 热门个股快讯", expanded=False):
        news_list, error = get_thshy_news_crawl()
        if error:
            st.warning(error)
        elif news_list:
            for news in news_list[:15]:
                render_news_item(news)
        else:
            st.info("暂无数据")

    # 底部说明
    st.markdown("---")
    st.caption("📍 数据来源: 财联社电报、东方财富快讯、同花顺快讯 | 每60秒自动更新缓存")