#!/usr/bin/env python3
"""
GPT-5.3-Codex vs Opus 4.6 - Cost Comparison Charts
创建详细的成本对比图表
"""

from PIL import Image, ImageDraw, ImageFont
import os

WIDTH = 3200
HEIGHT = 2400
DPI = 300

COLORS = {
    'bg': '#FAFAFA',
    'gpt_color': '#107C41',  # OpenAI Green
    'gpt_light': '#E8F5E9',
    'opus_color': '#D97706',  # Anthropic Orange
    'opus_light': '#FEF3C7',
    'text_primary': '#263238',
    'text_secondary': '#546E7A',
    'grid': '#E0E0E0',
}

FONT_DIR = './canvas-fonts'
FONT_REGULAR = os.path.join(FONT_DIR, 'InstrumentSans-Regular.ttf')
FONT_BOLD = os.path.join(FONT_DIR, 'InstrumentSans-Bold.ttf')

def create_cost_comparison():
    """创建成本对比图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(FONT_BOLD, 44)
        font_subtitle = ImageFont.truetype(FONT_BOLD, 28)
        font_label = ImageFont.truetype(FONT_REGULAR, 20)
        font_small = ImageFont.truetype(FONT_REGULAR, 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    title = "Token Cost Comparison: GPT-5.3-Codex vs Opus 4.6"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_x = (WIDTH - title_bbox[2]) // 2
    draw.text((title_x, 60), title, fill=COLORS['text_primary'], font=font_title)

    # Subtitle
    subtitle = "基于官方定价 | 2026年2月 | 单位: USD/1M tokens"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_x = (WIDTH - subtitle_bbox[2]) // 2
    draw.text((subtitle_x, 115), subtitle, fill=COLORS['text_secondary'], font=font_subtitle)

    # Pricing data
    models = [
        ("GPT-5 Mini", 0.025, 2.000, "极低成本"),
        ("GPT-5.2", 1.750, 14.000, "性价比标准"),
        ("Claude Haiku 4", 0.800, 4.000, "经济型"),
        ("Claude Sonnet 4.5", 3.000, 15.000, "平衡型"),
        ("Claude Opus 4.6", 15.000, 75.000, "旗舰深度"),
    ]

    y_start = 200
    row_height = 180
    max_bar_width = 1400

    for i, (name, input_price, output_price, desc) in enumerate(models):
        y = y_start + i * row_height

        # Background
        if i % 2 == 0:
            draw.rectangle([(100, y), (WIDTH - 100, y + row_height - 20)],
                           fill='#F5F5F5')

        # Model name
        draw.text((120, y + 25), name, fill=COLORS['text_primary'], font=font_label)
        draw.text((120, y + 50), desc, fill=COLORS['text_secondary'], font=font_small)

        # Input bar (scale to max $15)
        input_bar_width = int((input_price / 15.000) * max_bar_width)
        color = COLORS['gpt_color'] if 'GPT' in name else COLORS['opus_color']
        draw.rounded_rectangle([(800, y + 30), (800 + input_bar_width, y + 70)],
                              radius=6, fill=color)
        draw.text((800 + input_bar_width + 10, y + 35), f"${input_price:.3f}",
                 fill=color, font=font_label)

        # Output bar (scale to max $75)
        output_bar_width = int((output_price / 75.000) * max_bar_width)
        draw.rounded_rectangle([(800, y + 85), (800 + output_bar_width, y + 125)],
                              radius=6, fill=color)
        draw.text((800 + output_bar_width + 10, y + 90), f"${output_price:.3f}",
                 fill=color, font=font_label)

    # Legend
    legend_y = y_start + len(models) * row_height + 40
    draw.text((120, legend_y), "输入价格 (Input)", fill=COLORS['text_primary'], font=font_label)
    draw.text((120, legend_y + 30), "输出价格 (Output)", fill=COLORS['text_primary'], font=font_label)

    # Note
    note_y = legend_y + 80
    note = "注意: GPT-5.3-Codex 官方定价尚未公布 | Opus 4.6 与 Opus 4.5 定价相同"
    draw.text((120, note_y), note, fill=COLORS['text_secondary'], font=font_small)

    # Save
    output_path = '/Users/damon/myWork/myBlog/gpt5.3-codex和opus4.6/images/cost-comparison.png'
    img.save(output_path, 'PNG', quality=95, DPI=(DPI, DPI))
    print(f"Cost comparison chart saved to: {output_path}")

def create_efficiency_analysis():
    """创建效率分析图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(FONT_BOLD, 44)
        font_subtitle = ImageFont.truetype(FONT_BOLD, 28)
        font_label = ImageFont.truetype(FONT_REGULAR, 20)
        font_small = ImageFont.truetype(FONT_REGULAR, 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    title = "Token Efficiency & Cost Analysis"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_x = (WIDTH - title_bbox[2]) // 2
    draw.text((title_x, 60), title, fill=COLORS['text_primary'], font=font_title)

    # Subtitle
    subtitle = "GPT-5.3-Codex 效率提升带来的实际成本降低"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_x = (WIDTH - subtitle_bbox[2]) // 2
    draw.text((subtitle_x, 115), subtitle, fill=COLORS['text_secondary'], font=font_subtitle)

    # Scenario: 1M token task
    y_start = 200
    y = y_start

    # Scenario description
    draw.text((120, y), "场景: 完成一个典型编程任务",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((120, y + 30), "传统模型需要: 100万输入 tokens + 50万输出 tokens",
             fill=COLORS['text_secondary'], font=font_small)

    y += 80

    # GPT-5.2 Baseline
    draw.rounded_rectangle([(120, y), (WIDTH - 120, y + 180)], radius=12,
                          fill=COLORS['gpt_light'], outline=COLORS['gpt_color'], width=2)
    draw.text((150, y + 20), "GPT-5.2 (基线)",
             fill=COLORS['gpt_color'], font=font_subtitle)
    draw.text((150, y + 60), "Tokens: 100万输入 + 50万输出",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 90), f"成本: ${1.75:.2f} + ${7.00:.2f} = ${8.75:.2f}",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 130), "处理时间: 基线",
             fill=COLORS['text_secondary'], font=font_small)

    y += 220

    # GPT-5.3-Codex (50% efficiency)
    draw.rounded_rectangle([(120, y), (WIDTH - 120, y + 180)], radius=12,
                          fill=COLORS['gpt_light'], outline=COLORS['gpt_color'], width=3)
    draw.text((150, y + 20), "GPT-5.3-Codex (效率提升 50%)",
             fill=COLORS['gpt_color'], font=font_subtitle)
    draw.text((150, y + 60), "Tokens: 50万输入 + 25万输出 (减少50%)",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 90), f"成本: ${0.875:.2f} + ${3.50:.2f} = ${4.375:.2f} (节省50%)",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 130), "处理时间: 减少25% (速度提升)",
             fill=COLORS['text_secondary'], font=font_small)

    y += 220

    # Claude Opus 4.6
    draw.rounded_rectangle([(120, y), (WIDTH - 120, y + 180)], radius=12,
                          fill=COLORS['opus_light'], outline=COLORS['opus_color'], width=2)
    draw.text((150, y + 20), "Claude Opus 4.6 (长上下文优势)",
             fill=COLORS['opus_color'], font=font_subtitle)
    draw.text((150, y + 60), "Tokens: 可能需要更少tokens (1M上下文)",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 90), f"成本: ${15.00:.2f}/M输入 + ${75.00:.2f}/M输出",
             fill=COLORS['text_primary'], font=font_label)
    draw.text((150, y + 130), "优势: 100万token上下文, Agent Teams协作",
             fill=COLORS['text_secondary'], font=font_small)

    # Save
    output_path = '/Users/damon/myWork/myBlog/gpt5.3-codex和opus4.6/images/efficiency-analysis.png'
    img.save(output_path, 'PNG', quality=95, DPI=(DPI, DPI))
    print(f"Efficiency analysis chart saved to: {output_path}")

