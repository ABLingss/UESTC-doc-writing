"""
通用代码扫描基础类型。
"""

from dataclasses import dataclass, field
from typing import List, Optional
import os
import re


@dataclass
class CodeStats:
    """代码统计信息。"""
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    chinese_comment_lines: int = 0
    total_files: int = 0


@dataclass
class ProjectOverview:
    """项目概览。"""
    name: str = ""
    language: str = ""
    total_lines: int = 0
    total_files: int = 0
    modules: List[str] = field(default_factory=list)
    stats: CodeStats = field(default_factory=CodeStats)
    structure: List[str] = field(default_factory=list)


def scan_project(root_dir: str, exts: List[str],
                 include_dirs: List[str] = None,
                 exclude_patterns: List[str] = None) -> ProjectOverview:
    """通用项目扫描器。

    Args:
        root_dir: 项目根目录
        exts: 文件扩展名列表, 如 ['.cpp', '.hpp']
        include_dirs: 限定扫描的子目录
        exclude_patterns: 排除的 glob 模式

    Returns:
        ProjectOverview
    """
    if exclude_patterns is None:
        exclude_patterns = ['test', 'build', '__pycache__', '.git',
                            'node_modules', 'third_party']

    overview = ProjectOverview(
        name=os.path.basename(os.path.abspath(root_dir)),
        language='+'.join(exts),
    )
    stats = CodeStats()
    structure = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 排除目录
        dirnames[:] = [d for d in dirnames
                       if not any(p in d.lower() for p in exclude_patterns)]

        rel_dir = os.path.relpath(dirpath, root_dir)
        if rel_dir == '.':
            rel_dir = ''

        for fname in sorted(filenames):
            if not any(fname.endswith(ext) for ext in exts):
                continue

            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, root_dir)

            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except Exception:
                continue

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

                # C 风格块注释开始
                if stripped.startswith('/*') or stripped.startswith('/**'):
                    in_block = True
                    stats.comment_lines += 1
                    if _has_chinese(stripped):
                        stats.chinese_comment_lines += 1
                    if '*/' in stripped:
                        in_block = False
                    continue

                # 行注释
                if (stripped.startswith('//') or
                    stripped.startswith('#') or
                    stripped.startswith('--')):
                    stats.comment_lines += 1
                    if _has_chinese(stripped):
                        stats.chinese_comment_lines += 1
                    continue

                stats.code_lines += 1

            structure.append(rel_path)

    overview.stats = stats
    overview.total_lines = stats.total_lines
    overview.total_files = stats.total_files
    overview.structure = structure
    return overview


def _has_chinese(text: str) -> bool:
    """检测是否包含中文字符。"""
    return bool(re.search(r'[一-鿿]', text))
