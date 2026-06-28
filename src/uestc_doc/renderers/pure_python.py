"""
纯 Python Mermaid 图渲染器 — 基于 Pillow。

简化版: 将 Mermaid 图转为基本的方框+箭头布局。
不解析完整 Mermaid 语法, 而是提供编程式绘图 API。

适用场景:
- 离线环境 (无网络 + 无 Node.js)
- CI 环境 (不想装 npm)
- 简单的流程图/类图/架构图

对于复杂图表, 建议使用 mermaid.ink 或 mmdc。
"""

import os
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont


def is_pillow_available() -> bool:
    """Pillow 总是可用 (作为核心依赖)。"""
    try:
        import PIL
        return True
    except ImportError:
        return False


# ═══════════════════════════════════════════════════════════════
# 字体查找
# ═══════════════════════════════════════════════════════════════

_FONT_CANDIDATES = [
    # macOS
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    # Windows
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/simsun.ttc',
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simfang.ttf',
    # Linux
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    # fallback via fc-list
]


def _find_cn_font():
    """查找系统中的中文字体。"""
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    # 尝试 fc-list
    import subprocess
    try:
        result = subprocess.run(
            ['fc-list', ':lang=zh', '-f', '%{file}\n'],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except Exception:
        pass
    # Pillow 默认字体
    return None


# ═══════════════════════════════════════════════════════════════
# 简易绘图引擎
# ═══════════════════════════════════════════════════════════════

def render_via_pillow(mmd_source: str, output_path: str,
                      scale: int = 2, theme: str = "default",
                      width: int = 1200, height: int = 900,
                      **kwargs) -> Optional[str]:
    """使用 Pillow 渲染简单图表。

    注意: 这是简化版, 仅支持 Mermaid graph TD/LR 的基本语法。
    对于 classDiagram/sequenceDiagram 等复杂图表, 请使用 mmdc 或 ink。

    Args:
        mmd_source: Mermaid 源码 (简化子集)
        output_path: 输出 PNG 路径
        scale: 缩放倍数
        width: 画布宽度
        height: 画布高度
        **kwargs: 额外参数

    Returns:
        成功返回 output_path, 失败返回 None
    """
    try:
        img = Image.new('RGB', (width * scale, height * scale), 'white')
        draw = ImageDraw.Draw(img)

        font_path = _find_cn_font()
        if font_path:
            font_lg = ImageFont.truetype(font_path, 16 * scale)
            font_sm = ImageFont.truetype(font_path, 12 * scale)
        else:
            font_lg = ImageFont.load_default()
            font_sm = ImageFont.load_default()

        # 解析 graph 类型
        lines = mmd_source.strip().split('\n')
        direction = 'TD'
        nodes = {}
        edges = []

        for line in lines:
            line = line.strip()
            if line.startswith('graph ') or line.startswith('flowchart '):
                parts = line.split()
                if len(parts) >= 2:
                    direction = parts[1].upper()
                continue
            if '-->' in line or '---' in line:
                arrow = '-->' if '-->' in line else '---'
                parts = line.split(arrow)
                if len(parts) == 2:
                    src = parts[0].strip()
                    dst = parts[1].strip().rstrip(';')
                    # 提取标签
                    src_label = src.split('[')[0].strip() if '[' in src else src
                    dst_label = dst.split('[')[0].strip() if '[' in dst else dst
                    src_text = _extract_label(src)
                    dst_text = _extract_label(dst)
                    nodes[src_label] = src_text
                    nodes[dst_label] = dst_text
                    edges.append((src_label, dst_label, arrow == '-->'))

        if not nodes:
            # 简单 fallback: 画一个带文字的方框
            draw.rectangle(
                [50 * scale, 50 * scale, (width - 50) * scale, (height - 50) * scale],
                outline='black', width=2 * scale
            )
            draw.text((width // 2 * scale, height // 2 * scale),
                      mmd_source[:200], fill='black', font=font_sm,
                      anchor='mm')
        else:
            # 简易布局
            node_list = list(nodes.keys())
            if direction in ('LR', 'RL'):
                cols = len(node_list)
                rows = 1
            else:
                cols = min(3, len(node_list))
                rows = (len(node_list) + cols - 1) // cols

            margin_x = 100 * scale
            margin_y = 80 * scale
            cell_w = (width - 2 * margin_x) // max(cols, 1)
            cell_h = min(120 * scale, (height - 2 * margin_y) // max(rows, 1))

            positions = {}
            for i, node_id in enumerate(node_list):
                if direction in ('LR', 'RL'):
                    r, c = 0, i
                else:
                    r, c = i // cols, i % cols
                x = margin_x + c * cell_w + cell_w // 4
                y = margin_y + r * cell_h + cell_h // 4
                positions[node_id] = (x, y)

                # 画方框
                label = nodes[node_id]
                tw = draw.textlength(label, font=font_sm)
                th = 20 * scale
                bx1 = x - tw // 2 - 10 * scale
                by1 = y - th // 2 - 5 * scale
                bx2 = x + tw // 2 + 10 * scale
                by2 = y + th // 2 + 5 * scale
                draw.rounded_rectangle(
                    [bx1, by1, bx2, by2],
                    radius=8 * scale, outline='#333333',
                    fill='#E8F0FE', width=2 * scale
                )
                draw.text((x, y), label, fill='#333333', font=font_sm,
                          anchor='mm')

            # 画边
            for src, dst, is_arrow in edges:
                if src in positions and dst in positions:
                    x1, y1 = positions[src]
                    x2, y2 = positions[dst]
                    draw.line([(x1, y1 + 20 * scale),
                               (x2, y2 - 20 * scale)],
                              fill='#666666', width=2 * scale)
                    if is_arrow:
                        # 简单箭头
                        draw.polygon(
                            [(x2, y2 - 20 * scale),
                             (x2 - 6 * scale, y2 - 28 * scale),
                             (x2 + 6 * scale, y2 - 28 * scale)],
                            fill='#666666'
                        )

        img = img.resize((width, height), Image.LANCZOS)
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        img.save(output_path, 'PNG')
        return output_path

    except Exception as e:
        print(f"[pillow] Render failed: {e}")
        return None


def _extract_label(node_str: str) -> str:
    """从节点定义中提取显示标签。"""
    node_str = node_str.strip()
    for delim_open, delim_close in [('[', ']'), ('{', '}'), ('(', ')'),
                                     ('>', ']')]:
        if delim_open in node_str and delim_close in node_str:
            start = node_str.index(delim_open) + 1
            end = node_str.rindex(delim_close)
            return node_str[start:end]
    return node_str
