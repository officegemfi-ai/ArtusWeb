"""Full-page screenshot of one page, cut into columns. Usage: shot.py PAGE WIDTH [colheight]   (PAGE without .html)"""
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
PAGE, W = sys.argv[1], int(sys.argv[2]); COLH = int(sys.argv[3]) if len(sys.argv) > 3 else (1500 if W > 700 else 1700)
H = 900 if W > 700 else 844
with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=W < 700, has_touch=W < 1000, reduced_motion='reduce')
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
    p.route('**/*', lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort())
    p.goto(f'http://127.0.0.1:8815/{PAGE}.html', wait_until='load'); p.wait_for_timeout(700)
    Hh = p.evaluate('document.documentElement.scrollHeight')
    for y in range(0, Hh, 700): p.evaluate(f'scrollTo(0,{y})'); p.wait_for_timeout(60)
    p.evaluate('scrollTo(0,0)'); p.wait_for_timeout(400)
    info = p.evaluate("({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, H: document.documentElement.scrollHeight, fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)})")
    f = f'{OUT}{PAGE}-{W}.png'; p.screenshot(path=f, full_page=True); ctx.close(); br.close()
im = Image.open(f).convert('RGB'); n = -(-im.height // COLH)
s = Image.new('RGB', (n * (im.width + 14) + 14, min(COLH, im.height) + 28), '#9a9a9a')
for i in range(n): s.paste(im.crop((0, i * COLH, im.width, min(im.height, (i + 1) * COLH))), (14 + i * (im.width + 14), 14))
s.save(f'{OUT}{PAGE}-{W}-sheet.png'); print(PAGE, W, info, 'sheet', s.size, 'errors', errs)
