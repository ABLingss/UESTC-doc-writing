# UESTC-doc-writing

> 电子科技大学学术报告/论文文档自动生成框架

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)](SKILL.md)

一套完整的 **Word 文档自动生成 Pipeline**，针对电子科技大学软件学院学术报告/论文模板深度优化。支持 Mermaid 图渲染、C/C++/Python 源码信息提取、章节 Pipeline 独立生成与合并。

**🤖 已适配 Claude Code Skill** — 在 Claude Code 中输入 `/uestc-doc` 即可让 AI 帮你写报告。

## 特性

- **🤖 Claude Code Skill 集成** — 一句话让 AI 帮你生成完整综设报告
- **即开即用的 .docx 生成** — 基于 `python-docx`，生成符合软院规范的 Word 文档
- **完全参数化** — 所有课程/导师/学生信息通过 `ProjectMeta` 传入，零个人信息硬编码
- **三种 Mermaid 渲染策略** — mermaid.ink API → mmdc CLI → 纯 Python/Pillow，自动降级
- **源码信息提取** — 支持 C/C++ 项目（识别 Pass/模块）和 Python 项目（识别类/函数/装饰器）
- **章节 Pipeline** — 每个章节独立生成 `.docx`，最后合并，支持并行生成
- **中期/后期报告双模式** — 内置 UESTC 软院模板，中期3章/后期4章+致谢
- **代码语法高亮** — C/C++/Python/LLVM IR/RISC-V/ARM/x86 共 7 种语言
- **脱敏模板** — `docs/` 目录包含已脱敏的中期和后期报告空白模板，可直接下载使用

---

## 🤖 注册为 Claude Code Skill

将本仓库注册为 Claude Code 技能后，直接在对话中说「帮我生成综设中期报告」即可让 AI 自动完成。

### 方法一：从 Skill Market 一键安装（推荐）

在 Claude Code 对话中输入：

```
/plugin install ABLingss/UESTC-doc-writing
```

Claude Code 会自动从 GitHub 拉取并注册技能。安装后直接对话即可触发。

### 方法二：通过 /config 命令

在 Claude Code 对话中输入：
```
/config
```
选择 **Skills** → **Add Skill** → 输入 `https://github.com/ABLingss/UESTC-doc-writing` 即可。

### 方法三：克隆仓库本地注册

```bash
git clone https://github.com/ABLingss/UESTC-doc-writing.git
cd UESTC-doc-writing
pip install -r requirements.txt
```

然后在 Claude Code 中：
```
/skill add uestc-doc ./SKILL.md
```

### 注册后的使用效果

注册后直接用自然语言驱动：

- 「帮我生成一份综设中期报告，课题是XXX，指导老师是XXX」
- 「给第三章加一个完成度评估表，包含前端/中端/后端三个模块」
- 「把这段 LLVM IR 代码加到4.3节，用语法高亮」
- 「渲染 DOCS.md 里的 Mermaid 图，插入到系统设计章节」
- 「扫描 src/ 目录，提取所有 Pass 的分类和行数统计，生成表格」

---

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

核心依赖: `python-docx`, `Pillow`

可选: 安装 [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) 以获得更高质量的本地图表渲染:
```bash
npm install -g @mermaid-js/mermaid-cli
```

### 5 分钟生成一份报告

```python
from uestc_doc import (
    new_document, ProjectMeta, StyleConfig,
    create_cover, insert_toc_field,
    add_chapter_start, add_heading, add_body_para,
    add_bold_para, add_table, add_code_block,
    add_references,
)

# 1. 定义项目元数据
meta = ProjectMeta(
    course_name="进阶式挑战性综合项目II",
    college="信息与软件工程学院",
    semester="2025-2026 学年 2 学期",
    project_name="SysY 语言编译器",
    advisor="某教授",
    students=[
        {"name": "张三", "id": "20240001"},
        {"name": "李四", "id": "20240002"},
    ],
    abstract_text="本报告聚焦于...",
    keywords_text="编译器；LLVM；代码优化",
)

# 2. 创建文档
doc = new_document()
create_cover(doc, meta)
insert_toc_field(doc)

# 3. 写第一章
add_chapter_start(doc, "引言", 1)
add_heading(doc, "1.1 项目背景", level=2)
add_body_para(doc, "这是正文内容，自动使用宋体12pt、首行缩进、1.5倍行距...")

add_heading(doc, "1.2 核心算法", level=2)
add_code_block(doc, """
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
""", language="cpp")

# 4. 插图
add_heading(doc, "1.3 系统架构", level=2)
add_body_para(doc, "下图展示了系统的总体架构：")
# add_mermaid_image(doc, "path/to/architecture.png", "图1-1 系统总体架构")

# 5. 表格
add_table(doc,
    ["模块", "完成度", "状态"],
    [["前端", "100%", "已完成"], ["中端", "100%", "已完成"], ["后端", "85%", "进行中"]],
    caption="表1-1 模块完成情况"
)

# 6. 参考文献
add_references(doc, [
    "[1] Aho A V, et al. Compilers: Principles, Techniques, and Tools[M]. 2006.",
    "[2] Lattner C, Adve V. LLVM: A Compilation Framework...[C]. CGO 2004.",
])

# 7. 保存
doc.save("我的报告.docx")
```

