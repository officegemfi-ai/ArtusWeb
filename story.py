"""The home banner story: capture it step by step while scrolling, and check its states.
Usage: story.py [WIDTH HEIGHT]   (default 1440 900)"""
import os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
W = int(sys.argv[1]) if len(sys.argv) > 2 else 1440
H = int(sys.argv[2]) if len(sys.argv) > 2 else 900
STEPS = [0, .06, .12, .2, .3, .4, .46, .54, .62, .68, .74, .78, .82, .86, .9, .94, 1.0]
block = lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort()
with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': W, 'height': H}); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
    p.route('**/*', block); p.goto('http://127.0.0.1:8815/index.html', wait_until='load'); p.wait_for_timeout(1800)
    info = p.evaluate("""() => { const w = document.querySelector('[data-heroscroll]'), h = w.querySelector('.hero');
        return {on: w.classList.contains('is-on'), track: w.offsetHeight, hero: h.offsetHeight, sticky: getComputedStyle(h).position, docH: document.documentElement.scrollHeight, sw: document.documentElement.scrollWidth,
                frames: w.querySelectorAll('.hero__frame').length, marks: w.querySelectorAll('.hs__m').length, chars: w.querySelectorAll('.hs__c').length} }""")
    print(W, H, info)
    total = info['track'] - info['hero']; ims = []
    for i, s in enumerate(STEPS):
        p.evaluate(f'scrollTo({{top: {round(s * total)}, behavior: "instant"}})'); p.wait_for_timeout(1300)
        f = f'{OUT}story-{W}-{i:02d}.png'; p.screenshot(path=f); ims.append(Image.open(f).convert('RGB'))
        if s in (0, .54, 1.0):
            print(' p=%.2f' % s, p.evaluate("""() => { const q = s => document.querySelector(s), o = e => +getComputedStyle(e).opacity, b = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] };
                return {clip: q('.hero__bg').style.clipPath.slice(0, 120), copy: o(q('.hero__in')), light: o(q('.hero__light')), L: [o(q('.hs__l')), b(q('.hs__l'))], R: [o(q('.hs__r')), b(q('.hs__r'))], lead: [o(q('.hs__lead')), b(q('.hs__lead'))],
                        logo: b(q('.hs__logo')), marks: [...document.querySelectorAll('.hs__m')].map(o), chars: [...document.querySelectorAll('.hs__c')].map(o), tag: [o(q('.hs__tag')), b(q('.hs__tag'))], bg: o(q('.hero__bg')),
                        frames: [...document.querySelectorAll('.hero__frame')].map(e => [o(e), b(e)]), hdr: q('.hdr').className, sw: document.documentElement.scrollWidth} }"""))
    # past the end: the banner lets go and the next section follows
    p.evaluate(f'scrollTo({{top: {total + 500}, behavior: "instant"}})'); p.wait_for_timeout(900); f = f'{OUT}story-{W}-after.png'; p.screenshot(path=f); ims.append(Image.open(f).convert('RGB'))
    tw = 600; th = round(H * tw / W); cols = 6; rows = -(-len(ims) // cols); g = 10
    sheet = Image.new('RGB', (cols * (tw + g) + g, rows * (th + g) + g), '#8a8a8a')
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th), Image.LANCZOS), (g + (i % cols) * (tw + g), g + (i // cols) * (th + g)))
    sheet.save(f'{OUT}story-{W}-sheet.jpg', quality=88); print('sheet', sheet.size, 'errors', errs)
    ctx.close(); br.close()
