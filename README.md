# CommentPilot - Lightweight Code Comment Quality Intelligent Analysis Engine
# 轻量级代码注释质量智能分析引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](https://github.com/gitstq/commentpilot)

**CommentPilot** 是一个零依赖的命令行工具，用于分析代码注释质量、覆盖率，并检测缺失或过时的注释。

## ✨ 核心特性

- 🔍 **注释覆盖率分析** - 统计代码中的注释比例
- ⚠️ **缺失注释检测** - 自动检测未添加注释的函数、类、模块
- 📝 **注释质量评分** - 智能评估注释质量
- 📋 **TODO/FIXME 追踪** - 汇总项目中的待办事项
- 🌐 **多语言支持** - Python, JavaScript, TypeScript, Go, Java, Rust, C/C++, C#, PHP, Ruby, Swift, Kotlin, Scala, Lua, Shell
- 📊 **TUI 仪表板** - 美观的终端界面展示
- 📄 **多格式报告** - JSON, HTML, Markdown
- ⚡ **零依赖** - 纯 Python 实现，无需安装第三方库

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/commentpilot.git
cd commentpilot

# 直接运行
python commentpilot.py ./your-project
```

### 使用方法

```bash
# 分析项目
python commentpilot.py ./src

# 输出 JSON 格式
python commentpilot.py ./src --format json --output report.json

# 输出 HTML 报告
python commentpilot.py ./src --format html --output report.html

# 排除特定目录
python commentpilot.py ./src --exclude "tests,docs,vendor"
```

## 📖 详细使用指南

### 命令行参数

| 参数 | 说明 |
|------|------|
| `path` | 要分析的项目目录 |
| `--format, -f` | 输出格式：console, json, markdown, html |
| `--output, -o` | 输出文件路径 |
| `--exclude, -e` | 排除的目录/文件模式（逗号分隔） |
| `--version, -v` | 显示版本号 |

### 支持的语言

| 语言 | 扩展名 |
|------|--------|
| Python | .py |
| JavaScript | .js, .mjs, .cjs |
| TypeScript | .ts, .tsx |
| Go | .go |
| Java | .java |
| Rust | .rs |
| C | .c, .h |
| C++ | .cpp, .hpp, .cc |
| C# | .cs |
| PHP | .php |
| Ruby | .rb |
| Swift | .swift |
| Kotlin | .kt, .kts |
| Scala | .scala |
| Lua | .lua |
| Shell | .sh, .bash, .zsh |

### 输出示例

```
============================================================
📊 CommentPilot Analysis Report
============================================================

📁 Project: /path/to/project
⏰ Analyzed: 2025-05-15T17:00:00

----------------------------------------
📈 Summary
----------------------------------------
  Total Files:      42
  Total Lines:      12,345
  Code Lines:       9,876
  Comment Lines:    1,234
  Coverage:         10.0%
  Quality Score:    65.5/100

----------------------------------------
🌐 Language Statistics
----------------------------------------
  python       25 files,  8,000 lines, 12.5% coverage
  javascript   12 files,  3,000 lines,  8.3% coverage
  go            5 files,  1,345 lines, 15.2% coverage

----------------------------------------
📋 TODO Summary
----------------------------------------
  TODO         15
  FIXME         3

----------------------------------------
💡 Recommendations
----------------------------------------
  ⚠️ Warning: Comment coverage is low (<20%). Add comments to improve code maintainability.
  📋 Found 18 TODO/FIXME items to review.

============================================================
```

## 📦 项目结构

```
commentpilot/
├── commentpilot.py      # 主程序
├── test_commentpilot.py # 测试脚本
├── README.md            # 说明文档
├── README_CN.md         # 中文说明
├── README_TW.md         # 繁体中文说明
├── LICENSE              # MIT 许可证
└── .gitignore           # Git 忽略配置
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为代码质量做出贡献的开发者！

---

**Made with ❤️ by CommentPilot Team**
