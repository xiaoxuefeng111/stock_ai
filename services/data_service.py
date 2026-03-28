# services/data_service.py
"""
Data service layer for stock analysis application.
Provides data fetching and caching functionality.
"""
import streamlit as st
import pandas as pd
import akshare as ak
from typing import Tuple, Optional, List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_api_call(func, *args, **kwargs):
    """安全的API调用包装器"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"API调用失败: {func.__name__}, 错误: {str(e)}")
        return None, f"数据获取失败: {str(e)}"


@st.cache_data(ttl=60)
def load_all_stocks() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """加载全市场股票列表（首次需要1-2分钟）"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df, None
    except Exception as e:
        error_msg = str(e)
        if "Connection" in error_msg or "timeout" in error_msg.lower():
            return None, f"网络连接失败，海外服务器可能无法访问东方财富数据源。建议在本地运行。错误: {error_msg}"
        return None, f"加载股票列表失败: {error_msg}"


@st.cache_data(ttl=30)
def get_market_index() -> Tuple[Optional[List[Dict]], Optional[str]]:
    """获取大盘指数"""
    try:
        df = ak.stock_zh_index_spot_em()
        # 指数名称和对应的代码（东方财富格式）
        index_map = {
            '上证指数': '000001',
            '深证成指': '399001',
            '创业板指': '399006',
            '科创50': '000688',
            '北证50': '899050'
        }
        result = []
        for name, code in index_map.items():
            row = df[df['代码'] == code]
            if not row.empty:
                r = row.iloc[0]
                result.append({
                    'name': name,
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
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        df = ak.stock_zt_pool_em(date=today)
        return df, None
    except Exception as e:
        return None, f"获取涨停池失败: {str(e)}"


@st.cache_data(ttl=60)
def get_limit_down_pool() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """获取跌停池"""
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        # 使用跌停池接口
        df = ak.stock_zt_pool_dtgc_em(date=today)
        return df, None
    except Exception as e:
        # 备用：从全市场数据统计跌停（跌幅>=9.9%）
        return None, f"获取跌停池失败: {str(e)}"


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


def get_quote_from_cache(symbol: str, all_stocks_df: pd.DataFrame) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """从缓存中获取实时行情"""
    if all_stocks_df is None:
        return None, "请先点击'初始化数据'加载股票列表"
    try:
        stock = all_stocks_df[all_stocks_df['代码'] == symbol]
        if stock.empty:
            return None, f"未找到股票代码: {symbol}"
        row = stock.iloc[0]
        # 尝试获取行业信息（可能不存在）
        industry = ''
        for col in ['所属行业', '行业', '细分行业']:
            if col in row.index and pd.notna(row[col]):
                industry = str(row[col])
                break
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
            "industry": industry,
        }, None
    except Exception as e:
        return None, f"获取行情失败: {str(e)}"


def get_watchlist_quotes(watchlist: List[Dict], all_stocks_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """获取自选股行情列表"""
    quotes = []
    for stock in watchlist:
        quote, _ = get_quote_from_cache(stock['symbol'], all_stocks_df)
        if quote:
            quotes.append(quote)
    return quotes


@st.cache_data(ttl=300)
def get_history(symbol: str, days: int = 60) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """获取历史数据"""
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        if df is None or df.empty:
            return None, "历史数据为空"
        df = df.tail(days).reset_index(drop=True)
        df['MA3'] = df['收盘'].rolling(3).mean()
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA13'] = df['收盘'].rolling(13).mean()
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
        error_msg = str(e)
        if "Connection" in error_msg or "timeout" in error_msg.lower():
            return None, f"网络连接失败，无法获取历史数据。错误: {error_msg}"
        return None, f"获取历史数据失败: {error_msg}"


@st.cache_data(ttl=300)
def get_ma_data(symbol: str, all_stocks_df: pd.DataFrame) -> Dict[str, float]:
    """获取均线数据用于自选股显示"""
    df, _ = get_history(symbol, 30)
    if df is not None and len(df) > 0:
        latest = df.iloc[-1]
        # 20天最高最低价（压力位/支撑位参考）
        high_20 = df['最高'].tail(20).max() if len(df) >= 20 else df['最高'].max()
        low_20 = df['最低'].tail(20).min() if len(df) >= 20 else df['最低'].min()
        # 30天最高成交量
        high_vol_30 = df['成交量'].max() if '成交量' in df.columns else 0
        # 30天最高成交额
        high_amount_30 = df['成交额'].max() if '成交额' in df.columns else 0
        return {
            'MA3': latest.get('MA3', 0),
            'MA5': latest.get('MA5', 0),
            'MA10': latest.get('MA10', 0),
            'MA13': latest.get('MA13', 0),
            'MA20': latest.get('MA20', 0),
            'high_vol_30': high_vol_30,
            'high_amount_30': high_amount_30,
            'high_20': float(high_20),
            'low_20': float(low_20),
            'MA5MIN': latest.get('MA5', 0)  # 先用日线MA5代替，后续可获取分时数据
        }
    return {'MA3': 0, 'MA5': 0, 'MA10': 0, 'MA13': 0, 'MA20': 0, 'high_vol_30': 0, 'high_amount_30': 0, 'high_20': 0, 'low_20': 0, 'MA5MIN': 0}


@st.cache_data(ttl=600)
def get_news(symbol: str, limit: int = 5) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """获取新闻"""
    try:
        df = ak.stock_news_em(symbol=symbol)
        if df is None or df.empty:
            return [], "无新闻数据"
        return [{"title": row['新闻标题'], "content": row['新闻内容'][:150], "time": row['发布时间']}
                for _, row in df.head(limit).iterrows()], None
    except Exception as e:
        return [], f"获取新闻失败: {str(e)}"


@st.cache_data(ttl=60)
def get_cls_news(limit: int = 20) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """获取财联社/主要财经快讯"""
    try:
        # 使用东方财富全球快讯作为财联社来源替代
        df = ak.stock_global_news_em()
        if df is None or df.empty:
            return [], "无财经快讯数据"
        news_list = []
        for _, row in df.head(limit).iterrows():
            news_list.append({
                "source": "财联社",
                "title": str(row.get('标题', row.get('新闻标题', ''))),
                "content": str(row.get('内容', row.get('新闻内容', '')))[:200],
                "time": str(row.get('时间', row.get('发布时间', ''))),
                "url": str(row.get('链接', row.get('新闻链接', '')))
            })
        return news_list, None
    except Exception as e:
        return [], f"获取财经快讯失败: {str(e)}"


@st.cache_data(ttl=60)
def get_eastmoney_news(limit: int = 20) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """获取东方财富快讯"""
    try:
        df = ak.stock_brief_news_em()
        if df is None or df.empty:
            return [], "无东方财富快讯数据"
        news_list = []
        for _, row in df.head(limit).iterrows():
            news_list.append({
                "source": "东方财富",
                "title": str(row.get('新闻标题', row.get('标题', ''))),
                "content": str(row.get('新闻内容', row.get('内容', '')))[:200],
                "time": str(row.get('发布时间', row.get('时间', ''))),
                "url": str(row.get('新闻链接', row.get('链接', '')))
            })
        return news_list, None
    except Exception as e:
        return [], f"获取东方财富快讯失败: {str(e)}"


@st.cache_data(ttl=60)
def get_sina_news(limit: int = 20) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """获取新浪财经新闻（使用CCTV财经新闻替代）"""
    try:
        df = ak.stock_cctv_news()
        if df is None or df.empty:
            return [], "无财经新闻数据"
        news_list = []
        for _, row in df.head(limit).iterrows():
            news_list.append({
                "source": "新浪财经",
                "title": str(row.get('标题', row.get('新闻标题', ''))),
                "content": str(row.get('内容', row.get('新闻内容', '')))[:200],
                "time": str(row.get('时间', row.get('发布时间', ''))),
                "url": str(row.get('链接', row.get('新闻链接', '')))
            })
        return news_list, None
    except Exception as e:
        return [], f"获取财经新闻失败: {str(e)}"


@st.cache_data(ttl=60)
def get_thshy_news(limit: int = 20) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """获取同花顺快讯（使用东方财富个股新闻替代，取热门股票）"""
    try:
        # 获取热门股票的新闻作为同花顺快讯来源
        hot_symbols = ['600519', '000001', '300750', '601318', '000858']
        news_list = []
        for symbol in hot_symbols[:2]:
            try:
                df = ak.stock_news_em(symbol=symbol)
                if df is not None and not df.empty:
                    for _, row in df.head(limit//2).iterrows():
                        news_list.append({
                            "source": "同花顺",
                            "title": str(row.get('新闻标题', '')),
                            "content": str(row.get('新闻内容', ''))[:200],
                            "time": str(row.get('发布时间', '')),
                            "url": str(row.get('新闻链接', ''))
                        })
            except:
                continue
        if not news_list:
            return [], "无同花顺快讯数据"
        return news_list[:limit], None
    except Exception as e:
        return [], f"获取同花顺快讯失败: {str(e)}"


def search_stock(keyword: str, all_stocks_df: pd.DataFrame) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """从缓存中搜索股票"""
    if all_stocks_df is None:
        return [], "请先点击'初始化数据'加载股票列表"
    try:
        mask = all_stocks_df['代码'].str.contains(keyword, case=False, na=False) | \
               all_stocks_df['名称'].str.contains(keyword, case=False, na=False)
        results = all_stocks_df[mask][['代码', '名称']].head(10)
        if results.empty:
            return [], f"未找到匹配 '{keyword}' 的股票"
        return results.to_dict('records'), None
    except Exception as e:
        return [], f"搜索失败: {str(e)}"


def format_volume(vol: float) -> str:
    """格式化成交量"""
    if vol >= 100000000:  # 1亿
        return f"{vol/100000000:.2f}亿手"
    elif vol >= 10000:  # 1万
        return f"{vol/10000:.1f}万手"
    else:
        return f"{vol:.0f}手"


def get_market_info(symbol: str) -> str:
    """获取市场信息"""
    if symbol.startswith('6'):
        return "沪市主板"
    elif symbol.startswith('0'):
        return "深市主板"
    elif symbol.startswith('3'):
        return "创业板"
    elif symbol.startswith('68'):
        return "科创板"
    else:
        return "A股"