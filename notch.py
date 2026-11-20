"""Emulate a notched phone (status bar on top, home bar below, and a side notch in landscape) and check nothing sits under them."""
import os
from playwright.sync_api import sync_playwright
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
CASES = [('portrait', 390, 844, {'top': 47, 'bottom': 34, 'left': 0, 'right': 0}), ('landscape', 844, 390, {'top': 0, 'bottom': 21, 'left': 47, 'right': 47})]
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for base, tag in (('http://127.0.0.1:8815/', 'real'), ('http://preview.test/', 'emu')):
        for name, w, h, ins in CASES:
            for pg in ('index', 'contact', 'sustainability'):
                ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True, reduced_motion='reduce'); p = ctx.new_page()
                if tag == 'emu':
                    EMU = os.path.dirname(os.path.abspath(__file__)) + '/preview-emu'
                    CT = {'.webp': 'image/webp', '.svg': 'image/svg+xml', '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg'}
                    def handler(route, EMU=EMU, CT=CT):
                        rel = route.request.url[len('http://preview.test/'):].split('#')[0] or 'index.html'; f = os.path.join(EMU, rel)
                        return route.fulfill(status=200, body=open(f, 'rb').read(), headers={'content-type': CT.get(os.path.splitext(f)[1], 'application/octet-stream')}) if os.path.isfile(f) else route.fulfill(status=404, body='no')
                    p.route('**/*', (lambda hh: (lambda route: hh(route) if route.request.url.startswith('http://preview.test/') else route.continue_()))(handler))
                cdp = ctx.new_cdp_session(p)
                try: cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': ins})
                except Exception as e: print('no override:', str(e)[:200]); raise SystemExit
                p.goto(base + ('' if (pg == 'index' and tag == 'emu') else pg + '.html'), wait_until='load'); p.wait_for_timeout(700)
                info = p.evaluate("""() => { const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)] };
                    const cs = getComputedStyle(document.documentElement);
                    return {sat: cs.getPropertyValue('--sat'), htmlPadTop: cs.paddingTop, htmlPadBottom: cs.paddingBottom, htmlBg: cs.backgroundColor, hdr: r('.hdr'), logo: r('.hdr__logo'), menuBtn: r('.hdr__menu'), h1: r('h1'), wrap: r('main .wrap'), sw: document.documentElement.scrollWidth} }""")
                print(tag, name, pg, info)
                p.screenshot(path=f'{OUT}notch-{tag}-{name}-{pg}.png')
                if name == 'portrait' and pg == 'index':
                    p.click('.hdr__menu'); p.wait_for_timeout(400); print('   menu', p.evaluate("(() => { const b = document.querySelector('#menu').getBoundingClientRect(); return [b.top, b.bottom] })()")); p.screenshot(path=f'{OUT}notch-{tag}-{name}-menu.png'); p.click('.hdr__menu')
                    p.evaluate('scrollTo(0, document.documentElement.scrollHeight)'); p.wait_for_timeout(500); p.screenshot(path=f'{OUT}notch-{tag}-{name}-bottom.png')
                    p.evaluate('scrollTo(0, 600)'); p.wait_for_timeout(500); p.screenshot(path=f'{OUT}notch-{tag}-{name}-stuck.png')
                ctx.close()
    br.close()
