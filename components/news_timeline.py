# components/news_timeline.py
import streamlit as st
from typing import List, Dict
from datetime import datetime

def render_news_timeline(news: List[Dict], announcements: List[Dict] = None, reports: List[Dict] = None, ai_summaries: bool = True):
    """渲染资讯时间线"""
    # 合并所有资讯
    all_items = []

    for n in news[:5]:
        all_items.append({
            'type': '新闻',
            'icon': '📰',
            'title': n.get('title', ''),
            'content': n.get('content', ''),
            'time': n.get('time', ''),
            'sentiment': n.get('sentiment', '中性')
        })

    if announcements:
        for a in announcements[:3]:
            all_items.append({
                'type': '公告',
                'icon': '📢',
                'title': a.get('title', ''),
                'content': a.get('content', ''),
                'time': a.get('time', ''),
                'sentiment': a.get('sentiment', '中性')
            })

    if reports:
        for r in reports[:2]:
            all_items.append({
                'type': '研报',
                'icon': '📄',
                'title': r.get('title', ''),
                'content': r.get('content', ''),
                'time': r.get('time', ''),
                'sentiment': '中性'
            })

    if not all_items:
        st.info("暂无资讯数据")
        return

    for item in all_items:
        sentiment_icon = "✅" if item['sentiment'] == '利好' else "❌" if item['sentiment'] == '利空' else "⚪"
        sentiment_color = "#ff4757" if item['sentiment'] == '利好' else "#2ed573" if item['sentiment'] == '利空' else "#666"

        with st.container():
            st.markdown(f"""
            <div style="padding:12px; margin:8px 0; background:#fafafa; border-radius:8px; border-left:3px solid {sentiment_color};">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span>
                        <span style="color:#888; font-size:0.8rem;">{item['time']}</span>
                        <span style="background:#e0e0e0; padding:2px 6px; border-radius:4px; font-size:0.75rem; margin-left:5px;">{item['icon']} {item['type']}</span>
                        <span style="color:{sentiment_color}; font-size:0.8rem; margin-left:5px;">{sentiment_icon} {item['sentiment']}</span>
                    </span>
                </div>
                <div style="font-weight:bold; margin-bottom:5px;">{item['title']}</div>
                <div style="font-size:0.85rem; color:#666;">{item['content'][:150]}...</div>
            </div>
            """, unsafe_allow_html=True)