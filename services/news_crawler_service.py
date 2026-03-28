# services/news_crawler_service.py
"""
新闻爬取服务 - 支持 crawl4ai 和 akshare 两种方式
优先使用 crawl4ai 爬取实时新闻，如未安装则回退到 akshare
"""
import streamlit as st
import pandas as pd
from typing import Tuple, List, Dict, Optional
import logging
import asyncio
import re

logger = logging.getLogger(__name__)

# 检查 crawl4ai 是否可用
CRAWL4AI_AVAILABLE = False
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
    logger.info("crawl4ai 已加载，将使用爬虫获取新闻")
except ImportError:
    logger.info("crawl4ai 未安装，将使用 akshare 获取新闻")

# 检查 BeautifulSoup 是否可用
BS4_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    logger.warning("BeautifulSoup 未安装，爬虫解析功能受限")


# 新闻源配置
NEWS_SOURCES = {
    'cls': {
        'name': '财联社',
        'url': 'https://www.cls.cn/telegraph',
        'color': '#e74c3c',
        'selectors': {
            'items': '.telegraph-list .telegraph-item',
            'title': '.telegraph-title',
            'time': '.telegraph-time'
        }
    },
    'eastmoney': {
        'name': '东方财富',
        'url': 'https://news.eastmoney.com/',
        'color': '#3498db',
        'selectors': {
            'items': '.news-item',
            'title': '.news-title',
            'time': '.news-time'
        }
    },
    'sina': {
        'name': '新浪财经',
        'url': 'https://finance.sina.com.cn/realstock/company/sh000001/nc.shtml',
        'color': '#f39c12',
        'selectors': {
            'items': '.news-item',
            'title': '.title',
            'time': '.time'
        }
    },
    'thshy': {
        'name': '同花顺',
        'url': 'https://news.10jqka.com.cn/',
        'color': '#9b59b6',
        'selectors': {
            'items': '.news-item',
            'title': '.title',
            'time': '.time'
        }
    }
}


async def crawl_cls_telegraph(limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """专门爬取财联社电报快讯"""
    if not CRAWL4AI_AVAILABLE:
        return [], "crawl4ai 未安装"

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from bs4 import BeautifulSoup

        # 配置浏览器启用 JS 渲染
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )

        # 配置爬虫运行参数
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="css:.telegraph-list",  # 等待快讯列表加载
            css_selector=".telegraph-list",  # 只提取快讯区域
            delay_before_return_html=2  # 等待2秒让JS执行
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url="https://www.cls.cn/telegraph",
                config=run_config
            )

            if not result.success:
                return [], f"爬取失败: {result.error_message}"

            news_list = []

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(result.html, 'html.parser')

            # 财联社快讯结构：寻找快讯条目
            items = soup.select('.telegraph-list-item, .flash-item, [class*="telegraph"]')

            if not items:
                # 备用：尝试从 markdown 内容解析
                lines = result.markdown.split('\n')
                for line in lines[:limit]:
                    line = line.strip()
                    # 跳过空行和导航内容
                    if line and len(line) > 15 and not line.startswith('#') and not line.startswith('['):
                        # 尝试解析时间和内容
                        time_str = ''
                        content = line

                        # 财联社格式通常是：时间 内容
                        import re
                        match = re.match(r'(\d{2}:\d{2})\s*(.+)', line)
                        if match:
                            time_str = match.group(1)
                            content = match.group(2)

                        news_list.append({
                            'source': '财联社',
                            'title': content[:80],
                            'content': content[:200],
                            'time': time_str,
                            'url': 'https://www.cls.cn/telegraph'
                        })
            else:
                for item in items[:limit]:
                    # 提取时间
                    time_elem = item.select_one('.time, .telegraph-time, [class*="time"]')
                    time_str = time_elem.get_text(strip=True) if time_elem else ''

                    # 提取内容
                    content_elem = item.select_one('.content, .telegraph-content, [class*="content"], p')
                    content = content_elem.get_text(strip=True) if content_elem else item.get_text(strip=True)

                    if content and len(content) > 10:
                        news_list.append({
                            'source': '财联社',
                            'title': content[:80],
                            'content': content[:200],
                            'time': time_str,
                            'url': 'https://www.cls.cn/telegraph'
                        })

            return news_list, None

    except Exception as e:
        logger.error(f"爬取财联社失败: {str(e)}")
        return [], f"爬取失败: {str(e)}"


