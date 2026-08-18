#!/usr/bin/env python3
"""Generate architecture and workflow diagrams as SVG, then convert to PNG."""

import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Architecture Diagram
# ---------------------------------------------------------------------------

def build_architecture_svg() -> str:
    W, H = 1200, 820
    layers = [
        {
            "label": "Scripts Layer",
            "color": "#3B82F6",       # blue-500
            "bg": "#EFF6FF",           # blue-50
            "border": "#93C5FD",       # blue-300
            "boxes": ["cli.py", "server.py", "trade.py"],
        },
        {
            "label": "Application Layer",
            "color": "#8B5CF6",       # violet-500
            "bg": "#F5F3FF",           # violet-50
            "border": "#C4B5FD",       # violet-300
            "boxes": ["Trader", "Executor", "Prompter"],
        },
        {
            "label": "Connectors Layer",
            "color": "#10B981",       # emerald-500
            "bg": "#ECFDF5",           # emerald-50
            "border": "#6EE7B7",       # emerald-300
            "boxes": ["Chroma", "News", "Search"],
        },
        {
            "label": "APIs Layer",
            "color": "#F59E0B",       # amber-500
            "bg": "#FFFBEB",           # amber-50
            "border": "#FCD34D",       # amber-300
            "boxes": ["Polymarket", "Gamma"],
        },
    ]

    layer_h = 130
    gap = 38
    start_y = 80
    layer_w = 960
    layer_x = (W - layer_w) / 2  # centered

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica Neue, Arial, sans-serif">',
        # white background
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        # title
        f'<text x="{W/2}" y="42" text-anchor="middle" font-size="24" '
        f'font-weight="700" fill="#1E293B">Polymarket Agents \u2014 Architecture Overview</text>',
    ]

    for i, layer in enumerate(layers):
        y = start_y + i * (layer_h + gap)

        # layer background
        parts.append(
            f'<rect x="{layer_x}" y="{y}" width="{layer_w}" height="{layer_h}" '
            f'rx="14" ry="14" fill="{layer["bg"]}" stroke="{layer["border"]}" stroke-width="2"/>'
        )

        # layer label (left side, vertical text area)
        label_x = layer_x + 22
        parts.append(
            f'<text x="{label_x}" y="{y + layer_h/2}" text-anchor="start" '
            f'font-size="15" font-weight="700" fill="{layer["color"]}">{layer["label"]}</text>'
        )

        # inner boxes
        n = len(layer["boxes"])
        box_w = 200
        box_h = 64
        total_boxes_w = n * box_w + (n - 1) * 30
        boxes_start_x = layer_x + layer_w - total_boxes_w - 30
        box_y = y + (layer_h - box_h) / 2

        for j, box_label in enumerate(layer["boxes"]):
            bx = boxes_start_x + j * (box_w + 30)
            parts.append(
                f'<rect x="{bx}" y="{box_y}" width="{box_w}" height="{box_h}" '
                f'rx="10" ry="10" fill="#FFFFFF" stroke="{layer["color"]}" stroke-width="2"/>'
            )
            # box label
            parts.append(
                f'<text x="{bx + box_w/2}" y="{box_y + box_h/2 + 6}" '
                f'text-anchor="middle" font-size="17" font-weight="600" fill="#334155">'
                f'{box_label}</text>'
            )

        # vertical arrow to next layer
        if i < len(layers) - 1:
            arrow_x = W / 2
            arrow_top = y + layer_h
            arrow_bottom = arrow_top + gap
            parts.append(_arrow_down(arrow_x, arrow_top, arrow_bottom, "#64748B"))

    parts.append('</svg>')
    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# Workflow Diagram
# ---------------------------------------------------------------------------

