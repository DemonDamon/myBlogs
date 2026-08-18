import base64
import os
import re

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

H2 = '<h2 style="margin:36px 0 16px;font-size:20px;font-weight:700;color:#1f3a5f;line-height:1.4;border-left:5px solid #3b6fc9;padding-left:12px;">{}</h2>'
H3 = '<h3 style="margin:24px 0 12px;font-size:17px;font-weight:700;color:#2c4a7c;">{}</h3>'
P = '<p style="margin:16px 0;line-height:1.9;font-size:15.5px;color:#3e3e3e;">{}</p>'
BLOCKQUOTE = ('<blockquote style="margin:20px 0;padding:12px 16px;background:#f2f6fb;'
              'border-left:4px solid #3b6fc9;color:#555;font-size:14.5px;line-height:1.8;">{}</blockquote>')
OL = '<p style="margin:8px 0 8px 24px;line-height:1.9;font-size:15.5px;color:#3e3e3e;">{}. {}</p>'
UL = '<p style="margin:8px 0 8px 24px;line-height:1.9;font-size:15.5px;color:#3e3e3e;">• {}</p>'
IMG = ('<p style="text-align:center;margin:20px 0;"><img src="{}" alt="{}" '
       'style="width:100%;max-width:640px;display:inline-block;"/></p>')
PRE_OPEN = ('<pre style="background:#282c34;color:#abb2bf;padding:14px 16px;border-radius:6px;'
            'overflow-x:auto;font-size:13px;line-height:1.7;margin:16px 0;white-space:pre-wrap;">'
            '<code style="font-family:Menlo,Consolas,monospace;">')
PRE_CLOSE = '</code></pre>'
TD_STYLE = 'border:1px solid #dfe3e8;padding:9px 12px;text-align:left;font-size:14px;color:#3e3e3e;'
TH_STYLE = 'border:1px solid #dfe3e8;padding:9px 12px;text-align:left;font-size:14px;background:#eef3fa;color:#1f3a5f;font-weight:700;'


def img_to_data_url(png_path):
    with open(png_path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


def inline_format(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#1f3a5f;">\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`',
                  r'<code style="background:#f0f2f5;color:#c7254e;padding:2px 6px;border-radius:3px;'
                  r'font-size:0.9em;font-family:Menlo,Consolas,monospace;">\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)',
                  r'<a href="\2" style="color:#576b95;text-decoration:none;">\1</a>', text)
    return text


def close_table(html_lines, in_table):
    if in_table:
        html_lines.append('</tbody></table>')
    return False


def convert(md_text, image_map):
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_code = False
    table_header_done = False
    title_dropped = False

    for line in lines:
        if line.strip().startswith('```'):
            if in_code:
                html_lines.append(PRE_CLOSE)
                in_code = False
            else:
                html_lines.append(PRE_OPEN)
                in_code = True
            continue
        if in_code:
            html_lines.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        if line.strip() == '---':
            in_table = close_table(html_lines, in_table)
            table_header_done = False
            html_lines.append('<hr style="border:none;border-top:1px solid #e3e6ea;margin:28px 0;"/>')
            continue

        if line.startswith('# '):
            in_table = close_table(html_lines, in_table)
            if not title_dropped:
                title_dropped = True
                continue
            html_lines.append(f'<h1 style="margin:28px 0 16px;font-size:22px;font-weight:700;color:#1f3a5f;">{inline_format(line[2:])}</h1>')
            continue
        if line.startswith('## '):
            in_table = close_table(html_lines, in_table)
            html_lines.append(H2.format(inline_format(line[3:])))
            continue
        if line.startswith('### '):
            in_table = close_table(html_lines, in_table)
            html_lines.append(H3.format(inline_format(line[4:])))
            continue

        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            in_table = close_table(html_lines, in_table)
            alt, src = img_match.group(1), img_match.group(2)
            data_url = ''
            for key in ('decision-chain', 'architecture', 'comparison'):
                if key in src:
                    data_url = image_map.get(key, '')
                    break
            if data_url:
                html_lines.append(IMG.format(data_url, alt))
            else:
                html_lines.append(P.format(f'<em>{alt}</em>'))
            continue

        if line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not in_table:
                html_lines.append('<table style="width:100%;border-collapse:collapse;margin:18px 0;">')
                in_table = True
                table_header_done = False
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            if not table_header_done:
                html_lines.append('<thead><tr>')
                for c in cells:
                    html_lines.append(f'<th style="{TH_STYLE}">{inline_format(c)}</th>')
                html_lines.append('</tr></thead><tbody>')
                table_header_done = True
            else:
                html_lines.append('<tr>')
                for c in cells:
                    html_lines.append(f'<td style="{TD_STYLE}">{inline_format(c)}</td>')
                html_lines.append('</tr>')
            continue
        elif in_table:
            in_table = close_table(html_lines, in_table)
            table_header_done = False

        if line.startswith('> '):
            html_lines.append(BLOCKQUOTE.format(inline_format(line[2:])))
            continue

        ol_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if ol_match:
            html_lines.append(OL.format(ol_match.group(1), inline_format(ol_match.group(2))))
            continue

        if line.startswith('- '):
            html_lines.append(UL.format(inline_format(line[2:])))
            continue

        if not line.strip():
            continue

        html_lines.append(P.format(inline_format(line)))

    close_table(html_lines, in_table)
    if in_code:
        html_lines.append(PRE_CLOSE)

    return '\n'.join(html_lines)


image_map = {
    'comparison': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'comparison_wechat.png')),
    'architecture': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'architecture_wechat.png')),
    'decision-chain': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'decision-chain_wechat.png')),
}

with open(os.path.join(BLOG_DIR, 'blog.md'), encoding='utf-8') as f:
    md = f.read()

html = convert(md, image_map)
out = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
       '<title>final-paste</title></head><body>'
       '<div id="content" style="max-width:677px;margin:0 auto;'
       'font-size:16px;color:#3e3e3e;font-family:-apple-system,BlinkMacSystemFont,'
       '\'Helvetica Neue\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">'
       + html + '</div></body></html>')

with open(os.path.join(BLOG_DIR, 'final-paste.html'), 'w', encoding='utf-8') as f:
    f.write(out)

print('final-paste.html size:', len(out))
print('imgs embedded:', html.count('data:image/png;base64'))
