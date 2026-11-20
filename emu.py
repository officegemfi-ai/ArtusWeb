"""Load the preview bundle the way the private preview serves it: first page wrapped in a bare skeleton, a foreign origin,
every outside host blocked. Compares each page with the real build and walks the menus and both forms."""
import os, shutil
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = HERE + '/preview'; EMU = HERE + '/preview-emu'; OUT = HERE + '/shots/'
shutil.rmtree(EMU, ignore_errors=True); shutil.copytree(P, EMU)
frag = open(P + '/index.html', encoding='utf-8').read()
SKEL = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}'
        'img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
open(EMU + '/index.html', 'w', encoding='utf-8').write(SKEL + frag)
CT = {'.webp': 'image/webp', '.svg': 'image/svg+xml', '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg'}
log = {'req': set(), 'miss': [], 'ext': [], 'err': []}
def handler(route):
    u = route.request.url
    if u.startswith('http://preview.test/'):
        rel = u[len('http://preview.test/'):].split('#')[0]
        if '?' in rel: log['miss'].append('QUERY ' + rel); return route.fulfill(status=404, body='no')
        rel = rel or 'index.html'; f = os.path.join(EMU, rel)
        if os.path.isfile(f):
            log['req'].add(rel); return route.fulfill(status=200, body=open(f, 'rb').read(), headers={'content-type': CT.get(os.path.splitext(f)[1], 'application/octet-stream')})
        log['miss'].append(rel); return route.fulfill(status=404, body='no')
    if u.startswith(('data:', 'blob:', 'http://127.0.0.1:8815/')): return route.continue_()
    log['ext'].append(u[:120]); route.abort()
