"""SVG for the hexagon-dot world map: one <path> per region, hexagons with integer coordinates."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
REGIONS = [('na', 'North America'), ('latam', 'Latin America'), ('eu', 'Europe'), ('me', 'Middle East'), ('af', 'Africa'), ('apac', 'Asia Pacific')]


def hexmap_svg(cls='hm', title='World map drawn in hexagon dots'):
    d = json.load(open(HERE + '/src/gen/world-hex.json'))
    W, H = d['W'], d['H'] + 4
    paths = []
    for key, name in REGIONS:
        pts = sorted(d['regions'][key], key=lambda p: (p[1], p[0]))
        dd = ''.join(f'M{x},{y}l7,4v8l-7,4l-7-4v-8z' for x, y in pts)
        paths.append(f'<path class="{cls}__r" data-region="{key}" d="{dd}"/>')
    return (f'<svg class="{cls}" viewBox="-8 -2 {W + 16} {H + 20}" role="img" aria-label="{title}" preserveAspectRatio="xMidYMid meet">' + ''.join(paths) + '</svg>')


if __name__ == '__main__':
    s = hexmap_svg(); print(len(s))
    open(HERE + '/shots/hexmap-test.html', 'w').write('<body style="margin:0;background:#fff"><style>.hm{width:1200px;display:block;margin:30px auto}.hm__r{fill:#D9D9D4}.hm__r[data-region=latam],.hm__r[data-region=me],.hm__r[data-region=af]{fill:#2E5E45}</style>' + s + '</body>')
