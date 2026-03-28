# components/chart.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def render_simple_chart(df: pd.DataFrame, name: str, symbol: str):
    """渲染简洁K线图"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1, 1]})

    ax1 = axes[0]
    for i, row in df.iterrows():
        color = 'red' if row['收盘'] >= row['开盘'] else 'green'
        ax1.bar(i, row['收盘'] - row['开盘'], bottom=row['开盘'], color=color, width=0.6)
        ax1.vlines(i, row['最低'], min(row['开盘'], row['收盘']), color=color)
        ax1.vlines(i, max(row['开盘'], row['收盘']), row['最高'], color=color)
    ax1.plot(df.index, df['MA5'], 'b-', label='MA5', linewidth=1)
    ax1.plot(df.index, df['MA10'], 'orange', label='MA10', linewidth=1)
    ax1.plot(df.index, df['MA20'], 'purple', label='MA20', linewidth=1)
    ax1.set_title(f'{name}({symbol})')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    colors = ['red' if df.iloc[i]['收盘'] >= df.iloc[i]['开盘'] else 'green' for i in range(len(df))]
    ax2.bar(df.index, df['成交量'], color=colors)
    ax2.set_title('成交量')
    ax2.grid(True, alpha=0.3)

    ax3 = axes[2]
    ax3.plot(df.index, df['MACD'], 'b-', label='MACD')
    ax3.plot(df.index, df['Signal'], 'orange', label='Signal')
    colors_macd = ['red' if x > 0 else 'green' for x in df['MACD'] - df['Signal']]
    ax3.bar(df.index, df['MACD'] - df['Signal'], color=colors_macd, alpha=0.5)
    ax3.set_title('MACD')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

def render_advanced_chart(df: pd.DataFrame, name: str, symbol: str, indicators: list, signals: list = None):
    """渲染高级图表（带指标和买卖点）- 第二阶段实现"""
    render_simple_chart(df, name, symbol)