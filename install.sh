#!/usr/bin/env bash
# 综设.skill 一键安装脚本
# Usage: bash -c "$(curl -fsSL https://raw.githubusercontent.com/ABLingss/UESTC-doc-writing/main/install.sh)"

set -e

REPO="https://github.com/ABLingss/UESTC-doc-writing.git"
SKILL_NAME="uestc-doc-writing"

# Detect runtime skills directory
if [ -d "$HOME/.claude" ]; then
    SKILLS_DIR="$HOME/.claude/skills"
    RUNTIME="Claude Code"
elif [ -d "$HOME/.codex" ]; then
    SKILLS_DIR="$HOME/.codex/skills"
    RUNTIME="Codex"
elif [ -d "$HOME/.cursor" ]; then
    SKILLS_DIR="$HOME/.cursor/skills"
    RUNTIME="Cursor"
else
    SKILLS_DIR="$HOME/.claude/skills"
    RUNTIME="Claude Code"
fi

INSTALL_PATH="$SKILLS_DIR/$SKILL_NAME"

echo "╔══════════════════════════════════════════╗"
echo "║  综设.skill 一键安装                      ║"
echo "║  Runtime: $RUNTIME"
echo "╚══════════════════════════════════════════╝"

if [ -d "$INSTALL_PATH" ]; then
    echo "[1/2] Updating existing install..."
    cd "$INSTALL_PATH"
    git pull --ff-only
else
    echo "[1/2] Cloning..."
    mkdir -p "$SKILLS_DIR"
    git clone "$REPO" "$INSTALL_PATH"
fi

echo "[2/2] Installing Python dependencies..."
cd "$INSTALL_PATH"
pip install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q

echo ""
echo "✅ 安装完成！"
echo ""
echo "   Skill 路径: $INSTALL_PATH"
echo "   重启 $RUNTIME 后生效。"
echo ""
echo "   使用方式 — 直接对话："
echo "     「帮我生成一份综设中期报告」"
echo "     「给第三章加一个完成度评估表」"
echo ""
