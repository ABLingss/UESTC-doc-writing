"""
UESTC-doc-writing — 学术报告/论文文档自动生成框架

提供:
- 符合学术规范的 Word 文档样式系统 (styles.py)
- 可复用文档组件 (components.py): 封面/目录/代码块/图表/表格
- Mermaid 图渲染管线: mermaid.ink / mmdc CLI / 纯Python fallback
- 代码信息提取器: C/C++ / Python 源码扫描
- 章节生成 Pipeline: 逐个章节独立生成, 最后合并
"""

__version__ = "1.0.0"

from .styles import StyleConfig, setup_styles, setup_page
from .components import (
    ProjectMeta,
    new_document,
    create_cover,
    insert_toc_field,
    add_heading,
    add_body_para,
    add_bold_para,
    add_inline_emphasized_para,
    add_list_item,
    add_numbered_item,
    add_code_block,
    add_mermaid_image,
    add_figure,
    add_table,
    add_chapter_start,
    add_references,
    add_page_numbers,
    add_header_footer,
)
