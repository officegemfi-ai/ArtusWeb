"""Walk the buyer sign-up form: validation on each step, the review, and sending (network mocked). Usage: formtest.py WIDTH"""
import json, os, sys
from playwright.sync_api import sync_playwright
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
W = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
H = 900 if W > 700 else 844
sent = []
with sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=W < 700, has_touch=W < 1000, reduced_motion='reduce')
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
    def handler(r):
        u = r.request.url
        if 'supabase.co' in u:
            if r.request.method == 'OPTIONS': return r.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type'})
            sent.append(json.loads(r.request.post_data)); return r.fulfill(status=200, headers={'content-type': 'application/json', 'access-control-allow-origin': '*'}, body=json.dumps({'ok': True, 'reference': 'TB-TEST1234'}))
        if u.startswith(('http://127.0.0.1', 'data:', 'blob:')): return r.continue_()
        r.abort()
    p.route('**/*', handler)
    p.goto('http://127.0.0.1:8815/buyers.html#apply', wait_until='load'); p.wait_for_timeout(900)
    form = p.locator('form[data-form=buyer]')
    def state(tag):
        s = p.evaluate("""() => { const f = document.querySelector('form[data-form=buyer]'); const cur = [...f.querySelectorAll('[data-step]')].findIndex(s => !s.hidden);
            return {step: cur + 1, current: document.querySelector('.prog li[aria-current]')?.textContent, errors: [...f.querySelectorAll('.f__err:not([hidden])')].map(e => e.textContent), badAgree: f.querySelectorAll('.agree.is-bad').length,
                    note: f.querySelector('.fnav__note').textContent, prevHidden: f.querySelector('[data-prev]').hidden, nextHidden: f.querySelector('[data-next]').hidden, sendHidden: f.querySelector('[data-submit]').hidden} }""")
        print(tag, s); return s
    def shot(name): p.locator('.formcard').screenshot(path=f'{OUT}form-{W}-{name}.png')
    # step 1: empty continue shows errors
    p.click('[data-next]'); p.wait_for_timeout(300); state('1 empty'); shot('1-errors')
    p.fill('#b-company', 'Example Trading LLC'); p.select_option('#b-country', 'United States'); p.fill('#b-city', 'Atlanta'); p.fill('#b-state', 'Georgia'); p.fill('#b-web', 'www.example.com')
    p.select_option('#b-years', '3 to 10 years')
    p.locator('label.opt', has_text='Wholesaler or distributor').click(); p.locator('label.opt', has_text='Online reseller').click()
    state('1 filled'); p.click('[data-next]'); p.wait_for_timeout(400); state('2 start')
    p.click('[data-next]'); p.wait_for_timeout(300); state('2 empty')
    p.fill('#b-name', 'Jordan Example'); p.fill('#b-title', 'Purchasing Manager'); p.fill('#b-email', 'not-an-email'); p.fill('#b-phone', '123')
    p.click('[data-next]'); p.wait_for_timeout(300); state('2 bad formats'); shot('2-errors')
    p.fill('#b-email', 'jordan@example.com'); p.fill('#b-phone', '+1 404 555 0100'); p.locator('label.opt', has_text='WhatsApp').click()
    p.click('[data-next]'); p.wait_for_timeout(400); state('3 start'); shot('3')
    p.click('[data-next]'); p.wait_for_timeout(300); state('3 empty')
    p.locator('label.opt', has_text='Footwear').click(); p.locator('label.opt', has_text='Apparel').click(); p.locator('label.opt', has_text='Athletic').click()
    p.locator('label.opt', has_text='Retail-ready').click(); p.locator('label.opt', has_text='Minor imperfections').click()
    p.select_option('#b-order', '2,000 to 10,000 units'); p.select_option('#b-freq', 'Monthly'); p.fill('#b-want', 'Running and lifestyle, sizes 7 to 12')
    p.click('[data-next]'); p.wait_for_timeout(400); state('4 start')
    p.locator('label.opt', has_text='Latin America').click(); p.locator('label.opt', has_text='Wholesale to retailers').click(); p.locator('label.opt', has_text='Online marketplaces').click()
    p.fill('#b-countries', 'Mexico, Colombia'); p.fill('#b-platforms', 'eBay, Whatnot'); p.fill('#b-ship', 'Atlanta, United States')
    p.check('input[name=own_freight][value=Yes]'); p.check('input[name=resale_licence][value="In progress"]')
    shot('4'); p.click('[data-next]'); p.wait_for_timeout(400); state('5 review'); shot('5-review')
    p.click('[data-submit]'); p.wait_for_timeout(300); state('5 unticked'); 
    for name in ('agree_accurate', 'agree_conditions', 'agree_terms'): p.check(f'input[name={name}]')
    p.fill('#b-notes', 'Test application from the build checks.')
    # back and forward keeps values
    p.click('[data-prev]'); p.wait_for_timeout(300); state('back to 4'); p.click('[data-next]'); p.wait_for_timeout(300)
    p.click('[data-submit]'); p.wait_for_timeout(1200)
    print('done visible:', p.evaluate("!document.getElementById('buyer-done').hidden"), 'form hidden:', p.evaluate("document.querySelector('form[data-form=buyer]').hidden"),
          'ref:', p.evaluate("document.querySelector('#buyer-done [data-ref]').textContent"), 'preview note hidden:', p.evaluate("document.querySelector('#buyer-done [data-preview-note]').hidden"))
    shot('6-done')
    print('errors', errs); ctx.close(); br.close()
print('requests sent:', len(sent))
if sent: print(json.dumps(sent[0], indent=1)[:2400])
