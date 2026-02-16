#!/bin/bash
# CoPaw 博客截图脚本 - 需先安装: pip install playwright && playwright install chromium
# 运行: bash copaw/scripts/capture_screenshots.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$(dirname "$SCRIPT_DIR")/images"
PYTHON_SCRIPT="$(dirname "$(dirname "$SCRIPT_DIR")")/.cursor/skills/tech-blog-generator/tools/capture_screenshots.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "Error: capture_screenshots.py not found at $PYTHON_SCRIPT"
  exit 1
fi

python3 "$PYTHON_SCRIPT" -o "$OUTPUT_DIR" --tasks '[
  {"url": "https://copaw.agentscope.io/", "name": "copaw_homepage", "wait_seconds": 5, "scrolls": [0, 1], "scroll_names": ["hero", "features"]},
  {"url": "https://openclaw.ai/", "name": "openclaw_homepage", "wait_seconds": 5, "scrolls": [0, 1], "scroll_names": ["hero", "features"]},
  {"url": "https://github.com/openclaw/openclaw", "name": "openclaw_github", "wait_seconds": 4, "scrolls": [0, 1], "scroll_names": ["header", "readme"]},
  {"url": "https://www.ithome.com/0/921/812.htm", "name": "ithome_copaw", "wait_seconds": 4, "scrolls": [0], "scroll_names": ["article"]}
]'

echo ""
echo "截图已保存到: $OUTPUT_DIR"
