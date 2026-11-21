"""One inline SVG sprite: the TREKSTONE logo, TREKSTONE's own icons (grade marks, four pictograms),
supporting line icons from Lucide (ISC licence) and a few drawn here in the same line style."""
import base64, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
LUCIDE = os.path.join(HERE, 'vendor/node_modules/lucide-static/icons')
LINE = {  # id: lucide file
    'package': 'package', 'tag': 'tag', 'route': 'route', 'doc': 'file-check', 'shield-check': 'shield-check', 'handshake': 'handshake',
    'stamp': 'stamp', 'scissors': 'scissors', 'eye-off': 'eye-off', 'map': 'map-pinned', 'globe': 'globe', 'store': 'store',
    'donate': 'heart-handshake', 'recycle': 'recycle', 'truck': 'truck', 'warehouse': 'warehouse', 'clipboard': 'clipboard-check',
    'review': 'search-check', 'sign': 'signature', 'send': 'send', 'mail': 'mail', 'phone': 'phone', 'pin': 'map-pin',
    'building': 'building-2', 'user': 'user-round-check', 'shirt': 'shirt', 'bag': 'shopping-bag', 'boxes': 'boxes', 'scale': 'scale',
    'landmark': 'landmark', 'chart': 'chart-column', 'lock': 'lock', 'login': 'log-in', 'badge': 'badge-check', 'layers': 'layers',
    'repeat': 'repeat', 'calendar': 'calendar-days', 'container': 'container', 'ban': 'ban',
}
CUSTOM = {  # drawn for TREKSTONE on the same 24-unit grid, same stroke
    'shoe': '<path d="M2.5 8.5C2.5 7.7 3.1 7 4 7h1.2c.5 0 .9.3 1.1.7.7 1.4 2 2.3 3.6 2.3.6 0 1.1-.3 1.5-.7l1-1.1c.5-.5 1.2-.6 1.8-.2l5.1 3.3c1.4.9 2.2 2.4 2.2 4.1V16a2 2 0 0 1-2 2h-15a2 2 0 0 1-2-2z"/><path d="M2.5 14.8h19"/><path d="M13.6 10.4l-1.3 1.5"/><path d="M15.8 11.8l-1.3 1.5"/>',
}
BRAND = {'shield': 'Shield', 'globe': 'Globe', 'compliance': 'Compliance', 'sustainability': 'Sustainability'}
GRADES = {'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'}


def _inner(svg):
    body = re.search(r'<svg\b[^>]*>(.*)</svg>', svg, re.S).group(1)
    return re.sub(r'\s+', ' ', re.sub(r'>\s+<', '><', body)).strip()


def _paths(svg):
    return ''.join(f'<path d="{d}"/>' for d in re.findall(r'<path\b[^>]*?\bd="([^"]+)"', svg)), re.search(r'viewBox="([^"]+)"', svg).group(1)


def favicon(logo_path):
    """The browser-tab icon: the hexagon mark of the logo, white on black, as a data URI."""
    subs = re.findall(r'M[^M]*', logo_path)
    mark = ''.join(subs[i] for i in (0, 1, 6, 7))          # the hexagon mark; the wordmark starts further right
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-133 -100 711 711"><rect x="-133" y="-100" width="711" height="711" fill="#0A0A0A"/>'
           f'<path fill="#fff" fill-rule="evenodd" d="{mark}"/></svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode(), svg


def logo_pieces():
    """The real logo, split into its own shapes: the four bands of the hexagon mark, then the nine letters (R and O keep their counters)."""
    subs = re.findall(r'M[^M]*', open(os.path.join(HERE, 'brand/logo-path.txt'), encoding='utf-8').read().strip())
    assert len(subs) == 15, len(subs)
    mark = [subs[i] for i in (0, 1, 6, 7)]
    letters = [''.join(subs[i] for i in grp) for grp in ([2], [3, 4], [5], [8], [9], [10], [11, 12], [13], [14])]
    return mark, letters


def build():
    out, boxes = [], {}
    logo = open(os.path.join(HERE, 'brand/logo-path.txt'), encoding='utf-8').read().strip()
    out.append(f'<symbol id="logo" viewBox="0 0 3491.72 511.92"><path fill-rule="evenodd" d="{logo}"/></symbol>')
    for key, name in BRAND.items():
        p, box = _paths(open(os.path.join(HERE, f'brand/icons/{name}.svg'), encoding='utf-8').read())
        out.append(f'<symbol id="b-{key}" viewBox="{box}">{p}</symbol>'); boxes['b-' + key] = box
    for key, name in GRADES.items():
        p, box = _paths(open(os.path.join(HERE, f'brand/icons/{name}.svg'), encoding='utf-8').read())
        out.append(f'<symbol id="g-{key}" viewBox="{box}">{p}</symbol>'); boxes['g-' + key] = box
    for key, name in LINE.items():
        out.append(f'<symbol id="i-{key}" viewBox="0 0 24 24">{_inner(open(os.path.join(LUCIDE, name + ".svg"), encoding="utf-8").read())}</symbol>')
    for key, body in CUSTOM.items():
        out.append(f'<symbol id="i-{key}" viewBox="0 0 24 24">{body}</symbol>')
    sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>' + ''.join(out) + '</defs></svg>'
    return sprite, boxes, set(LINE) | set(CUSTOM)


if __name__ == '__main__':
    s, b, names = build(); print(len(s), sorted(names))
