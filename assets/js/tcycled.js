/* Artus tcycled page · reveal on scroll, the loop and menu, loaded with defer */
try {
  (() => {
    document.documentElement.classList.add('js');
    const motion = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    const els = document.querySelectorAll('.ep-rv');
    if ('IntersectionObserver' in window && motion) {
      const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
      els.forEach(el => io.observe(el));
    } else els.forEach(el => el.classList.add('is-in'));
    // the loop draws itself once it is on screen
    const ring = document.querySelector('.tcl-ring');
    if (ring) {
      if ('IntersectionObserver' in window && motion) {
        const ro = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { ring.classList.add('is-drawn'); ro.disconnect(); } }), { threshold: 0.3 });
        ro.observe(ring);
      } else ring.classList.add('is-drawn');
    }
    document.querySelectorAll('.ep-menu a').forEach(a => a.addEventListener('click', () => a.closest('details').removeAttribute('open')));
  })();
  
} catch (e) { setTimeout(() => { throw e; }); }
