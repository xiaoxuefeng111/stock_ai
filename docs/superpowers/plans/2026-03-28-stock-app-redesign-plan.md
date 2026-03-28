# 股票分析应用 UI重构与功能扩展 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将单页面股票分析应用重构为四Tab架构，新增市场情绪、技术指标策略、AI深度分析等功能

**Architecture:** 采用Streamlit多Tab布局，将现有单文件拆分为模块化结构：services层处理数据和AI，components层封装可复用UI组件，pages层实现各Tab页面

**Tech Stack:** Streamlit, AkShare, Pandas, Matplotlib, OpenAI SDK (阿里百炼)

---

## 文件结构规划

```
stock_streamlit/
├── app.py                      # 主入口，Tab布局 + 全局样式
├── services/
│   ├── __init__.py
│   ├── data_service.py         # 数据获取服务（AkShare封装）
│   ├── ai_service.py           # AI分析服务
│   └── sentiment_service.py    # 情绪计算服务
├── components/
│   ├── __init__.py
│   ├── stock_card.py           # 自选股卡片组件
│   ├── market_index.py         # 大盘指数组件
│   ├── sentiment_panel.py      # 市场情绪面板组件
│   ├── news_timeline.py        # 资讯时间线组件
│   └── chart.py                # 图表组件
├── utils/
│   ├── __init__.py
│   ├── indicators.py           # 技术指标计算
│   ├── theme.py                # 主题管理
│   └── helpers.py              # 工具函数
├── pages/
│   ├── __init__.py
│   ├── tab_watchlist.py        # Tab1: 自选股
│   ├── tab_analysis.py         # Tab2: 个股分析
│   ├── tab_indicators.py       # Tab3: 技术指标
│   └── tab_ai.py               # Tab4: AI深度分析
├── watchlist.json              # 自选股持久化
├── .env                        # 配置文件
└── requirements.txt
```

---

## 第一阶段：基础重构

### Task 1: 创建目录结构和基础文件

**Files:**
- Create: `services/__init__.py`
- Create: `components/__init__.py`
- Create: `utils/__init__.py`
- Create: `pages/__init__.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p services components utils pages
```

- [ ] **Step 2: 创建__init__.py文件**

创建空的`__init__.py`文件使目录成为Python包

- [ ] **Step 3: 验证目录结构**

```bash
ls -la services/ components/ utils/ pages/
```

---

### Task 2: 提取数据服务层

**Files:**
- Create: `services/data_service.py`
- Modify: `app.py` (删除数据函数，改为导入)

- [ ] **Step 1: 创建 data_service.py**

将以下函数从 `app.py` 移动到 `services/data_service.py`:
- `load_all_stocks()`
- `get_quote_from_cache()`
- `get_watchlist_quotes()`
- `get_history()`
- `get_ma_data()`
- `get_news()`
- `search_stock()`
- `format_volume()`
- `get_market_info()`
- 新增: `get_market_index()` - 获取大盘指数
- 新增: `get_limit_up_pool()` - 获取涨停池
- 新增: `get_north_flow()` - 获取北向资金

