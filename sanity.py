"""Every page at several widths: script errors, outside requests, sideways overflow, broken images, links that go nowhere."""
import os, re
from playwright.sync_api import sync_playwright
REPO = '/home/claude/artusweb'
PAGES = ['index', 'brand-protection', 'how-it-works', 'sustainability', 'buyers', 'contact', 'privacy', 'terms', '404']
problems = 0
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for W, H in ((360, 740), (390, 844), (820, 1180), (1180, 800), (1440, 900), (1920, 1080)):
        ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=W < 700, has_touch=W < 1000); p = ctx.new_page()
        errs, ext, bad = [], [], []
        p.on('pageerror', lambda e: errs.append(str(e)[:160])); p.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)
        p.on('response', lambda r: bad.append(f'{r.status} {r.url[-60:]}') if r.status >= 400 else None)
        def handler(r):
            if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')): r.continue_()
            else: ext.append(r.request.url[:90]); r.abort()
        p.route('**/*', handler)
        for pg in PAGES:
            p.goto(f'http://127.0.0.1:8815/{pg}.html', wait_until='load'); p.wait_for_timeout(350)
            Hh = p.evaluate('document.documentElement.scrollHeight')
            for y in range(0, Hh, 800): p.evaluate(f'scrollTo(0,{y})'); p.wait_for_timeout(40)
            r = p.evaluate("""() => { const de = document.documentElement;
                const wide = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > de.clientWidth + 1 && !e.closest('.hero__bg,.fhero__bg,.earth,.cta,.bhero,.hp,svg') }).slice(0, 4).map(e => (e.className && e.className.baseVal === undefined ? e.className : e.tagName) + ':' + Math.round(e.getBoundingClientRect().right));
                const imgs = [...document.images].filter(i => i.complete && !i.naturalWidth && i.loading !== 'lazy').map(i => i.src.slice(-40));
                const uses = [...document.querySelectorAll('use')].length;
                const hidden = [...document.querySelectorAll('.rv:not(.in)')].length;
                return {sw: de.scrollWidth, cw: de.clientWidth, wide, imgs, uses, hidden} }""")
            flag = r['sw'] > r['cw'] or r['wide'] or r['imgs'] or errs or ext or bad or r['hidden']
            if flag:
                problems += 1; print(W, pg, r, 'errors', errs, 'outside', ext, 'failed', bad)
            errs.clear(); ext.clear(); bad.clear()
        ctx.close()
    br.close()
# links and anchors
ids = {}
for pg in PAGES:
    t = open(f'{REPO}/{pg}.html', encoding='utf-8').read(); ids[pg + '.html'] = set(re.findall(r'\bid="([^"]+)"', t))
for pg in PAGES:
    t = open(f'{REPO}/{pg}.html', encoding='utf-8').read()
    for href in set(re.findall(r'href="([^"]+)"', t)):
        if href.startswith(('http', 'mailto:', 'tel:', 'data:')): continue
        path, _, frag = href.partition('#'); path = path.lstrip('/').split('?')[0] or pg + '.html'
        if path.endswith('.html'):
            if path not in ids: problems += 1; print('MISSING PAGE', pg, href)
            elif frag and frag not in ids[path]: problems += 1; print('MISSING ANCHOR', pg, href)
        elif not os.path.exists(os.path.join(REPO, path)): problems += 1; print('MISSING FILE', pg, href)
    for src in set(re.findall(r'(?:src|srcset)="([^"]+)"', t)):
        for part in src.split(','):
            f = part.strip().split(' ')[0].split('?')[0].lstrip('/')
            if f and not f.startswith(('http', 'data:')) and not os.path.exists(os.path.join(REPO, f)): problems += 1; print('MISSING ASSET', pg, f)
print('problems:', problems)
