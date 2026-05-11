# 🔬 DeepProbe

> **Lightweight Local AI Deep Research Engine**
> 轻量级本地AI深度研究引擎

[中文](#中文) | [繁體中文](#繁體中文) | [English](#english)

---

<a id="中文"></a>

## 🎉 项目介绍

**DeepProbe** 是一款隐私优先的轻量级本地AI深度研究引擎，支持多源搜索聚合、智能内容分析、本地知识图谱构建和自动化研究报告生成。**零外部依赖**，纯Python实现，数据完全本地化处理，无需API Key即可使用核心功能。

### 💡 灵感来源

在AI研究工具日益依赖云端服务的今天，开发者的研究数据隐私和API成本成为两大核心痛点。DeepProbe 参考了本地化AI研究工具的产品理念，但采用完全独立自研的架构设计，强调**零依赖、隐私优先、离线可用**三大核心价值。

### ✨ 自研差异化亮点

- 🚫 **零外部依赖** — 纯Python标准库实现，无需安装任何第三方包
- 🔒 **隐私优先** — 所有数据本地存储，支持SQLite持久化缓存
- 📡 **5大搜索源** — DuckDuckGo、Wikipedia、GitHub、arXiv、Hacker News
- 📊 **智能分析** — TF-IDF关键词提取、情感分析、主题识别、实体提取
- 📝 **多格式报告** — Markdown / HTML / JSON 三种输出格式
- 🖥️ **双模式交互** — CLI命令行 + TUI终端交互界面
- 💾 **智能缓存** — 24小时TTL缓存，避免重复搜索
- 🌐 **多语言支持** — 中英文双语界面与文档

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **多源搜索聚合** | 聚合DuckDuckGo、Wikipedia、GitHub、arXiv、Hacker News五大搜索源 |
| 📊 **智能内容分析** | TF-IDF关键词提取、情感分析、主题识别、实体提及追踪 |
| 📝 **自动报告生成** | 一键生成Markdown/HTML/JSON格式的研究报告 |
| 🔒 **本地知识图谱** | SQLite持久化存储，构建本地研究知识库 |
| 🖥️ **TUI交互界面** | 精美的终端交互界面，支持菜单导航 |
| 💾 **智能缓存系统** | 24小时TTL缓存，减少重复请求，支持离线查阅 |
| ⚡ **三级研究深度** | quick(快速) / standard(标准) / deep(深度) 三种模式 |
| 🌐 **多语言界面** | 中英文双语CLI界面，报告语言自动检测 |
| 📦 **零依赖安装** | 纯Python标准库，复制即用，无需pip install |

---

## 🚀 快速开始

### 环境要求

- **Python**: >= 3.8（推荐3.9+）
- **操作系统**: Windows / macOS / Linux（跨平台）
- **网络**: 搜索功能需要网络连接（缓存模式下可离线查阅）

### 安装

```bash
# 方式一：直接克隆（推荐，零依赖）
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe
export PYTHONPATH=src
python -m deepprobe --help

# 方式二：pip安装
pip install .

# 方式三：开发模式安装
pip install -e .
```

### 基本使用

```bash
# 快速研究
deepprobe research "artificial intelligence trends 2026"

# 标准深度研究（多源搜索）
deepprobe research "quantum computing applications" --depth standard

# 深度研究（全源搜索+详细分析）
deepprobe research "renewable energy technology" --depth deep --format html

# 指定搜索源
deepprobe research "machine learning" --sources duckduckgo,wikipedia,github,arxiv

# 导出为HTML报告
deepprobe research "blockchain technology" --format html --output report.html

# 查看研究历史
deepprobe history

# 导出已有研究
deepprobe export <research-id> --format markdown

# 启动交互式TUI界面
deepprobe tui

# 查看可用搜索源
deepprobe sources

# 管理配置
deepprobe config --list
deepprobe config --set search.max_results_per_source 20
```

---

## 📖 详细使用指南

### 研究深度说明

| 深度 | 搜索源 | 最大结果 | 适用场景 |
|------|--------|---------|---------|
| `quick` | DuckDuckGo | 5/源 | 快速了解主题概览 |
| `standard` | DuckDuckGo + Wikipedia | 10/源 | 日常研究、技术调研 |
| `deep` | 全部5个源 | 20/源 | 深度学术研究、全面分析 |

### 搜索源说明

| 源名称 | 类型 | 说明 | 是否需要API Key |
|--------|------|------|----------------|
| `duckduckgo` | Web搜索 | 隐私友好的网页搜索 | ❌ |
| `wikipedia` | 百科全书 | 维基百科知识库 | ❌ |
| `github` | 代码仓库 | GitHub开源项目搜索 | ❌（有Token更好） |
| `arxiv` | 学术论文 | arXiv开放获取论文 | ❌ |
| `news` | 新闻聚合 | Hacker News + 新闻搜索 | ❌ |

### 配置管理

```bash
# 查看所有配置
deepprobe config --list

# 修改配置
deepprobe config --set search.cache_ttl_hours 48
deepprobe config --set report.default_format html
deepprobe config --set ui.color_enabled false

# 重置为默认配置
deepprobe config --reset
```

### 项目结构

```
DeepProbe/
├── src/deepprobe/
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # CLI入口
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   └── engine.py        # 核心研究引擎
│   ├── search/
│   │   ├── registry.py      # 搜索源注册表
│   │   └── sources/         # 搜索源实现
│   │       ├── duckduckgo_source.py
│   │       ├── wikipedia_source.py
│   │       ├── github_source.py
│   │       ├── arxiv_source.py
│   │       └── news_source.py
│   ├── analysis/
│   │   └── content_analyzer.py  # 内容分析引擎
│   ├── report/
│   │   └── generator.py     # 报告生成器
│   ├── storage/
│   │   └── engine.py        # SQLite存储引擎
│   └── ui/
│       └── tui.py           # 终端交互界面
├── tests/
│   └── test_deepprobe.py    # 单元测试
├── pyproject.toml           # 项目配置
├── LICENSE                  # MIT许可证
└── README.md                # 项目文档
```

---

## 💡 设计思路与迭代规划

### 设计理念

1. **零依赖哲学** — 使用Python标准库实现所有功能，降低用户使用门槛
2. **隐私优先** — 数据本地化处理，不依赖任何云服务
3. **模块化架构** — 搜索、分析、报告、存储四大模块独立解耦
4. **可扩展性** — 基于`SourceRegistry`模式，轻松添加新搜索源

### 技术选型

| 组件 | 技术选择 | 原因 |
|------|---------|------|
| 语言 | Python 3.8+ | 最大兼容性，标准库丰富 |
| 存储 | SQLite | 零配置，内置于Python |
| HTTP | urllib | 标准库，无额外依赖 |
| HTML解析 | 正则表达式 | 轻量级，避免引入lxml/beautifulsoup |
| CLI | argparse | 标准库，功能完善 |

### 后续迭代计划

- [ ] 🤖 **LLM增强分析** — 可选接入OpenAI/Claude等LLM进行深度分析
- [ ] 📊 **可视化图表** — 生成研究趋势图表（ASCII/HTML）
- [ ] 🔄 **增量研究** — 基于历史研究进行增量更新
- [ ] 📡 **更多搜索源** — PubMed、Semantic Scholar等
- [ ] 🌐 **Web界面** — 可选的Web Dashboard
- [ ] 📱 **API服务** — RESTful API接口

---

## 📦 打包与部署

### 本地运行

```bash
# 克隆项目
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe

# 直接运行
export PYTHONPATH=src
python -m deepprobe research "your query"
```

### pip安装

```bash
pip install git+https://github.com/gitstq/DeepProbe.git
deepprobe research "your query"
```

### 运行测试

```bash
cd DeepProbe
python -m unittest tests.test_deepprobe -v
```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下规范：

1. **Fork** 本仓库
2. 创建功能分支：`git checkout -b feat/your-feature`
3. 提交代码：`git commit -m 'feat: 添加新功能'`
4. 推送分支：`git push origin feat/your-feature`
5. 提交 **Pull Request**

### 提交规范

遵循 Angular 提交规范：
- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<a id="繁體中文"></a>

## 🎉 專案介紹

**DeepProbe** 是一款隱私優先的輕量級本地AI深度研究引擎，支援多源搜尋聚合、智慧內容分析、本地知識圖譜建構和自動化研究報告生成。**零外部依賴**，純Python實現，資料完全本地化處理，無需API Key即可使用核心功能。

### 💡 靈感來源

在AI研究工具日益依賴雲端服務的今天，開發者的研究資料隱私和API成本成為兩大核心痛點。DeepProbe 參考了本地化AI研究工具的產品理念，但採用完全獨立自研的架構設計，強調**零依賴、隱私優先、離線可用**三大核心價值。

### ✨ 自研差異化亮點

- 🚫 **零外部依賴** — 純Python標準庫實現，無需安裝任何第三方套件
- 🔒 **隱私優先** — 所有資料本地存儲，支援SQLite持久化快取
- 📡 **5大搜尋源** — DuckDuckGo、Wikipedia、GitHub、arXiv、Hacker News
- 📊 **智慧分析** — TF-IDF關鍵詞提取、情感分析、主題識別、實體提取
- 📝 **多格式報告** — Markdown / HTML / JSON 三種輸出格式
- 🖥️ **雙模式互動** — CLI命令列 + TUI終端互動介面
- 💾 **智慧快取** — 24小時TTL快取，避免重複搜尋
- 🌐 **多語言支援** — 中英文雙語介面與文件

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **多源搜尋聚合** | 聚合DuckDuckGo、Wikipedia、GitHub、arXiv、Hacker News五大搜尋源 |
| 📊 **智慧內容分析** | TF-IDF關鍵詞提取、情感分析、主題識別、實體提及追蹤 |
| 📝 **自動報告生成** | 一鍵生成Markdown/HTML/JSON格式的研究報告 |
| 🔒 **本地知識圖譜** | SQLite持久化存儲，建構本地研究知識庫 |
| 🖥️ **TUI互動介面** | 精美的終端互動介面，支援選單導航 |
| 💾 **智慧快取系統** | 24小時TTL快取，減少重複請求，支援離線查閱 |
| ⚡ **三級研究深度** | quick(快速) / standard(標準) / deep(深度) 三種模式 |
| 🌐 **多語言介面** | 中英文雙語CLI介面，報告語言自動偵測 |
| 📦 **零依賴安裝** | 純Python標準庫，複製即用，無需pip install |

---

## 🚀 快速開始

### 環境要求

- **Python**: >= 3.8（推薦3.9+）
- **作業系統**: Windows / macOS / Linux（跨平台）
- **網路**: 搜尋功能需要網路連接（快取模式下可離線查閱）

### 安裝

```bash
# 方式一：直接克隆（推薦，零依賴）
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe
export PYTHONPATH=src
python -m deepprobe --help

# 方式二：pip安裝
pip install .

# 方式三：開發模式安裝
pip install -e .
```

### 基本使用

```bash
# 快速研究
deepprobe research "artificial intelligence trends 2026"

# 標準深度研究（多源搜尋）
deepprobe research "quantum computing applications" --depth standard

# 深度研究（全源搜尋+詳細分析）
deepprobe research "renewable energy technology" --depth deep --format html

# 指定搜尋源
deepprobe research "machine learning" --sources duckduckgo,wikipedia,github,arxiv

# 啟動互動式TUI介面
deepprobe tui

# 查看研究歷史
deepprobe history
```

---

## 📖 詳細使用指南

### 研究深度說明

| 深度 | 搜尋源 | 最大結果 | 適用場景 |
|------|--------|---------|---------|
| `quick` | DuckDuckGo | 5/源 | 快速了解主題概覽 |
| `standard` | DuckDuckGo + Wikipedia | 10/源 | 日常研究、技術調研 |
| `deep` | 全部5個源 | 20/源 | 深度學術研究、全面分析 |

### 設定管理

```bash
# 查看所有設定
deepprobe config --list

# 修改設定
deepprobe config --set search.cache_ttl_hours 48
deepprobe config --set report.default_format html

# 重置為預設設定
deepprobe config --reset
```

---

## 💡 設計思路與迭代規劃

### 設計理念

1. **零依賴哲學** — 使用Python標準庫實現所有功能，降低使用者使用門檻
2. **隱私優先** — 資料本地化處理，不依賴任何雲端服務
3. **模組化架構** — 搜尋、分析、報告、存儲四大模組獨立解耦
4. **可擴展性** — 基於`SourceRegistry`模式，輕鬆添加新搜尋源

### 後續迭代計劃

- [ ] 🤖 **LLM增強分析** — 可選接入OpenAI/Claude等LLM進行深度分析
- [ ] 📊 **視覺化圖表** — 生成研究趨勢圖表
- [ ] 🔄 **增量研究** — 基於歷史研究進行增量更新
- [ ] 📡 **更多搜尋源** — PubMed、Semantic Scholar等
- [ ] 🌐 **Web介面** — 可選的Web Dashboard

---

## 📦 打包與部署

### 本地運行

```bash
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe
export PYTHONPATH=src
python -m deepprobe research "your query"
```

### pip安裝

```bash
pip install git+https://github.com/gitstq/DeepProbe.git
deepprobe research "your query"
```

### 運行測試

```bash
cd DeepProbe
python -m unittest tests.test_deepprobe -v
```

---

## 🤝 貢獻指南

歡迎貢獻！請遵循以下規範：

1. **Fork** 本倉庫
2. 建立功能分支：`git checkout -b feat/your-feature`
3. 提交程式碼：`git commit -m 'feat: 添加新功能'`
4. 推送分支：`git push origin feat/your-feature`
5. 提交 **Pull Request**

---

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<a id="english"></a>

## 🎉 Introduction

**DeepProbe** is a privacy-first, lightweight local AI deep research engine. It aggregates multiple search sources, performs intelligent content analysis, builds local knowledge graphs, and generates comprehensive research reports automatically. **Zero external dependencies** — built entirely with Python's standard library. Your data stays local, and no API key is required for core functionality.

### 💡 Inspiration

As AI research tools increasingly rely on cloud services, developer data privacy and API costs have become critical concerns. DeepProbe was inspired by the concept of localized AI research tools but built with a completely independent, original architecture emphasizing **zero dependencies, privacy-first, and offline-capable** design.

### ✨ Differentiation Highlights

- 🚫 **Zero Dependencies** — Pure Python standard library, no third-party packages needed
- 🔒 **Privacy-First** — All data stored locally with SQLite persistent caching
- 📡 **5 Search Sources** — DuckDuckGo, Wikipedia, GitHub, arXiv, Hacker News
- 📊 **Smart Analysis** — TF-IDF keyword extraction, sentiment analysis, topic identification, entity tracking
- 📝 **Multi-format Reports** — Markdown / HTML / JSON output formats
- 🖥️ **Dual Mode Interface** — CLI command-line + TUI terminal interactive interface
- 💾 **Smart Caching** — 24-hour TTL cache to avoid redundant searches
- 🌐 **Multilingual** — Bilingual Chinese/English interface and documentation

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-Source Search** | Aggregates DuckDuckGo, Wikipedia, GitHub, arXiv, Hacker News |
| 📊 **Smart Content Analysis** | TF-IDF keywords, sentiment analysis, topic identification, entity extraction |
| 📝 **Auto Report Generation** | One-click Markdown/HTML/JSON research reports |
| 🔒 **Local Knowledge Graph** | SQLite persistent storage for local research knowledge base |
| 🖥️ **TUI Interface** | Beautiful terminal UI with menu navigation |
| 💾 **Smart Cache System** | 24h TTL cache, offline review support |
| ⚡ **3 Research Depths** | quick / standard / deep modes |
| 🌐 **Multilingual UI** | Bilingual CLI, auto-detected report language |
| 📦 **Zero-Dependency** | Pure Python stdlib, copy and run |

---

## 🚀 Quick Start

### Requirements

- **Python**: >= 3.8 (3.9+ recommended)
- **OS**: Windows / macOS / Linux (cross-platform)
- **Network**: Required for search (cached results available offline)

### Installation

```bash
# Option 1: Clone directly (recommended, zero dependencies)
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe
export PYTHONPATH=src
python -m deepprobe --help

# Option 2: pip install
pip install .

# Option 3: Development mode
pip install -e .
```

### Usage

```bash
# Quick research
deepprobe research "artificial intelligence trends 2026"

# Standard depth (multi-source)
deepprobe research "quantum computing applications" --depth standard

# Deep research (all sources + detailed analysis)
deepprobe research "renewable energy technology" --depth deep --format html

# Specify sources
deepprobe research "machine learning" --sources duckduckgo,wikipedia,github,arxiv

# Export as HTML report
deepprobe research "blockchain technology" --format html --output report.html

# View research history
deepprobe history

# Export existing research
deepprobe export <research-id> --format markdown

# Launch interactive TUI
deepprobe tui

# List available sources
deepprobe sources

# Manage configuration
deepprobe config --list
deepprobe config --set search.max_results_per_source 20
```

---

## 📖 Detailed Guide

### Research Depth

| Depth | Sources | Max Results | Use Case |
|-------|---------|-------------|----------|
| `quick` | DuckDuckGo | 5/source | Quick topic overview |
| `standard` | DuckDuckGo + Wikipedia | 10/source | Daily research, tech survey |
| `deep` | All 5 sources | 20/source | Deep academic research, comprehensive analysis |

### Search Sources

| Source | Type | Description | API Key Required |
|--------|------|-------------|------------------|
| `duckduckgo` | Web Search | Privacy-friendly web search | ❌ |
| `wikipedia` | Encyclopedia | Wikipedia knowledge base | ❌ |
| `github` | Code Repository | GitHub open source search | ❌ (Token helps) |
| `arxiv` | Academic Papers | arXiv open access papers | ❌ |
| `news` | News Aggregator | Hacker News + web news | ❌ |

### Configuration

```bash
# List all config
deepprobe config --list

# Set config values
deepprobe config --set search.cache_ttl_hours 48
deepprobe config --set report.default_format html
deepprobe config --set ui.color_enabled false

# Reset to defaults
deepprobe config --reset
```

### Project Structure

```
DeepProbe/
├── src/deepprobe/
│   ├── __init__.py          # Package init
│   ├── __main__.py          # CLI entry point
│   ├── core/
│   │   ├── config.py        # Configuration manager
│   │   └── engine.py        # Core research engine
│   ├── search/
│   │   ├── registry.py      # Source registry
│   │   └── sources/         # Search source implementations
│   │       ├── duckduckgo_source.py
│   │       ├── wikipedia_source.py
│   │       ├── github_source.py
│   │       ├── arxiv_source.py
│   │       └── news_source.py
│   ├── analysis/
│   │   └── content_analyzer.py  # Content analysis engine
│   ├── report/
│   │   └── generator.py     # Report generator
│   ├── storage/
│   │   └── engine.py        # SQLite storage engine
│   └── ui/
│       └── tui.py           # Terminal UI
├── tests/
│   └── test_deepprobe.py    # Unit tests (25 tests)
├── pyproject.toml           # Project config
├── LICENSE                  # MIT License
└── README.md                # Documentation
```

---

## 💡 Design Philosophy & Roadmap

### Design Principles

1. **Zero-Dependency Philosophy** — All features implemented with Python standard library
2. **Privacy-First** — All data processed locally, no cloud services required
3. **Modular Architecture** — Search, Analysis, Report, Storage modules fully decoupled
4. **Extensibility** — `SourceRegistry` pattern for easy addition of new sources

### Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.8+ | Maximum compatibility, rich stdlib |
| Storage | SQLite | Zero-config, built into Python |
| HTTP | urllib | Standard library, no extra deps |
| HTML Parsing | Regex | Lightweight, avoids lxml/bs4 |
| CLI | argparse | Standard library, feature-complete |

### Roadmap

- [ ] 🤖 **LLM-Enhanced Analysis** — Optional OpenAI/Claude integration
- [ ] 📊 **Visualization** — Research trend charts (ASCII/HTML)
- [ ] 🔄 **Incremental Research** — Update based on historical research
- [ ] 📡 **More Sources** — PubMed, Semantic Scholar, etc.
- [ ] 🌐 **Web Dashboard** — Optional web interface
- [ ] 📱 **REST API** — API service endpoint

---

## 📦 Installation & Deployment

### Local Run

```bash
git clone https://github.com/gitstq/DeepProbe.git
cd DeepProbe
export PYTHONPATH=src
python -m deepprobe research "your query"
```

### pip Install

```bash
pip install git+https://github.com/gitstq/DeepProbe.git
deepprobe research "your query"
```

### Run Tests

```bash
cd DeepProbe
python -m unittest tests.test_deepprobe -v
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit: `git commit -m 'feat: add new feature'`
4. Push: `git push origin feat/your-feature`
5. Submit a **Pull Request**

### Commit Convention

Following Angular commit convention:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tooling

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <strong>⭐ If you find DeepProbe useful, please give it a star! ⭐</strong>
</p>

<p align="center">
  Built with ❤️ by <a href="https://github.com/gitstq">gitstq</a> | 
  <a href="https://github.com/gitstq/DeepProbe/issues">Report Bug</a> | 
  <a href="https://github.com/gitstq/DeepProbe/releases">Releases</a>
</p>