```python
# services/data_service.py
import streamlit as st
import pandas as pd
import akshare as ak
from typing import Tuple, Optional, List, Dict, Any

@st.cache_data(ttl=60)
def load_all_stocks() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """加载全市场股票列表"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df, None
    except Exception as e:
        return None, f"加载股票列表失败: {str(e)}"

@st.cache_data(ttl=30)
def get_market_index() -> Tuple[Optional[List[Dict]], Optional[str]]:
    """获取大盘指数"""
    try:
        df = ak.stock_zh_index_spot_em()
        indices = ['上证指数', '深证成指', '创业板指', '科创50']
        codes = ['sh000001', 'sz399001', 'sz399006', 'sh000688']
        result = []
        for idx, code in zip(indices, codes):
            row = df[df['代码'] == code.replace('sh', '').replace('sz', '')]
            if not row.empty:
                r = row.iloc[0]
                result.append({
                    'name': idx,
                    'price': float(r['最新价']),
                    'change_pct': float(r['涨跌幅'])
                })
        return result, None
    except Exception as e:
        return None, f"获取大盘指数失败: {str(e)}"

@st.cache_data(ttl=60)
def get_limit_up_pool() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """获取涨停池"""
    try:
        df = ak.stock_zt_pool_em(date=None)
        return df, None
    except Exception as e:
        return None, f"获取涨停池失败: {str(e)}"

@st.cache_data(ttl=60)
def get_north_flow() -> Tuple[Optional[float], Optional[str]]:
    """获取北向资金净流入"""
    try:
        df = ak.stock_hsgt_north_net_flow_in_em()
        if not df.empty:
            return float(df.iloc[-1]['当日净流入']), None
        return 0.0, None
    except Exception as e:
        return None, f"获取北向资金失败: {str(e)}"

# ... 其他函数（从app.py移动，保持原有实现）
def get_quote_from_cache(symbol, all_stocks_df):
    """从缓存中获取实时行情"""
    if all_stocks_df is None:
        return None, "请先初始化数据"
    try:
        stock = all_stocks_df[all_stocks_df['代码'] == symbol]
        if stock.empty:
            return None, f"未找到股票代码: {symbol}"
        row = stock.iloc[0]
        return {
            "symbol": symbol, "name": row['名称'], "price": float(row['最新价']),
            "change_pct": float(row['涨跌幅']), "change": float(row['涨跌额']),
            "high": float(row['最高']), "low": float(row['最低']),
            "open": float(row['今开']), "volume": float(row['成交量']),
            "amount": float(row['成交额']),
        }, None
    except Exception as e:
        return None, f"获取行情失败: {str(e)}"

def get_watchlist_quotes(watchlist, all_stocks_df):
    """获取自选股行情列表"""
    quotes = []
    for stock in watchlist:
        quote, _ = get_quote_from_cache(stock['symbol'], all_stocks_df)
        if quote:
            quotes.append(quote)
    return quotes

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

@st.cache_data(ttl=300)
def get_ma_data(symbol, all_stocks_df):
    """获取均线数据"""
    df, _ = get_history(symbol, 30)
    if df is not None and len(df) > 0:
        latest = df.iloc[-1]
        return {'MA5': latest.get('MA5', 0), 'MA13': 0, 'MA20': latest.get('MA20', 0),
                'high_vol_30': df['成交量'].max() if '成交量' in df.columns else 0}
    return {'MA5': 0, 'MA13': 0, 'MA20': 0, 'high_vol_30': 0}

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

def search_stock(keyword, all_stocks_df):
    """搜索股票"""
    if all_stocks_df is None:
        return [], "请先初始化数据"
    try:
        mask = all_stocks_df['代码'].str.contains(keyword, case=False, na=False) | \
               all_stocks_df['名称'].str.contains(keyword, case=False, na=False)
        results = all_stocks_df[mask][['代码', '名称']].head(10)
        if results.empty:
            return [], f"未找到匹配 '{keyword}' 的股票"
        return results.to_dict('records'), None
    except Exception as e:
        return [], f"搜索失败: {str(e)}"

def format_volume(vol):
    """格式化成交量"""
    if vol >= 100000000:
        return f"{vol/100000000:.2f}亿手"
    elif vol >= 10000:
        return f"{vol/10000:.1f}万手"
    return f"{vol:.0f}手"

def get_market_info(symbol):
    """获取市场信息"""
    if symbol.startswith('6'): return "沪市主板"
    elif symbol.startswith('0'): return "深市主板"
    elif symbol.startswith('3'): return "创业板"
    elif symbol.startswith('68'): return "科创板"
    return "A股"
```

- [ ] **Step 2: 更新 app.py 导入**

```python
from services.data_service import (
    load_all_stocks, get_quote_from_cache, get_watchlist_quotes,
    get_history, get_ma_data, get_news, search_stock,
    format_volume, get_market_info, get_market_index,
    get_limit_up_pool, get_north_flow
)
```

- [ ] **Step 3: 验证导入正确**

运行 `py -c "from services.data_service import *"` 确认无报错

- [ ] **Step 4: 提交**

```bash
git add services/data_service.py app.py
git commit -m "refactor: 提取数据服务层到 services/data_service.py"
```

---

### Task 3: 提取AI服务层

**Files:**
- Create: `services/ai_service.py`
- Modify: `app.py`

- [ ] **Step 1: 创建 ai_service.py**

```python
# services/ai_service.py
import os
from openai import OpenAI
from typing import Optional

def get_ai_config():
    """获取AI配置"""
    return {
        'api_key': os.getenv("DASHSCOPE_API_KEY", ""),
        'base_url': os.getenv("DASHSCOPE_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1"),
        'model': os.getenv("DASHSCOPE_MODEL", "glm-5")
    }

def ai_analyze(context: str, question: str, style: str = "短线交易", depth: str = "详细报告") -> str:
    """AI分析"""
    config = get_ai_config()
    if not config['api_key']:
        return "⚠️ 请配置 DASHSCOPE_API_KEY"

    style_prompts = {
        "短线交易": "从短线交易角度分析，关注日内波动、支撑压力位、买卖时机",
        "中长线投资": "从中长线投资角度分析，关注趋势、基本面、估值水平",
        "价值投资": "从价值投资角度分析，关注企业内在价值、安全边际",
        "技术面分析": "纯技术面分析，关注K线形态、指标信号、量价关系",
        "基本面分析": "从基本面分析，关注财务数据、行业地位、成长性"
    }

    depth_prompts = {
        "简要解读": "用3-5句话简洁总结核心观点",
        "详细报告": "详细分析各维度，给出完整报告",
        "专业级深度分析": "深度专业分析，包含详细的逻辑推演和数据支撑"
    }

    try:
        client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {'role': 'system', 'content': f'你是专业股票分析师。{style_prompts.get(style, "")}{depth_prompts.get(depth, "")}客观分析数据，不提供投资建议。'},
                {'role': 'user', 'content': f"数据:{context}\n问题:{question}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI分析出错: {str(e)}"

def ai_multi_dimension_analysis(context: dict, style: str, depth: str) -> dict:
    """多维度AI分析 - 第三阶段实现"""
    # TODO: 第三阶段实现结构化分析输出
    return {}

def ai_industry_compare(stock_data: dict, industry_data: dict) -> str:
    """行业对比分析 - 第三阶段实现"""
    # TODO: 第三阶段实现行业对比
    return "行业对比分析功能将在第三阶段实现"

def ai_similarity_analysis(current_pattern: str, history_patterns: list) -> str:
    """历史相似走势分析 - 第三阶段实现"""
    # TODO: 第三阶段实现相似走势分析
    return "历史相似走势分析功能将在第三阶段实现"
```

