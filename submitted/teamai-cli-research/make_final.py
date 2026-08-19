import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_html import convert_markdown_to_html, img_to_data_url

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

image_map = {
    'architecture': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'architecture.png')),
    'friction-flow': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'friction-flow.png')),
    'recall-pipeline': img_to_data_url(os.path.join(BLOG_DIR, 'images', 'recall-pipeline.png')),
}

with open(os.path.join(BLOG_DIR, 'blog.md'), encoding='utf-8') as f:
    md_text = f.read()

content_html = convert_markdown_to_html(md_text, image_map)

out = os.path.join(BLOG_DIR, 'final-paste.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>' + content_html + '</body></html>')

print(f'generated: {out} ({os.path.getsize(out)} bytes)')
print(f'img count: {content_html.count("<img")}')
