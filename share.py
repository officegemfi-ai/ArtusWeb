"""Link-preview image (1200 x 630) in the new look: the forest globe, the logo and the headline in Archivo."""
import base64, io, os
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.environ.get('TREKSTONE_SITE', '/home/claude/artusweb')
b64 = lambda f: base64.b64encode(open(f, 'rb').read()).decode()
logo = open(HERE + '/brand/trekstone-logo-white.svg', encoding='utf-8').read()
font = b64(HERE + '/vendor/node_modules/@fontsource-variable/archivo/files/archivo-latin-wdth-normal.woff2')
img = b64(REPO + '/assets/img/hero-globe-1920.webp')
html = f'''<html><head><style>@font-face{{font-family:Archivo;src:url(data:font/woff2;base64,{font}) format("woff2");font-weight:100 900;font-stretch:62% 125%}}</style></head>
<body style="margin:0;width:1200px;height:630px;background:#0C0C0C;color:#fff;font-family:Archivo;position:relative;overflow:hidden">
<img src="data:image/webp;base64,{img}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:30% 42%">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,10,10,.72) 0%,rgba(10,10,10,.45) 42%,rgba(10,10,10,0) 72%)"></div>
<div style="position:absolute;left:80px;top:72px;width:236px">{logo}</div>
<div style="position:absolute;left:80px;bottom:80px;right:80px">
<p style="margin:0;font-size:15px;line-height:20px;font-weight:700;font-stretch:116%;letter-spacing:.16em;text-transform:uppercase;color:#6FA88A">Responsible inventory management</p>
<div style="width:80px;height:4px;margin-top:26px;background:#3A7658"></div>
<h1 style="margin:32px 0 0;font-size:62px;line-height:1.04;font-weight:300;font-stretch:125%;letter-spacing:.004em;text-transform:uppercase">Excess inventory,<br>under your<br>control.</h1>
</div></body></html>'''
with sync_playwright() as pw:
    br = pw.chromium.launch(); p = br.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    p.set_content(html); p.wait_for_timeout(900); png = p.screenshot(); br.close()
im = Image.open(io.BytesIO(png)).convert('RGB'); out = REPO + '/assets/img/share.jpg'
im.save(out, 'JPEG', quality=86, optimize=True, progressive=True); im.save(HERE + '/shots/share.png'); print(out, os.path.getsize(out), im.size)
