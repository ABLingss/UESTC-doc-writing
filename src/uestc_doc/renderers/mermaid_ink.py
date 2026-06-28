"""
mermaid.ink HTTP API 渲染器 — 零本地依赖, 需要网络。

URL 格式: https://mermaid.ink/img/{base64(pako_deflate(mmd))}
"""

import base64
import zlib
import urllib.request
import os
from typing import Optional


def is_ink_available() -> bool:
    """检测 mermaid.ink 是否可达。"""
    try:
        req = urllib.request.Request("https://mermaid.ink/",
                                     method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def _encode_mermaid(mmd_source: str) -> str:
    """将 Mermaid 源码编码为 mermaid.ink URL 格式 (pako + base64)。"""
    # pako 兼容: raw deflate
    compressed = zlib.compress(mmd_source.encode('utf-8'))[2:-4]
    return base64.urlsafe_b64encode(compressed).decode('ascii')


def render_via_ink(mmd_source: str, output_path: str,
                   scale: int = 2, theme: str = "default",
                   bg_color: str = "white",
                   timeout: int = 30) -> Optional[str]:
    """通过 mermaid.ink API 渲染 Mermaid 图为 PNG。

    Args:
        mmd_source: Mermaid 源码
        output_path: 输出 PNG 路径
        scale: 缩放倍数 (1-3)
        theme: 主题 (default/forest/neutral/dark)
        bg_color: 背景色
        timeout: HTTP 超时秒数

    Returns:
        成功返回 output_path, 失败返回 None
    """
    # 包装主题
    themed = f"%%{{init: {{'theme': '{theme}'}}}}%%\n{mmd_source}"
    encoded = _encode_mermaid(themed)

    url = f"https://mermaid.ink/img/{encoded}?scale={scale}&bgColor={bg_color}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        # 如果返回太小, 可能是错误页
        if len(data) < 200:
            # 尝试不加 scale 重试
            url2 = f"https://mermaid.ink/img/{encoded}?bgColor={bg_color}"
            req2 = urllib.request.Request(url2)
            with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                data = resp2.read()

        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(data)
        return output_path

    except Exception as e:
        print(f"[mermaid.ink] Render failed: {e}")
        return None