async def crawl_news_source(source_key: str, limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """使用 crawl4ai 爬取单个新闻源"""
    if not CRAWL4AI_AVAILABLE:
        return [], "crawl4ai 未安装"

    # 财联社使用专门的爬取方法
    if source_key == 'cls':
        return await crawl_cls_telegraph(limit)

    source = NEWS_SOURCES.get(source_key)
    if not source:
        return [], f"未知的新闻源: {source_key}"

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from bs4 import BeautifulSoup

        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            delay_before_return_html=2
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=source['url'], config=run_config)

            if not result.success:
                return [], f"爬取失败: {result.error_message}"

            news_list = []
            soup = BeautifulSoup(result.html, 'html.parser')

            # 尝试多种新闻列表选择器
            selectors = [
                '.news-item', '.news-list-item', '.article-item',
                '[class*="news"]', '[class*="item"]', 'li'
            ]

            items = []
            for selector in selectors:
                items = soup.select(selector)
                if items and len(items) > 3:
                    break

            for item in items[:limit]:
                # 提取标题
                title_elem = item.select_one('a, .title, h2, h3, h4')
                title = title_elem.get_text(strip=True) if title_elem else ''

                # 提取时间
                time_elem = item.select_one('.time, .date, [class*="time"]')
                time_str = time_elem.get_text(strip=True) if time_elem else ''

                # 提取链接
                link_elem = item.select_one('a[href]')
                url = link_elem.get('href', '') if link_elem else source['url']
                if url and not url.startswith('http'):
                    url = source['url'].rstrip('/') + url

                if title and len(title) > 10:
                    news_list.append({
                        'source': source['name'],
                        'title': title[:80],
                        'content': title[:200],
                        'time': time_str,
                        'url': url
                    })

            return news_list, None

    except Exception as e:
        logger.error(f"爬取 {source['name']} 失败: {str(e)}")
        return [], f"爬取失败: {str(e)}"


