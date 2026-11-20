"""Build the TREKSTONE website: a short homepage plus one page per tab, from hand-written sources in src/.

    python3 build.py             -> writes the site into the repository working tree
    python3 build.py --preview   -> also writes a self-contained copy for the private preview (preview/)

Pages are plain HTML fragments with a few {{tokens}} for icons, the logo, the region map and shared values."""
import hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('TREKSTONE_SITE', '/home/claude/artusweb')   # the folder the finished site is written into
sys.path.insert(0, HERE)
import icons            # noqa: E402
from hexmap import hexmap_svg  # noqa: E402

SITE = 'https://www.trekstone.net/'
LOGIN = 'https://staging.trekstone.net/login'       # the client portal; swap for the production address before launch
ENDPOINT = 'https://jmccuivshndginwxilgj.supabase.co/functions/v1/site-forms'
SITE_KEY = 'sb_publishable_kVizC2x1oGhIiD4UMZ3oUw_VRCRRJan'      # publishable key of the TREKSTONE Supabase project (safe to ship in the page)
LIVE_HOSTS = ['www.trekstone.net', 'trekstone.net', 'artusgroup.net', 'www.artusgroup.net', 'officegemfi-ai.github.io']
NAV = [('Brand protection', 'brand-protection.html'), ('How it works', 'how-it-works.html'), ('Sustainability', 'sustainability.html'),
       ('Buyers', 'buyers.html'), ('Contact', 'contact.html')]
DESC = ('TREKSTONE gives surplus footwear and apparel a controlled path back to market: vetted buyers under contract, '
        'geo-restricted channels and documented proof of where every pair goes.')
PAGES = [
    dict(src='home', out='index.html', title='TREKSTONE | Controlled excess inventory management', desc=DESC, body='dark-top', cta='brand'),
    dict(src='brand', out='brand-protection.html', title='Brand protection | TREKSTONE', cta='brand',
         desc='How TREKSTONE keeps excess inventory out of the markets you protect: geo-restricted channels, vetted buyers under contract, NFR marking and de-branding, and a chain of custody for every pair.'),
    dict(src='how', out='how-it-works.html', title='How it works | TREKSTONE', cta='brand',
         desc='A controlled path for every lot: intake and grading A to D, routing to approved channels, protection at every hand-off and documented outcomes. Start with one lot in 90 days.'),
    dict(src='sustainability', out='sustainability.html', title='Sustainability and compliance | TREKSTONE', body='dark-top top-forest', cta='brand',
         desc='Resale and reuse first, donation through vetted networks, certified recycling last, with documentation built for the EU ban on destroying unsold goods, California SB 707, ESRS E5 and GRI 306.'),
    dict(src='buyers', out='buyers.html', title='Buyers | TREKSTONE', body='dark-top', cta='buyer',
         desc='Branded footwear and apparel overstock for vetted buyers. Register your company once and receive offers that match your profile, with grade, quantity and resale conditions stated up front.'),
    dict(src='contact', out='contact.html', title='Contact | TREKSTONE', cta=None,
         desc='Tell TREKSTONE what you have and where it is. We come back with a grading and routing plan.'),
    dict(src='privacy', out='privacy.html', title='Privacy Policy | TREKSTONE', cta=None,
         desc='How TREKSTONE handles personal information on this website, including buyer applications and enquiries.'),
    dict(src='terms', out='terms.html', title='Terms & Conditions | TREKSTONE', cta=None, desc='The terms that apply to the TREKSTONE website.'),
    dict(src='notfound', out='404.html', title='Page not found | TREKSTONE', cta=None, desc='This page could not be found.', root='/', noindex=True),
]
CTA = {
    'brand': '''<section class="cta on-dark" aria-labelledby="cta-title">
      <div class="wrap cta__in">
        <div><p class="eyebrow rv">Contact</p><h2 class="title rv" style="--d:1;margin-top:20px" id="cta-title">Tell us what you have <em>and where it is.</em></h2><p class="lead rv" style="--d:2">We will come back with a grading and routing plan.</p></div>
        <div class="rv" style="--d:2"><div class="btns"><a class="btn btn--white" href="contact.html">Discuss a lot</a><a class="btn btn--line-dark" href="buyers.html">Become a buyer</a></div>
        <p class="cta__direct">Souren Ohanian · <a href="mailto:soureno@trekstone.net">soureno@trekstone.net</a></p></div>
      </div>
    </section>''',
    'buyer': '''<section class="cta on-dark" aria-labelledby="cta-title">
      <div class="wrap cta__in">
        <div><p class="eyebrow rv">For brands</p><h2 class="title rv" style="--d:1;margin-top:20px" id="cta-title">Holding excess inventory <em>of your own?</em></h2><p class="lead rv" style="--d:2">Tell us what you have and where it is. We will come back with a grading and routing plan.</p></div>
        <div class="rv" style="--d:2"><div class="btns"><a class="btn btn--white" href="contact.html">Discuss a lot</a><a class="btn btn--line-dark" href="brand-protection.html">See the controls</a></div></div>
      </div>
    </section>''',
}


