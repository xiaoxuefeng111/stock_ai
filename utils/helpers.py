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