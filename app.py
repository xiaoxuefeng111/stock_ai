# app.py - Tab布局框架
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

# 中文支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(
    page_title="股票分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 导入服务
from services.data_service import *
from services.ai_service import ai_analyze, get_ai_config
from services.sentiment_service import calculate_market_sentiment, calculate_stock_sentiment
from utils.helpers import *
from utils.theme import get_theme, toggle_theme
from components.market_index import render_market_index_simple
from components.sentiment_panel import render_sentiment_panel
from components.stock_card import render_stock_card
from components.news_timeline import render_news_timeline
from components.chart import render_simple_chart

# 全局样式
st.markdown("""
<style>
    .stock-card { background:#fff; border-radius:8px; padding:12px 15px; margin:8px 0; box-shadow:0 1px 3px rgba(0,0,0,0.12); border:1px solid #e8e8e8; }
    .stock-card-up { border-left:4px solid #ff4757; }
    .stock-card-down { border-left:4px solid #2ed573; }
    .card-row { display:flex; align-items:center; }
    .price-up { color:#ff4757; }
    .price-down { color:#2ed573; }
</style>
""", unsafe_allow_html=True)

# 应用主题样式
from utils.theme import apply_theme_styles
apply_theme_styles()

# 初始化 Session State
if "all_stocks" not in st.session_state:
    st.session_state.all_stocks = None
if "stocks_loaded" not in st.session_state:
    st.session_state.stocks_loaded = False
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = None

# 顶部标题栏
col_title, col_init, col_theme = st.columns([3, 2, 1])
with col_title:
    st.title("📊 股票分析")
with col_init:
    if st.session_state.stocks_loaded:
        st.caption(f"✅ 已加载 {len(st.session_state.all_stocks)} 只股票")
    else:
        if st.button("🔄 初始化数据", key="init_data_btn", use_container_width=True):
            with st.spinner("正在加载全市场股票数据（约1-2分钟）..."):
                df, error = load_all_stocks()
                if error:
                    st.error(error)
                else:
                    st.session_state.all_stocks = df
                    st.session_state.stocks_loaded = True
                    st.rerun()
with col_theme:
    theme_icon = "🌙" if get_theme() == 'light' else "☀️"
    if st.button(theme_icon, key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

# Tab 布局
from pages.tab_watchlist import render_tab_watchlist
from pages.tab_analysis import render_tab_analysis
from pages.tab_indicators import render_tab_indicators
from pages.tab_ai import render_tab_ai
from pages.tab_news import render_tab_news

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⭐ 自选股", "📈 个股分析", "📊 技术指标", "🤖 AI分析", "🔥 热点资讯"])

with tab1:
    render_tab_watchlist()
with tab2:
    render_tab_analysis()
with tab3:
    render_tab_indicators()
with tab4:
    render_tab_ai()
with tab5:
    render_tab_news()

# 底部状态栏
st.markdown("---")
st.caption("数据: AkShare | AI: 阿里百炼 | ⚠️ 仅供参考，不构成投资建议")