# CommentPilot - 輕量級程式碼註解品質智慧分析引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](https://github.com/gitstq/commentpilot)

**CommentPilot** 是一個零依賴的命令列工具，用於分析程式碼註解品質、覆蓋率，並偵測缺失或過時的註解。

## ✨ 核心特性

- 🔍 **註解覆蓋率分析** - 統計程式碼中的註解比例
- ⚠️ **缺失註解偵測** - 自動偵測未新增註解的函式、類別、模組
- 📝 **註解品質評分** - 智慧評估註解品質
- 📋 **TODO/FIXME 追蹤** - 彙總專案中的待辦事項
- 🌐 **多語言支援** - 支援 16+ 種程式語言
- 📊 **TUI 儀表板** - 美觀的終端介面展示
- 📄 **多格式報告** - JSON, HTML, Markdown
- ⚡ **零依賴** - 純 Python 實作

## 🚀 快速開始

```bash
# 分析專案
python commentpilot.py ./src

# 輸出 HTML 報告
python commentpilot.py ./src --format html --output report.html
```

## 📄 開源協議

本專案採用 MIT 協議開源。

---

**Made with ❤️ by CommentPilot Team**
