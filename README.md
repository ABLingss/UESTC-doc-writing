# 综设.skill

> *「你的综设报告，一句话就够了。」*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green)](https://agentskills.io)
[![skills.sh](https://img.shields.io/badge/skills.sh-Compatible-blue)](https://skills.sh)
[![Multi-Runtime](https://img.shields.io/badge/Runtime-Claude%20Code%20·%20Codex%20·%20Cursor-blueviolet)](#-安装)

<br>

**电子科技大学综合设计报告一键生成。中期/后期双模板，Mermaid 架构图自动渲染，C/C++/Python/中间表示 IR/目标平台/目标平台/x86 七种语言代码高亮，源码信息自动提取。**

<sub>基于开放的 [Agent Skills 协议](https://agentskills.io)，可在 Claude Code、Codex、Cursor 等兼容 runtime 中运行。同时也是完整 Python 库，可独立调用。</sub>

[效果](#-效果演示) · [安装](#-安装) · [Python 库](#-python-库快速开始) · [报告结构](#报告结构) · [架构](#架构)

---

## ✨ 效果演示

**安装 Skill 后，跟 AI 对话就行了：**

```
用户 ❯ 帮我生成一份综设中期报告，课题是 XXX项目，指导老师是某老师

AI   ❯ 好的。请确认以下信息：
        课程：综合设计项目
        学院：XX学院
        课题：XXX项目
        ...
        确认无误，开始生成。

        已生成 中期报告.docx，包含：
        ✅ 封面 + 摘要 + 目录
        ✅ 第一章 综合设计的进展情况（方案设计/推理分析/具体实现/知识技能）
        ✅ 第二章 存在问题与解决方案
        ✅ 第三章 前期任务完成度与后续实施计划
        ✅ 参考文献

        请在 Word 中右键目录 → 更新域。
```

**不只是生成空壳——AI 会帮你写内容：**

```
用户 ❯ 给 1.2 推理分析加两个复杂工程问题：核心模块构建 和 寄存器分配

AI   ❯ 已更新 1.2 节，新增：
        复杂工程问题一：静态单赋值形式的构建与销毁
        - 核心结构 的数学定义与 Phi 节点放置
        - 迭代支配边界的计算复杂度
        - 变量重命名的正确性保证

        复杂工程问题二：寄存器分配与溢出处理
        - 贪心+活跃区间分析的分配策略
        - Spill 代码生成的正确性
        - 传送亲和性优化
```

```
用户 ❯ 把 src/ir/opt/核心算法.cpp 的第 45-78 行插入到 1.3 节，用 C++ 高亮，标题「代码1-1 Rename 阶段」

AI   ❯ 已插入代码块「代码1-1 Rename 阶段」，C++ 语法高亮，行号 45-78。
```

```
用户 ❯ 3.1 完成度改成表格：前端 100%、中端 100%、后端 85%、测试 70%

AI   ❯ 已更新表3-1 前期任务完成度总览：

        | 模块   | 完成度 | 验证状态    |
        |--------|--------|-------------|
        | 前端   | 100%   | 测试通过    |
        | 中端   | 100%   | 语义验证通过 |
        | 后端   | 85%    | 核心完成    |
        | 测试   | 70%    | 进行中      |
```

**对比：手写 vs 综设.skill**

| | 手写 Word | 综设.skill |
|---|---|---|
| 封面信息 | 手动填，容易写错 | 一句话 |
| 目录 | 手动插域 → 更新 | 自动生成 |
| 格式（字体/字号/行距/缩进） | 逐个段落调 | 自动符合学术规范 |
| 代码块 | 手动换字体、着色 | 自动语法高亮 + 行号 |
| Mermaid 图 | 截图 → 缩放 → 对齐 | 自动渲染 → 插入 |
| 改格式 | 全文档重调 | 改一行 StyleConfig |
| 导师名字写错了 | F | 改一个参数重跑 |

---

## 📦 安装

本 Skill 基于开放的 [Agent Skills](https://agentskills.io) 协议。

### 方式一：自然语言安装（推荐）

打开 Claude Code（或 Codex、Cursor），直接说：

```
帮我安装这个 skill：https://github.com/ABLingss/UESTC-doc-writing
```

### 方式二：npx CLI 安装

```bash
npx skills add ABLingss/UESTC-doc-writing
```

支持 `-a claude-code` / `-a codex` / `-a cursor` 等参数指定 runtime。

### 方式三：Git 克隆安装

```bash
git clone https://github.com/ABLingss/UESTC-doc-writing.git
cd UESTC-doc-writing
pip install -r requirements.txt
```

Skill 目录放到对应 runtime 的 skills 路径：

| Runtime | 路径 |
|---|---|
| Claude Code | `~/.claude/skills/uestc-doc-writing/` |
| Codex CLI | `~/.codex/skills/uestc-doc-writing/` |
| Cursor | `~/.cursor/skills/uestc-doc-writing/` |

### 方式四：纯 Python 库安装（不使用 Skill）

```bash
pip install -r requirements.txt
```

核心依赖：`python-docx`、`Pillow`。可选：`npm install -g @mermaid-js/mermaid-cli` 获得更高质量本地图渲染。

### 直接下载模板

不需要写代码？直接下载 `docs/` 目录下的空白模板手动填写：
- [`中期报告模板.docx`](docs/中期报告模板.docx)
- [`总结报告模板.docx`](docs/总结报告模板.docx)

---

## 🐍 Python 库快速开始

### 5 分钟生成一份报告

```python
from uestc_doc import (
    new_document, ProjectMeta,
    create_cover, insert_toc_field,
    add_chapter_start, add_heading, add_body_para,
    add_bold_para, add_table, add_code_block, add_references,
)

meta = ProjectMeta(
    course_name="综合设计项目",
    college="XX学院",
    semester="2025-2026 学年 2 学期",
    project_name="XXX项目",
    advisor="指导教师姓名",
    students=[{"name": "张三", "id": "20240001"}],
    abstract_text="本报告聚焦于...",
    keywords_text="系统；中间表示；代码优化",
)

doc = new_document()
create_cover(doc, meta)
insert_toc_field(doc)

add_chapter_start(doc, "引言", 1)
add_heading(doc, "1.1 项目背景", level=2)
add_body_para(doc, "这是正文，自动宋体12pt、首行缩进、1.5倍行距。")

add_code_block(doc, """
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
""", language="cpp", caption="代码1-1 斐波那契递归")

add_table(doc,
    ["模块", "完成度", "状态"],
    [["前端", "100%", "已完成"], ["中端", "100%", "已完成"]],
    caption="表1-1 模块完成情况"
)

add_references(doc, [
    "[1] Aho A V, et al. Systems: Principles, Techniques, and Tools[M]. 2006.",
])

doc.save("我的报告.docx")
```

### 使用内置模板一行生成

```python
from uestc_doc import ProjectMeta
from uestc_doc.templates.uestc_thesis import build_report, ReportType

meta = ProjectMeta(
    course_name="综合设计项目",
    college="XX学院",
    semester="2025-2026 学年 2 学期",
    project_name="My Project",
    advisor="指导教师",
    students=[{"name": "张三", "id": "20240001"}],
)

# 中期报告
build_report(meta, ReportType.MIDTERM).save("中期报告.docx")

# 后期报告
build_report(meta, ReportType.FINAL,
    acknowledgments="感谢指导教师的悉心指导。").save("后期报告.docx")
```

模板支持通过 `**kwargs` 注入全部内容，详见 [SKILL.md](SKILL.md)。

---

## 报告结构

| 章节 | 中期报告 | 后期报告 |
|------|---------|---------|
| 第一章 | 综合设计的进展情况 | 复杂工程问题归纳与实施方案可行性研究 |
| 1.1 | 针对工程问题的方案设计 | 需求分析与建模 |
| 1.2 | 针对工程问题的推理分析 | 复杂工程问题归纳 |
| 1.3 | 针对工程问题的具体实现 | 实施方案与可行性研究 |
| 1.4 | 知识技能学习情况 | — |
| 第二章 | 存在问题与解决方案 | 存在问题与解决方案 |
| 第三章 | 前期任务完成度与后续实施计划 | 执行情况与完成度 |
| 第四章 | — | 分工协作与交流情况 |
| 结尾 | 参考文献 | 参考文献 + 致谢 |

---

## 架构

```
src/uestc_doc/
├── __init__.py          # 公共 API
├── styles.py            # 样式系统 (15种, StyleConfig 全参数化)
├── components.py        # 30+ 组件 (封面/目录/代码块/图表/表格/页码)
├── renderers/           # Mermaid 渲染 (3策略自动降级)
│   ├── mermaid_ink.py   #   mermaid.ink API (零依赖)
│   ├── mmdc_cli.py      #   mmdc CLI (本地高质量)
│   └── pure_python.py   #   Pillow (离线 fallback)
├── extractors/          # 源码信息提取
│   ├── cpp_scanner.py   #   C/C++ 项目 (Pass识别/分类)
│   └── python_scanner.py#   Python 项目 (AST解析)
└── templates/uestc_thesis/
    ├── builder.py       #   组装器 (中期/后期)
    └── sections.py      #   14个章节骨架
```

## License

MIT © ABLingss
