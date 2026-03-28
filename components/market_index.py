# components/market_index.py
import streamlit as st
from typing import List, Dict

def render_market_index(indices: List[Dict]):
    """渲染大盘指数"""
    if not indices:
        st.warning("大盘指数数据加载中...")
        return

    cols = st.columns(len(indices))
    for i, idx in enumerate(indices):
        with cols[i]:
            pct = idx['change_pct']
            color = "red" if pct >= 0 else "green"
            arrow = "📈" if pct >= 0 else "📉"
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:#f8f9fa; border-radius:8px;">
                <div style="font-size:0.9rem; color:#666;">{idx['name']}</div>
                <div style="font-size:1.2rem; font-weight:bold;">{idx['price']:,.2f}</div>
                <div style="color:{color}; font-size:0.85rem;">{arrow} {pct:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

def render_market_index_simple(indices: List[Dict]):
    """简化版大盘指数"""
    if not indices:
        st.warning("大盘指数数据加载中...")
        return

    cols = st.columns(len(indices))
    for i, idx in enumerate(indices):
        with cols[i]:
            pct = idx['change_pct']
            is_up = pct >= 0
            bg_color = "#fff5f5" if is_up else "#f0fff4"
            color = "#ff4757" if is_up else "#2ed573"
            arrow = "↑" if is_up else "↓"
            st.markdown(f"""
            <div style="text-align:center; padding:8px; background:{bg_color}; border-radius:6px; border-left:3px solid {color};">
                <div style="font-size:0.85rem; color:#666;">{idx['name']}</div>
                <div style="font-size:1.1rem; font-weight:bold;">{idx['price']:,.2f}</div>
                <div style="color:{color}; font-size:0.8rem;">{arrow}{abs(pct):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)