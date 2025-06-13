# 🤖 AI简历分析系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/ai-resume-analyzer)](https://github.com/yourusername/ai-resume-analyzer/issues)

一个基于AI的智能简历分析和比较工具，帮助HR和招聘人员快速、客观地评估候选人简历。

![AI简历分析系统](https://via.placeholder.com/800x400/1f77b4/ffffff?text=AI+Resume+Analyzer)

## ✨ 功能特点

### 🎯 核心功能
- 📄 **智能简历解析** - 支持PDF格式简历自动提取和分析
- 🤖 **AI驱动评估** - 基于多种先进AI模型的智能评分
- 📊 **多维度分析** - 教育背景、工作经验、技能匹配、项目经验等全方位评估
- 📈 **可视化展示** - 直观的图表和评分展示
- 📋 **详细报告** - 生成专业的候选人分析报告
- 💾 **PDF导出** - 支持完整的分析报告导出
- 🔄 **批量比较** - 多个候选人简历对比分析

### 🚀 技术亮点
- **免费使用** - 支持多种免费AI模型，无需API Key
- **中文优化** - 专门针对中文简历优化的分析算法
- **实时分析** - 快速响应，秒级完成分析
- **跨平台** - 支持Windows、macOS、Linux
- **易于部署** - 一键打包成可执行文件

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 后端开发语言 |
| **Streamlit** | 1.28+ | Web界面框架 |
| **OpenRouter** | Latest | AI模型接口 |
| **ReportLab** | 4.0+ | PDF生成 |
| **PyPDF2** | 3.0+ | PDF解析 |
| **Plotly** | 5.0+ | 数据可视化 |
| **Pandas** | 2.0+ | 数据处理 |

## 🚀 快速开始

### 📋 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- 4GB+ 内存推荐

### 🔧 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境（可选）**
```bash
cp .env.example .env
# 编辑 .env 文件添加API Key（使用付费模型时需要）
```

4. **启动应用**
```bash
streamlit run app.py
```

5. **访问应用**
   
   在浏览器中打开 `http://localhost:8501`

### 🎮 使用指南

#### 基础使用流程

1. **📤 上传简历** - 在侧边栏选择PDF格式的简历文件
2. **🤖 选择模型** - 从9种免费AI模型中选择（推荐DeepSeek系列）
3. **⚡ 开始分析** - 点击"开始分析"按钮，等待AI处理
4. **📊 查看结果** - 浏览详细的分析结果和多维度评分
5. **📄 导出报告** - 生成并下载PDF格式的专业分析报告

#### 高级功能

- **🔄 批量对比** - 同时上传多个简历进行横向比较
- **⚖️ 权重调整** - 根据岗位需求调整各维度权重
- **📚 历史记录** - 查看和管理历史分析结果
- **🎨 自定义配置** - 个性化评分标准和显示选项

## 📊 评分体系

### 🎯 评分维度

| 维度 | 权重 | 评估内容 |
|------|------|----------|
| 🎓 **教育背景** | 20% | 学历层次、院校声誉、专业匹配度 |
| 💼 **工作经验** | 30% | 工作年限、职位层级、行业相关性 |
| 🛠️ **技能匹配** | 25% | 专业技能、技术能力、证书资质 |
| 🚀 **项目经验** | 15% | 项目复杂度、成果展示、创新性 |
| 🌟 **综合素质** | 10% | 沟通能力、领导力、学习能力 |

### 📈 评分标准

- **9-10分**: 优秀 - 完全符合或超出岗位要求
- **7-8分**: 良好 - 基本符合岗位要求，有一定优势
- **5-6分**: 一般 - 满足基本要求，需要进一步评估
- **3-4分**: 较差 - 部分满足要求，存在明显不足
- **1-2分**: 不符合 - 不满足基本要求

## 🤖 支持的AI模型

### 免费模型（无需API Key）

| 模型 | 提供商 | 特点 |
|------|--------|------|
| 🌟 **DeepSeek Chat V3** | DeepSeek | 最新版本，中文优化 |
| 🔥 **DeepSeek R1** | DeepSeek | 推理能力强，逻辑清晰 |
| 🎯 **Qwen3-32B** | 阿里云 | 大参数模型，性能优异 |
| ✨ **Gemini 2.0 Flash** | Google | 快速响应，多模态支持 |

## 📁 项目结构

```
ai-resume-analyzer/
├── 📄 app.py                    # 主应用程序
├── ⚙️ config.py                # 配置文件
├── 🔧 pdf_fix.py               # PDF处理模块
├── 📦 requirements.txt         # 依赖包列表
├── 🌍 .env.example             # 环境变量模板
├── 📚 README.md                # 项目说明
├── 🚫 .gitignore               # Git忽略文件
├── 📖 docs/                    # 文档目录
│   ├── 打包说明.md
│   ├── 故障排除指南.md
│   ├── PDF修复说明.md
│   ├── 表格布局修复说明.md
│   └── 完整内容显示优化说明.md
├── 🧪 test_*.py               # 测试文件
└── 🏗️ build/                   # 构建目录
```

## 🔧 部署选项

### 🖥️ 本地运行
```bash
streamlit run app.py
```

### 📦 打包为可执行文件
```bash
# 使用PyInstaller
python build_exe.py

# 或使用简化脚本
python simple_build.py
```

### ☁️ 云端部署
- **Streamlit Cloud** - 免费托管
- **Heroku** - 容器化部署
- **Docker** - 容器化运行

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🔄 贡献流程

1. **Fork** 这个仓库
2. **创建** 特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **创建** Pull Request

### 🐛 报告问题

发现Bug？请通过 [Issues](https://github.com/yourusername/ai-resume-analyzer/issues) 报告。

### 💡 功能建议

有好的想法？欢迎在 [Discussions](https://github.com/yourusername/ai-resume-analyzer/discussions) 中分享。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 优秀的Web应用框架
- [OpenRouter](https://openrouter.ai/) - 提供免费AI模型接口
- [ReportLab](https://www.reportlab.com/) - PDF生成库
- 所有贡献者和用户的支持

## 📞 联系我们

- 📧 **邮箱**: [your-email@example.com]
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/yourusername/ai-resume-analyzer/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/yourusername/ai-resume-analyzer/discussions)

## 📈 更新日志

### 🎉 v1.3.0 (最新)
- ✅ 优化PDF内容显示，移除文本截断
- ✅ 更新AI模型列表，支持最新模型
- ✅ 改进表格布局和样式
- ✅ 增强中文字体支持

### 🔄 v1.2.0
- ✅ 修复PDF导出中文显示问题
- ✅ 优化表格布局，解决内容溢出
- ✅ 添加自动字体检测功能

### 🚀 v1.1.0
- ✅ 支持批量简历比较
- ✅ 添加可视化图表
- ✅ 优化用户界面

### 🎯 v1.0.0
- ✅ 初始版本发布
- ✅ 基础简历分析功能
- ✅ PDF导出功能

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！⭐**

[🏠 首页](https://github.com/yourusername/ai-resume-analyzer) • [📖 文档](docs/) • [🐛 报告问题](https://github.com/yourusername/ai-resume-analyzer/issues) • [💡 功能建议](https://github.com/yourusername/ai-resume-analyzer/discussions)

</div>

---

> **免责声明**: 本工具仅用于辅助招聘决策，不应作为唯一的评判标准。最终的招聘决定应综合考虑多种因素。