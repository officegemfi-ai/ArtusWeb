"""Interaction checks: phone menu, header states, region map, pipeline tabs, FAQ, the enquiry form."""
import json, os
from playwright.sync_api import sync_playwright
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
ok = lambda name, cond, extra='': print(('PASS ' if cond else 'FAIL ') + name, extra)
sent = []
with sync_playwright() as pw:
    br = pw.chromium.launch()
    def page(W, H, touch=False):
        ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=touch and W < 700, has_touch=touch); p = ctx.new_page(); p.errs = []
        p.on('pageerror', lambda e: p.errs.append(str(e)[:160]))
        def handler(r):
            u = r.request.url
            if 'supabase.co' in u:
                if r.request.method == 'OPTIONS': return r.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type, apikey'})
                sent.append((dict(r.request.headers), json.loads(r.request.post_data))); return r.fulfill(status=200, headers={'content-type': 'application/json', 'access-control-allow-origin': '*'}, body='{"ok":true,"reference":"TE-TEST0001"}')
            if u.startswith(('http://127.0.0.1', 'data:', 'blob:')): return r.continue_()
            r.abort()
        p.route('**/*', handler); return ctx, p
    # ---- phone menu ----
    ctx, p = page(390, 844, True)
    p.goto('http://127.0.0.1:8815/index.html', wait_until='load'); p.wait_for_timeout(500)
    ok('menu closed at start', p.evaluate("document.getElementById('menu').hidden"))
    p.click('.hdr__menu'); p.wait_for_timeout(300)
    ok('menu opens', p.evaluate("!document.getElementById('menu').hidden && document.querySelector('.hdr__menu').getAttribute('aria-expanded') === 'true'"))
    p.screenshot(path=OUT + 'i-menu.png')
    p.keyboard.press('Escape'); p.wait_for_timeout(200); ok('Escape closes menu', p.evaluate("document.getElementById('menu').hidden"))
    p.click('.hdr__menu'); p.click('#menu a[href="buyers.html"]'); p.wait_for_load_state('load'); p.wait_for_timeout(400)
    ok('menu link goes to buyers', p.url.endswith('buyers.html'), p.url); ok('current tab marked', p.evaluate("document.querySelector('#menu a[aria-current]')?.textContent") == 'Buyers')
    ctx.close()
    # ---- header states ----
    ctx, p = page(1440, 900)
    p.goto('http://127.0.0.1:8815/index.html', wait_until='load'); p.wait_for_timeout(400)
    top = p.evaluate("getComputedStyle(document.getElementById('hdr')).color"); p.evaluate('scrollTo(0, 900)'); p.wait_for_timeout(500)
    ok('header: white text over the dark hero, ink once scrolled', top == 'rgb(255, 255, 255)' and p.evaluate("getComputedStyle(document.getElementById('hdr')).color") == 'rgb(10, 10, 10)', top)
    # ---- region map ----
    p.goto('http://127.0.0.1:8815/brand-protection.html', wait_until='load'); p.wait_for_timeout(500)
    st = lambda: p.evaluate("({on: [...document.querySelectorAll('.hm__r.is-on')].map(e => e.dataset.region), count: document.querySelector('[data-geo-count]').textContent})")
    ok('map starts with three regions', st() == {'on': ['latam', 'me', 'af'], 'count': '3 of 6 regions approved'}, st())
    p.click('.chip[data-region="eu"]'); p.click('.chip[data-region="af"]'); p.wait_for_timeout(700)
    ok('toggling regions updates map and count', st() == {'on': ['latam', 'eu', 'me'], 'count': '3 of 6 regions approved'}, st())
    p.locator('.geo').screenshot(path=OUT + 'i-map.png')
    for r in ('latam', 'eu', 'me'): p.click(f'.chip[data-region="{r}"]')
    ok('none approved wording', st()['count'] == 'No regions approved', st()['count'])
    # ---- pipeline tabs ----
    p.goto('http://127.0.0.1:8815/how-it-works.html', wait_until='load'); p.wait_for_timeout(500)
    p.click('#pt-3'); p.wait_for_timeout(600)
    ok('tab click shows its panel', p.evaluate("!document.getElementById('pp-3').hidden && document.getElementById('pp-1').hidden && document.getElementById('pt-3').getAttribute('aria-selected') === 'true'"))
    p.keyboard.press('ArrowRight'); p.wait_for_timeout(300)
    ok('arrow key moves to the next tab', p.evaluate("document.activeElement.id === 'pt-4' && !document.getElementById('pp-4').hidden"))
    p.locator('.pipe').screenshot(path=OUT + 'i-pipe.png')
    # ---- FAQ ----
    p.goto('http://127.0.0.1:8815/buyers.html', wait_until='load'); p.wait_for_timeout(400)
    p.locator('.faq summary').first.click(); p.wait_for_timeout(200); ok('FAQ opens', p.evaluate("document.querySelector('.faq details').open"))
    # ---- enquiry form ----
    p.goto('http://127.0.0.1:8815/contact.html', wait_until='load'); p.wait_for_timeout(500)
    p.click('form[data-form=enquiry] [data-submit]'); p.wait_for_timeout(300)
    errs = p.evaluate("[...document.querySelectorAll('form[data-form=enquiry] .f__err:not([hidden])')].map(e => e.textContent)")
    ok('empty enquiry shows three errors and sends nothing', len(errs) == 3 and not sent, errs)
    p.fill('#e-name', 'Test Brand'); p.fill('#e-company', 'Example Brand Inc'); p.fill('#e-email', 'test@example.com'); p.locator('label.opt', has_text='Footwear').click(); p.fill('#e-units', '12,000 pairs')
    p.click('form[data-form=enquiry] [data-submit]'); p.wait_for_timeout(1200)
    ok('enquiry sends once with the site key', len(sent) == 1 and sent[0][0].get('apikey', '').startswith('sb_publishable_') and sent[0][1]['form'] == 'enquiry', sent[0][1] if sent else '')
    ok('thank-you shown with reference', p.evaluate("!document.getElementById('enquiry-done').hidden && document.querySelector('#enquiry-done [data-ref]').textContent") == 'Reference TE-TEST0001')
    p.locator('.formcard').screenshot(path=OUT + 'i-enquiry-done.png')
    ok('no script errors', not p.errs, p.errs); ctx.close()
    # ---- no JavaScript ----
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, java_script_enabled=False); p = ctx.new_page(); p.goto('http://127.0.0.1:8815/index.html', wait_until='load'); p.wait_for_timeout(300)
    ok('page is readable without JavaScript', p.evaluate("getComputedStyle(document.querySelector('.hero .display')).opacity") == '1'); ctx.close()
    br.close()
