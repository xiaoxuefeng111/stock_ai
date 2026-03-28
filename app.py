import streamlit as st
import pandas as pd
import akshare as ak
import dashscope
from dashscope import Generation
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import traceback

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

# API 初始化
@st.cache_resource
def init_api():
    api_key = os.getenv("DASHSCOPE_API_KEY", "")
    if not api_key:
        return None
    dashscope.api_key = api_key
    return True

api_ready = init_api()

# ==================== 数据函数 ====================

@st.cache_data(ttl=60)
def get_quote(symbol):
    """获取实时行情"""
    try:
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == symbol]
        if stock.empty:
            return None, f"未找到股票代码: {symbol}"
        row = stock.iloc[0]
        return {
            "symbol": symbol,
            "name": row['名称'],
            "price": float(row['最新价']),
            "change_pct": float(row['涨跌幅']),
            "change": float(row['涨跌额']),
            "high": float(row['最高']),
            "low": float(row['最低']),
            "open": float(row['今开']),
            "volume": float(row['成交量']),
            "amount": float(row['成交额']),
        }, None
    except Exception as e:
        error_msg = f"获取行情失败: {str(e)}"
        return None, error_msg

@st.cache_data(ttl=300)
def get_history(symbol, days=60):
    """获取历史数据"""
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        if df is None or df.empty:
            return None, "历史数据为空"
        df = df.tail(days).reset_index(drop=True)
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
        exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain / loss.replace(0, 0.001)))
        return df, None
    except Exception as e:
        return None, f"获取历史数据失败: {str(e)}"

@st.cache_data(ttl=600)
def get_news(symbol, limit=5):
    """获取新闻"""
    try:
        df = ak.stock_news_em(symbol=symbol)
        if df is None or df.empty:
            return [], "无新闻数据"
        return [{"title": row['新闻标题'], "content": row['新闻内容'][:150], "time": row['发布时间']}
                for _, row in df.head(limit).iterrows()], None
    except Exception as e:
        return [], f"获取新闻失败: {str(e)}"

# ==================== 图表 ====================

def plot_chart(df, name, symbol):
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
    return fig

# ==================== AI 分析（阿里百炼）====================

def ai_analyze(context, question):
    if not api_ready:
        return "⚠️ 请在 Streamlit Cloud 的 Secrets 中配置 DASHSCOPE_API_KEY"
    try:
        response = Generation.call(
            model='qwen-plus',
            messages=[
                {'role': 'system', 'content': '你是专业股票分析师，客观分析数据，不提供投资建议。'},
                {'role': 'user', 'content': f"数据:{context}\n问题:{question}"}
            ],
            result_format='message'
        )
        if response.status_code == 200:
            return response.output.choices[0]['message']['content']
        else:
            return f"AI分析失败: {response.code} - {response.message}"
    except Exception as e:
        return f"AI分析出错: {str(e)}"

# ==================== UI ====================

# 移动端优化样式
st.markdown("""
<style>
    .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 8px;}
    @media (max-width: 768px) {
        .stMetric > div > div {font-size: 1rem !important;}
    }
    .error-box {background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;}
</style>
""", unsafe_allow_html=True)

st.title("📊 股票分析")

# 显示 API 状态
if not api_ready:
    st.warning("⚠️ AI分析未启用，请配置 DASHSCOPE_API_KEY")

# 热门股票
hot_stocks = {"茅台": "600519", "平安银行": "000001", "五粮液": "000858",
              "宁德时代": "300750", "比亚迪": "002594"}

# 选择股票
col1, col2 = st.columns([3, 1])
with col1:
    selected = st.selectbox("选择股票", list(hot_stocks.keys()))
with col2:
    custom = st.text_input("或输入代码", "")

symbol = custom.strip() if custom.strip() else hot_stocks[selected]

if st.button("🔍 分析", type="primary", use_container_width=True):
    errors = []

    with st.spinner("加载中..."):
        # 1. 获取行情
        quote, quote_error = get_quote(symbol)

        if quote_error:
            st.error(f"❌ {quote_error}")
            st.info("💡 提示：Streamlit Cloud 服务器在海外，可能无法访问中国股票数据源。\n\n建议：本地运行 `streamlit run app.py` 获取完整功能。")
            errors.append(quote_error)

        if not quote:
            st.stop()

        # 行情卡片
        st.subheader(f"{quote['name']} ({symbol})")
        c1, c2, c3, c4 = st.columns(4)
        pct = quote['change_pct']
        arrow = "📈" if pct > 0 else "📉"

        c1.metric("价格", f"{quote['price']:.2f}", f"{arrow} {pct:.2f}%")
        c2.metric("最高", f"{quote['high']:.2f}")
        c3.metric("最低", f"{quote['low']:.2f}")
        c4.metric("成交额", f"{quote['amount']/1e8:.1f}亿")

        st.markdown("---")

        # 2. 获取历史数据
        df, hist_error = get_history(symbol, 60)

        if hist_error:
            st.warning(f"⚠️ {hist_error}")
            errors.append(hist_error)

        if df is not None:
            st.subheader("📈 技术图表")
            st.pyplot(plot_chart(df, quote['name'], symbol))

            latest = df.iloc[-1]
            c1, c2, c3 = st.columns(3)
            c1.metric("MA5", f"{latest['MA5']:.2f}")
            c2.metric("RSI", f"{latest['RSI']:.1f}")
            c3.metric("MACD", f"{latest['MACD']:.3f}")

        st.markdown("---")

        # 3. 获取新闻
        news, news_error = get_news(symbol)

        if news_error:
            st.warning(f"⚠️ {news_error}")

        if news:
            st.subheader("📰 新闻")
            for n in news:
                st.markdown(f"**{n['title']}** ({n['time']})")
                st.caption(n['content'])

        st.markdown("---")

        # 4. AI 分析
        if api_ready and df is not None:
            st.subheader("🤖 AI分析")
            with st.spinner("分析中..."):
                ctx = {
                    "quote": quote,
                    "indicators": {"MA5": float(latest['MA5']), "MA10": float(latest['MA10']),
                                   "RSI": float(latest['RSI']), "MACD": float(latest['MACD'])},
                    "change": round((df.iloc[-1]['收盘'] - df.iloc[0]['收盘']) / df.iloc[0]['收盘'] * 100, 2)
                }
                result = ai_analyze(json.dumps(ctx), f"分析{quote['name']}技术面和走势")
                st.markdown(result)
        elif not api_ready:
            st.info("💡 AI分析需要配置阿里百炼 API Key")

        # 显示错误汇总
        if errors:
            st.markdown("---")
            st.error(f"遇到 {len(errors)} 个错误")
            with st.expander("查看详细错误"):
                for e in errors:
                    st.code(e)

        st.warning("⚠️ 仅供参考，不构成投资建议")

st.caption("数据: AkShare | AI: 阿里百炼")