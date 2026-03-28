# 股票分析 AI Agent

> 基于 Streamlit + 阿里百炼的智能股票分析应用

## 项目地址

- **在线访问**: https://stockai-wmrqq3qk9g3nxyykgfam73.streamlit.app/
- **GitHub**: https://github.com/xiaoxuefeng111/stock_ai

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📈 实时行情 | A股实时价格、涨跌幅、成交额，支持北证50等5大指数 |
| ⭐ 自选股管理 | 自选股列表、涨跌背景色、压力支撑位、均线数据 |
| 📊 技术分析 | K线图、均线(MA5/10/20)、MACD、RSI |
| 🔥 热点资讯 | 财联社电报、东方财富快讯、同花顺快讯实时聚合 |
| 🤖 AI分析 | 阿里百炼(通义千问)智能分析，多维度评估 |
| 📱 移动端 | 支持手机浏览器 + Flutter App |

---

## 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    用户端                            │
│  ┌─────────────┐        ┌─────────────────────┐    │
│  │ 手机浏览器  │        │   Flutter App       │    │
│  │ (直接访问)  │        │   (WebView壳)       │    │
│  └──────┬──────┘        └──────────┬──────────┘    │
└─────────┼──────────────────────────┼───────────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────┐
│              Streamlit Cloud (免费托管)              │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │   app.py    │→│   AkShare   │→│  阿里百炼   │  │
│  │ (主程序)    │  │ (股票数据)  │  │ (AI分析)   │  │
│  └─────────────┘  └─────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 项目结构

```
stock_streamlit/
├── app.py                    # Streamlit 主程序
├── requirements.txt          # Python 依赖
├── .env                      # 本地环境变量 (不上传)
├── .gitignore               # Git 忽略文件
├── README.md                # 项目说明
├── .streamlit/
│   └── config.toml          # Streamlit 配置
├── components/              # UI 组件
│   ├── market_index.py      # 大盘指数组件
│   ├── sentiment_panel.py   # 市场情绪面板
│   ├── stock_card.py        # 自选股卡片
│   └── news_timeline.py     # 新闻时间线
├── pages/                   # Tab 页面
│   ├── tab_watchlist.py     # 自选股页
│   ├── tab_analysis.py      # 个股分析页
│   ├── tab_indicators.py    # 技术指标页
│   ├── tab_ai.py            # AI分析页
│   └── tab_news.py          # 热点资讯页
├── services/                # 服务层
│   ├── data_service.py      # 数据服务
│   ├── ai_service.py        # AI服务
│   ├── sentiment_service.py # 情绪计算
│   └── news_crawler_service.py # 新闻爬虫
├── utils/                   # 工具函数
│   ├── helpers.py           # 辅助函数
│   ├── indicators.py        # 指标计算
│   └── theme.py             # 主题管理
└── flutter_app/             # Flutter 手机 App
    ├── lib/
    │   └── main.dart        # Flutter 主程序
    ├── pubspec.yaml         # Flutter 依赖
    └── android/
        └── app/src/main/
            └── AndroidManifest.xml  # Android 配置
```

---

## 快速开始

### 方式一：在线使用

直接访问：https://stockai-wmrqq3qk9g3nxyykgfam73.streamlit.app/

### 方式二：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/xiaoxuefeng111/stock_ai.git
cd stock_ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
# 创建 .env 文件，填入：
# DASHSCOPE_API_KEY=你的阿里百炼密钥

# 4. 运行
streamlit run app.py

# 5. 局域网访问（手机可用）
streamlit run app.py --server.address 0.0.0.0
```

---

## 部署步骤

### 第一步：准备代码

```bash
# 项目文件
stock_streamlit/
├── app.py              # 主程序
├── requirements.txt    # 依赖
└── .streamlit/
    └── config.toml     # 配置
```

### 第二步：推送到 GitHub

```bash
# 初始化
git init
git add .
git commit -m "Initial commit"
git branch -M main

