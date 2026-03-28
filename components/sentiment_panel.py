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

    st.markdown("#### 🌡️ 市场情绪")

    # 恐惧贪婪指数
    col1, col2 = st.columns([3, 1])
    with col1:
        bar_color = get_fear_greed_color(fear_greed)
        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <span style="font-size:0.9rem;">恐惧贪婪指数</span>
            <div style="background:#e0e0e0; border-radius:10px; height:20px; margin-top:5px;">
                <div style="background:{bar_color}; width:{fear_greed}%; height:100%; border-radius:10px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#666;">
                <span>恐惧</span>
                <span style="font-weight:bold;">{fear_greed} ({fear_label})</span>
                <span>贪婪</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        heat = sentiment.get('heat_score', 50)
        st.metric("市场热度", f"{heat}分")

    # 涨跌统计
    up = sentiment.get('up_count', 0)
    down = sentiment.get('down_count', 0)
    limit_up = sentiment.get('limit_up', 0)

    cols = st.columns(5)
    cols[0].metric("上涨", up, delta=None)
    cols[1].metric("下跌", down, delta=None)
    cols[2].metric("涨停", limit_up, delta=None)
    cols[3].metric("跌停", limit_down, delta=None)

    st.markdown("---")