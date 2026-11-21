"""The regulation band on the green earth: capture it on both pages and measure how well the text reads against the picture."""
import io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
block = lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort()
def lin(c): c = c / 255.0; return np.where(c <= .03928, c / 12.92, ((c + .055) / 1.055) ** 2.4)
def rel(rgb): rgb = np.asarray(rgb, np.float64); return .2126 * lin(rgb[..., 0]) + .7152 * lin(rgb[..., 1]) + .0722 * lin(rgb[..., 2])
worst = []
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for pg in ('sustainability', 'index'):
        for w, h in ((1440, 900), (820, 1180), (390, 844)):
            ctx = br.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 700, has_touch=w < 1000, reduced_motion='reduce'); p = ctx.new_page(); p.route('**/*', block)
            p.goto(f'http://127.0.0.1:8815/{pg}.html', wait_until='load'); p.wait_for_timeout(500)
            sec = p.locator('.band--earth'); sec.scroll_into_view_if_needed(); p.wait_for_timeout(300)
            p.wait_for_function("(() => { const i = document.querySelector('.band--earth .earth img'); return i && i.complete && i.naturalWidth > 0 })()", timeout=10000); p.wait_for_timeout(500)
            p.add_style_tag(content='.hdr{display:none!important}'); p.wait_for_timeout(150)      # the fixed header would otherwise land somewhere inside a tall capture
            if 'end' in sys.argv: p.add_style_tag(content='.earth img{animation:none!important;transform:scale(1.22) translate3d(.6%,.5%,0)!important}'); p.wait_for_timeout(150)   # the far end of the slow drift
            f = f'{OUT}earth-{pg}-{w}.png'; sec.screenshot(path=f)
            info = p.evaluate("(() => { const i = document.querySelector('.band--earth .earth img'); return {src: i.currentSrc.split('/').pop(), box: [document.querySelector('.band--earth').offsetWidth, document.querySelector('.band--earth').offsetHeight]} })()")
            # contrast: hide the text, photograph the band, and compare each text's colour with the lightest spot behind it
            boxes = p.evaluate("""() => { const sec = document.querySelector('.band--earth'), o = sec.getBoundingClientRect(), out = [];
                sec.querySelectorAll('.eyebrow, .title, .title em, .lead, .reg__where, .reg__when, .reg h3, .reg p:last-child, .note, .btn, .textlink').forEach(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
                    if (r.width) out.push({t: (e.className || e.tagName).toString().slice(0, 14) + ':' + e.textContent.trim().slice(0, 16), x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height, color: cs.color, size: parseFloat(cs.fontSize), weight: +cs.fontWeight || 400}) });
                return out }""")
            p.add_style_tag(content='.band--earth .wrap{visibility:hidden!important}'); p.wait_for_timeout(150)
            bg = np.asarray(Image.open(io.BytesIO(sec.screenshot())).convert('RGB')).astype(np.float64)
            for b in boxes:
                x0, y0, x1, y1 = [int(round(v)) for v in (b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h'])]
                reg = bg[max(0, y0):y1, max(0, x0):x1]
                if reg.size == 0: continue
                import re
                m = [float(v) for v in re.findall(r'[\d.]+', b['color'])]; a = m[3] if len(m) > 3 else 1.0
                lumbg = rel(reg); cut = np.percentile(lumbg, 99); sel = lumbg >= cut; bgpx = reg[sel].mean(axis=0)   # the lightest 1% behind this text (single stars aside)
                txt = np.array(m[:3]) * a + bgpx * (1 - a)
                l1, l2 = float(rel(txt)), float(rel(bgpx)); ratio = (max(l1, l2) + .05) / (min(l1, l2) + .05)
                large = b['size'] >= 24 or (b['size'] >= 18.66 and b['weight'] >= 700)
                worst.append((ratio / (3.0 if large else 4.5), ratio, pg, w, b['t'], 'large' if large else 'small'))
            print(pg, w, info); ctx.close()
    br.close()
worst.sort()
print('lowest contrast against the lightest 1% behind each text (needs 4.5, or 3 for large type):')
for wv in worst[:5]: print('  %.2f:1  %s %s  %s  (%s)' % (wv[1], wv[2], wv[3], wv[4], wv[5]))
print('ALL TEXT READS' if worst[0][0] >= 1 else 'SOME TEXT TOO FAINT')
