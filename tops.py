"""First screen of every page at one size, tiled. Usage: tops.py WIDTH HEIGHT"""
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
W, H = int(sys.argv[1]), int(sys.argv[2])
PAGES = ['index', 'brand-protection', 'how-it-works', 'sustainability', 'buyers', 'contact']
ims = []
with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=W < 700, has_touch=W < 1000); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)[:160]))
    p.route('**/*', lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort())
    for pg in PAGES:
        p.goto(f'http://127.0.0.1:8815/{pg}.html', wait_until='load'); p.wait_for_timeout(1500)
        f = f'{OUT}top-{pg}-{W}.png'; p.screenshot(path=f); ims.append(Image.open(f).convert('RGB'))
    ctx.close(); br.close()
cols = 3 if W > 700 else 6; rows = -(-len(ims) // cols); g = 14
s = Image.new('RGB', (cols * (W + g) + g, rows * (H + g) + g), '#999')
for i, im in enumerate(ims): s.paste(im, (g + (i % cols) * (W + g), g + (i // cols) * (H + g)))
s.save(f'{OUT}tops-{W}.png'); print(s.size, errs)
