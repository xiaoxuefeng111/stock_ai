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