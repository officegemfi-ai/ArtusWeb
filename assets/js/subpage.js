/* Artus subpages · reveal on scroll and menu, loaded with defer */
try {
  (() => {
    document.documentElement.classList.add('js');
    const els = document.querySelectorAll('.ep-rv');
    if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
      els.forEach(el => io.observe(el));
    } else els.forEach(el => el.classList.add('is-in'));
    document.querySelectorAll('.ep-menu a').forEach(a => a.addEventListener('click', () => a.closest('details').removeAttribute('open')));
  })();
  
} catch (e) { setTimeout(() => { throw e; }); }
