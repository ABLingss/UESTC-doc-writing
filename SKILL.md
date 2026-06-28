---
name: uestc-doc
description: |-
  Use this skill whenever the user wants to create, generate, or build academic reports, thesis documents, or .docx files for Chinese university coursework — especially UESTC (电子科技大学) software engineering comprehensive design reports. Triggers include: any mention of '综设报告', '中期报告', '后期报告', '学术报告', '论文', 'docx生成', 'Word文档', or requests to produce formatted academic documents with tables of contents, Mermaid diagrams, code blocks with syntax highlighting, data tables, or letterheads. Also use when extracting code information from C/C++/Python projects for documentation, rendering Mermaid diagrams to PNG, or building report generation pipelines. Covers both midterm (中期) and final (后期) report formats with fully parameterized templates — never hardcodes personal/school info.
license: MIT. Complete terms in LICENSE
---

# UESTC Academic Report Generation

## Overview

Generate professional .docx academic reports for UESTC software engineering coursework. The framework provides parameterized templates, Mermaid diagram rendering, C/C++/Python source extraction, and a chapter pipeline — all via Python with `python-docx`.

## Quick Reference

| Task | Approach |
|------|----------|
| Generate midterm report | `build_report(meta, ReportType.MIDTERM)` — 3 chapters |
| Generate final report | `build_report(meta, ReportType.FINAL)` — 4 chapters + acknowledgments |
| Custom document from scratch | `new_document()` + `create_cover()` + manual sections |
| Insert syntax-highlighted code | `add_code_block(doc, code, language="cpp")` |
| Insert data table | `add_table(doc, headers, rows, caption="Table 1")` |
| Insert Mermaid diagram | `add_mermaid_image(doc, "path/to/diagram.png", caption="Fig 1")` |
| Render Mermaid to PNG | `render_mermaid(mmd_source, output_path)` |
| Scan C++ project | `scan_cpp_project("/path/to/src")` |
| Scan Python project | `scan_python_project("/path/to/src")` |
| Customize styles | `StyleConfig(header_text="...", cn_font_body="...")` |

---

## Installation

```bash
pip install -r requirements.txt
```

Core: `python-docx`, `Pillow`. Optional: `npm install -g @mermaid-js/mermaid-cli` for local diagram rendering.

---

## Creating Reports

### Quick Start: Template-Based

CRITICAL: Always use `ProjectMeta` to pass course/instructor/student info — never hardcode personal data.

```python
from uestc_doc import ProjectMeta
from uestc_doc.templates.uestc_thesis import build_report, ReportType

meta = ProjectMeta(
    course_name="综合设计项目",
    college="XX学院",
    semester="2025-2026 学年 2 学期",
    project_name="My Project",
    advisor="指导教师姓名",
    students=[
        {"name": "张三", "id": "20240001"},
        {"name": "李四", "id": "20240002"},
    ],
    abstract_text="本报告聚焦于...",
    keywords_text="关键词1；关键词2；关键词3",
)

# Midterm report (3 chapters: 进展 + 问题与方案 + 完成度与计划)
doc = build_report(meta, report_type=ReportType.MIDTERM)
doc.save("中期报告.docx")

# Final report (4 chapters + acknowledgments)
doc = build_report(meta, report_type=ReportType.FINAL,
    acknowledgments="感谢指导教师的悉心指导。\n感谢团队成员的通力协作。")
doc.save("后期报告.docx")
```

### Report Structures

**Midterm (中期) — 3 chapters:**
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

**Final (后期) — 4 chapters + acknowledgments:**
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

### Injecting Custom Content

All section functions accept `**kwargs` for content injection:

```python
doc = build_report(meta, report_type=ReportType.FINAL,
    # Chapter 1 content
    requirements={
        'functional_reqs': [
            ('FR1: Lexical Analysis', 'Support all language token types...'),
            ('FR2: Syntax Analysis', 'Build complete AST with 26 node types...'),
        ],
        'nonfunctional_reqs': [
            ('NFR1: Correctness', 'AC rate >= 95% on 示例 test suite.'),
        ],
    },
    problems_induction={
        'problems': [
            ('核心结构 Construction', [
                '核心结构 form is the mathematical foundation of modern system optimization.',
                'Phi node placement requires iterative dominance frontier computation.',
            ]),
        ],
    },
    # Chapter 2: Problems & Solutions
    problems={
        'problems': [
            ('Problem 1: 核心结构 Correctness', [
                'The 6-phase 核心算法 transformation is extremely complex...',
            ]),
        ],
        'solutions': [
            ('Solution 1: Pruned 核心结构 + Strict Stack Management', [
                'Use liveness info to prune unnecessary Phi nodes (30-40% reduction).',
            ]),
        ],
    },
    # Chapter 3: Completion status
    core_completion={
        'features': [
            ["Frontend", "解析+AST+代码生成", "Complete", "DONE", "LLI verified"],
            ["Midend", "核心分析模块", "Complete", "DONE", "Per-pass verified"],
        ],
    },
    # Chapter 4: Team
    team={
        'members': [
            ["Team Lead", "Architecture", "PipelineManager/RangeAnalysis", "35%"],
            ["Member 2", "Frontend+Test", "解析/代码生成", "35%"],
        ],
    },
)
```