### 使用内置 UESTC 模板

```python
from uestc_doc import ProjectMeta
from uestc_doc.templates.uestc_thesis import build_report, ReportType

meta = ProjectMeta(
    course_name="进阶式挑战性综合项目II",
    college="信息与软件工程学院",
    semester="2025-2026 学年 2 学期",
    project_name="My Project",
    advisor="某教授",
    students=[{"name": "张三", "id": "20240001"}],
    abstract_text="本报告...",
    keywords_text="关键词1；关键词2",
)

# 生成中期报告 (3章: 进展 + 问题与方案 + 完成度与计划)
doc = build_report(meta, report_type=ReportType.MIDTERM)
doc.save("中期报告.docx")

# 生成后期报告 (4章+致谢: 工程问题与可行性 + 问题与方案 + 执行情况 + 分工协作)
doc = build_report(meta, report_type=ReportType.FINAL,
    acknowledgments="感谢指导老师和团队成员。")
doc.save("后期报告.docx")
```

### 报告结构

**中期报告 (3章):**
```
第一章 综合设计的进展情况
  1.1 针对工程问题的方案设计
  1.2 针对工程问题的推理分析
  1.3 针对工程问题的具体实现
  1.4 知识技能学习情况
第二章 存在问题与解决方案
  2.1 存在的主要问题
  2.2 解决方案
第三章 前期任务完成度与后续实施计划
参考文献
```

**后期报告 (4章 + 致谢):**
```
第一章 复杂工程问题归纳与实施方案可行性研究
  1.1 需求分析与建模
  1.2 复杂工程问题归纳
  1.3 实施方案与可行性研究
第二章 存在问题与解决方案
  2.1 存在的主要问题
  2.2 解决方案
第三章 执行情况与完成度
  3.1 项目执行过程概述
  3.2 核心功能完成情况
  3.3 仿真运行效果
  3.4 完成度评估
第四章 分工协作与交流情况
参考文献
致谢
```

### 注入自定义内容

```python
doc = build_report(meta, report_type=ReportType.FINAL,
    design={
        'architecture_desc': '本系统采用三层架构...',
        'sections': [
            ('前端设计', 2, ['前端负责...', '词法分析采用Flex...']),
            ('中端设计', 2, ['中端IR采用LLVM兼容格式...']),
        ],
    },
    requirements={
        'functional_reqs': [
            ('FR1: 词法分析', '支持所有SysY关键字...'),
            ('FR2: 语法分析', '构建完整AST...'),
        ],
        'complex_problems': [
            ('复杂工程问题一：SSA构建', [
                'SSA形式的数学定义...',
                'Phi函数插入的IDF算法...',
            ]),
        ],
    },
    testing={
        'test_results': [
            ('功能测试', '138', '138', '100%'),
            ('性能测试', '12', '12', '100%'),
        ],
    },
)
```

## 架构

```
src/uestc_doc/
├── __init__.py          # 公共 API
├── styles.py            # 样式系统 (15种样式, 完全参数化)
├── components.py        # 可复用组件 (封面/目录/代码块/图表/表格/参考文献)
├── renderers/           # Mermaid 图渲染 (3种策略, 自动降级)
│   ├── mermaid_ink.py   #   mermaid.ink HTTP API (零依赖)
│   ├── mmdc_cli.py      #   mmdc CLI (本地高质量)
│   └── pure_python.py   #   Pillow 手动绘制 (离线fallback)
├── extractors/          # 源码信息提取
│   ├── common.py        #   通用扫描器 (代码统计/中文注释率)
│   ├── cpp_scanner.py   #   C/C++ 项目 (识别Pass/模块/依赖关系)
│   └── python_scanner.py#   Python 项目 (AST解析/装饰器分类)
└── templates/           # 报告模板
    └── uestc_thesis/    #   UESTC 软院综合设计报告
        ├── builder.py   #   报告组装器 (中期/后期双模式)
        └── sections.py  #   章节骨架 (参数化内容注入)
```

## 更多

- **`extractors`** 模块可独立使用，扫描任意 C/C++/Python 项目生成 JSON 清单
- **`renderers`** 模块可独立使用，批量渲染 Mermaid `.mmd` 文件为 PNG
- **模板系统** 基于骨架+注入模式，用户通过 kwargs 传入项目特定内容
- 样式系统通过 `StyleConfig` 可覆盖所有字体/字号/间距/颜色，适配不同院系模板

## 适用场景

- 电子科技大学软件学院进阶式挑战性综合项目报告
- 编译器/系统软件课程设计报告
- 本科毕业设计论文
- 任何需要按模板生成 .docx 文档的学术场景## License

GPL-3.0 © ABLingss
