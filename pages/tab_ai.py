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

    # 股票选择
    search = st.text_input("搜索股票", key="ai_search", placeholder="输入代码或名称")
    if search.strip() and st.session_state.stocks_loaded:
        from services.data_service import search_stock
        results, _ = search_stock(search.strip(), st.session_state.all_stocks)
        if results:
            options = [f"{r['代码']} - {r['名称']}" for r in results]
            selected = st.selectbox("选择股票", options, key="ai_select")
            if st.button("确认分析股票"):
                st.session_state.selected_symbol = selected.split(" - ")[0]
                st.rerun()

    if not symbol:
        st.info("👆 请先选择股票进行AI分析")
        return

    if not st.session_state.stocks_loaded:
        st.warning("⚠️ 请先在自选股Tab初始化数据")
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

    # 多维度分析选项
    st.markdown("#### 分析维度")
    col1, col2, col3 = st.columns(3)
    with col1:
        analyze_technical = st.checkbox("技术面分析", value=True)
        analyze_fund_flow = st.checkbox("资金流向分析", value=True)
    with col2:
        analyze_sentiment = st.checkbox("市场情绪分析", value=True)
        analyze_news = st.checkbox("新闻舆情分析", value=False)
    with col3:
        analyze_industry = st.checkbox("行业对比分析", value=False)
        analyze_history = st.checkbox("历史相似走势", value=False)

    # 开始分析按钮
    if st.button("🚀 开始AI分析", type="primary"):
        with st.status("正在进行分析...", expanded=True) as status:
            # 步骤1：获取实时行情
            status.update(label="📊 正在获取实时行情数据...")
            quote, _ = get_quote_from_cache(symbol, st.session_state.all_stocks)

            # 步骤2：获取历史数据
            status.update(label="📈 正在获取历史K线数据...")
            df, _ = get_history(symbol, 60)

            if quote and df is not None:
                # 步骤3：构建分析上下文
                status.update(label="🔧 正在构建分析上下文...")
                latest = df.iloc[-1]

                # 构建分析上下文
                ctx = {
                    "symbol": symbol,
                    "name": quote['name'],
                    "quote": {
                        "price": quote['price'],
                        "change_pct": quote['change_pct'],
                        "high": quote['high'],
                        "low": quote['low'],
                        "volume": quote['volume'],
                        "amount": quote['amount']
                    },
                    "indicators": {
                        "MA5": float(latest.get('MA5', 0)),
                        "MA10": float(latest.get('MA10', 0)),
                        "MA20": float(latest.get('MA20', 0)),
                        "RSI": float(latest.get('RSI', 50)),
                        "MACD": float(latest.get('MACD', 0))
                    }
                }

                # 步骤4：调用AI分析
                status.update(label="🤖 正在调用AI进行智能分析（可能需要10-30秒）...")

                # 构建问题
                question_parts = []
                if analyze_technical:
                    question_parts.append("技术面（K线形态、指标信号、趋势判断）")
                if analyze_fund_flow:
                    question_parts.append("资金流向")
                if analyze_sentiment:
                    question_parts.append("市场情绪")
                if analyze_news:
                    question_parts.append("新闻舆情")
                if analyze_industry:
                    question_parts.append("行业对比")
                if analyze_history:
                    question_parts.append("历史相似走势参考")

                question = f"请分析{'、'.join(question_parts)}，给出投资建议和风险提示"

                result = ai_analyze(json.dumps(ctx, ensure_ascii=False), question, style, depth)

                # 步骤5：完成
                status.update(label="✅ 分析完成！", state="complete")

                # 显示结果
                st.markdown("#### 📋 分析结果")
                st.markdown(result)

                # 多维度评分
                st.markdown("#### 📊 多维度评估")
                cols = st.columns(5)

                # 简化的评分展示
                rsi = latest.get('RSI', 50)
                rsi_score = 100 - abs(rsi - 50) * 2  # RSI越接近50越好

                macd = latest.get('MACD', 0)
                macd_score = 70 if macd > 0 else 30

                trend_score = 70 if latest.get('MA5', 0) > latest.get('MA20', 0) else 30
                momentum_score = 70 if quote['change_pct'] > 0 else 30
                volume_score = min(100, quote['volume'] / 1000000)  # 成交量评分

                cols[0].metric("技术面", f"{int(rsi_score)}分")
                cols[1].metric("趋势", f"{int(trend_score)}分")
                cols[2].metric("动量", f"{int(momentum_score)}分")
                cols[3].metric("成交量", f"{int(volume_score)}分")
                cols[4].metric("综合", f"{int((rsi_score + trend_score + momentum_score + volume_score)/4)}分")

                # 风险提示
                st.warning("⚠️ 以上分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
            else:
                st.error("获取数据失败，请检查股票代码")

    # AI实时问答
    st.markdown("---")
    st.markdown("#### 💬 AI实时问答")

    # 初始化对话历史
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []

    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.ai_chat_history:
            if msg['role'] == 'user':
                st.markdown(f"**🧑 你:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI:** {msg['content']}")

    # 输入框
    user_question = st.text_input("输入问题:", key="ai_chat_input", placeholder="例如: 这只股票适合长期持有吗?")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("发送", type="primary"):
            if user_question.strip() and symbol:
                # 添加用户消息
                st.session_state.ai_chat_history.append({'role': 'user', 'content': user_question})

                with st.status("🤖 AI正在思考...", expanded=False):
                    # 获取上下文
                    quote, _ = get_quote_from_cache(symbol, st.session_state.all_stocks)
                    df, _ = get_history(symbol, 60)

                    if quote and df is not None:
                        latest = df.iloc[-1]
                        ctx = {
                            "symbol": symbol,
                            "name": quote['name'],
                            "quote": quote,
                            "indicators": {
                                "MA5": float(latest.get('MA5', 0)),
                                "RSI": float(latest.get('RSI', 50)),
                                "MACD": float(latest.get('MACD', 0))
                            }
                        }

                        # 调用AI
                        result = ai_analyze(json.dumps(ctx, ensure_ascii=False), user_question)
                        st.session_state.ai_chat_history.append({'role': 'assistant', 'content': result})
                        st.rerun()

    with col2:
        if st.button("清空对话"):
            st.session_state.ai_chat_history = []
            st.rerun()

    # 投资建议说明
    st.markdown("---")
    st.markdown("#### 💡 分析风格说明")
    st.markdown("""
    - **短线交易**: 关注日内波动、支撑压力位、买卖时机
    - **中长线投资**: 关注趋势、基本面、估值水平
    - **价值投资**: 关注企业内在价值、安全边际
    - **技术面分析**: 关注K线形态、指标信号、量价关系
    - **基本面分析**: 关注财务数据、行业地位、成长性
    """)