# 推送（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/stock_ai.git
git push -u origin main
```

### 第三步：部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 点击 **New app**
3. 选择 GitHub 仓库
4. 点击 **Advanced settings**，添加 Secret：
   ```toml
   DASHSCOPE_API_KEY = "sk-你的密钥"
   ```
5. 点击 **Deploy**

### 第四步：获取公网 URL

部署成功后获得：
```
https://stockai-xxxx.streamlit.app/
```

---

## API 配置

### 阿里百炼（通义千问）

1. 访问 https://bailian.console.aliyun.com
2. 开通服务
3. 创建 API Key
4. 配置到环境变量或 Streamlit Secrets

```toml
# Streamlit Cloud Secrets
DASHSCOPE_API_KEY = "sk-xxxxxxxx"
```

---

## 构建 Android App

### 前提条件

- 安装 Flutter SDK: https://docs.flutter.dev/get-started/install
- 安装 Android Studio（或至少 Android SDK）

### 构建步骤

```bash
# 1. 进入 Flutter 项目
cd stock_streamlit/flutter_app

# 2. 获取依赖
flutter pub get

# 3. 构建 APK
flutter build apk --release

# 4. APK 位置
# build/app/outputs/flutter-apk/app-release.apk
```

### 修改 URL

编辑 `flutter_app/lib/main.dart`：

```dart
final String streamlitUrl = 'https://你的streamlit地址.streamlit.app/';
```

---

## 使用说明

### 网页版

1. 打开网址
2. 选择股票（下拉框或输入代码）
3. 点击「分析」按钮
4. 查看行情、图表、新闻、AI分析

### 手机 App

1. 安装 APK
2. 打开 App（自动加载网页）
3. 使用方式同网页版

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python |
| 数据源 | AkShare |
| AI | 阿里百炼 (通义千问) |
| 托管 | Streamlit Cloud |
| App | Flutter + WebView |

---

## 核心依赖

```txt
streamlit>=1.30.0      # Web 框架
akshare>=1.12.0        # 股票数据
pandas>=2.0.0          # 数据处理
matplotlib>=3.7.0      # 图表绑制
openai>=1.0.0          # AI SDK
python-dotenv>=1.0.0   # 环境变量
crawl4ai>=0.3.0        # AI爬虫（可选，用于实时新闻）
```

---

## 常见问题

### Q: 数据加载慢？

AkShare 获取数据有时较慢，属于正常现象。

### Q: 图表中文乱码？

系统缺少中文字体，可在代码中指定字体路径。

### Q: AI 分析报错？

检查 DASHSCOPE_API_KEY 是否正确配置。

### Q: 手机无法访问本地服务？

确保手机和电脑在同一局域网，使用 `--server.address 0.0.0.0` 启动。

### Q: 新闻数据不是最新的？

安装 crawl4ai 可获取实时新闻：`pip install crawl4ai`

---

## 扩展功能（待实现）

- [ ] 多股对比分析
- [x] 自选股管理
- [ ] 价格预警推送
- [ ] 历史回测功能
- [ ] 财报深度分析
- [ ] 港股/美股支持

---

## 注意事项

⚠️ **重要声明**

- 本应用仅供参考学习，不构成任何投资建议
- 股市有风险，投资需谨慎
- 数据可能存在延迟或错误，请以官方数据为准

---

## 更新日志

### v1.1.0 (2026-03-28)

- 新增「热点资讯」Tab页
- 集成财联社电报、东方财富快讯、同花顺快讯
- 添加北证50指数到大盘显示
- 自选股卡片优化：成交额显示、涨跌背景色
- 市场情绪面板：跌停数统计、恐惧贪婪颜色渐变
- 支持 crawl4ai AI爬虫获取实时新闻

### v1.0.0 (2026-03-28)

- 初始版本发布
- 支持 A 股实时行情
- 支持技术分析图表
- 支持新闻资讯
- 支持 AI 智能分析
- 完成 Streamlit Cloud 部署
- 完成 Flutter WebView App 框架

---

## 联系方式

- GitHub: https://github.com/xiaoxuefeng111
- 项目地址: https://github.com/xiaoxuefeng111/stock_ai

---

## License

MIT License