- [ ] **Step 2: 更新 app.py 导入**

- [ ] **Step 3: 验证并提交**

---

### Task 4: 创建情绪计算服务

**Files:**
- Create: `services/sentiment_service.py`

- [ ] **Step 1: 创建情绪计算服务**

```python
# services/sentiment_service.py
import pandas as pd
import numpy as np
from typing import Dict, Optional
import streamlit as st

@st.cache_data(ttl=60)
def calculate_market_sentiment(all_stocks_df: pd.DataFrame, limit_up_df: Optional[pd.DataFrame] = None) -> Dict:
    """计算市场情绪"""
    if all_stocks_df is None:
        return {}

    # 涨跌家数
    up_count = len(all_stocks_df[all_stocks_df['涨跌幅'] > 0])
    down_count = len(all_stocks_df[all_stocks_df['涨跌幅'] < 0])
    total = len(all_stocks_df)

    # 涨停/跌停
    limit_up = len(limit_up_df) if limit_up_df is not None else 0

    # 市场热度评分 (0-100)
    heat_score = int((up_count / total) * 100) if total > 0 else 50

    # 恐惧贪婪指数 (简化版)
    avg_change = all_stocks_df['涨跌幅'].mean()
    fear_greed = 50 + avg_change * 5  # 简化计算
    fear_greed = max(0, min(100, int(fear_greed)))

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
```

- [ ] **Step 2: 验证并提交**

---

### Task 5: 创建工具函数模块

**Files:**
- Create: `utils/helpers.py`
- Create: `utils/theme.py`
- Create: `utils/indicators.py`

- [ ] **Step 1: 创建 helpers.py**

```python
# utils/helpers.py
import json
import os
from typing import List, Dict

WATCHLIST_FILE = "watchlist.json"

def load_watchlist() -> List[Dict]:
    """加载自选股"""
    try:
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return [{"symbol": "600519", "name": "贵州茅台"},
            {"symbol": "000001", "name": "平安银行"},
            {"symbol": "000858", "name": "五粮液"}]

def save_watchlist(watchlist: List[Dict]):
    """保存自选股"""
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=2)

def add_to_watchlist(symbol: str, name: str) -> tuple:
    """添加自选股"""
    watchlist = load_watchlist()
    if not any(s['symbol'] == symbol for s in watchlist):
        watchlist.append({"symbol": symbol, "name": name})
        save_watchlist(watchlist)
        return True, "添加成功"
    return False, "已在自选股中"

def remove_from_watchlist(symbol: str) -> tuple:
    """删除自选股"""
    watchlist = load_watchlist()
    watchlist = [s for s in watchlist if s['symbol'] != symbol]
    save_watchlist(watchlist)
    return True, "删除成功"
```

- [ ] **Step 2: 创建 theme.py**

```python
# utils/theme.py
import streamlit as st

THEMES = {
    'light': {
        'bg': '#FFFFFF',
        'card': '#F8F9FA',
        'up': '#FF4757',
        'down': '#2ED573',
        'text': '#2D3436',
        'border': '#E8E8E8'
    },
    'dark': {
        'bg': '#1A1A2E',
        'card': '#16213E',
        'up': '#FF6B6B',
        'down': '#4ECDC4',
        'text': '#FFFFFF',
        'border': '#2D3436'
    }
}

def get_theme():
    """获取当前主题"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    return st.session_state.theme

def toggle_theme():
    """切换主题"""
    current = get_theme()
    st.session_state.theme = 'dark' if current == 'light' else 'light'

def get_theme_colors():
    """获取主题颜色"""
    return THEMES[get_theme()]

def apply_theme_styles():
    """应用主题样式"""
    colors = get_theme_colors()
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {colors['bg']}; }}
        .stock-card {{ background-color: {colors['card']}; border-color: {colors['border']}; }}
        .stock-name {{ color: {colors['text']}; }}
        .price-up {{ color: {colors['up']}; }}
        .price-down {{ color: {colors['down']}; }}
    </style>
    """, unsafe_allow_html=True)
```

- [ ] **Step 3: 创建 indicators.py**

