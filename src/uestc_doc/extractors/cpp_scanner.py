"""
C/C++ 项目扫描器 — 提取编译模块/Pass信息、文件头注释、中文注释统计。

适用于:
- 编译器项目 (识别 Analysis/Transform Pass)
- 任何 C/C++ 项目 (提取函数声明、模块结构)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import os
import re
import json

from .common import CodeStats, ProjectOverview, scan_project


@dataclass
class CppPassInfo:
    """C/C++ 模块/Pass 信息。"""
    name: str = ""               # 类名或函数名
    file_path: str = ""          # 源文件路径
    header_path: str = ""        # 头文件路径
    category: str = "Other"      # 分类: Analysis/Transform/Scalar/...
    description: str = ""        # 从注释提取的描述
    algorithm: str = ""          # 算法说明
    complexity: str = ""         # 时间复杂度
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他Pass
    line_count: int = 0


# 默认分类词典 — 可按需覆盖
DEFAULT_PASS_CATEGORIES = {
    # Analysis
    'dominant': 'Analysis', 'dominance': 'Analysis',
    'loopinfo': 'Analysis', 'loop': 'Analysis',
    'alias': 'Analysis', 'aliastest': 'Analysis',
    'sideeffect': 'Analysis', 'effect': 'Analysis',
    'postdominant': 'Analysis', 'rangeanalysis': 'Analysis',
    'range': 'Analysis', 'lazyvalue': 'Analysis',
    'scev': 'Analysis', 'scalar': 'Analysis',

    # Transform - Scalar
    'mem2reg': 'Scalar', 'promote': 'Scalar',
    'dce': 'Scalar', 'deadcode': 'Scalar',
    'adce': 'DeadCode', 'aggressive': 'DeadCode',
    'dae': 'Scalar', 'deadarg': 'Scalar',
    'sccp': 'Scalar', 'constantprop': 'Scalar',
    'tailrecursion': 'Scalar', 'tail': 'Scalar',
    'funcinline': 'Scalar', 'inline': 'Scalar',

    # Transform - ControlFlow
    'cfgsimplify': 'ControlFlow', 'cfg': 'ControlFlow',
    'ifconversion': 'ControlFlow', 'ifconv': 'ControlFlow',
    'breakcritical': 'ControlFlow',
    'unifyexit': 'ControlFlow',

    # Transform - Redundancy
    'gvn': 'Redundancy', 'gvnpre': 'Redundancy',
    'pre': 'Redundancy',
    'instsimplify': 'Redundancy', 'simplify': 'Redundancy',
    'reassociate': 'Redundancy', 'reassoc': 'Redundancy',

    # Transform - Memory
    'loadelimination': 'Memory', 'loadelim': 'Memory',
    'dse': 'Memory', 'deadstore': 'Memory',
    'gep': 'Memory', 'gepevaluate': 'Memory',
    'gepcombine': 'Memory',
    'storeonlyglobal': 'Memory', 'soge': 'Memory',

    # Transform - Loop
    'loopsimplify': 'Loop', 'lcssa': 'Loop',
    'looprotate': 'Loop', 'licm': 'Loop',
    'loopdeletion': 'Loop',

    # Transform - Advanced
    'rangeaware': 'Advanced', 'rangeawareness': 'Advanced',
    'constraint': 'Advanced', 'constraintelim': 'Advanced',
    'constanthoist': 'Advanced', 'hoist': 'Advanced',

    # Global
    'module': 'Global', 'function': 'Framework',
    'passmanager': 'Framework', 'passbuilder': 'Framework',
    'pipeline': 'Framework', 'pipelinebuilder': 'Framework',
}

# 需要排除的路径模式
DEFAULT_EXCLUDE = [
    'test', 'tests', 'unittest', 'benchmark',
    'build', 'cmake-build', 'out', '.git',
    'third_party', 'thirdparty', 'vendor',
    '__pycache__', 'node_modules',
]


def scan_cpp_project(root_dir: str,
                     include_dirs: List[str] = None,
                     pass_categories: Dict[str, str] = None,
                     exclude_patterns: List[str] = None
                     ) -> Dict:
    """扫描 C/C++ 项目，提取所有信息。

    Args:
        root_dir: 项目根目录
        include_dirs: 要扫描的子目录 (相对于 root_dir)
        pass_categories: Pass名 → 分类 的映射字典
        exclude_patterns: 排除目录名列表

    Returns:
        {
            'overview': ProjectOverview,
            'passes': [CppPassInfo, ...],
            'headers': {file: header_comment_text},
        }
    """
    if pass_categories is None:
        pass_categories = DEFAULT_PASS_CATEGORIES
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE

    src_dir = root_dir
    if include_dirs:
        search_paths = [os.path.join(root_dir, d) for d in include_dirs]
    else:
        search_paths = [root_dir]

    overview = ProjectOverview(
        name=os.path.basename(os.path.abspath(root_dir)),
        language='C++',
    )
    passes = []
    headers = {}
    stats = CodeStats()

    for search_path in search_paths:
        if not os.path.isdir(search_path):
            continue

        for dirpath, dirnames, filenames in os.walk(search_path):
            dirnames[:] = [d for d in dirnames
                          if not any(p in d.lower()
                                     for p in exclude_patterns)]

            rel_dir = os.path.relpath(dirpath, root_dir)

            for fname in sorted(filenames):
                if not (fname.endswith('.cpp') or fname.endswith('.cc') or
                        fname.endswith('.cxx') or fname.endswith('.hpp') or
                        fname.endswith('.h') or fname.endswith('.hxx')):
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
                stats = _update_stats(stats, lines)
                overview.structure.append(rel_path)

                # 提取文件头注释
                header_comment = _extract_header_comment(lines)
                if header_comment:
                    headers[rel_path] = header_comment

                # 识别 Pass/模块
                file_passes = _identify_passes(lines, rel_path,
                                               pass_categories)
                passes.extend(file_passes)

    # 建立依赖关系
    passes = _resolve_dependencies(passes)

    overview.stats = stats
    overview.total_lines = stats.total_lines
    overview.total_files = stats.total_files

    return {
        'overview': overview,
        'passes': [p.__dict__ for p in passes],
        'headers': headers,
    }


def _update_stats(stats: CodeStats, lines: List[str]) -> CodeStats:
    """更新统计信息。"""
    stats.total_files += 1
    stats.total_lines += len(lines)
    in_block = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            stats.blank_lines += 1
            continue
        if in_block:
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            if '*/' in stripped:
                in_block = False
            continue
        if stripped.startswith('/*'):
            in_block = True
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            if '*/' in stripped:
                in_block = False
            continue
        if stripped.startswith('//'):
            stats.comment_lines += 1
            if _has_chinese(stripped):
                stats.chinese_comment_lines += 1
            continue
        stats.code_lines += 1
    return stats


def _has_chinese(text: str) -> bool:
    return bool(re.search(r'[一-鿿]', text))


def _extract_header_comment(lines: List[str]) -> Optional[str]:
    """提取文件顶部块注释。"""
    comment_lines = []
    in_comment = False
    for line in lines[:50]:
        stripped = line.strip()
        if stripped.startswith('/*') or stripped.startswith('/**'):
            in_comment = True
            comment_lines.append(stripped)
            if '*/' in stripped:
                break
            continue
        if in_comment:
            comment_lines.append(stripped)
            if '*/' in stripped:
                break
            continue
        if not stripped and not in_comment:
            continue
        if not in_comment:
            break
    return '\n'.join(comment_lines) if comment_lines else None


def _identify_passes(lines: List[str], file_path: str,
                     categories: Dict) -> List[CppPassInfo]:
    """识别文件中的 Pass/模块类。"""
    found = []
    content = '\n'.join(lines)

    # 查找类定义
    class_pattern = re.compile(
        r'//\s*(.*?)\n\s*class\s+(\w+)\s*:?\s*public\s+(\w+)',
        re.MULTILINE
    )
    for m in class_pattern.finditer(content):
        desc = m.group(1).strip()
        class_name = m.group(2)
        base = m.group(3)

        category = 'Other'
        name_lower = class_name.lower()
        for key, cat in categories.items():
            if key in name_lower:
                category = cat
                break

        found.append(CppPassInfo(
            name=class_name,
            file_path=file_path,
            category=category,
            description=desc,
            line_count=len(lines),
        ))

    # 查找独立函数 (run/execute/optimize)
    func_pattern = re.compile(
        r'//\s*(.*?)\n\s*(?:virtual\s+)?(?:void|bool|int|auto)\s+'
        r'(\w*(?:run|pass|optimize|transform|analyse|execute)\w*)\s*\(',
        re.MULTILINE | re.IGNORECASE
    )
    for m in func_pattern.finditer(content):
        desc = m.group(1).strip()
        func_name = m.group(2)

        category = 'Other'
        for key, cat in categories.items():
            if key in func_name.lower():
                category = cat
                break

        found.append(CppPassInfo(
            name=func_name,
            file_path=file_path,
            category=category,
            description=desc,
            line_count=len(lines),
        ))

    return found


def _resolve_dependencies(passes: List[CppPassInfo]) -> List[CppPassInfo]:
    """建立 Pass 间的依赖关系。"""
    names = {p.name for p in passes}
    for p in passes:
        deps = []
        for other in names:
            if other != p.name and other.lower() in p.description.lower():
                deps.append(other)
        p.dependencies = deps
    return passes