### Building From Scratch

For full control, build documents piece by piece:

```python
from uestc_doc import (
    new_document, StyleConfig, ProjectMeta,
    create_cover, insert_toc_field,
    add_chapter_start, add_heading, add_body_para,
    add_bold_para, add_list_item, add_code_block,
    add_table, add_mermaid_image, add_references,
)

config = StyleConfig(
    header_text="学术报告",
    cn_font_body="宋体",
    cn_font_heading="黑体",
)

doc = new_document(config)
create_cover(doc, meta, config)
insert_toc_field(doc)

add_chapter_start(doc, "Introduction", 1)
add_heading(doc, "1.1 Background", level=2)
add_body_para(doc, "First paragraph with automatic first-line indent...")
add_bold_para(doc, "Key Point:")
add_list_item(doc, "Supporting detail one")
add_list_item(doc, "Supporting detail two")

add_references(doc, [
    "[1] Author. Title[M]. Publisher, 2024.",
])
doc.save("report.docx")
```

---

## Code Blocks

### Basic Usage

```python
# Language-specific highlighting (cpp, python, llvm, asm, riscv, arm)
add_code_block(doc, """
int main() {
    printf("Hello, World!\\n");
    return 0;
}
""", language="cpp")

# With caption
add_code_block(doc, code_string,
    language="python",
    caption="Code 4-1 Core Algorithm Implementation")

# From file (auto-detect language by extension)
add_code_block(doc, file="src/opt/核心算法.cpp",
    start_line=45, end_line=78,
    caption="Code 4-2 核心算法 Rename Phase")

# Highlight specific lines
add_code_block(doc, code_string,
    language="cpp",
    highlight_lines=[12, 13, 14])  # Highlight lines 12-14
```

### Supported Languages

| Language | `language=` | Keywords highlighted |
|----------|------------|---------------------|
| C/C++ | `"cpp"`, `"c"` | 70 C/C++ keywords + type names |
| Python | `"python"`, `"py"` | 40 Python keywords |
| LLVM IR | `"llvm"`, `"ir"` | 40 IR instructions + C++ keywords |
| 目标平台 ASM | `"riscv"`, `"rv"` | RV64G instructions + registers |
| 目标平台 ASM | `"arm"`, `"aarch64"` | AArch64 instructions + registers |
| x86 ASM | `"x86"`, `"asm"` | x86-64 instructions + registers |
| Auto-detect | `""` or omit | Combines all keyword sets |

### Code Block Styling

```python
# Customize via StyleConfig
config = StyleConfig(
    code_bg="F0F0F0",           # Background color
    code_font="Consolas",        # Font family
    size_code=8.5,               # Font size (pt)
    code_keyword=RGBColor(...),  # Keyword color
    code_comment=RGBColor(...),  # Comment color
    code_string=RGBColor(...),   # String color
)
```

CRITICAL: Never use plain text paragraphs for code. Always use `add_code_block()` — it provides line numbers, syntax highlighting, and proper monospace formatting. Plain text code in reports looks unprofessional.

---

## Tables

### Basic Table

```python
add_table(doc,
    ["Module", "Completion", "Status"],
    [
        ["Frontend", "100%", "Complete"],
        ["Midend", "100%", "Complete"],
        ["Backend", "85%", "In Progress"],
    ],
    caption="Table 3-1 Module Completion Status"
)
```

### Column Widths

```python
from docx.shared import Cm

add_table(doc, headers, rows,
    caption="Table 4-1 Performance Comparison",
    col_widths=[Cm(4), Cm(3), Cm(3), Cm(4)]
)
```

CRITICAL: Tables use `Table Grid` style with centered header text (bold 12pt). Data cells are centered. Always provide a caption for academic formatting.

---

## Mermaid Diagrams

### Three Rendering Strategies (Auto-Fallback)

```python
from uestc_doc.renderers import render_mermaid, render_mermaid_batch, RendererType

# Auto-detect best renderer (mmdc > mermaid.ink > pure python)
render_mermaid(mmd_source, "output/diagram.png")

# Force specific renderer
render_mermaid(mmd_source, "output/diagram.png",
    renderer=RendererType.MMDC,  # Local high-quality
    scale=3, theme="forest")

# Batch render
render_mermaid_batch({
    "architecture": "graph TD\n  A-->B-->C",
    "class_diagram": "classDiagram\n  class Foo{...}",
}, output_dir="output/")
```

