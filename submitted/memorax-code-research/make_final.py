import base64
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_html import convert_markdown_to_html, img_to_data_url

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

CDN_ARCH = 'https://mmbiz.qpic.cn/mmbiz_png/2ibvEmypBbLfncVqicZYDJT13kSlVHHPSo8dictzuacMOYoib3vhIicdt5nZmBGicwIBArzzWznKhTlWtZJia3SmtYLvaiaBsK0NmIiaIyCGLlRwgyZc/640?wx_fmt=png&from=appmsg'
CDN_LIFECYCLE = 'https://mmbiz.qpic.cn/sz_mmbiz_png/2ibvEmypBbLfbnAPetjjiazhj62E8Hd3E0SDv3GM73OicJBGPr7eXH4ROpGOdiauyN9hz0fE8ghHwF6Cl6iaCxEnQOWhyD1D9cC7iaDPltGmZpyJQ/640?wx_fmt=png&from=appmsg'
DATAFLOW_B64 = img_to_data_url(os.path.join(BLOG_DIR, 'images', 'data-flow_small.png'))

image_map = {
    'architecture': CDN_ARCH,
    'memory-lifecycle': CDN_LIFECYCLE,
    'data-flow': DATAFLOW_B64,
}

with open(os.path.join(BLOG_DIR, 'blog.md'), 'r', encoding='utf-8') as f:
    md_text = f.read()

content_html = convert_markdown_to_html(md_text, image_map)

out = os.path.join(BLOG_DIR, 'final-paste.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(content_html)

print(f'generated: {out} ({os.path.getsize(out)} bytes)')
print(f'data url size: {len(DATAFLOW_B64)}')
print(f'img count: {content_html.count("<img")}')