```python
# utils/indicators.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def calc_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
    """计算均线"""
    for p in periods:
        df[f'MA{p}'] = df['收盘'].rolling(p).mean()
    return df

def calc_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """计算MACD"""
    exp1 = df['收盘'].ewm(span=fast, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df

def calc_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """计算RSI"""
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss.replace(0, 0.001)))
    return df

def calc_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """计算KDJ"""
    low_min = df['最低'].rolling(n).min()
    high_max = df['最高'].rolling(n).max()
    df['KDJ_RSV'] = (df['收盘'] - low_min) / (high_max - low_min) * 100
    df['KDJ_K'] = df['KDJ_RSV'].ewm(alpha=1/m1, adjust=False).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(alpha=1/m2, adjust=False).mean()
    df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
    return df

def calc_boll(df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
    """计算布林带"""
    df['BOLL_MID'] = df['收盘'].rolling(period).mean()
    std = df['收盘'].rolling(period).std()
    df['BOLL_UPPER'] = df['BOLL_MID'] + std_dev * std
    df['BOLL_LOWER'] = df['BOLL_MID'] - std_dev * std
    return df

def detect_macd_cross(df: pd.DataFrame) -> List[Tuple[str, str]]:
    """检测MACD金叉死叉"""
    signals = []
    for i in range(1, len(df)):
        if df['MACD'].iloc[i-1] <= df['MACD_Signal'].iloc[i-1] and \
           df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i]:
            signals.append((df.index[i], 'buy'))
        elif df['MACD'].iloc[i-1] >= df['MACD_Signal'].iloc[i-1] and \
             df['MACD'].iloc[i] < df['MACD_Signal'].iloc[i]:
            signals.append((df.index[i], 'sell'))
    return signals

def detect_ma_cross(df: pd.DataFrame, short: int = 5, long: int = 20) -> List[Tuple[str, str]]:
    """检测均线交叉"""
    signals = []
    short_ma = f'MA{short}'
    long_ma = f'MA{long}'
    for i in range(1, len(df)):
        if df[short_ma].iloc[i-1] <= df[long_ma].iloc[i-1] and \
           df[short_ma].iloc[i] > df[long_ma].iloc[i]:
            signals.append((df.index[i], 'buy'))
        elif df[short_ma].iloc[i-1] >= df[long_ma].iloc[i-1] and \
             df[short_ma].iloc[i] < df[long_ma].iloc[i]:
            signals.append((df.index[i], 'sell'))
    return signals
```

- [ ] **Step 4: 验证并提交**

---

### Task 6: 创建大盘指数组件

**Files:**
- Create: `components/market_index.py`

- [ ] **Step 1: 创建大盘指数组件**

```python
# components/market_index.py
import streamlit as st
from typing import List, Dict

def render_market_index(indices: List[Dict]):
    """渲染大盘指数"""
    if not indices:
        st.warning("⚠️ 大盘指数数据加载中...")
        return

    cols = st.columns(4)
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
        return

    html = '<div style="display:flex; gap:15px; flex-wrap:wrap;">'
    for idx in indices:
        pct = idx['change_pct']
        color = "#ff4757" if pct >= 0 else "#2ed573"
        arrow = "↑" if pct >= 0 else "↓"
        html += f'''
        <div style="padding:5px 10px; background:#f5f5f5; border-radius:4px;">
            <span style="color:#666;">{idx['name']}</span>
            <span style="font-weight:bold; margin-left:5px;">{idx['price']:,.0f}</span>
            <span style="color:{color}; margin-left:5px;">{arrow}{abs(pct):.2f}%</span>
        </div>
        '''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
```

- [ ] **Step 2: 验证并提交**

---

### Task 7: 创建市场情绪面板组件

**Files:**
- Create: `components/sentiment_panel.py`

- [ ] **Step 1: 创建情绪面板组件**

```python
# components/sentiment_panel.py
import streamlit as st
from typing import Dict

def render_sentiment_panel(sentiment: Dict, north_flow: float = None):
    """渲染市场情绪面板"""
    if not sentiment:
        return

    fear_greed = sentiment.get('fear_greed', 50)
    fear_label = sentiment.get('fear_greed_label', '中性')

    st.markdown("#### 🌡️ 市场情绪")

    # 恐惧贪婪指数
    col1, col2 = st.columns([3, 1])
    with col1:
        bar_color = "#ff4757" if fear_greed >= 60 else "#2ed573" if fear_greed <= 40 else "#666"
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
    cols[3].metric("北向资金", f"{north_flow/1e8:.1f}亿" if north_flow else "--", delta=None)

    st.markdown("---")
```

- [ ] **Step 2: 验证并提交**

---

### Task 8: 创建自选股卡片组件

**Files:**
- Create: `components/stock_card.py`

- [ ] **Step 1: 创建自选股卡片组件**