PAGES = ['index', 'brand-protection', 'how-it-works', 'sustainability', 'buyers', 'contact', 'privacy', 'terms']
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for w, h in ((1440, 900), (390, 844)):
        for pg in PAGES:
            shots = {}
            for tag, url in (('emu', f'http://preview.test/{"" if pg == "index" else pg + ".html"}'), ('real', f'http://127.0.0.1:8815/{pg}.html')):
                ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 700, has_touch=w < 1000, reduced_motion='reduce'); p = ctx.new_page()
                p.on('pageerror', lambda e, t=tag, g=pg: log['err'].append(f'{t} {g} {str(e)[:160]}'))
                p.on('console', lambda m, t=tag, g=pg: log['err'].append(f'{t} {g} console {m.text[:160]}') if m.type in ('error', 'warning') else None)
                p.route('**/*', handler); p.goto(url, wait_until='load'); p.wait_for_timeout(700)
                H = p.evaluate('document.documentElement.scrollHeight')
                for y in range(0, H, 700): p.evaluate(f'scrollTo(0,{y})'); p.wait_for_timeout(60)
                p.evaluate('scrollTo(0,0)'); p.wait_for_timeout(500)
                info = p.evaluate("""() => ({sw: document.documentElement.scrollWidth, H: document.documentElement.scrollHeight, font: getComputedStyle(document.querySelector('h1')).fontFamily.slice(0, 12),
                    fontsOk: document.fonts.check('16px Archivo') && document.fonts.check('16px Inter'), icons: [...document.querySelectorAll('svg use')].filter(u => { const r = u.getBoundingClientRect(); return r.width === 0 }).length,
                    imgs: [...document.images].filter(i => i.complete && !i.naturalWidth).length, title: document.title, live: location.hostname})""")
                f = f'{OUT}emu-{tag}-{pg}-{w}.png'; p.screenshot(path=f, full_page=True); shots[tag] = (f, info); ctx.close()
            a = Image.open(shots['emu'][0]).convert('RGB'); b = Image.open(shots['real'][0]).convert('RGB'); ia, ib = shots['emu'][1], shots['real'][1]
            diff = '-'
            if a.size == b.size:
                d = np.asarray(ImageChops.difference(a, b)).max(axis=2); diff = f'{(d > 10).mean() * 100:.3f}% px differ'
            ok = a.size == b.size and ia['sw'] <= w and ia['fontsOk'] and ia['imgs'] == 0
            print('OK  ' if ok else 'LOOK', w, pg.ljust(17), 'emu', a.size, 'real', b.size, diff, {k: ia[k] for k in ('sw', 'fontsOk', 'icons', 'imgs', 'title')})
    # ---- walk the preview like a visitor ----
    for w, h in ((1440, 900), (390, 844)):
        ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 700, has_touch=w < 1000); p = ctx.new_page()
        p.on('pageerror', lambda e: log['err'].append('walk ' + str(e)[:160])); p.on('console', lambda m: log['err'].append('walk console ' + m.text[:160]) if m.type == 'error' else None)
        p.route('**/*', handler); p.goto('http://preview.test/', wait_until='load'); p.wait_for_timeout(900)
        def go(href):
            if w < 700:
                p.click('.hdr__menu'); p.wait_for_timeout(350); p.click(f'#menu a[href="{href}"]')
            else: p.click(f'.hdr__nav a[href="{href}"]')
            p.wait_for_load_state('load'); p.wait_for_timeout(600)
            return p.url, p.evaluate("document.querySelector('h1').textContent.trim().slice(0, 40)"), p.evaluate("document.querySelector('.hdr__nav a[aria-current], #menu a[aria-current]')?.textContent")
        for href in ('brand-protection.html', 'how-it-works.html', 'sustainability.html', 'buyers.html', 'contact.html'): print(w, 'nav', go(href))
        p.click('.hdr__logo'); p.wait_for_load_state('load'); p.wait_for_timeout(500); print(w, 'logo ->', p.url, p.evaluate("document.querySelector('h1').textContent.trim().slice(0, 30)"), 'body class', p.evaluate('document.body.className'))
        # home doors -> buyers, then the whole sign-up form in preview mode
        p.goto('http://preview.test/buyers.html#apply', wait_until='load'); p.wait_for_timeout(700)
        p.fill('#b-company', 'Example Trading LLC'); p.select_option('#b-country', 'United States'); p.fill('#b-city', 'Atlanta')
        p.locator('label.opt', has_text='Wholesaler or distributor').click(); p.click('[data-next]'); p.wait_for_timeout(350)
        p.fill('#b-name', 'Jordan Example'); p.fill('#b-title', 'Purchasing Manager'); p.fill('#b-email', 'jordan@example.com'); p.fill('#b-phone', '+1 404 555 0100'); p.click('[data-next]'); p.wait_for_timeout(350)
        p.locator('label.opt', has_text='Footwear').click(); p.locator('label.opt', has_text='Retail-ready').click(); p.select_option('#b-order', '2,000 to 10,000 units'); p.click('[data-next]'); p.wait_for_timeout(350)
        p.locator('label.opt', has_text='Latin America').click(); p.locator('label.opt', has_text='Wholesale to retailers').click(); p.fill('#b-ship', 'Atlanta, United States'); p.click('[data-next]'); p.wait_for_timeout(350)
        for name in ('agree_accurate', 'agree_conditions', 'agree_terms'): p.check(f'input[name={name}]')
        p.click('[data-submit]'); p.wait_for_timeout(1500)
        print(w, 'buyer form in preview:', p.evaluate("""() => ({done: !document.getElementById('buyer-done').hidden, formHidden: document.querySelector('form[data-form=buyer]').hidden,
            note: (document.querySelector('#buyer-done [data-preview-note]') || {}).hidden === false ? document.querySelector('#buyer-done [data-preview-note]').textContent.trim() : 'NOTE HIDDEN',
            ref: document.querySelector('#buyer-done [data-ref]').hidden})"""))
        p.screenshot(path=f'{OUT}emu-walk-buyer-done-{w}.png')
        ctx.close()
    br.close()
print('files requested', len(log['req']), 'of', sum(len(f) for _, _, f in os.walk(EMU)), '· never requested:', sorted(set(os.path.relpath(os.path.join(d, f), EMU) for d, _, fs in os.walk(EMU) for f in fs) - log['req']))
print('missing', log['miss']); print('outside hosts asked for', sorted(set(log['ext']))); print('errors', log['err'])
