import base64
import re
import os


def img_to_data_url(png_path):
    with open(png_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/png;base64,{data}'


def convert_markdown_to_html(md_text, image_map):
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_code = False
    table_header_done = False

    def close_table():
        nonlocal in_table, table_header_done
        if in_table:
            html_lines.append('</tbody></table>')
            in_table = False
            table_header_done = False

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                html_lines.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Horizontal rule
        if line.strip() == '---':
            close_table()
            html_lines.append('<hr/>')
            continue

        # Headings
        if line.startswith('# '):
            close_table()
            html_lines.append(f'<h1>{inline_format(line[2:])}</h1>')
            continue
        if line.startswith('## '):
            close_table()
            html_lines.append(f'<h2>{inline_format(line[3:])}</h2>')
            continue

        # Images
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            close_table()
            alt = img_match.group(1)
            src = img_match.group(2)
            data_url = None
            for key, url in image_map.items():
                if key in src:
                    data_url = url
                    break
            if data_url:
                html_lines.append(f'<p><img src="{data_url}" alt="{alt}" style="width:100%;max-width:640px;display:block;margin:20px auto;"/></p>')
            else:
                html_lines.append(f'<p>{alt}</p>')
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not in_table:
                html_lines.append('<table style="width:100%;border-collapse:collapse;margin:16px 0;">')
                in_table = True
                table_header_done = False
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            if not table_header_done:
                html_lines.append('<thead><tr>')
                for c in cells:
                    html_lines.append(f'<th style="border:1px solid #ddd;padding:8px;text-align:left;background:#f5f5f5;">{inline_format(c)}</th>')
                html_lines.append('</tr></thead><tbody>')
                table_header_done = True
            else:
                html_lines.append('<tr>')
                for c in cells:
                    html_lines.append(f'<td style="border:1px solid #ddd;padding:8px;text-align:left;">{inline_format(c)}</td>')
                html_lines.append('</tr>')
            continue
        else:
            close_table()

        # Blockquotes
        if line.startswith('> '):
            html_lines.append(f'<blockquote style="border-left:4px solid #ddd;padding:8px 16px;margin:16px 0;color:#666;">{inline_format(line[2:])}</blockquote>')
            continue

        # Ordered list items
        ol_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if ol_match:
            html_lines.append(f'<p style="margin:8px 0;padding-left:24px;">{ol_match.group(1)}. {inline_format(ol_match.group(2))}</p>')
            continue

        # Unordered list items
        if line.startswith('- '):
            html_lines.append(f'<p style="margin:8px 0;padding-left:24px;">• {inline_format(line[2:])}</p>')
            continue

        # Empty line
        if not line.strip():
            continue

        # Regular paragraph
        html_lines.append(f'<p style="margin:16px 0;line-height:1.75;">{inline_format(line)}</p>')

    if in_table:
        html_lines.append('</tbody></table>')
    if in_code:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def inline_format(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em;">\1</code>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color:#576b95;text-decoration:none;">\1</a>', text)
    return text