def read(rel):
    return open(os.path.join(HERE, rel), encoding='utf-8').read()


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()[:10]


def countries():
    import pycountry
    fix = {'Congo, The Democratic Republic of the': 'Congo (Democratic Republic)', 'Micronesia, Federated States of': 'Micronesia', 'Palestine, State of': 'Palestine',
           'Virgin Islands, British': 'British Virgin Islands', 'Virgin Islands, U.S.': 'U.S. Virgin Islands', 'Korea, Republic of': 'South Korea',
           "Korea, Democratic People's Republic of": 'North Korea', 'Russian Federation': 'Russia', 'Iran, Islamic Republic of': 'Iran', 'Viet Nam': 'Vietnam',
           "Lao People's Democratic Republic": 'Laos', 'Syrian Arab Republic': 'Syria', 'Tanzania, United Republic of': 'Tanzania', 'Moldova, Republic of': 'Moldova',
           'Bolivia, Plurinational State of': 'Bolivia', 'Venezuela, Bolivarian Republic of': 'Venezuela', 'Taiwan, Province of China': 'Taiwan',
           'Brunei Darussalam': 'Brunei', 'Bonaire, Sint Eustatius and Saba': 'Bonaire, Sint Eustatius and Saba', 'Holy See (Vatican City State)': 'Vatican City',
           'Saint Helena, Ascension and Tristan da Cunha': 'Saint Helena', 'Macao': 'Macau', 'Türkiye': 'Türkiye', "Côte d'Ivoire": "Côte d'Ivoire"}
    drop = {'Antarctica', 'Bouvet Island', 'Heard Island and McDonald Islands', 'French Southern Territories', 'South Georgia and the South Sandwich Islands',
            'United States Minor Outlying Islands', 'British Indian Ocean Territory'}
    names = set()
    for c in pycountry.countries:
        n = getattr(c, 'common_name', None) or c.name
        n = fix.get(c.name, fix.get(n, n))
        if n not in drop: names.add(n)
    import unicodedata
    key = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    names = sorted(names, key=key)
    assert 'United States' in names and 'United Kingdom' in names and 'South Korea' in names, 'country names'
    return names


