/* TREKSTONE site script: header, calm reveals, the region map, the pipeline tabs and the two forms. */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const ENDPOINT = '__ENDPOINT__';
  const SITE_KEY = '__SITE_KEY__';              // the project's publishable key: public by design, it only identifies this website
  const LIVE_HOSTS = __LIVE_HOSTS__;
  // Forms only send from the real site. Anywhere else (a preview, a saved copy) they run through to the end without sending.
  const isLive = LIVE_HOSTS.includes(location.hostname) || /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  const loadedAt = Date.now();

  /* ---------- header ---------- */
  const hdr = $('#hdr');
  if (hdr) {
    const onScroll = () => hdr.classList.toggle('is-stuck', scrollY > 8);
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
    const btn = $('.hdr__menu', hdr), menu = $('#menu');
    if (btn && menu) {
      const set = open => {
        hdr.classList.toggle('is-open', open); btn.setAttribute('aria-expanded', String(open)); menu.hidden = !open;
        document.documentElement.style.overflow = open ? 'hidden' : '';
      };
      btn.addEventListener('click', () => set(menu.hidden));
      menu.addEventListener('click', e => { if (e.target.closest('a')) set(false); });
      addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); } });
      const wide = matchMedia('(min-width: 961px)');
      if (wide.addEventListener) wide.addEventListener('change', e => { if (e.matches) set(false); });
    }
  }

  /* ---------- reveal on scroll, once ---------- */
  const rv = $$('.rv');
  if ('IntersectionObserver' in window && rv.length) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }),
      { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
    rv.forEach(el => io.observe(el));
  } else rv.forEach(el => el.classList.add('in'));

  /* ---------- home: on scroll the banner folds into a square frame, then into the logo ----------
     Larger screens with motion allowed. Scrolling is never taken over: CSS holds the banner in place (position: sticky)
     while the visitor scrolls on, and this only reads how far they have got. Each frame changes clip-path, opacity and
     transform, nothing that moves the layout; positions are measured once per resize. */
  (() => {
    const wrap = $('[data-heroscroll]'); if (!wrap) return;
    const hero = $('.hero', wrap), bg = $('.hero__bg', hero), pic = $('picture', bg), img = $('img', bg), shade = $('.hero__shade', bg);
    const light = $('.hero__light', hero), copy = $('.hero__in', hero), strip = $('.hero__strip', hero), end = $('.hs__end', hero);
    if (!bg || !pic || !img || !shade || !light || !copy || !end) return;
    const L = $('.hs__l', end), R = $('.hs__r', end), lead = $('.hs__lead', end), logo = $('.hs__logo', end), tag = $('.hs__tag', end);
    const marks = $$('.hs__m', logo), chars = $$('.hs__c', logo);
    // two inner frames that show the same picture smaller, like windows stacked into depth (built the first time the story runs)
    let frames = [];
    function buildFrames() {
      const stack = document.createElement('div'); stack.className = 'hero__frames';
      frames = [0.075, 0.2].map(inset => {
        const el = document.createElement('div'), im = new Image(); el.className = 'hero__frame'; im.alt = ''; im.src = img.currentSrc || img.src; el.append(im); stack.append(el);
        return { inset, el };
      });
      bg.append(stack);
    }
    const mq = matchMedia('(min-width: 901px) and (min-height: 600px) and (prefers-reduced-motion: no-preference)');
    const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v)), lerp = (a, b, t) => a + (b - a) * t;
    const ease = x => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2), easeOut = x => 1 - Math.pow(1 - x, 3);
    const px = v => v.toFixed(2) + 'px';
    const VB_W = 3491.72, VB_H = 511.92, MARK_W = 444.94;       // the logo's own drawing size; the hexagon mark is its first 445 units
    let on = false, g = null, target = 0, cur = 0, raf = 0, last = 0;

    function reset() {
      if (raf) cancelAnimationFrame(raf); raf = 0; last = 0;                       // a glide still on its way must not draw over the plain banner
      [bg, pic, shade, light, copy, strip, L, R, lead, logo, tag].forEach(el => el && (el.style.cssText = ''));
      marks.concat(chars).forEach(el => (el.style.cssText = '')); frames.forEach(f => (f.el.style.cssText = ''));
    }
    function measure() {
      const W = hero.clientWidth, H = hero.clientHeight;
      const top = wrap.getBoundingClientRect().top + scrollY, total = Math.max(1, wrap.offsetHeight - H);
      const side = clamp(Math.min(W * .34, H * .56), 280, 620), gap = Math.max(36, W * .025);
      const cy = Math.max(H * .47, (hdr ? hdr.offsetHeight : 0) + 28 + side / 2);
      // the logo it ends on: centred on the same spot, its hexagon mark at the left end
      const lw = clamp(W * .5, 420, 860), u = lw / VB_W, hr = VB_H * u / 2, hw = MARK_W * u / 2, hx = (W - lw) / 2 + hw;
      // where the middle of the globe sits before anything moves (the picture covers the banner, placed at 18% 42%)
      const iw = img.naturalWidth || 1920, ih = img.naturalHeight || 980, s0 = Math.max(W / iw, H / ih);
      const fx = (W - iw * s0) * .18 + .6 * iw * s0, fy = (H - ih * s0) * .42 + .5 * ih * s0;
      g = { W, H, top, total, side, cy, hr, hw, hx, fx, fy, shrink: clamp(2 * hr / side * 1.7, .1, 1) };
      pic.style.transformOrigin = px(fx) + ' ' + px(fy);
      L.style.right = R.style.left = px((W + side) / 2 + gap); L.style.top = R.style.top = px(cy);
      lead.style.top = px(cy + side / 2 + 32);
      logo.style.left = px((W - lw) / 2); logo.style.top = px(cy - hr); logo.style.width = px(lw);
      tag.style.top = px(cy + hr + 30);
      frames.forEach(f => {
        const ins = f.inset * side, w = side - 2 * ins;
        f.el.style.left = px((W - w) / 2); f.el.style.top = px(cy - side / 2 + ins); f.el.style.width = px(w); f.el.style.height = px(side - ins * 1.9);
        f.el.style.transformOrigin = '50% ' + px(side / 2 - ins);
      });
    }
    function apply(p) {
      const { W, H, side, cy, hr, hw, hx, fx, fy, shrink } = g;
      const c = ease(clamp(p / .44));                               // banner -> square
      const m = ease(clamp((p - .6) / .2));                         // square -> the hexagon of the logo mark
      const out = ease(clamp((p - .58) / .1));                      // the words leave before the logo arrives
      // the window: six points, a square that turns into a hexagon
      const l = lerp(0, (W - side) / 2, c), r = W - l, t = lerp(0, cy - side / 2, c), b = lerp(H, cy + side / 2, c);
      const sq = [[W / 2, t], [r, t], [r, b], [W / 2, b], [l, b], [l, t]];
      const hex = [[hx, cy - hr], [hx + hw, cy - hr / 2], [hx + hw, cy + hr / 2], [hx, cy + hr], [hx - hw, cy + hr / 2], [hx - hw, cy - hr / 2]];
      bg.style.clipPath = 'polygon(' + sq.map((q, i) => px(lerp(q[0], hex[i][0], m)) + ' ' + px(lerp(q[1], hex[i][1], m))).join(',') + ')';
      // the picture: the globe glides to the middle of the window and steps back, then shrinks with the window on the way to the logo
      pic.style.transform = `translate3d(${px(c * (W / 2 - fx) + m * (hx - W / 2))},${px(c * (cy - fy))},0) scale(${(lerp(1, .88, c) * lerp(1, shrink, m)).toFixed(4)})`;
      shade.style.opacity = (1 - c * .9).toFixed(4);
      bg.style.opacity = (1 - ease(clamp((p - .79) / .09))).toFixed(4);           // the picture fades and leaves the logo mark it was covering
      const fa = ease(clamp((c - .78) / .22)), grow = (r - l) / side;
      frames.forEach((f, i) => { f.el.style.opacity = (fa * (1 - clamp(m * 3))).toFixed(4); f.el.style.transform = `scale(${(grow * lerp(1.06 + i * .04, 1, fa)).toFixed(4)})`; });
      light.style.opacity = ease(clamp((p - .01) / .1)).toFixed(4);              // the page turns light behind the window, before the gap around it shows
      const a = 1 - easeOut(clamp(p / .17));
      copy.style.opacity = a.toFixed(4); copy.style.transform = `translate3d(0,${px(-easeOut(clamp(p / .3)) * 70)},0)`; copy.style.pointerEvents = a < .5 ? 'none' : '';
      if (strip) strip.style.opacity = a.toFixed(4);
      // the headline splits around the square and the lead sits under it
      const s = ease(clamp((p - .21) / .23)), exX = Math.max(0, (r - l - side) / 2), exY = Math.max(0, (b - t - side) / 2);
      L.style.opacity = R.style.opacity = (s * (1 - out)).toFixed(4);
      L.style.transform = `translate3d(${px(-exX + (1 - s) * 70 - out * 40)},-50%,0)`;
      R.style.transform = `translate3d(${px(exX - (1 - s) * 70 + out * 40)},-50%,0)`;
      const ld = ease(clamp((p - .34) / .2));
      lead.style.opacity = (ld * (1 - out)).toFixed(4); lead.style.transform = `translate3d(-50%,${px(exY + (1 - ld) * 18 + out * 12)},0)`;
      // the logo: its mark waits under the hexagon and is left standing as the picture fades, then the letters follow one by one
      const mk = ease(clamp((p - .785) / .025)).toFixed(4); marks.forEach(el => { el.style.opacity = mk; });
      chars.forEach((el, i) => { const k = easeOut(clamp((p - .81 - i * .011) / .07)); el.style.opacity = k.toFixed(4); el.style.transform = `translate(${px(-70 * (1 - k))},0)`; });
      const tg = ease(clamp((p - .915) / .06)); tag.style.opacity = tg.toFixed(4); tag.style.transform = `translate3d(0,${px((1 - tg) * 10)},0)`;
    }
    const read = () => { target = clamp((scrollY - g.top) / g.total); };
    function tick(now) {
      raf = 0; if (!on) return;
      const dt = last ? Math.min(.05, (now - last) / 1000) : .016; last = now;
      cur += (target - cur) * (1 - Math.exp(-dt / .11));                           // a soft glide toward the scroll position, so mouse wheels do not step
      if (Math.abs(target - cur) < .0004) cur = target;
      apply(cur);
      if (cur !== target) raf = requestAnimationFrame(tick); else last = 0;
    }
    const kick = () => { if (!on) return; read(); if (!raf) raf = requestAnimationFrame(tick); };
    function layout() {
      on = mq.matches; wrap.classList.toggle('is-on', on);
      if (!on) { reset(); return; }
      if (!frames.length) buildFrames();
      measure(); read(); cur = target; apply(cur);
    }
    addEventListener('scroll', kick, { passive: true });
    addEventListener('resize', layout);
    if (mq.addEventListener) mq.addEventListener('change', layout);
    if (!img.complete) img.addEventListener('load', () => { if (on) layout(); }, { once: true });
    addEventListener('beforeprint', () => { if (on) { on = false; wrap.classList.remove('is-on'); reset(); } });   // on paper: the plain banner
    addEventListener('afterprint', layout);
    // keyboard: the banner's buttons fade as it folds, so bring the banner back when one of them takes focus
    copy.addEventListener('focusin', () => { if (on && cur > .02) scrollTo(0, g.top); });
    layout();
  })();

  /* ---------- brand protection: approve or restrict regions on the map ---------- */
  $$('[data-geo]').forEach(geo => {
    const chips = $$('.chip', geo), out = $('[data-geo-count]', geo);
    const sync = () => {
      let n = 0;
      chips.forEach(c => {
        const on = c.getAttribute('aria-pressed') === 'true'; if (on) n++;
        $$(`.hm__r[data-region="${c.dataset.region}"]`, geo).forEach(p => p.classList.toggle('is-on', on));
      });
      if (out) out.textContent = n === 0 ? 'No regions approved' : n === chips.length ? 'All regions approved' : `${n} of ${chips.length} regions approved`;
    };
    chips.forEach(c => c.addEventListener('click', () => { c.setAttribute('aria-pressed', String(c.getAttribute('aria-pressed') !== 'true')); sync(); }));
    sync();
  });

  /* ---------- tabs (how it works) ---------- */
  $$('[data-tabs]').forEach(root => {
    const tabs = $$('[role="tab"]', root), panels = $$('[role="tabpanel"]', root);
    const select = (i, focus) => tabs.forEach((t, k) => {
      const on = k === i;
      t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; panels[k].hidden = !on;
      if (on) { panels[k].classList.remove('is-swap'); void panels[k].offsetWidth; panels[k].classList.add('is-swap'); if (focus) t.focus(); }
    });
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(i));
      t.addEventListener('keydown', e => {
        const d = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
        if (d) { e.preventDefault(); select((i + d + tabs.length) % tabs.length, true); }
      });
    });
  });

  /* ---------- forms ---------- */
  $$('form[data-form]').forEach(form => {
    const kind = form.dataset.form;
    const card = form.closest('.formcard') || form;
    const steps = $$('[data-step]', form), prog = $$('.prog li', card);
    const prev = $('[data-prev]', form), next = $('[data-next]', form), send = $('[data-submit]', form);
    const note = $('.fnav__note', form), msg = $('.fmsg', form), done = document.getElementById(form.dataset.done || '');
    let cur = 0;
    const control = f => $('input,select,textarea', f);

    function check(f, quiet) {
      let bad = '';
      const min = Number(f.dataset.min || 0), el = control(f);
      if (min) { if ($$('input:checked', f).length < min) bad = f.dataset.msg || 'Choose at least one.'; }
      else if (el) {
        const v = el.value.trim();
        if (el.type === 'checkbox') { if (el.required && !el.checked) bad = f.dataset.msg || 'Please tick this box to continue.'; }
        else if (el.required && !v) bad = f.dataset.msg || 'This is needed.';
        else if (v && el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) bad = 'Enter a valid email address.';
        else if (v && el.type === 'tel' && v.replace(/\D/g, '').length < 7) bad = 'Enter a phone number with its country code.';
      }
      if (!quiet) {
        f.classList.toggle('is-bad', !!bad);
        const e = $('.f__err', f); if (e) { e.textContent = bad; e.hidden = !bad; }
        if (el && !min) el.setAttribute('aria-invalid', String(!!bad));
      }
      return !bad;
    }
    function validate(scope, quiet) {
      let first = null;
      $$('[data-field]', scope).forEach(f => { if (!check(f, quiet) && !first) first = f; });
      if (first && !quiet) { const el = control(first); if (el) el.focus({ preventScroll: true }); first.scrollIntoView({ block: 'center' }); }
      return !first;
    }
    const recheck = e => { const f = e.target.closest('[data-field]'); if (f && f.classList.contains('is-bad')) check(f); };
    form.addEventListener('input', recheck); form.addEventListener('change', recheck);

    function values() {
      const o = {};
      new FormData(form).forEach((v, k) => {
        if (k === 'company_website_confirm') return;                       // the trap field for bots
        v = String(v).trim(); if (!v) return;
        if (k.endsWith('[]')) (o[k.slice(0, -2)] = o[k.slice(0, -2)] || []).push(v); else o[k] = v;
      });
      return o;
    }
    function summary() {
      const dl = $('[data-review]', form); if (!dl) return;
      const d = values(); dl.textContent = '';
      $$('[data-field][data-label]', form).forEach(f => {
        const el = control(f); if (!el) return;
        let v = d[el.name.replace('[]', '')]; if (Array.isArray(v)) v = v.join(', '); if (!v) return;
        const div = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
        dt.textContent = f.dataset.label; dd.textContent = v; div.append(dt, dd); dl.append(div);
      });
    }
    function show(i, move) {
      cur = i;
      steps.forEach((s, k) => { s.hidden = k !== i; });
      prog.forEach((p, k) => { p.classList.toggle('is-done', k < i); if (k === i) p.setAttribute('aria-current', 'step'); else p.removeAttribute('aria-current'); });
      const last = i === steps.length - 1;
      if (prev) prev.hidden = i === 0;
      if (next) next.hidden = last;
      if (send) send.hidden = !last;
      if (note && steps.length > 1) note.textContent = `Step ${i + 1} of ${steps.length}`;
      if (last) summary();
      if (move) {
        const h = $('h2,h3', steps[i]); if (h) { h.tabIndex = -1; h.focus({ preventScroll: true }); }
        const top = card.getBoundingClientRect().top + scrollY - (hdr ? hdr.offsetHeight : 0) - 16;
        scrollTo({ top, behavior: 'smooth' });
      }
    }
    if (next) next.addEventListener('click', () => { if (validate(steps[cur])) show(cur + 1, true); });
    if (prev) prev.addEventListener('click', () => show(cur - 1, true));

    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (cur < steps.length - 1) { if (validate(steps[cur])) show(cur + 1, true); return; }   // Enter on an earlier step moves on
      for (let i = 0; i < steps.length; i++) if (!validate(steps[i], true)) { show(i, true); validate(steps[i]); return; }
      const trap = form.elements.company_website_confirm;
      const payload = { form: kind, data: values(), hp: trap ? trap.value : '', ms: Date.now() - loadedAt, page: location.pathname };
      const label = send.textContent; send.disabled = true; send.textContent = 'Sending…'; if (msg) msg.hidden = true;
      try {
        let ref = '';
        if (isLive) {
          const r = await fetch(ENDPOINT, { method: 'POST', headers: { 'content-type': 'application/json', apikey: SITE_KEY }, body: JSON.stringify(payload) });
          const j = await r.json().catch(() => ({}));
          if (!r.ok || !j.ok) { const err = new Error(j.error || 'failed'); err.status = r.status; throw err; }
          ref = j.reference || '';
        } else await new Promise(r => setTimeout(r, 600));
        form.hidden = true; const head = $('.formcard__head', card); if (head) head.hidden = true;
        if (done) {
          const refEl = $('[data-ref]', done); if (refEl) { refEl.textContent = ref ? `Reference ${ref}` : ''; refEl.hidden = !ref; }
          const pv = $('[data-preview-note]', done); if (pv) pv.hidden = isLive;
          done.hidden = false; done.tabIndex = -1; done.focus({ preventScroll: true });
          scrollTo({ top: card.getBoundingClientRect().top + scrollY - (hdr ? hdr.offsetHeight : 0) - 16, behavior: 'smooth' });
        }
      } catch (err) {
        if (msg) {
          msg.textContent = err.status === 429 ? 'That is a lot of attempts in a short time. Please wait a while and try again, or write to soureno@trekstone.net.'
            : err.status === 422 ? 'Some details could not be accepted. Please check the form and try again.'
            : 'This could not be sent just now. Please try again in a moment, or write to soureno@trekstone.net.';
          msg.hidden = false;
        }
      } finally { send.disabled = false; send.textContent = label; }
    });
    show(0);
  });
})();
