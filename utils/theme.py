import streamlit as st

THEMES = {
    'light': {
        'bg': '#FFFFFF',
        'card': '#F8F9FA',
        'up': '#FF4757',
        'down': '#2ED573',
        'text': '#2D3436',
        'border': '#E8E8E8',
        'secondary_bg': '#F0F0F0',
        'muted': '#636E72'
    },
    'dark': {
        'bg': '#1A1A2E',
        'card': '#16213E',
        'up': '#FF6B6B',
        'down': '#4ECDC4',
        'text': '#FFFFFF',
        'border': '#2D3436',
        'secondary_bg': '#0F3460',
        'muted': '#B2BEC3'
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
    is_dark = get_theme() == 'dark'

    st.markdown(f"""
    <style>
        /* 全局背景 */
        .stApp {{
            background-color: {colors['bg']};
            color: {colors['text']};
        }}

        /* 卡片样式 */
        .stock-card {{
            background-color: {colors['card']};
            border-color: {colors['border']};
        }}
        .stock-name {{ color: {colors['text']}; }}
        .stock-label {{ color: {colors['muted']}; }}
        .stock-value {{ color: {colors['text']}; }}

        /* 价格颜色 */
        .price-up {{ color: {colors['up']}; }}
        .price-down {{ color: {colors['down']}; }}

        /* 指标区域 */
        .stock-price-row {{
            background-color: {colors['secondary_bg']};
        }}

        /* 深色模式特殊处理 */
        {"[data-testid='stMetric'] { background-color: " + colors['card'] + "; padding: 10px; border-radius: 8px; }" if is_dark else ""}

        /* 按钮样式 */
        .stButton>button {{
            background-color: {colors['card']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}
        .stButton>button:hover {{
            background-color: {colors['secondary_bg']};
        }}

        /* 输入框 */
        .stTextInput>div>div>input {{
            background-color: {colors['card']};
            color: {colors['text']};
        }}

        /* 选择框 */
        .stSelectbox>div>div>select {{
            background-color: {colors['card']};
            color: {colors['text']};
        }}

        /* Expander */
        .streamlit-expanderHeader {{
            background-color: {colors['card']};
            color: {colors['text']};
        }}
    </style>
    """, unsafe_allow_html=True)

def get_chart_style():
    """获取图表样式配置"""
    colors = get_theme_colors()
    return {
        'bg_color': colors['bg'],
        'grid_color': colors['border'] if get_theme() == 'dark' else '#E0E0E0',
        'text_color': colors['text'],
        'up_color': colors['up'],
        'down_color': colors['down']
    }