def build_workflow_svg() -> str:
    W, H = 640, 1080
    steps = [
        {"num": 1, "title": "get_all_tradeable_events", "sub": "获取所有可交易事件"},
        {"num": 2, "title": "filter_events_with_rag", "sub": "RAG 筛选事件"},
        {"num": 3, "title": "map_filtered_events_to_markets", "sub": "映射到市场"},
        {"num": 4, "title": "filter_markets", "sub": "RAG 筛选市场"},
        {"num": 5, "title": "source_best_trade", "sub": "计算最佳交易",
         "sub_steps": ["retrieve_relevant_context", "generate_trade_decision"]},
        {"num": 6, "title": "execute_market_order", "sub": "执行交易"},
    ]

    box_w = 440
    box_h = 76
    gap = 44
    start_y = 70
    box_x = (W - box_w) / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica Neue, Arial, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        # title
        f'<text x="{W/2}" y="38" text-anchor="middle" font-size="22" '
        f'font-weight="700" fill="#1E293B">one_best_trade() Workflow</text>',
    ]

    cur_y = start_y
    arrow_color = "#64748B"

    # color palette for step boxes
    step_colors = [
        ("#3B82F6", "#EFF6FF", "#93C5FD"),  # blue
        ("#8B5CF6", "#F5F3FF", "#C4B5FD"),  # violet
        ("#10B981", "#ECFDF5", "#6EE7B7"),  # emerald
        ("#F59E0B", "#FFFBEB", "#FCD34D"),  # amber
        ("#EF4444", "#FEF2F2", "#FCA5A5"),  # red
        ("#0EA5E9", "#F0F9FF", "#7DD3FC"),  # sky
    ]

    for i, step in enumerate(steps):
        color, bg, border = step_colors[i]
        h = box_h
        # step 5 is taller to accommodate sub-steps
        if "sub_steps" in step:
            h = box_h + 70

        # main box
        parts.append(
            f'<rect x="{box_x}" y="{cur_y}" width="{box_w}" height="{h}" '
            f'rx="12" ry="12" fill="{bg}" stroke="{border}" stroke-width="2"/>'
        )

        # step number circle
        circle_cx = box_x + 32
        circle_cy = cur_y + 28
        parts.append(
            f'<circle cx="{circle_cx}" cy="{circle_cy}" r="16" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{circle_cx}" y="{circle_cy + 5}" text-anchor="middle" '
            f'font-size="15" font-weight="700" fill="#FFFFFF">{step["num"]}</text>'
        )

        # English title
        parts.append(
            f'<text x="{box_x + 60}" y="{cur_y + 33}" text-anchor="start" '
            f'font-size="16" font-weight="700" fill="#1E293B" '
            f'font-family="Menlo, Monaco, Courier New, monospace">{step["title"]}</text>'
        )

        # Chinese subtitle
        parts.append(
            f'<text x="{box_x + 60}" y="{cur_y + 55}" text-anchor="start" '
            f'font-size="13" fill="#64748B">{step["sub"]}</text>'
        )

        # sub-steps for step 5
        if "sub_steps" in step:
            sub_y = cur_y + 76
            parts.append(
                f'<line x1="{box_x + 30}" y1="{sub_y}" x2="{box_x + box_w - 30}" '
                f'y2="{sub_y}" stroke="{border}" stroke-width="1" stroke-dasharray="4,3"/>'
            )
            for k, sub_step in enumerate(step["sub_steps"]):
                sy = sub_y + 22 + k * 24
                parts.append(
                    f'<text x="{box_x + 50}" y="{sy}" text-anchor="start" '
                    f'font-size="13" fill="#475569" '
                    f'font-family="Menlo, Monaco, Courier New, monospace">'
                    f'\u2192 {sub_step}</text>'
                )

        cur_y += h

        # arrow to next step
        if i < len(steps) - 1:
            arrow_top = cur_y
            arrow_bottom = cur_y + gap
            parts.append(_arrow_down(W / 2, arrow_top, arrow_bottom, arrow_color))
            cur_y = arrow_bottom

    parts.append('</svg>')
    return '\n'.join(parts)


def _arrow_down(x: float, y_top: float, y_bottom: float, color: str) -> str:
    """Return SVG markup for a downward arrow."""
    head = 8
    return (
        f'<line x1="{x}" y1="{y_top}" x2="{x}" y2="{y_bottom - head}" '
        f'stroke="{color}" stroke-width="2.5"/>'
        f'<polygon points="{x},{y_bottom} {x - head},{y_bottom - head * 1.6} '
        f'{x + head},{y_bottom - head * 1.6}" fill="{color}"/>'
    )


# ---------------------------------------------------------------------------
# Convert SVG -> PNG
# ---------------------------------------------------------------------------

def svg_to_png(svg_path: Path, png_path: Path, scale: float = 2.0) -> None:
    """Convert SVG to high-res PNG using rsvg-convert."""
    # Read SVG dimensions from the file to compute scaled output size
    import re
    svg_text = svg_path.read_text(encoding="utf-8")
    m = re.search(r'width="(\d+)"\s+height="(\d+)"', svg_text)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        out_w, out_h = int(w * scale), int(h * scale)
        cmd = [
            "rsvg-convert",
            "-w", str(out_w),
            "-h", str(out_h),
            "-f", "png",
            "-o", str(png_path),
            str(svg_path),
        ]
    else:
        cmd = [
            "rsvg-convert",
            "-z", str(scale),
            "-f", "png",
            "-o", str(png_path),
            str(svg_path),
        ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main() -> None:
    diagrams = [
        ("architecture", build_architecture_svg),
        ("workflow", build_workflow_svg),
    ]

    for name, builder in diagrams:
        svg_path = OUTPUT_DIR / f"{name}.svg"
        png_path = OUTPUT_DIR / f"{name}.png"

        svg_content = builder()
        svg_path.write_text(svg_content, encoding="utf-8")
        print(f"  [OK] SVG written: {svg_path}")

        svg_to_png(svg_path, png_path, scale=2.0)
        print(f"  [OK] PNG written: {png_path}")

    print("\nAll diagrams generated successfully.")


if __name__ == "__main__":
    main()