### Inserting Rendered Diagrams

```python
add_mermaid_image(doc, "output/architecture.png",
    caption="Figure 3-1 System Architecture",
    width_cm=14.0)  # Auto-height-limited to 18cm
```

| Renderer | Requires | Quality | Speed |
|----------|---------|---------|-------|
| `mmdc` CLI | `npm install -g @mermaid-js/mermaid-cli` | Best | Fast |
| `mermaid.ink` API | Internet | Good | Medium |
| Pure Python/Pillow | Nothing | Basic | Instant |

---

## Content Extraction

### Scan C++ Projects

```python
from uestc_doc.extractors import scan_cpp_project

result = scan_cpp_project("/path/to/system/src")
# result['overview']  — ProjectOverview with stats
# result['passes']    — [CppPassInfo, ...] categorized by type
# result['headers']   — {file: header_comment, ...}
```

Auto-categorizes C++ classes/functions into: Analysis, Scalar, ControlFlow, Redundancy, Memory, Loop, Advanced, Framework.

### Scan Python Projects

```python
from uestc_doc.extractors import scan_python_project

result = scan_python_project("/path/to/ml_project")
# result['modules']   — [PyModuleInfo, ...] with classes, functions, decorators
```

Auto-infers categories: Model, View, Controller, Training, Data, Utility, Config.

### Code Statistics

```python
from uestc_doc.extractors.common import scan_project

overview = scan_project("/path/to/project", exts=['.cpp', '.hpp'])
# overview.stats.total_lines
# overview.stats.code_lines
# overview.stats.comment_lines
# overview.stats.chinese_comment_lines
```

---

## Style Customization

All styles are parameterized via `StyleConfig`:

```python
from uestc_doc import StyleConfig
from docx.shared import Cm, RGBColor

config = StyleConfig(
    # Page margins
    margin_top_body=Cm(2.54),
    margin_bottom_body=Cm(2.54),
    margin_left_body=Cm(3.18),
    margin_right_body=Cm(3.18),

    # Fonts
    en_font="Times New Roman",
    cn_font_body="宋体",
    cn_font_heading="黑体",
    code_font="Consolas",

    # Sizes (pt)
    size_body=12.0,
    size_h1=16.0,    # Chapter titles
    size_h2=14.0,    # Section titles
    size_h3=12.0,    # Subsection titles
    size_code=9.0,

    # Header text
    header_text="学术报告",

    # Colors
    code_bg="F5F5F5",
    code_keyword=RGBColor(0x00, 0x00, 0xFF),
    code_comment=RGBColor(0x00, 0x80, 0x00),
)

doc = new_document(config)
```

---

## Page Numbering and Headers/Footers

```python
from uestc_doc.components import add_page_numbers, add_header_footer

# Add page numbers (centered, bottom)
add_page_numbers(doc, position="bottom_center", start_at=1)

# Custom header with section name
add_header_footer(doc,
    header_text="Chapter 3: System Design",
    show_page_number=True)
```

---

## Critical Rules

- **Never hardcode personal info** — Use `ProjectMeta` for all course/instructor/student data
- **Chapter starts use page breaks** — `add_chapter_start()` auto-inserts `\page`
- **TOC requires Word update** — After opening, right-click TOC → Update Field → Update entire table
- **Code blocks need language** — Specify `language=` for proper syntax highlighting; plain text code looks unprofessional
- **Tables need captions** — Academic formatting requires table captions (e.g., "Table 3-1 ...")
- **Figures need captions** — Every `add_mermaid_image()` / `add_figure()` should have a `caption=`
- **Mermaid images auto-height-limit** — Max 18cm tall, auto-constrained to fit A4 page
- **Fonts must exist on system** — SimHei/SimSun (Windows), PingFang (macOS), or install via `apt install fonts-wqy-zenhei` (Linux)
- **First-line indent is automatic** — `add_body_para()` applies 0.74cm indent matching the template spec
- **Line spacing is 1.5x** — Body text uses 1.5x line spacing per UESTC requirements
- **Never use `\n` in paragraph text** — Use separate `add_body_para()` calls for each paragraph
- **Authors are fully parameterized** — No Claude, no hardcoded names anywhere in generated documents

---

## Dependencies

- **python-docx >= 0.8.11**: Document creation and manipulation
- **Pillow >= 9.0.0**: Image handling (Mermaid PNG reading, pure Python rendering)
- **Node.js + @mermaid-js/mermaid-cli** (optional): High-quality local Mermaid rendering
- **Internet** (optional): For mermaid.ink API rendering