def main():
    preview = '--preview' in sys.argv
    sprite, boxes, line_icons = icons.build()
    css = read('src/css/site.css'); js = read('src/js/site.js')
    js = js.replace('__ENDPOINT__', ENDPOINT).replace('__SITE_KEY__', SITE_KEY).replace('__LIVE_HOSTS__', json.dumps(LIVE_HOSTS))
    names = countries()
    country_opts = '<option value="" selected disabled>Select a country</option>' + ''.join(f'<option>{n}</option>' for n in names)
    year = '2026'
    icon_uri, _ = icons.favicon(open(os.path.join(HERE, 'brand/logo-path.txt'), encoding='utf-8').read())
    region_map = hexmap_svg()

    def render(page, root='', inline_sprite=False, css_href=None, js_href=None):
        sp = '' if inline_sprite else root + 'assets/img/sprite.svg'

        def use(i): return f'<use href="{sp}#{i}"/>'

        def svg_ic(sym, extra=''):
            return f'<svg class="ic{extra}" aria-hidden="true" focusable="false">{use(sym)}</svg>'

        def ic(name, mods):
            assert name in line_icons, ('unknown icon', name)
            return svg_ic('i-' + name, ''.join(' ' + x for x in mods))

        def hx(name, mods, brand=False):
            if brand: assert 'b-' + name in boxes, ('unknown TREKSTONE icon', name)
            else: assert name in line_icons, ('unknown icon', name)
            cls = 'hx' + ''.join(f' hx--{x}' for x in mods)
            return f'<span class="{cls}">' + (svg_ic('b-' + name, ' ic--fill') if brand else svg_ic('i-' + name)) + '</span>'

        def grade(m):
            g, mod = m.group(1), m.group(2)
            return (f'<svg class="grade grade--{g}{" grade--" + mod if mod else ""}" viewBox="{boxes["g-" + g]}" role="img" aria-label="Grade {g.upper()}">{use("g-" + g)}</svg>')

        def logo(m):
            a11y = 'aria-hidden="true" focusable="false"' if m.group(1) else 'role="img" aria-label="TREKSTONE"'
            return f'<svg class="logo" viewBox="0 0 3491.72 511.92" {a11y}>{use("logo")}</svg>'

        def tokens(t):
            mods = lambda m: [x for x in m.group(2).split(':') if x]
            t = re.sub(r'\{\{ic:([\w-]+)((?::[\w-]+)*)\}\}', lambda m: ic(m.group(1), mods(m)), t)
            t = re.sub(r'\{\{hx:([\w-]+)((?::[\w-]+)*)\}\}', lambda m: hx(m.group(1), mods(m)), t)
            t = re.sub(r'\{\{bx:([\w-]+)((?::[\w-]+)*)\}\}', lambda m: hx(m.group(1), mods(m), brand=True), t)
            t = re.sub(r'\{\{grade:([a-d])(?::(\w+))?\}\}', grade, t)
            t = re.sub(r'\{\{logo(:plain)?\}\}', logo, t)
            t = (t.replace('{{map}}', region_map).replace('{{countries}}', country_opts).replace('{{year}}', year).replace('{{login}}', LOGIN)
                 .replace('{{endpoint}}', ENDPOINT))
            return t

        current = page['out']
        nav = ''.join(f'<a href="{root}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>' for label, href in NAV)
        body = read(f'src/pages/{page["src"]}.html')
        header = read('src/partials/header.html').replace('{{nav}}', nav)
        footer = read('src/partials/footer.html')
        cta = CTA.get(page.get('cta') or '', '')
        main = tokens(header) + '\n  <main id="main">\n' + tokens(body).rstrip('\n') + ('\n    ' + tokens(cta) if cta else '') + '\n  </main>\n' + tokens(footer)
        if root:   # the not-found page is served from any address, so its links start at the site root
            main = re.sub(r'(href|src|srcset)="(?!https?:|mailto:|tel:|#|/|data:)', lambda m: f'{m.group(1)}="{root}', main)
        assert '{{' not in main, (page['src'], re.findall(r'\{\{[^}]*\}\}', main)[:5])
        url = SITE + ('' if page['out'] == 'index.html' else page['out'])
        ld = ''
        if page['out'] == 'index.html':
            ld = '<script type="application/ld+json">' + json.dumps({
                '@context': 'https://schema.org', '@type': 'Organization', 'name': 'TREKSTONE', 'url': SITE, 'logo': SITE + 'assets/img/trekstone-logo-ink.svg',
                'email': 'soureno@trekstone.net', 'telephone': '+1-424-387-9213',
                'address': {'@type': 'PostalAddress', 'streetAddress': '580 Silver Spur Road', 'addressLocality': 'Rancho Palos Verdes', 'addressRegion': 'CA', 'postalCode': '90275', 'addressCountry': 'US'}},
                ensure_ascii=False, separators=(',', ':')) + '</script>\n  '
        robots = '<meta name="robots" content="noindex" />\n  ' if page.get('noindex') else ''
        hero_preload = ('<link rel="preload" href="assets/img/hero-globe-1920.webp" as="image" type="image/webp" media="(min-width: 641px)" fetchpriority="high" />\n  '
                        '<link rel="preload" href="assets/img/hero-globe-m.webp" as="image" type="image/webp" media="(max-width: 640px)" fetchpriority="high" />\n  ') if page['out'] == 'index.html' else ''
        head = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#0A0A0A" />
  <title>{page['title']}</title>
  <meta name="description" content="{page['desc']}" />
  {robots}<link rel="canonical" href="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="TREKSTONE" />
  <meta property="og:title" content="{page['title']}" />
  <meta property="og:description" content="{page['desc']}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}assets/img/share.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="TREKSTONE. Excess inventory, under your control." />
  <meta name="twitter:card" content="summary_large_image" />
  {ld}<link rel="icon" href="{icon_uri}" type="image/svg+xml" />
  <link rel="preload" href="{root}assets/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="{root}assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin />
  {hero_preload}<link rel="stylesheet" href="{css_href or root + 'assets/css/site.css?v=' + sha(css)}" />
  <script>document.documentElement.className='js'</script>
  <noscript><style>.js .rv{{opacity:1;transform:none}}</style></noscript>
