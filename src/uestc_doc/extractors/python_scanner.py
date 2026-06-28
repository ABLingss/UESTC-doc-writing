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
                        exclude_patterns: List[str] = None,
                        skip_init: bool = True
                        ) -> Dict:
    """扫描 Python 项目。

    Args:
        root_dir: 项目根目录
        include_dirs: 要扫描的子目录
        exclude_patterns: 排除目录名列表
        skip_init: 是否跳过 __init__.py (默认 True)

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
                if skip_init and fname == '__init__.py':
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
    class_methods = {}  # {class_name: [method_names]} for dedup
    functions = []
    decorators = set()

    current_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            current_class = node.name
            class_methods[node.name] = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorators.add(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorators.add(dec.attr)

        if isinstance(node, ast.FunctionDef):
            # 跳过 dunder
            if not node.name.startswith('_'):
                func_name = node.name
                if current_class and current_class in class_methods:
                    # Per-class tracking: avoid listing 'forward' 11 times
                    if func_name not in class_methods[current_class]:
                        class_methods[current_class].append(func_name)
                else:
                    functions.append(func_name)
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

    # Merge class methods into functions for display
    all_funcs = list(functions)
    for cls_name, methods in class_methods.items():
        for m in methods:
            all_funcs.append(f"{cls_name}.{m}")

    return PyModuleInfo(
        name=os.path.splitext(os.path.basename(fpath))[0],
        file_path=rel_path,
        docstring=docstring,
        classes=classes,
        functions=all_funcs,
        decorators=list(decorators),
        imports=imports[:20],  # 截断
        line_count=len(lines),
        category=category,
    )


def _infer_py_category(rel_path, classes, functions, decorators):
    """推断 Python 模块类别。"""
    path_lower = rel_path.lower()
    dec_set = set(decorators)

    # ── 路径关键词匹配 ──
    CATEGORY_KEYWORDS = [
        # (category, [keywords])
        ('Model',       ['model', 'nn.', 'layer', 'embedding', 'attention',
                         'encoder', 'decoder', 'transformer', 'backbone',
                         'network', 'classifier', 'detector']),
        ('Pipeline',    ['pipeline', 'workflow']),
        ('View',        ['view', 'ui', 'gui', 'widget', 'window', 'dialog',
                         'uis/', '/ui/', 'uis\\', '\\ui\\']),
        ('Controller',  ['controller', 'route', 'router', 'handler']),
        ('API',         ['/api/', '\\api\\', 'api.', 'endpoint', 'rest']),
        ('Auth',        ['auth', 'login', 'oauth', 'token', 'jwt']),
        ('Database',    ['db', 'database', 'sql', 'orm', 'mongo', 'redis']),
        ('Service',     ['service', 'client', 'sdk']),
        ('Core',        ['core', 'engine', 'kernel', 'registry', 'cache',
                         'scheduler', 'queue']),
        ('Training',    ['train', 'optim', 'scheduler', 'finetune', 'lora']),
        ('Data',        ['data', 'dataset', 'dataloader', 'preprocess',
                         'transform', 'augment', 'feature', 'indicator']),
        ('Config',      ['config', 'setting', 'constant', 'env']),
        ('Test',        ['test', 'testing', 'unittest', 'benchmark']),
        ('Logging',     ['log', 'logging', 'monitor', 'alert']),
        ('Utility',     ['util', 'helper', 'tool', 'common', 'format',
                         'convert', 'parser', 'validator']),
        ('CLI',         ['cli', 'command', 'argparse', 'main', 'entry']),
        ('Loss',        ['loss', 'metric']),
        ('Signal',      ['signal', 'slot', 'event', 'callback', 'message']),
    ]

    for cat, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in path_lower:
                return cat

    # ── 装饰器推断 ──
    if dec_set & {'torch', 'nn', 'Module', 'Parameter', 'dataclass'}:
        return 'Model'
    if dec_set & {'app', 'router', 'bp', 'route', 'get', 'post',
                  'put', 'delete', 'patch'}:
        return 'API'
    if dec_set & {'staticmethod', 'classmethod', 'property'}:
        if classes:
            return 'Core'

    # ── 类名推断 ──
    class_names = ' '.join(classes).lower()
    if any(kw in class_names for kw in
           ['model', 'network', 'encoder', 'decoder', 'layer', 'attention',
            'classifier', 'detector', 'segmenter', 'predictor']):
        return 'Model'
    if any(kw in class_names for kw in
           ['service', 'client', 'sdk', 'api']):
        return 'Service'
    if any(kw in class_names for kw in
           ['engine', 'manager', 'registry', 'cache', 'scheduler']):
        return 'Core'
    if any(kw in class_names for kw in
           ['config', 'setting', 'constant']):
        return 'Config'
    if any(kw in class_names for kw in
           ['pipeline', 'workflow', 'generator']):
        return 'Pipeline'
    if any(kw in class_names for kw in
           ['preprocessor', 'processor', 'augment', 'extractor']):
        return 'Data'
    if any(kw in class_names for kw in
           ['widget', 'window', 'dialog', 'panel', 'view', 'ui']):
        return 'View'

    return 'Other'


# ═══════════════════════════════════════════════════════════════
# Markdown 输出
# ═══════════════════════════════════════════════════════════════

def to_markdown(result: Dict, title: str = "Project Overview",
                max_funcs: int = 8) -> str:
    """将扫描结果格式化为 Markdown 报告，适合直接插入综设报告。

    Args:
        result: scan_python_project() 的返回值
        title: 报告标题
        max_funcs: 每个模块最多显示的函数数

    Returns:
        Markdown 字符串
    """
    overview = result['overview']
    modules = result['modules']
    stats = overview.stats

    lines = []
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"**{overview.name}** | "
                 f"{overview.total_files} 文件 | "
                 f"{stats.total_lines} 行 | "
                 f"代码 {stats.code_lines} | "
                 f"注释 {stats.comment_lines}"
                 f"（中文 {stats.chinese_comment_lines}）")
    lines.append("")

    # 按分类汇总
    from collections import Counter
    cat_counts = Counter(m.category for m in modules)
    parts = [f"{cat}: {cnt}" for cat, cnt in cat_counts.most_common()]
    lines.append(f"**模块分类**: {' | '.join(parts)}")
    lines.append("")

    # 详细表
    lines.append("| 分类 | 文件 | 行数 | 类 | 函数 |")
    lines.append("|------|------|------|-----|------|")
    for m in sorted(modules, key=lambda m: (m.category, m.name)):
        funcs = m.functions[:max_funcs]
        func_str = ', '.join(funcs) if funcs else '-'
        if len(m.functions) > max_funcs:
            func_str += f" ... (+{len(m.functions) - max_funcs})"
        lines.append(
            f"| {m.category} | `{m.file_path}` | {m.line_count} | "
            f"{', '.join(m.classes) if m.classes else '-'} | "
            f"{func_str} |"
        )

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI 入口: python -m uestc_doc.extractors.python_scanner <project_dir>"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m uestc_doc.extractors.python_scanner <project_dir> [--md] [--all]")
        print("  --md  输出 Markdown 格式")
        print("  --all 包含 __init__.py")
        sys.exit(1)

    root_dir = sys.argv[1]
    fmt = 'md' if '--md' in sys.argv else 'text'
    skip_init = '--all' not in sys.argv

    result = scan_python_project(root_dir, skip_init=skip_init)
    overview = result['overview']
    modules = result['modules']
    stats = overview.stats

    if fmt == 'md':
        print(to_markdown(result, title=f"{overview.name} 源码分析"))
    else:
        print(f"=== {overview.name} ===")
        print(f"Files: {overview.total_files}, Lines: {stats.total_lines}")
        print(f"Code: {stats.code_lines}, Comments: {stats.comment_lines}, "
              f"Chinese: {stats.chinese_comment_lines}")
        from collections import Counter
        cat_counts = Counter(m.category for m in modules)
        print(f"Categories: {dict(cat_counts)}")
        for m in modules:
            funcs = ', '.join(m.functions[:6])
            print(f"  [{m.category}] {m.name} ({m.file_path}) "
                  f"L={m.line_count} C={len(m.classes)} F={len(m.functions)}")


if __name__ == '__main__':
    main()
