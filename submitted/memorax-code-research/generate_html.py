import base64
import re
import os

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

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
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_header_done = False
            html_lines.append('<hr/>')
            continue

        # Headings
        if line.startswith('# '):
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_header_done = False
            html_lines.append(f'<h1>{inline_format(line[2:])}</h1>')
            continue
        if line.startswith('## '):
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_header_done = False
            html_lines.append(f'<h2>{inline_format(line[3:])}</h2>')
            continue

        # Images
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_header_done = False
            alt = img_match.group(1)
            src = img_match.group(2)
            # Map to PNG data URL
            if 'architecture' in src:
                data_url = image_map.get('architecture')
            elif 'memory-lifecycle' in src:
                data_url = image_map.get('memory-lifecycle')
            elif 'data-flow' in src:
                data_url = image_map.get('data-flow')
            else:
                data_url = ''
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
                table_header_done = True
                continue
            tag = 'th' if not table_header_done else 'td'
            style = 'border:1px solid #ddd;padding:8px;text-align:left;' if tag == 'td' else 'border:1px solid #ddd;padding:8px;text-align:left;background:#f5f5f5;'
            if not table_header_done:
                html_lines.append('<thead><tr>')
                for c in cells:
                    html_lines.append(f'<{tag} style="{style}">{inline_format(c)}</{tag}>')
                html_lines.append('</tr></thead><tbody>')
                table_header_done = True
            else:
                html_lines.append('<tr>')
                for c in cells:
                    html_lines.append(f'<{tag} style="{style}">{inline_format(c)}</{tag}>')
                html_lines.append('</tr>')
            continue
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False
                table_header_done = False

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
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em;">\1</code>', text)
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color:#576b95;text-decoration:none;">\1</a>', text)
    return text

# Load images as data URLs
image_map = {
    'architecture': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'architecture_small.png')),
    'memory-lifecycle': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'memory-lifecycle_small.png')),
    'data-flow': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'data-flow_small.png')),
}

# Read blog.md
with open(os.path.join(BLOG_DIR, 'blog.md'), 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert to HTML
content_html = convert_markdown_to_html(md_text, image_map)

# Create full HTML page
full_html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Blog Content</title></head>
<body>
<div id="content" style="max-width:677px;margin:0 auto;font-size:16px;color:#333;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif;">
{content_html}
</div>
<script>
// Auto-select and copy content to clipboard
function copyToClipboard() {{
    var content = document.getElementById('content');
    var range = document.createRange();
    range.selectNodeContents(content);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    try {{
        document.execCommand('copy');
        document.title = 'COPIED_OK';
    }} catch(e) {{
        document.title = 'COPY_FAIL:' + e.message;
    }}
}}
// Auto-copy after page loads
setTimeout(copyToClipboard, 500);
</script>
</body>
</html>'''

# Save to file
output_path = os.path.join(BLOG_DIR, 'blog-with-images.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f'HTML generated: {output_path}')
print(f'File size: {os.path.getsize(output_path)} bytes')
