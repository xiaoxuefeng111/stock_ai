# components/stock_card.py
import streamlit as st
from typing import Dict, List

def get_market_info(symbol: str) -> str:
    """获取市场板块信息"""
    if symbol.startswith('68'):
        return "科创板"
    elif symbol.startswith('6'):
        return "沪市主板"
    elif symbol.startswith('0'):
        return "深市主板"
    elif symbol.startswith('3'):
        return "创业板"
    elif symbol.startswith('8') or symbol.startswith('4'):
        return "北交所"
    else:
        return "A股"

def render_stock_card(quote: Dict, ma_data: Dict, sentiment_tags: List[str], on_analyze, on_remove, industry: str = ""):
    """渲染自选股卡片 - 4行布局"""
    pct = quote['change_pct']
    is_up = pct >= 0
    price_class = "price-up" if is_up else "price-down"
    arrow = "↑" if is_up else "↓"
    market = get_market_info(quote['symbol'])

    # 涨跌背景色
    bg_color = "#fff5f5" if is_up else "#f0fff4"
    border_color = "#ff4757" if is_up else "#2ed573"

    # 压力位/支撑位
    high_20 = ma_data.get('high_20', quote.get('high', 0))
    low_20 = ma_data.get('low_20', quote.get('low', 0))

    # 股票名称
    stock_name = quote.get('name', quote.get('symbol', '未知'))
    stock_symbol = quote.get('symbol', '')

    st.markdown(f"""
    <div style="background:{bg_color}; border-radius:8px; padding:12px 15px; margin:8px 0; box-shadow:0 1px 3px rgba(0,0,0,0.1); border-left:4px solid {border_color};">
        <div style="padding-bottom:6px; border-bottom:1px solid #f0f0f0; margin-bottom:6px;">
            <span style="font-size:1.1rem; font-weight:bold; color:#2d3436;">{stock_name}</span>
            <span style="font-size:0.85rem; color:#636e72; margin-left:8px;">{stock_symbol}</span>
            <span style="font-size:0.75rem; color:#b2bec3; margin-left:8px; padding:1px 5px; background:#f5f5f5; border-radius:3px;">{market}</span>
            <span style="font-size:0.75rem; color:#b2bec3; margin-left:6px; padding:1px 5px; background:#f5f5f5; border-radius:3px;">{industry}</span>
        </div>
        <div style="font-size:0.8rem; color:#636e72; margin-bottom:6px;">
            <span>压力位 <b style="color:#2d3436;">{high_20:.2f}</b></span>
            <span style="margin-left:12px;">支撑位 <b style="color:#2d3436;">{low_20:.2f}</b></span>
            <span style="margin-left:12px;">成交量 <b style="color:#2d3436;">{format_volume(quote.get('volume', 0))}</b></span>
            <span style="margin-left:12px;">成交额 <b style="color:#2d3436;">{format_amount(ma_data.get('amount', 0))}</b></span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:8px; background:#ffffff80; border-radius:6px; padding:8px; margin-bottom:6px;">
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#636e72;">当前价</div>
                <div style="font-size:1rem; font-weight:bold;" class="{price_class}">{quote.get('price', 0):.2f}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#636e72;">当日涨幅</div>
                <div style="font-size:1rem; font-weight:bold;" class="{price_class}">{arrow}{abs(pct):.2f}%</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#636e72;">开盘价</div>
                <div style="font-size:1rem; font-weight:bold; color:#2d3436;">{quote.get('open', 0):.2f}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#636e72;">最高价</div>
                <div style="font-size:1rem; font-weight:bold; color:#ff4757;">{quote.get('high', 0):.2f}</div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:8px; font-size:0.8rem;">
            <div style="text-align:center;">
                <div style="color:#636e72;">5分钟均线</div>
                <div style="font-weight:500; color:#2d3436;">{ma_data.get('MA5MIN', quote.get('price', 0)):.2f}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#636e72;">5日均线</div>
                <div style="font-weight:500; color:#2d3436;">{ma_data.get('MA5', 0):.2f}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#636e72;">13日均线</div>
                <div style="font-weight:500; color:#2d3436;">{ma_data.get('MA13', 0):.2f}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#636e72;">20日均线</div>
                <div style="font-weight:500; color:#2d3436;">{ma_data.get('MA20', 0):.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("分析", key=f"analyze_{quote['symbol']}", type="primary", use_container_width=True):
            on_analyze(quote['symbol'])
    with col2:
        if st.button("删除", key=f"remove_{quote['symbol']}", use_container_width=True):
            on_remove(quote['symbol'])

def format_volume(vol: float) -> str:
    """格式化成交量"""
    if vol >= 100000000:
        return f"{vol/100000000:.1f}亿手"
    elif vol >= 10000:
        return f"{vol/10000:.0f}万手"
    return f"{vol:.0f}手"

def format_amount(amount: float) -> str:
    """格式化成交额"""
    if amount >= 100000000:  # 1亿
        return f"{amount/100000000:.2f}亿"
    elif amount >= 10000:  # 1万
        return f"{amount/10000:.1f}万"
    return f"{amount:.0f}元"