```python
# components/stock_card.py
import streamlit as st
from typing import Dict, List

def render_stock_card(quote: Dict, ma_data: Dict, sentiment_tags: List[str], on_analyze, on_remove):
    """渲染自选股卡片"""
    pct = quote['change_pct']
    is_up = pct >= 0
    card_class = "stock-card-up" if is_up else "stock-card-down"
    price_class = "price-up" if is_up else "price-down"
    arrow = "📈" if is_up else "📉"

    st.markdown(f"""
    <div class="stock-card {card_class}">
        <div class="stock-header">
            <span>
                <span class="stock-name">{quote['name']}</span>
                <span class="stock-code">{quote['symbol']}</span>
            </span>
        </div>
        <div class="stock-row">
            <span class="stock-label">当量 {format_volume(quote['volume'])}</span>
            <span class="stock-label">30天高量 {format_volume(ma_data.get('high_vol_30', 0))}</span>
        </div>
        <div class="stock-price-row">
            <div class="price-item">
                <div class="price-label">当前价</div>
                <div class="price-value {price_class}">{quote['price']:.2f}</div>
            </div>
            <div class="price-item">
                <div class="price-label">当日涨幅</div>
                <div class="price-value {price_class}">{arrow} {pct:.2f}%</div>
            </div>
            <div class="price-item">
                <div class="price-label">开盘价</div>
                <div class="price-value">{quote['open']:.2f}</div>
            </div>
        </div>
        <div class="data-grid">
            <div class="grid-item">
                <div class="stock-label">MA5</div>
                <div class="stock-value">{ma_data.get('MA5', 0):.2f}</div>
            </div>
            <div class="grid-item">
                <div class="stock-label">MA13</div>
                <div class="stock-value">{ma_data.get('MA13', 0):.2f}</div>
            </div>
            <div class="grid-item">
                <div class="stock-label">MA20</div>
                <div class="stock-value">{ma_data.get('MA20', 0):.2f}</div>
            </div>
        </div>
        <div style="margin-top:8px; font-size:0.8rem;">
            {' '.join(sentiment_tags)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📊 分析", key=f"analyze_{quote['symbol']}", type="primary", use_container_width=True):
            on_analyze(quote['symbol'])
    with col2:
        if st.button("🗑️ 删除", key=f"remove_{quote['symbol']}", use_container_width=True):
            on_remove(quote['symbol'])

def format_volume(vol: float) -> str:
    """格式化成交量"""
    if vol >= 100000000:
        return f"{vol/100000000:.2f}亿手"
    elif vol >= 10000:
        return f"{vol/10000:.1f}万手"
    return f"{vol:.0f}手"
```

- [ ] **Step 2: 验证并提交**

---

### Task 9: 创建资讯时间线组件

**Files:**
- Create: `components/news_timeline.py`

- [ ] **Step 1: 创建资讯时间线组件**

```python
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
```

- [ ] **Step 2: 验证并提交**

---

### Task 10: 重构主应用为Tab布局（框架版）

**Files:**
- Modify: `app.py` (创建Tab框架，不含Tab页面内容)

**注意:** 此任务只创建框架，Tab页面内容在 Task 11-14 中创建

- [ ] **Step 1: 重写 app.py 为Tab框架**

```python
# app.py - 第一阶段只创建框架，Tab内容由各Tab页面模块提供
import streamlit as st
import pandas as pd
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

# 导入服务（这些文件已在前面的任务中创建）
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
    .stock-header { display:flex; justify-content:space-between; margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #f0f0f0; }
    .stock-name { font-size:1.1rem; font-weight:bold; color:#2d3436; }
    .stock-code { font-size:0.8rem; color:#636e72; margin-left:8px; }
    .stock-row { display:flex; justify-content:space-between; margin:6px 0; }
    .stock-label { font-size:0.8rem; color:#636e72; }
    .stock-value { font-size:0.9rem; font-weight:500; color:#2d3436; }
    .price-up { color:#ff4757; }
    .price-down { color:#2ed573; }
    .stock-price-row { display:flex; justify-content:space-around; padding:10px 0; background:#fafafa; border-radius:6px; margin:8px 0; }
    .price-item { text-align:center; }
    .price-label { font-size:0.75rem; color:#636e72; }
    .price-value { font-size:1.1rem; font-weight:bold; margin-top:4px; }
    .data-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin:6px 0; }
    .grid-item { text-align:center; }
</style>
""", unsafe_allow_html=True)

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
col_title, col_theme = st.columns([5, 1])
with col_title:
    st.title("📊 股票分析")
with col_theme:
    theme_icon = "🌙" if get_theme() == 'light' else "☀️"
    if st.button(theme_icon, key="theme_toggle"):
        toggle_theme()
        st.rerun()

# Tab 布局 - 导入在顶部完成，避免运行时导入
from pages.tab_watchlist import render_tab_watchlist
from pages.tab_analysis import render_tab_analysis
from pages.tab_indicators import render_tab_indicators
from pages.tab_ai import render_tab_ai

tab1, tab2, tab3, tab4 = st.tabs(["⭐ 自选股", "📈 个股分析", "📊 技术指标", "🤖 AI分析"])

with tab1:
    render_tab_watchlist()
with tab2:
    render_tab_analysis()
with tab3:
    render_tab_indicators()
with tab4:
    render_tab_ai()

# 底部状态栏
st.markdown("---")
st.caption("数据: AkShare | AI: 阿里百炼 | ⚠️ 仅供参考，不构成投资建议")
```

- [ ] **Step 2: 注意事项**

此步骤在 Task 11-14 完成后才能正常运行。可以先提交框架代码，后续任务添加Tab页面后再测试。

- [ ] **Step 3: 提交**

```bash
git add app.py
git commit -m "refactor: 重构app.py为Tab布局框架"
```

---

### Task 11: 创建自选股Tab页面

