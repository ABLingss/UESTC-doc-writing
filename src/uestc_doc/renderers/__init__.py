"""
Mermaid 图渲染器 — 三种策略，按优先级自动降级:

1. mmdc_cli    — @mermaid-js/mermaid-cli (本地, 高质量, 需 npm install)
2. mermaid_ink — mermaid.ink HTTP API (零依赖, 需网络)
3. pure_python — Pillow 手动绘制 (纯Python, 离线可用, 最简图)

Usage:
    from uestc_doc.renderers import render_mermaid, RendererType

    # 自动选择最佳可用渲染器
    path = render_mermaid(mmd_source, "output/diagram.png")

    # 指定渲染器
    path = render_mermaid(mmd_source, "output/diagram.png",
                          renderer=RendererType.MMDC)
"""

from .mermaid_ink import render_via_ink, is_ink_available
from .mmdc_cli import render_via_mmdc, is_mmdc_available
from .pure_python import render_via_pillow, is_pillow_available

# ═══════════════════════════════════════════════════════════════
# 统一接口
# ═══════════════════════════════════════════════════════════════

from enum import Enum
from typing import Optional, Dict
import os


class RendererType(Enum):
    AUTO = "auto"
    MMDC = "mmdc"
    INK = "ink"
    PILLOW = "pillow"


_RENDERERS = {
    RendererType.MMDC: (render_via_mmdc, is_mmdc_available),
    RendererType.INK: (render_via_ink, is_ink_available),
    RendererType.PILLOW: (render_via_pillow, is_pillow_available),
}


def _detect_best_renderer() -> RendererType:
    """检测最佳可用渲染器 (mmdc > ink > pillow)。"""
    for rtype in [RendererType.MMDC, RendererType.INK, RendererType.PILLOW]:
        _, checker = _RENDERERS[rtype]
        if checker():
            return rtype
    return RendererType.PILLOW  # 总是可用


def render_mermaid(mmd_source: str, output_path: str,
                   renderer: RendererType = RendererType.AUTO,
                   scale: int = 2,
                   theme: str = "default",
                   **kwargs) -> Optional[str]:
    """渲染 Mermaid 图为 PNG。

    Args:
        mmd_source: Mermaid 源码字符串 或 .mmd 文件路径
        output_path: 输出 PNG 路径
        renderer: 渲染器类型 (AUTO 自动选择)
        scale: 缩放倍数 (仅 ink/mmdc 有效)
        theme: Mermaid 主题 (default/forest/neutral)
        **kwargs: 传递给具体渲染器的额外参数

    Returns:
        成功返回 output_path，失败返回 None

    Raises:
        RuntimeError: 所有渲染器均不可用
    """
    # 如果 mmd_source 是文件路径, 读取内容
    if os.path.exists(mmd_source) and '\n' not in mmd_source:
        with open(mmd_source, 'r', encoding='utf-8') as f:
            mmd_source = f.read()

    if renderer == RendererType.AUTO:
        renderer = _detect_best_renderer()

    render_func, _ = _RENDERERS.get(renderer, (None, None))
    if render_func is None:
        raise ValueError(f"Unknown renderer: {renderer}")

    return render_func(mmd_source, output_path, scale=scale, theme=theme,
                       **kwargs)


def render_mermaid_batch(mmd_files: Dict[str, str],
                         output_dir: str,
                         renderer: RendererType = RendererType.AUTO,
                         **kwargs) -> Dict[str, Optional[str]]:
    """批量渲染 Mermaid 图。

    Args:
        mmd_files: {name: mmd_source} 字典
        output_dir: 输出目录
        renderer: 渲染器
        **kwargs: 传给 render_mermaid

    Returns:
        {name: output_path_or_None}
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    for name, source in mmd_files.items():
        out_path = os.path.join(output_dir, f"{name}.png")
        results[name] = render_mermaid(source, out_path, renderer=renderer,
                                       **kwargs)
    return results
