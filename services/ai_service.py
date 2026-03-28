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