**Files:**
- Create: `pages/tab_watchlist.py`

- [ ] **Step 1: 创建自选股Tab**

```python
# pages/tab_watchlist.py
import streamlit as st
from services.data_service import *
from services.sentiment_service import calculate_market_sentiment, calculate_stock_sentiment
from utils.helpers import *
from components.market_index import render_market_index_simple
from components.sentiment_panel import render_sentiment_panel
from components.stock_card import render_stock_card

def render_tab_watchlist():
    """渲染自选股Tab"""

    # 初始化数据按钮
    col_init, col_status = st.columns([1, 3])
    with col_init:
        if st.button("🔄 初始化数据", type="secondary"):
            with st.spinner("正在加载全市场股票数据（约1-2分钟）..."):
                df, error = load_all_stocks()
                if error:
                    st.error(error)
                else:
                    st.session_state.all_stocks = df
                    st.session_state.stocks_loaded = True
                    st.success(f"✅ 已加载 {len(df)} 只股票！")

    with col_status:
        if st.session_state.stocks_loaded:
            st.info(f"✅ 数据已初始化，共 {len(st.session_state.all_stocks)} 只股票")
        else:
            st.warning("⚠️ 请先点击'初始化数据'按钮")

    st.markdown("---")

    # 大盘指数
    if st.session_state.stocks_loaded:
        indices, _ = get_market_index()
        render_market_index_simple(indices)

        st.markdown("---")

        # 市场情绪
        sentiment = calculate_market_sentiment(st.session_state.all_stocks)
        north_flow, _ = get_north_flow()
        render_sentiment_panel(sentiment, north_flow)

        st.markdown("---")

    # 自选股列表
    st.markdown("### 自选股")

    if st.session_state.stocks_loaded and st.session_state.watchlist:
        quotes = get_watchlist_quotes(st.session_state.watchlist, st.session_state.all_stocks)

        for q in quotes:
            ma_data = get_ma_data(q['symbol'], st.session_state.all_stocks)
            sentiment_tags = calculate_stock_sentiment(q, ma_data).get('tags', [])

            def on_analyze(symbol):
                st.session_state.selected_symbol = symbol

            def on_remove(symbol):
                remove_from_watchlist(symbol)
                st.session_state.watchlist = load_watchlist()

            render_stock_card(q, ma_data, sentiment_tags, on_analyze, on_remove)

    # 添加自选股
    st.markdown("---")
    st.markdown("#### ➕ 添加自选股")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("搜索股票", key="watchlist_search", placeholder="输入代码或名称")

    with col2:
        selected = None
        if search.strip() and st.session_state.stocks_loaded:
            results, _ = search_stock(search.strip(), st.session_state.all_stocks)
            if results:
                options = [f"{r['代码']} - {r['名称']}" for r in results]
                selected = st.selectbox("选择股票", options, key="watchlist_select")

    with col3:
        if st.button("添加", type="primary", use_container_width=True):
            if selected:
                symbol = selected.split(" - ")[0]
                name = selected.split(" - ")[1]
                success, msg = add_to_watchlist(symbol, name)
                st.session_state.watchlist = load_watchlist()
                if success:
                    st.success(msg)
                else:
                    st.warning(msg)
                st.rerun()
```

- [ ] **Step 2: 验证并提交**

---

### Task 12: 创建个股分析Tab页面

**Files:**
- Create: `pages/tab_analysis.py`

- [ ] **Step 1: 创建个股分析Tab**

