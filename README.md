# 股票分析 AI Agent

> 基于 Streamlit + 阿里百炼的智能股票分析应用

## 项目地址

- **在线访问**: https://stockai-wmrqq3qk9g3nxyykgfam73.streamlit.app/
- **GitHub**: https://github.com/xiaoxuefeng111/stock_ai

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📈 实时行情 | A股实时价格、涨跌幅、成交量 |
| 📊 技术分析 | K线图、均线(MA5/10/20)、MACD、RSI |
| 📰 热点资讯 | 财联社/东方财富/新浪/同花顺快讯 (crawl4ai爬虫) |
| 🤖 AI分析 | 阿里百炼(通义千问)智能分析 |
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

# 3. 可选：安装 AI 爬虫支持（获取更丰富的新闻源）
pip install crawl4ai

# 4. 配置 API Key
# 创建 .env 文件，填入：
# DASHSCOPE_API_KEY=你的阿里百炼密钥

# 5. 运行
streamlit run app.py

# 6. 局域网访问（手机可用）
streamlit run app.py --server.address 0.0.0.0
```

> **💡 新闻源说明**：
> - 默认使用 AkShare API 获取新闻数据
> - 安装 `crawl4ai` 后可启用 AI 爬虫模式，获取财联社、新浪财经等实时快讯
> - 两种模式自动切换，无需额外配置

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
crawl4ai>=0.3.0        # AI爬虫（可选，用于新闻抓取）
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

---

## 扩展功能（待实现）

- [ ] 多股对比分析
- [ ] 自选股管理
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
- 集成 crawl4ai AI爬虫支持
- 新闻源：财联社、东方财富、新浪财经、同花顺
- 自动切换爬虫/API模式

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