</head>
<body class="{page.get('body', '')}">
  {sprite if inline_sprite else ''}<a class="skip" href="#main">Skip to content</a>
'''
        tail = f'  <script defer src="{js_href or root + "assets/js/site.js?v=" + sha(js)}"></script>\n</body>\n</html>\n'
        return head + main + tail

    def emit(dest, **kw):
        os.makedirs(os.path.join(dest, 'assets/css'), exist_ok=True); os.makedirs(os.path.join(dest, 'assets/js'), exist_ok=True)
        os.makedirs(os.path.join(dest, 'assets/fonts'), exist_ok=True); os.makedirs(os.path.join(dest, 'assets/img'), exist_ok=True)
        sizes = {}
        for page in PAGES:
            html = render(page, root=page.get('root', ''), **kw)
            open(os.path.join(dest, page['out']), 'w', encoding='utf-8', newline='\n').write(html); sizes[page['out']] = len(html.encode())
        return sizes

    # ---------- the site ----------
    sizes = emit(REPO)
    open(os.path.join(REPO, 'assets/css/site.css'), 'w', encoding='utf-8', newline='\n').write(css)
    open(os.path.join(REPO, 'assets/js/site.js'), 'w', encoding='utf-8', newline='\n').write(js)
    open(os.path.join(REPO, 'assets/img/sprite.svg'), 'w', encoding='utf-8', newline='\n').write(
        sprite.replace('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">', '<svg xmlns="http://www.w3.org/2000/svg">'))
    V = os.path.join(HERE, 'vendor/node_modules/@fontsource-variable')
    shutil.copy(os.path.join(V, 'archivo/files/archivo-latin-wdth-normal.woff2'), os.path.join(REPO, 'assets/fonts/'))
    shutil.copy(os.path.join(V, 'inter/files/inter-latin-wght-normal.woff2'), os.path.join(REPO, 'assets/fonts/'))
    pages_for_map = [p for p in PAGES if not p.get('noindex')]
    open(os.path.join(REPO, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{SITE}{"" if p["out"] == "index.html" else p["out"]}</loc></url>\n' for p in pages_for_map) + '</urlset>\n')
    open(os.path.join(REPO, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n')
    for old in ('assets/js/index.js', 'assets/js/scenes3d.js'):
        if os.path.exists(os.path.join(REPO, old)): os.remove(os.path.join(REPO, old))
    print('site:', ' · '.join(f'{k} {v}' for k, v in sizes.items()), f'· css {len(css)} · js {len(js)} · sprite {len(sprite)}')

    # ---------- a self-contained copy for the private preview ----------
    if preview:
        import base64
        P = os.path.join(HERE, 'preview'); shutil.rmtree(P, ignore_errors=True)
        b64 = lambda f: base64.b64encode(open(f, 'rb').read()).decode()
        pcss = css.replace('url(../fonts/archivo-latin-wdth-normal.woff2)', 'url(data:font/woff2;base64,' + b64(os.path.join(V, 'archivo/files/archivo-latin-wdth-normal.woff2')) + ')')
        pcss = pcss.replace('url(../fonts/inter-latin-wght-normal.woff2)', 'url(data:font/woff2;base64,' + b64(os.path.join(V, 'inter/files/inter-latin-wght-normal.woff2')) + ')')
        assert '../fonts/' not in pcss
        emit(P, inline_sprite=True, css_href='assets/css/site.css', js_href='assets/js/site.js')
        open(os.path.join(P, 'assets/css/site.css'), 'w', encoding='utf-8', newline='\n').write(pcss)
        open(os.path.join(P, 'assets/js/site.js'), 'w', encoding='utf-8', newline='\n').write(js)
        os.rmdir(os.path.join(P, 'assets/fonts'))
        # the preview's first page is published as a fragment: no doctype, html, head or body tags of its own
        full = open(os.path.join(P, 'index.html'), encoding='utf-8').read()
        body = full[full.index('<body'):]; body = body[body.index('>') + 1:body.rindex('</body>')]
        cls = re.search(r'<body class="([^"]*)"', full).group(1)
        boot = ('<script>document.documentElement.className="js";document.documentElement.lang="en";'
                + (f'document.body.classList.add({", ".join(json.dumps(c) for c in cls.split())});' if cls.strip() else '') + '</script>')
        frag = ('<title>TREKSTONE Website</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
                '<link rel="stylesheet" href="assets/css/site.css" />\n' + boot + '\n' + body.strip() + '\n')
        for bad in (r'<!doctype', r'<html[\s>]', r'<head[\s>]', r'<body[\s>]', r'</body>', r'</html>', r'</head>'):
            assert not re.search(bad, frag, re.I), bad
        open(os.path.join(P, 'index.html'), 'w', encoding='utf-8', newline='\n').write(frag)
        os.remove(os.path.join(P, '404.html'))
        # the fonts travel inside the stylesheet here, and the link-preview image is only for the real address
        for name in os.listdir(P):
            if name.endswith('.html') and name != 'index.html':
                t = open(os.path.join(P, name), encoding='utf-8').read()
                t, n = re.subn(r'[ \t]*<link rel="preload" href="assets/fonts/[^"]+"[^>]*>\n', '', t); assert n == 2, (name, n)
                t = re.sub(r'[ \t]*<meta property="og:image[^"]*"[^>]*>\n', '', t)
                assert 'assets/fonts/' not in t and 'share.jpg' not in t, name
                open(os.path.join(P, name), 'w', encoding='utf-8', newline='\n').write(t)
        used = set()
        for name in os.listdir(P):
            if name.endswith('.html'):
                for m in re.finditer(r'assets/img/[\w./-]+\.(?:webp|svg|jpg|png)', open(os.path.join(P, name), encoding='utf-8').read()): used.add(m.group(0))
        for m in re.finditer(r'assets/img/[\w./-]+\.(?:webp|svg|jpg|png)', pcss + js): used.add(m.group(0))
        for rel in sorted(used):
            shutil.copy(os.path.join(REPO, rel), os.path.join(P, rel))
        print('preview:', len(frag), 'bytes for the first page ·', len(pcss), 'css ·', len(used), 'images')


if __name__ == '__main__':
    main()