```python
# pages/tab_analysis.py
import streamlit as st
import json
from services.data_service import *
from services.ai_service import ai_analyze
from utils.helpers import add_to_watchlist, load_watchlist
from components.news_timeline import render_news_timeline
from components.chart import render_simple_chart

def render_tab_analysis():
    """渲染个股分析Tab"""

    # 股票选择
    col1, col2 = st.columns([4, 1])
    with col1:
        search = st.text_input("🔍 搜索股票", key="analysis_search", placeholder="输入代码或名称")

    symbol = st.session_state.get('selected_symbol')

    if search.strip() and st.session_state.stocks_loaded:
        results, _ = search_stock(search.strip(), st.session_state.all_stocks)
        if results:
            options = [f"{r['代码']} - {r['名称']}" for r in results]
            selected = st.selectbox("选择股票", options, key="analysis_select")
            if st.button("分析此股票"):
                st.session_state.selected_symbol = selected.split(" - ")[0]
                st.rerun()

    if not symbol:
        st.info("👆 请选择或搜索股票进行分析")
        return

    if not st.session_state.stocks_loaded:
        st.warning("⚠️ 请先在自选股Tab初始化数据")
        return

    # 获取数据
    quote, _ = get_quote_from_cache(symbol, st.session_state.all_stocks)
    if not quote:
        st.error("未找到股票")
        return

    # 行情概览
    st.subheader(f"{quote['name']} ({symbol})")
    cols = st.columns(4)
    pct = quote['change_pct']
    arrow = "📈" if pct >= 0 else "📉"
    cols[0].metric("当前价", f"{quote['price']:.2f}", f"{arrow} {pct:.2f}%")
    cols[1].metric("最高", f"{quote['high']:.2f}")
    cols[2].metric("最低", f"{quote['low']:.2f}")
    cols[3].metric("成交额", f"{quote['amount']/1e8:.1f}亿")

    # 加入自选股
    if not any(s['symbol'] == symbol for s in st.session_state.watchlist):
        if st.button("⭐ 加入自选股"):
            add_to_watchlist(symbol, quote['name'])
            st.session_state.watchlist = load_watchlist()
            st.success("已添加")
            st.rerun()

    st.markdown("---")

    # 简洁图表
    with st.expander("📈 技术图表", expanded=True):
        df, _ = get_history(symbol, 60)
        if df is not None:
            render_simple_chart(df, quote['name'], symbol)

            # 基础指标
            latest = df.iloc[-1]
            cols = st.columns(4)
            cols[0].metric("MA5", f"{latest['MA5']:.2f}")
            cols[1].metric("MA10", f"{latest['MA10']:.2f}")
            cols[2].metric("RSI", f"{latest['RSI']:.1f}")
            macd_status = "金叉" if latest['MACD'] > 0 else "死叉"
            cols[3].metric("MACD", f"{latest['MACD']:.3f}", macd_status)

    st.markdown("---")

    # 资讯时间线
    with st.expander("📰 资讯时间线", expanded=True):
        news, _ = get_news(symbol, 10)
        render_news_timeline(news)

    st.markdown("---")

    # AI简要分析
    with st.expander("🤖 AI简要分析"):
        if st.button("开始分析"):
            with st.spinner("分析中..."):
                ctx = {
                    "quote": quote,
                    "indicators": {"MA5": float(latest['MA5']), "RSI": float(latest['RSI'])}
                }
                result = ai_analyze(json.dumps(ctx), f"简要分析{quote['name']}投资价值")
                st.markdown(result)
```

- [ ] **Step 2: 创建图表组件 components/chart.py**

```python
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
    pass
```

- [ ] **Step 3: 验证并提交**

---

## 第二阶段：技术深化

**说明:** 第二至第四阶段的任务依赖第一阶段完成后的代码结构。以下提供任务框架，详细代码将在实施时根据第一阶段结果补充。

### Task 13: 创建技术指标Tab页面

**Files:**
- Create: `pages/tab_indicators.py`
- Modify: `components/chart.py`

**前置条件:** 第一阶段所有任务完成

- [ ] **Step 1: 创建 tab_indicators.py 基础结构**

```python
# pages/tab_indicators.py
import streamlit as st
from services.data_service import get_history, search_stock
from utils.indicators import calc_ma, calc_macd, calc_rsi, calc_kdj, calc_boll
from components.chart import render_simple_chart

def render_tab_indicators():
    """渲染技术指标Tab"""
    st.markdown("### 📊 技术指标分析")

    # 股票选择
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("搜索股票", key="indicators_search")
    with col2:
        period = st.selectbox("周期", ["日线", "周线", "月线"], key="indicators_period")

    symbol = st.session_state.get('selected_symbol')

    if not symbol:
        st.info("👆 请先在自选股或个股分析Tab选择股票")
        return

    # 指标选择器
    st.markdown("#### 指标选择")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_ma = st.checkbox("均线 (MA)", value=True)
        ma_periods = st.multiselect("均线周期", [5, 10, 20, 60], default=[5, 10, 20])
    with col2:
        show_macd = st.checkbox("MACD", value=True)
    with col3:
        show_rsi = st.checkbox("RSI", value=True)
        rsi_period = st.number_input("RSI周期", min_value=5, max_value=30, value=14)
    with col4:
        show_kdj = st.checkbox("KDJ", value=False)

    # 参数调整
    with st.expander("⚙️ 高级参数"):
        if show_macd:
            col1, col2, col3 = st.columns(3)
            macd_fast = col1.number_input("MACD快线", min_value=5, max_value=20, value=12)
            macd_slow = col2.number_input("MACD慢线", min_value=15, max_value=40, value=26)
            macd_signal = col3.number_input("MACD信号线", min_value=5, max_value=15, value=9)

    # 获取数据并计算指标
    df, _ = get_history(symbol, 120)
    if df is not None:
        df = calc_ma(df, ma_periods if show_ma else [])
        if show_macd:
            df = calc_macd(df, macd_fast, macd_slow, macd_signal)
        if show_rsi:
            df = calc_rsi(df, rsi_period)
        if show_kdj:
            df = calc_kdj(df)

        # 显示图表
        render_simple_chart(df, st.session_state.get('stock_name', symbol), symbol)

        # 显示指标数值
        st.markdown("#### 最新指标值")
        latest = df.iloc[-1]
        cols = st.columns(4)
        if show_ma and ma_periods:
            cols[0].metric(f"MA{ma_periods[0]}", f"{latest.get(f'MA{ma_periods[0]}', 0):.2f}")
        if show_macd:
            cols[1].metric("MACD", f"{latest.get('MACD', 0):.3f}")
        if show_rsi:
            cols[2].metric("RSI", f"{latest.get('RSI', 0):.1f}")
        if show_kdj:
            cols[3].metric("KDJ-K", f"{latest.get('KDJ_K', 0):.1f}")
```

