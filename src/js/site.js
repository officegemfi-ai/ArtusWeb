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
