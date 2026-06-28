"""
代码信息提取器 — 从项目源码中提取结构化信息用于报告生成。

支持:
- C/C++: 头文件注释、函数声明、Pass/模块分类
- Python: 模块docstring、类/函数定义、装饰器标记
- 通用: 代码行数统计、中文注释率、文件树

Usage:
    from uestc_doc.extractors import scan_cpp_project, scan_python_project
    inventory = scan_cpp_project("/path/to/project")
"""

from .cpp_scanner import scan_cpp_project, CppPassInfo
from .python_scanner import scan_python_project, to_markdown, PyModuleInfo
from .common import ProjectOverview, CodeStats, scan_project
