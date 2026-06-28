"""
UESTC 软院综合设计报告模板。

支持两种报告结构:
- midterm:  中期报告 (3章: 进展 + 问题与方案 + 完成度与计划)
- final:    后期报告 (6章: 引言 + 需求 + 设计 + 实现 + 测试 + 总结)

Usage:
    from uestc_doc.templates.uestc_thesis import build_report

    meta = ProjectMeta(
        course_name="进阶式挑战性综合项目II",
        college="信息与软件工程学院",
        semester="2025-2026 学年 2 学期",
        project_name="SysY 语言编译器",
        advisor="某教授",
        students=[{"name": "张三", "id": "20240001"}],
        abstract_text="本报告...",
        keywords_text="关键词1；关键词2",
    )

    doc = build_report(meta, report_type="midterm")
    doc.save("中期报告.docx")
"""

from .builder import build_report, ReportType
