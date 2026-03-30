# services/sentiment_service.py
import pandas as pd
import numpy as np
from typing import Dict, Optional
import streamlit as st

@st.cache_data(ttl=60)
def calculate_market_sentiment(all_stocks_df: pd.DataFrame, limit_up_df: Optional[pd.DataFrame] = None) -> Dict:
    """计算市场情绪"""
    if all_stocks_df is None or all_stocks_df.empty:
        return {
            'up_count': 0,
            'down_count': 0,
            'limit_up': 0,
            'heat_score': 50,
            'fear_greed': 50,
            'fear_greed_label': '中性'
        }

    # 清理数据中的空值
    valid_df = all_stocks_df[all_stocks_df['涨跌幅'].notna()]

    # 涨跌家数
    up_count = len(valid_df[valid_df['涨跌幅'] > 0])
    down_count = len(valid_df[valid_df['涨跌幅'] < 0])
    total = len(valid_df)

    # 涨停/跌停
    limit_up = len(limit_up_df) if limit_up_df is not None else 0

    # 市场热度评分 (0-100)
    heat_score = int((up_count / total) * 100) if total > 0 else 50

    # 恐惧贪婪指数 (简化版)
    avg_change = valid_df['涨跌幅'].mean()
    fear_greed = 50
    if avg_change is not None and not pd.isna(avg_change):
        fear_greed = max(0, min(100, int(50 + avg_change * 5)))

    return {
        'up_count': up_count,
        'down_count': down_count,
        'limit_up': limit_up,
        'heat_score': heat_score,
        'fear_greed': fear_greed,
        'fear_greed_label': get_fear_greed_label(fear_greed)
    }

def get_fear_greed_label(value: int) -> str:
    """恐惧贪婪标签"""
    if value <= 20: return "极度恐惧"
    elif value <= 40: return "恐惧"
    elif value <= 60: return "中性"
    elif value <= 80: return "贪婪"
    else: return "极度贪婪"

def calculate_stock_sentiment(quote: dict, ma_data: dict, fund_flow: Optional[dict] = None) -> Dict:
    """计算个股情绪"""
    sentiment_tags = []

    # 主力资金标签
    if fund_flow:
        main_flow = fund_flow.get('main_net_inflow', 0)
        if main_flow > 0:
            sentiment_tags.append(f"🔥 主力流入+{main_flow/1e8:.1f}亿")
        else:
            sentiment_tags.append(f"❄️ 主力流出{main_flow/1e8:.1f}亿")

    # 动量情绪
    pct = quote.get('change_pct', 0)
    if pct > 5:
        sentiment_tags.append("📈 强势上涨")
    elif pct > 2:
        sentiment_tags.append("📈 偏强")
    elif pct < -5:
        sentiment_tags.append("📉 弱势下跌")
    elif pct < -2:
        sentiment_tags.append("📉 偏弱")

    # 均线情绪
    if ma_data.get('MA5', 0) > ma_data.get('MA20', 0):
        sentiment_tags.append("📊 多头排列")
    else:
        sentiment_tags.append("📊 空头排列")

    return {
        'tags': sentiment_tags,
        'sentiment': '偏多' if pct > 0 else '偏空'
    }