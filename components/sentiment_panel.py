# components/sentiment_panel.py
import streamlit as st
from typing import Dict

def get_fear_greed_color(value: int) -> str:
    """根据恐惧贪婪值获取颜色"""
    if value <= 20:
        return "#27ae60"  # 深绿 - 极度恐惧
    elif value <= 40:
        return "#2ed573"  # 绿色 - 恐惧
    elif value <= 60:
        return "#95a5a6"  # 灰色 - 中性
    elif value <= 80:
        return "#e67e22"  # 橙色 - 贪婪
    else:
        return "#e74c3c"  # 红色 - 极度贪婪

def render_sentiment_panel(sentiment: Dict, limit_down: int = 0):
    """渲染市场情绪面板"""
    if not sentiment:
        return

    fear_greed = sentiment.get('fear_greed', 50)
    fear_label = sentiment.get('fear_greed_label', '中性')

    # 紧凑布局：标题和指标一行
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        bar_color = get_fear_greed_color(fear_greed)
        st.markdown(f"""
        <div style="margin-bottom:2px;">
            <span style="font-size:0.85rem; font-weight:500;">🌡️ 恐惧贪婪: </span>
            <span style="font-weight:bold; color:{bar_color};">{fear_greed}</span>
            <span style="font-size:0.8rem; color:#666;">({fear_label})</span>
        </div>
        <div style="background:#e0e0e0; border-radius:6px; height:8px; margin-top:2px;">
            <div style="background:{bar_color}; width:{fear_greed}%; height:100%; border-radius:6px;"></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        heat = sentiment.get('heat_score', 50)
        st.metric("热度", f"{heat}分", label_visibility="visible")
    with col3:
        st.metric("涨停/跌停", f"{sentiment.get('limit_up', 0)}/{limit_down}", label_visibility="visible")

    # 涨跌统计 - 一行紧凑显示
    up = sentiment.get('up_count', 0)
    down = sentiment.get('down_count', 0)
    st.markdown(f"""
    <div style="display:flex; gap:20px; font-size:0.85rem; margin-top:5px;">
        <span>📈 上涨: <b style="color:#ff4757;">{up}</b></span>
        <span>📉 下跌: <b style="color:#2ed573;">{down}</b></span>
    </div>
    """, unsafe_allow_html=True)