def create_scenario_cost():
    """创建场景成本对比图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(FONT_BOLD, 44)
        font_subtitle = ImageFont.truetype(FONT_BOLD, 28)
        font_label = ImageFont.truetype(FONT_REGULAR, 20)
        font_small = ImageFont.truetype(FONT_REGULAR, 16)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    title = "Real-World Scenario Cost Comparison"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_x = (WIDTH - title_bbox[2]) // 2
    draw.text((title_x, 60), title, fill=COLORS['text_primary'], font=font_title)

    # Subtitle
    subtitle = "实际使用场景成本对比 (月度使用: 220万输入 + 110万输出 tokens)"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_x = (WIDTH - subtitle_bbox[2]) // 2
    draw.text((subtitle_x, 115), subtitle, fill=COLORS['text_secondary'], font=font_subtitle)

    # Scenario data
    scenarios = [
        ("简单代码生成", "GPT-5 Mini", 2.26, COLORS['gpt_color']),
        ("日常编程", "GPT-5.2", 19.25, COLORS['gpt_color']),
        ("中型项目", "Claude Sonnet 4.5", 23.10, COLORS['opus_color']),
        ("大型复杂项目", "Claude Opus 4.6", 115.50, COLORS['opus_color']),
    ]

    y_start = 200
    row_height = 200
    max_bar_width = 1800

    for i, (scenario, model, cost, color) in enumerate(scenarios):
        y = y_start + i * row_height

        # Background
        if i % 2 == 0:
            draw.rectangle([(100, y), (WIDTH - 100, y + row_height - 20)],
                           fill='#F5F5F5')

        # Scenario and model
        draw.text((120, y + 25), scenario, fill=COLORS['text_primary'], font=font_label)
        draw.text((120, y + 55), model, fill=color, font=font_subtitle)

        # Cost bar
        bar_width = int((cost / 115.50) * max_bar_width)
        draw.rounded_rectangle([(800, y + 30), (800 + bar_width, y + 100)],
                              radius=8, fill=color)
        draw.text((800 + bar_width + 15, y + 50), f"${cost:.2f}",
                 fill=color, font=font_subtitle)
        draw.text((800 + bar_width + 15, y + 80), "/月",
                 fill=COLORS['text_secondary'], font=font_small)

        # Comparison
        if i > 0:
            base_cost = scenarios[0][2]
            ratio = cost / base_cost
            draw.text((120, y + 100), f"倍数: {ratio:.1f}x",
                     fill=COLORS['text_secondary'], font=font_small)

    # Save
    output_path = '/Users/damon/myWork/myBlog/gpt5.3-codex和opus4.6/images/scenario-cost.png'
    img.save(output_path, 'PNG', quality=95, DPI=(DPI, DPI))
    print(f"Scenario cost chart saved to: {output_path}")

if __name__ == '__main__':
    print("Creating cost comparison charts...")
    create_cost_comparison()
    create_efficiency_analysis()
    create_scenario_cost()
    print("All charts created successfully.")
