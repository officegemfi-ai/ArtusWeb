"""The banner story must stay out of the way where it does not belong: phones, tablets, reduced motion, no JavaScript, print.
Also: keyboard focus brings the banner back, a resize switches it off cleanly, and frames keep coming while scrolling."""
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import numpy as np
OUT = os.path.dirname(os.path.abspath(__file__)) + '/shots/'
URL = 'http://127.0.0.1:8815/index.html'
block = lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1', 'data:', 'blob:')) else r.abort()
STATE = """() => { const w = document.querySelector('[data-heroscroll]'), h = w.querySelector('.hero'), bg = w.querySelector('.hero__bg'), e = w.querySelector('.hs__end');
  return {on: w.classList.contains('is-on'), track: w.offsetHeight, hero: h.offsetHeight, pos: getComputedStyle(h).position, clip: bg.style.clipPath || '', endDisplay: getComputedStyle(e).display,
          frames: w.querySelectorAll('.hero__frame').length, copy: getComputedStyle(w.querySelector('.hero__in')).opacity, inline: [...w.querySelectorAll('[style]')].filter(x => !x.classList.contains('rv')).length, sw: document.documentElement.scrollWidth} }"""
res = []
def ok(name, cond, extra=''): res.append(cond); print('PASS' if cond else 'FAIL', name, extra)
with sync_playwright() as pw:
    br = pw.chromium.launch()
    def page(w, h, **kw):
        ctx = br.new_context(viewport={'width': w, 'height': h}, **kw); p = ctx.new_page(); p.errs = []
        p.on('pageerror', lambda e: p.errs.append(str(e)[:160])); p.route('**/*', block); p.goto(URL, wait_until='load'); p.wait_for_timeout(1500); return ctx, p
    # phone and tablet: the plain banner
    for w, h, mob in ((390, 844, True), (820, 1180, False), (900, 700, False)):
        ctx, p = page(w, h, is_mobile=mob, has_touch=True); s = p.evaluate(STATE)
        ok(f'{w}px: story off, plain banner', not s['on'] and s['pos'] != 'sticky' and s['track'] == s['hero'] and s['endDisplay'] == 'none' and s['frames'] == 0 and not s['clip'] and s['sw'] <= w, str(s))
        p.screenshot(path=f'{OUT}modes-{w}.png'); ctx.close()
    # short window: off
    ctx, p = page(1440, 560); s = p.evaluate(STATE); ok('short window (560px high): story off', not s['on'] and s['endDisplay'] == 'none', str(s)); ctx.close()
    # reduced motion: off
    ctx, p = page(1440, 900, reduced_motion='reduce'); s = p.evaluate(STATE); ok('reduced motion: story off', not s['on'] and s['pos'] != 'sticky' and s['endDisplay'] == 'none', str(s)); p.screenshot(path=f'{OUT}modes-reduced.png'); ctx.close()
    # no JavaScript: plain banner, readable
    ctx = br.new_context(viewport={'width': 1440, 'height': 900}, java_script_enabled=False); p = ctx.new_page(); p.route('**/*', block); p.goto(URL, wait_until='load'); p.wait_for_timeout(800)
    p.screenshot(path=f'{OUT}modes-nojs.png'); im = np.asarray(Image.open(f'{OUT}modes-nojs.png').convert('L'))
    ok('no JavaScript: banner drawn with its headline', im[200:500, 80:700].max() > 200 and im[:, :].mean() < 60, f'mean {im.mean():.1f}'); ctx.close()
    # desktop: on; top of page looks like the plain banner
    ctx, p = page(1440, 900); s = p.evaluate(STATE)
    ok('desktop: story on, banner pinned', s['on'] and s['pos'] == 'sticky' and s['track'] == 3 * s['hero'] and s['frames'] == 2 and s['sw'] <= 1440, str(s))
    p.screenshot(path=f'{OUT}modes-desktop-top.png')
    # compare with the banner as it was before the story existed (same moment after loading, so the slow drift is in step)
    a = Image.open(f'{OUT}modes-desktop-top.png').convert('RGB'); b = Image.open(f'{OUT}before-index-1440.png').convert('RGB')
    d = np.asarray(ImageChops.difference(a, b)).max(axis=2); ok('desktop at the top looks like the banner did before', (d > 24).mean() < .004, f'{(d > 24).mean() * 100:.3f}% of pixels differ')
    # keyboard: fold the banner away, then tab to its first button
    total = p.evaluate("document.querySelector('[data-heroscroll]').offsetHeight - innerHeight")
    p.evaluate(f'scrollTo({{top: {round(.5 * total)}, behavior: "instant"}})'); p.wait_for_timeout(900)
    hidden = p.evaluate("getComputedStyle(document.querySelector('.hero__in')).opacity")
    p.evaluate("document.querySelector('.hero .btn').focus({preventScroll: true})"); p.wait_for_timeout(1600)
    back = p.evaluate("({y: Math.round(scrollY), op: getComputedStyle(document.querySelector('.hero__in')).opacity, active: document.activeElement.textContent.trim()})")
    ok('keyboard focus on a banner button brings the banner back', hidden == '0' and back['y'] < 5 and float(back['op']) > .95, f'{hidden} -> {back}')
    # frames keep coming during a steady scroll through the whole story
    p.evaluate("""() => { window.__dt = []; let last = performance.now(); const f = t => { window.__dt.push(t - last); last = t; window.__raf = requestAnimationFrame(f) }; window.__raf = requestAnimationFrame(f) }""")
    for i in range(0, 121):
        p.evaluate(f'scrollTo({{top: {round(i / 120 * total)}, behavior: "instant"}})'); p.wait_for_timeout(16)
    p.wait_for_timeout(500)
    dt = p.evaluate("(() => { cancelAnimationFrame(window.__raf); return window.__dt })()"); dt = sorted(dt)
    ok('scrolling through the story stays fluid in this test browser', dt[int(len(dt) * .95)] < 50, f'frames {len(dt)}, median {dt[len(dt) // 2]:.1f} ms, 95th {dt[int(len(dt) * .95)]:.1f} ms, worst {dt[-1]:.1f} ms')
    # print: the plain banner
    p.evaluate("window.dispatchEvent(new Event('beforeprint'))"); s = p.evaluate(STATE); ok('before printing: story off and cleaned up', not s['on'] and not s['clip'], str(s))
    p.evaluate("window.dispatchEvent(new Event('afterprint'))"); s = p.evaluate(STATE); ok('after printing: story back on', s['on'], '')
    # a resize to a small window switches it off and leaves nothing behind
    p.evaluate(f'scrollTo({{top: {round(.5 * total)}, behavior: "instant"}})'); p.wait_for_timeout(700)
    p.set_viewport_size({'width': 800, 'height': 900}); p.wait_for_timeout(700); s = p.evaluate(STATE)
    ok('resize to 800px: story off, nothing left behind', not s['on'] and not s['clip'] and s['copy'] == '1' and s['track'] == s['hero'], str(s))
    p.set_viewport_size({'width': 1440, 'height': 900}); p.wait_for_timeout(700); s = p.evaluate(STATE); ok('resize back to 1440px: story on again', s['on'] and s['track'] == 3 * s['hero'], '')
    ok('no script errors', not p.errs, str(p.errs)); ctx.close(); br.close()
print('ALL PASS' if all(res) else 'SOME FAILED', f'({sum(res)}/{len(res)})')
