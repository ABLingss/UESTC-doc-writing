"""
mmdc CLI 渲染器 — 使用 @mermaid-js/mermaid-cli。

需要: npm install -g @mermaid-js/mermaid-cli
"""

import subprocess
import shutil
import tempfile
import os
from typing import Optional


def is_mmdc_available() -> bool:
    """检测 mmdc 是否在 PATH 中。"""
    return shutil.which('mmdc') is not None


def render_via_mmdc(mmd_source: str, output_path: str,
                    scale: int = 2, theme: str = "default",
                    width: int = None, height: int = None,
                    puppeteer_config: str = None,
                    **kwargs) -> Optional[str]:
    """通过 mmdc CLI 渲染 Mermaid 图为 PNG。

    Args:
        mmd_source: Mermaid 源码
        output_path: 输出 PNG 路径
        scale: 缩放倍数
        theme: 主题
        width: 宽度 (px)
        height: 高度 (px)
        puppeteer_config: Puppeteer 配置 JSON 路径

    Returns:
        成功返回 output_path, 失败返回 None
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd',
                                     delete=False,
                                     encoding='utf-8') as f:
        f.write(mmd_source)
        tmp_mmd = f.name

    try:
        cmd = ['mmdc', '-i', tmp_mmd, '-o', output_path,
               '-s', str(scale), '-t', theme]

        if width:
            cmd.extend(['-w', str(width)])
        if height:
            cmd.extend(['-H', str(height)])
        if puppeteer_config:
            cmd.extend(['-p', puppeteer_config])

        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=60)
        if result.returncode != 0:
            print(f"[mmdc] Render failed: {result.stderr}")
            return None

        return output_path if os.path.exists(output_path) else None

    except FileNotFoundError:
        print("[mmdc] mmdc not found. Install: npm install -g @mermaid-js/mermaid-cli")
        return None
    except subprocess.TimeoutExpired:
        print("[mmdc] Render timed out (>60s)")
        return None
    except Exception as e:
        print(f"[mmdc] Error: {e}")
        return None
    finally:
        if os.path.exists(tmp_mmd):
            os.unlink(tmp_mmd)