- [ ] **Step 2: 验证并提交**

```bash
git add pages/tab_indicators.py
git commit -m "feat: 添加技术指标Tab基础功能"
```

---

### Task 14: 实现指标组合策略

**Files:**
- Modify: `pages/tab_indicators.py`
- Modify: `utils/indicators.py`

- [ ] **Step 1: 添加策略检测函数到 indicators.py**

```python
# 添加到 utils/indicators.py
STRATEGIES = {
    "MACD金叉+RSI超卖": {
        "conditions": ["macd_cross_up", "rsi_oversold"],
        "description": "MACD金叉且RSI<30，超卖反弹信号"
    },
    "KDJ金叉+成交量放大": {
        "conditions": ["kdj_cross_up", "volume_increase"],
        "description": "KDJ金叉且成交量放大，短期买入信号"
    },
    "BOLL下轨支撑": {
        "conditions": ["boll_lower_support"],
        "description": "价格触及布林下轨，可能反弹"
    },
    "MA多头排列": {
        "conditions": ["ma_bullish"],
        "description": "均线多头排列，上涨趋势"
    }
}

def check_strategy(df, strategy_name):
    """检查策略是否触发"""
    # TODO: 实现具体策略检测逻辑
    return False
```

- [ ] **Step 2: 在 tab_indicators.py 添加策略选择器**

- [ ] **Step 3: 验证并提交**

---

### Task 15: 实现买卖点标记

**Files:**
- Modify: `components/chart.py`
- Modify: `pages/tab_indicators.py`

- [ ] **Step 1: 修改 chart.py 添加买卖点标记功能**

```python
def render_chart_with_signals(df, name, symbol, signals):
    """渲染带买卖点标记的图表"""
    # signals: [(index, 'buy'), (index, 'sell'), ...]
    fig, ax = plt.subplots(figsize=(12, 6))
    # ... 绘制K线
    for idx, signal_type in signals:
        if signal_type == 'buy':
            ax.annotate('买', xy=(idx, df.iloc[idx]['最低']),
                       color='red', fontsize=10, ha='center')
        else:
            ax.annotate('卖', xy=(idx, df.iloc[idx]['最高']),
                       color='green', fontsize=10, ha='center')
    st.pyplot(fig)
```

- [ ] **Step 2: 验证并提交**

---

## 第三阶段：AI智能

### Task 16: 创建AI深度分析Tab页面

**Files:**
- Create: `pages/tab_ai.py`

- [ ] **Step 1: 创建AI分析Tab基础结构**

```python
# pages/tab_ai.py
import streamlit as st
import json
from services.data_service import get_history, get_quote_from_cache
from services.ai_service import ai_analyze
from utils.helpers import load_watchlist

def render_tab_ai():
    """渲染AI深度分析Tab"""
    st.markdown("### 🤖 AI深度分析")

    symbol = st.session_state.get('selected_symbol')
    if not symbol:
        st.info("👆 请先选择股票")
        return

    # 分析配置
    st.markdown("#### 分析配置")
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("分析风格",
            ["短线交易", "中长线投资", "价值投资", "技术面分析", "基本面分析"])
    with col2:
        depth = st.selectbox("分析深度",
            ["简要解读", "详细报告", "专业级深度分析"])

    if st.button("开始AI分析", type="primary"):
        with st.spinner("AI分析中..."):
            # 获取数据
            quote, _ = get_quote_from_cache(symbol, st.session_state.all_stocks)
            df, _ = get_history(symbol, 60)

            if quote and df is not None:
                latest = df.iloc[-1]
                ctx = {
                    "quote": quote,
                    "indicators": {
                        "MA5": float(latest['MA5']),
                        "MA10": float(latest['MA10']),
                        "RSI": float(latest['RSI']),
                        "MACD": float(latest['MACD'])
                    }
                }
                result = ai_analyze(json.dumps(ctx, ensure_ascii=False),
                                    f"从{style}角度分析投资价值", style, depth)
                st.markdown("#### 分析结果")
                st.markdown(result)

    # TODO: 第三阶段添加多维度分析、行业对比等功能
```

- [ ] **Step 2: 验证并提交**

---

### Task 17-19: AI高级功能

**说明:** 这些任务在第三阶段实施时根据第一阶段结果补充详细代码

- Task 17: 多维度分析输出
- Task 18: 同行业对比分析
- Task 19: 历史相似走势分析

---

## 第四阶段：优化完善

### Task 20-22: 优化功能

**说明:** 这些任务在前三阶段完成后实施

- Task 20: 完善深色主题
- Task 21: AI实时问答
- Task 22: 性能优化和错误处理

---

## 执行顺序总结

| 阶段 | 任务数 | 预计时间 |
|------|--------|----------|
| 第一阶段 | 12个任务 | 基础框架 |
| 第二阶段 | 3个任务 | 技术指标 |
| 第三阶段 | 4个任务 | AI分析 |
| 第四阶段 | 3个任务 | 优化完善 |

**总计: 22个任务**