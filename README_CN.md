# CommentPilot - 轻量级代码注释质量智能分析引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](https://github.com/gitstq/commentpilot)

**CommentPilot** 是一个零依赖的命令行工具，用于分析代码注释质量、覆盖率，并检测缺失或过时的注释。

## ✨ 核心特性

- 🔍 **注释覆盖率分析** - 统计代码中的注释比例
- ⚠️ **缺失注释检测** - 自动检测未添加注释的函数、类、模块
- 📝 **注释质量评分** - 智能评估注释质量
- 📋 **TODO/FIXME 追踪** - 汇总项目中的待办事项
- 🌐 **多语言支持** - 支持 16+ 种编程语言
- 📊 **TUI 仪表板** - 美观的终端界面展示
- 📄 **多格式报告** - JSON, HTML, Markdown
- ⚡ **零依赖** - 纯 Python 实现

## 🚀 快速开始

```bash
# 分析项目
python commentpilot.py ./src

# 输出 HTML 报告
python commentpilot.py ./src --format html --output report.html
```

## 📄 开源协议

本项目采用 MIT 协议开源。

---

**Made with ❤️ by CommentPilot Team**
