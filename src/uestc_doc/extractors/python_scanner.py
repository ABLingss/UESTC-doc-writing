"""
Python 项目扫描器 — 模块docstring、类/函数定义、装饰器标记。

适用于:
- ML/DL 项目 (识别模型类、训练函数)
- Web 后端 (识别路由、中间件)
- 通用 Python 项目
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import os
import re
import ast

from .common import CodeStats, ProjectOverview


@dataclass
class PyModuleInfo:
    """Python 模块信息。"""
    name: str = ""
    file_path: str = ""
    docstring: str = ""
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    line_count: int = 0
    category: str = ""  # model/view/controller/util/...


DEFAULT_EXCLUDE = [
    'test', 'tests', '__pycache__', '.git',
    'venv', '.venv', 'env', 'build', 'dist',
    'node_modules', '.egg-info', 'migrations',
]


def scan_python_project(root_dir: str,
                        include_dirs: List[str] = None,
                        exclude_patterns: List[str] = None
                        ) -> Dict:
    """扫描 Python 项目。

    Args:
        root_dir: 项目根目录
        include_dirs: 要扫描的子目录
        exclude_patterns: 排除目录名列表

    Returns:
        {
            'overview': ProjectOverview,
            'modules': [PyModuleInfo, ...],
        }
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE

    search_paths = [root_dir]
    if include_dirs:
        search_paths = [os.path.join(root_dir, d) for d in include_dirs]

    overview = ProjectOverview(
        name=os.path.basename(os.path.abspath(root_dir)),
        language='Python',
    )
    modules = []
    stats = CodeStats()

    for search_path in search_paths:
        if not os.path.isdir(search_path):
            continue

        for dirpath, dirnames, filenames in os.walk(search_path):
            dirnames[:] = [d for d in dirnames
                          if not any(p in d.lower()
                                     for p in exclude_patterns)]

            for fname in sorted(filenames):
                if not fname.endswith('.py'):
                    continue
                if fname.startswith('__') and fname != '__init__.py':
                    continue

                fpath = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(fpath, root_dir)

                try:
                    with open(fpath, 'r', encoding='utf-8',
                              errors='replace') as f:
                        content = f.read()
                        lines = content.split('\n')
                except Exception:
                    continue

                # 统计
                stats = _update_py_stats(stats, lines)
                overview.structure.append(rel_path)

                # AST 解析
                module_info = _parse_python_module(fpath, rel_path, content,
                                                   lines)
                if module_info:
                    modules.append(module_info)

    overview.stats = stats
    overview.total_lines = stats.total_lines
    overview.total_files = stats.total_files

    return {
        'overview': overview,
        'modules': sorted(modules, key=lambda m: m.category or ''),
    }


def _update_py_stats(stats, lines):
    stats.total_files += 1
    stats.total_lines += len(lines)
    in_triple = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            stats.blank_lines += 1
            continue
        if in_triple:
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            if '"""' in stripped or "'''" in stripped:
                in_triple = False
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            if stripped.count('"""') < 2 and stripped.count("'''") < 2:
                in_triple = True
            continue
        if stripped.startswith('#'):
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            continue
        stats.code_lines += 1
    return stats


def _has_chinese(text):
    return bool(re.search(r'[一-鿿]', text))


def _parse_python_module(fpath, rel_path, content, lines):
    """解析单个 Python 文件。"""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    docstring = ast.get_docstring(tree) or ''

    classes = []
    functions = []
    decorators = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorators.add(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorators.add(dec.attr)

        if isinstance(node, ast.FunctionDef):
            # 跳过 dunder
            if not node.name.startswith('_'):
                functions.append(node.name)
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorators.add(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorators.add(dec.attr)
                elif isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name):
                        decorators.add(dec.func.id)

    # 提取 imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # 推断分类
    category = _infer_py_category(rel_path, classes, functions, decorators)

    return PyModuleInfo(
        name=os.path.splitext(os.path.basename(fpath))[0],
        file_path=rel_path,
        docstring=docstring,
        classes=classes,
        functions=functions,
        decorators=list(decorators),
        imports=imports[:20],  # 截断
        line_count=len(lines),
        category=category,
    )


def _infer_py_category(rel_path, classes, functions, decorators):
    """推断 Python 模块类别。"""
    path_lower = rel_path.lower()

    if 'model' in path_lower or 'nn.' in path_lower:
        return 'Model'
    if 'view' in path_lower or 'ui' in path_lower or 'gui' in path_lower:
        return 'View'
    if 'controller' in path_lower or 'route' in path_lower:
        return 'Controller'
    if 'train' in path_lower or 'optim' in path_lower:
        return 'Training'
    if 'data' in path_lower or 'dataset' in path_lower:
        return 'Data'
    if 'test' in path_lower:
        return 'Test'
    if 'util' in path_lower or 'helper' in path_lower:
        return 'Utility'
    if 'config' in path_lower or 'setting' in path_lower:
        return 'Config'
    if 'loss' in path_lower:
        return 'Loss'
    if 'metric' in path_lower or 'eval' in path_lower:
        return 'Evaluation'

    # 根据装饰器推断
    dec_set = set(decorators)
    if dec_set & {'torch', 'nn', 'Module', 'Parameter'}:
        return 'Model'
    if dec_set & {'app', 'router', 'bp', 'route', 'get', 'post'}:
        return 'Controller'

    return 'Other'