def run_crawl_sync(source_key: str, limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """同步运行爬虫"""
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(crawl_news_source(source_key, limit))
        loop.close()
        return result
    except Exception as e:
        return [], f"爬虫执行失败: {str(e)}"


@st.cache_data(ttl=60)
def get_cls_news_crawl(limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """获取财联社快讯"""
    import akshare as ak
    try:
        news_list = []

        # 首选：财联社电报（短快讯，更新最快）
        try:
            df = ak.stock_telegraph_cls()
            if df is not None and not df.empty:
                # 按时间倒序排列（最新的在最前面）
                df = df.sort_values(by='时间', ascending=False)

                for _, row in df.head(limit).iterrows():
                    # 字段：时间, 标题, 内容, 来源
                    time_val = str(row.get('时间', '')).strip()
                    title_val = str(row.get('标题', '')).strip()
                    content_val = str(row.get('内容', '')).strip()
                    source_val = str(row.get('来源', '')).strip()

                    if title_val:
                        news_list.append({
                            "source": f"财联社-{source_val}" if source_val else "财联社",
                            "title": title_val[:80],
                            "content": content_val[:200] if content_val else title_val[:200],
                            "time": time_val,
                            "url": "https://www.cls.cn/telegraph"
                        })
                if news_list:
                    return news_list, None
        except Exception as e:
            logger.warning(f"stock_telegraph_cls 失败: {e}")

        # 备用：财联社全部快讯
        try:
            df = ak.stock_info_global_cls()
            if df is not None and not df.empty:
                # 按时间倒序排列
                df = df.sort_values(by='发布时间', ascending=False)

                for _, row in df.head(limit).iterrows():
                    title_val = str(row.get('标题', '')).strip()
                    content_val = str(row.get('内容', '')).strip()
                    time_val = str(row.get('发布时间', '')).strip()
                    url_val = str(row.get('链接', ''))

                    if title_val:
                        news_list.append({
                            "source": "财联社",
                            "title": title_val[:80],
                            "content": content_val[:200] if content_val else title_val[:200],
                            "time": time_val,
                            "url": url_val if url_val else "https://www.cls.cn/telegraph"
                        })
                if news_list:
                    return news_list, None
        except Exception as e:
            logger.warning(f"stock_info_global_cls 失败: {e}")

        return [], "无财联社快讯数据"

    except Exception as e:
        return [], f"获取财联社快讯失败: {str(e)}"


@st.cache_data(ttl=60)
def get_eastmoney_news_crawl(limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """获取东方财富快讯"""
    import akshare as ak
    try:
        # 东方财富综合快讯（symbol为空=全市场）
        df = ak.stock_news_em()

        if df is None or df.empty:
            return [], "无东方财富快讯数据"

        news_list = []
        for _, row in df.head(limit).iterrows():
            # 兼容多种字段名
            title_val = str(row.get('标题', row.get('新闻标题', ''))).strip()
            content_val = str(row.get('内容', row.get('新闻内容', ''))).strip()
            time_val = str(row.get('发布时间', row.get('时间', ''))).strip()
            url_val = str(row.get('链接', row.get('新闻链接', '')))

            if title_val:
                news_list.append({
                    "source": "东方财富",
                    "title": title_val[:80],
                    "content": content_val[:200] if content_val else title_val[:200],
                    "time": time_val,
                    "url": url_val if url_val else ""
                })

        return news_list, None
    except Exception as e:
        return [], f"获取东方财富快讯失败: {str(e)}"


@st.cache_data(ttl=60)
def get_ths_news_crawl(limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """获取同花顺快讯"""
    import akshare as ak
    try:
        # 同花顺全市场最新快讯
        df = ak.stock_info_global_ths()

        if df is None or df.empty:
            return [], "无同花顺快讯数据"

        news_list = []
        for _, row in df.head(limit).iterrows():
            # 字段：标题, 内容, 发布时间, 链接
            title_val = str(row.get('标题', '')).strip()
            content_val = str(row.get('内容', '')).strip()
            time_val = str(row.get('发布时间', '')).strip()
            url_val = str(row.get('链接', ''))

            if title_val:
                news_list.append({
                    "source": "同花顺",
                    "title": title_val[:80],
                    "content": content_val[:200] if content_val else title_val[:200],
                    "time": time_val,
                    "url": url_val if url_val else ""
                })

        return news_list, None
    except Exception as e:
        return [], f"获取同花顺快讯失败: {str(e)}"


@st.cache_data(ttl=60)
def get_thshy_news_crawl(limit: int = 20) -> Tuple[List[Dict], Optional[str]]:
    """获取热门个股快讯"""
    import akshare as ak
    try:
        hot_symbols = ['600519', '000001', '300750', '601318', '000858']
        news_list = []
        for symbol in hot_symbols[:3]:
            try:
                df = ak.stock_news_em(symbol=symbol)
                if df is not None and not df.empty:
                    for _, row in df.head(7).iterrows():
                        news_list.append({
                            "source": "热门个股",
                            "title": str(row.get('新闻标题', '')).strip()[:80],
                            "content": str(row.get('新闻内容', '')).strip()[:200],
                            "time": str(row.get('发布时间', '')),
                            "url": str(row.get('新闻链接', ''))
                        })
            except:
                continue

        if not news_list:
            return [], "无个股快讯数据"
        return news_list[:limit], None
    except Exception as e:
        return [], f"获取个股快讯失败: {str(e)}"


def get_crawler_status() -> Dict:
    """获取爬虫状态信息"""
    return {
        'crawl4ai_available': CRAWL4AI_AVAILABLE,
        'mode': 'crawl4ai' if CRAWL4AI_AVAILABLE else 'akshare',
        'sources': list(NEWS_SOURCES.keys())
    }