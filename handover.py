"""Preview sheets for the hand-over: first screens on desktop and phone, every page at full length, and the buyer sign-up steps."""
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = HERE + '/handover/'; os.makedirs(OUT, exist_ok=True)
BASE = 'http://127.0.0.1:8815/'
PAGES = [('index', 'Home'), ('brand-protection', 'Brand protection'), ('how-it-works', 'How it works'), ('sustainability', 'Sustainability'), ('buyers', 'Buyers'), ('contact', 'Contact')]
BG = '#D9DBD6'
def font(size):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()
def sheet(tiles, cols, gap, name, labels=None, label_size=30, quality=88):
    rows = -(-len(tiles) // cols); lab = (label_size + 22) if labels else 0
    colw = [max(t.width for t in tiles[c::cols]) for c in range(cols)]
    rowh = [max(t.height for t in tiles[r * cols:(r + 1) * cols]) for r in range(rows)]
    W = sum(colw) + gap * (cols + 1); H = sum(rowh) + rows * lab + gap * (rows + 1)
    s = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(s); f = font(label_size) if labels else None
    y = gap
    for r in range(rows):
        x = gap
        for c in range(cols):
            i = r * cols + c
            if i < len(tiles):
                if labels: d.text((x, y), labels[i], fill='#141514', font=f)
                s.paste(tiles[i], (x, y + lab))
            x += colw[c] + gap
        y += rowh[r] + lab + gap
    s.save(OUT + name, quality=quality, optimize=True, progressive=True); print(name, s.size, os.path.getsize(OUT + name) // 1024, 'KB')
def block(r): return r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort()

with sync_playwright() as pw:
    br = pw.chromium.launch()
    # ---- 1. first screens, desktop (captured at 2x, shown at 1440 wide) ----
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2); p = ctx.new_page(); p.route('**/*', block); tiles = []
    for pg, _ in PAGES:
        p.goto(BASE + pg + '.html', wait_until='load'); p.wait_for_timeout(2200); f = OUT + f'_d-{pg}.png'; p.screenshot(path=f); tiles.append(Image.open(f).convert('RGB').resize((1920, 1200), Image.LANCZOS))
    sheet(tiles, 2, 32, 'trekstone-pages-desktop.jpg', [n for _, n in PAGES], 34)
    ctx.close()
    # ---- 2. every page at full length (2x capture, shown at half size) ----
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2, reduced_motion='reduce'); p = ctx.new_page(); p.route('**/*', block); tiles = []
    for pg, _ in PAGES:
        p.goto(BASE + pg + '.html', wait_until='load'); p.wait_for_timeout(700)
        H = p.evaluate('document.documentElement.scrollHeight')
        for y in range(0, H, 700): p.evaluate(f'scrollTo(0,{y})'); p.wait_for_timeout(70)
        p.evaluate('scrollTo(0,0)'); p.wait_for_timeout(500)
        f = OUT + f'_f-{pg}.png'; p.screenshot(path=f, full_page=True); im = Image.open(f).convert('RGB'); tiles.append(im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS))
    sheet(tiles, 6, 30, 'trekstone-pages-full.jpg', [n for _, n in PAGES], 30, quality=86)
    ctx.close()
    # ---- 3. first screens, phone ----
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True); p = ctx.new_page(); p.route('**/*', block); tiles = []
    for pg, _ in PAGES:
        p.goto(BASE + pg + '.html', wait_until='load'); p.wait_for_timeout(2200); f = OUT + f'_p-{pg}.png'; p.screenshot(path=f); tiles.append(Image.open(f).convert('RGB'))
    # plus the open menu and the map further down the brand page
    p.goto(BASE + 'index.html', wait_until='load'); p.wait_for_timeout(900); p.click('.hdr__menu'); p.wait_for_timeout(700); f = OUT + '_p-menu.png'; p.screenshot(path=f); tiles.append(Image.open(f).convert('RGB'))
    sheet(tiles, 7, 28, 'trekstone-pages-phone.jpg', [n for _, n in PAGES] + ['Menu'], 30)
    ctx.close()
    # ---- 4. the buyer sign-up, step by step ----
    ctx = br.new_context(viewport={'width': 1280, 'height': 1700}, device_scale_factor=2, reduced_motion='reduce'); p = ctx.new_page()
    def handler(r):
        u = r.request.url
        if 'supabase.co' in u:
            if r.request.method == 'OPTIONS': return r.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type, apikey'})
            return r.fulfill(status=200, headers={'content-type': 'application/json', 'access-control-allow-origin': '*'}, body='{"ok":true,"reference":"TB-4F2A91C7"}')
        return block(r)
    p.route('**/*', handler); p.goto(BASE + 'buyers.html#apply', wait_until='load'); p.wait_for_timeout(900); tiles = []
    def snap(n):
        p.mouse.move(5, 5); p.evaluate('document.activeElement && document.activeElement.blur()'); p.wait_for_timeout(350)
        f = OUT + f'_s-{n}.png'; p.locator('.formcard').screenshot(path=f); im = Image.open(f).convert('RGB'); tiles.append(im.resize((im.width // 2, im.height // 2), Image.LANCZOS))
    p.fill('#b-company', 'Example Trading LLC'); p.select_option('#b-country', 'United States'); p.fill('#b-state', 'Georgia'); p.fill('#b-city', 'Atlanta'); p.fill('#b-web', 'www.example.com'); p.select_option('#b-years', '3 to 10 years')
    p.locator('label.opt', has_text='Wholesaler or distributor').click(); p.locator('label.opt', has_text='Online reseller').click(); snap(1)
    p.click('[data-next]'); p.wait_for_timeout(500)
    p.fill('#b-name', 'Jordan Example'); p.fill('#b-title', 'Purchasing Manager'); p.fill('#b-email', 'jordan@example.com'); p.fill('#b-phone', '+1 404 555 0100'); p.locator('label.opt', has_text='WhatsApp').click(); snap(2)
    p.click('[data-next]'); p.wait_for_timeout(500)
    p.locator('label.opt', has_text='Footwear').click(); p.locator('label.opt', has_text='Apparel').click(); p.locator('label.opt', has_text='Athletic').click()
    p.locator('label.opt', has_text='Retail-ready').click(); p.locator('label.opt', has_text='Minor imperfections').click()
    p.select_option('#b-order', '2,000 to 10,000 units'); p.select_option('#b-freq', 'Monthly'); p.fill('#b-want', 'Running and lifestyle, sizes 7 to 12'); snap(3)
    p.click('[data-next]'); p.wait_for_timeout(500)
    p.locator('label.opt', has_text='Latin America').click(); p.locator('label.opt', has_text='Wholesale to retailers').click(); p.locator('label.opt', has_text='Online marketplaces').click()
    p.fill('#b-countries', 'Mexico, Colombia'); p.fill('#b-platforms', 'eBay, Whatnot'); p.fill('#b-ship', 'Atlanta, United States'); p.check('input[name=own_freight][value=Yes]'); p.check('input[name=resale_licence][value="In progress"]'); snap(4)
    p.click('[data-next]'); p.wait_for_timeout(500)
    for name in ('agree_accurate', 'agree_conditions', 'agree_terms'): p.check(f'input[name={name}]')
    snap(5)
    p.click('[data-submit]'); p.wait_for_timeout(1500); snap(6)
    sheet(tiles, 3, 32, 'trekstone-buyer-signup.jpg', ['1  Company', '2  Contact', '3  What you buy', '4  Where you sell', '5  Review and send', 'Confirmation'], 30)
    ctx.close(); br.close()
for f in os.listdir(OUT):
    if f.startswith('_'): os.remove(OUT + f)
