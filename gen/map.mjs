// World map as a field of hexagon dots, grouped into six sales regions.
// Land shapes: Natural Earth 1:110m via world-atlas (public domain). Output: src/gen/world-hex.json
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { feature } from 'topojson-client';
import { geoNaturalEarth1, geoContains, geoBounds } from 'd3-geo';
const topo = JSON.parse(readFileSync(new URL('../vendor/node_modules/world-atlas/countries-110m.json', import.meta.url)));
const all = feature(topo, topo.objects.countries).features.filter(f => !['Antarctica', 'Fr. S. Antarctic Lands'].includes(f.properties.name));
const NA = new Set(['United States of America', 'Canada', 'Greenland']);
const LATAM = new Set(['Mexico', 'Guatemala', 'Belize', 'Honduras', 'El Salvador', 'Nicaragua', 'Costa Rica', 'Panama', 'Cuba', 'Haiti', 'Dominican Rep.', 'Jamaica', 'Bahamas', 'Puerto Rico',
  'Trinidad and Tobago', 'Colombia', 'Venezuela', 'Guyana', 'Suriname', 'Ecuador', 'Peru', 'Bolivia', 'Brazil', 'Paraguay', 'Uruguay', 'Argentina', 'Chile', 'Falkland Is.']);
const EU = new Set(['Norway', 'Sweden', 'Finland', 'Denmark', 'Iceland', 'United Kingdom', 'Ireland', 'Portugal', 'Spain', 'France', 'Belgium', 'Netherlands', 'Luxembourg', 'Germany', 'Switzerland',
  'Austria', 'Italy', 'Slovenia', 'Croatia', 'Bosnia and Herz.', 'Serbia', 'Montenegro', 'Kosovo', 'Macedonia', 'Albania', 'Greece', 'Bulgaria', 'Romania', 'Moldova', 'Ukraine', 'Belarus', 'Poland',
  'Czechia', 'Slovakia', 'Hungary', 'Lithuania', 'Latvia', 'Estonia', 'Cyprus', 'N. Cyprus', 'Georgia', 'Armenia', 'Azerbaijan']);
const ME = new Set(['Turkey', 'Syria', 'Lebanon', 'Israel', 'Palestine', 'Jordan', 'Iraq', 'Iran', 'Kuwait', 'Saudi Arabia', 'Qatar', 'United Arab Emirates', 'Oman', 'Yemen']);
const AF = new Set(['Tanzania', 'W. Sahara', 'Dem. Rep. Congo', 'Somalia', 'Kenya', 'Sudan', 'Chad', 'South Africa', 'Lesotho', 'Zimbabwe', 'Botswana', 'Namibia', 'Senegal', 'Mali', 'Mauritania', 'Benin',
  'Niger', 'Nigeria', 'Cameroon', 'Togo', 'Ghana', "Côte d'Ivoire", 'Guinea', 'Guinea-Bissau', 'Liberia', 'Sierra Leone', 'Burkina Faso', 'Central African Rep.', 'Congo', 'Gabon', 'Eq. Guinea', 'Zambia',
  'Malawi', 'Mozambique', 'eSwatini', 'Angola', 'Burundi', 'Madagascar', 'Gambia', 'Tunisia', 'Algeria', 'Eritrea', 'Morocco', 'Egypt', 'Libya', 'Ethiopia', 'Djibouti', 'Somaliland', 'Uganda', 'Rwanda', 'S. Sudan']);
function region(name, lon) {
  if (name === 'Russia') return lon < 60 && lon > 0 ? 'eu' : 'apac';
  if (name === 'France' && lon < -30) return 'latam';
  if (NA.has(name)) return 'na'; if (LATAM.has(name)) return 'latam'; if (EU.has(name)) return 'eu';
  if (ME.has(name)) return 'me'; if (AF.has(name)) return 'af'; return 'apac';
}
const W = 2000, DX = 20, DY = 17;
const proj = geoNaturalEarth1().fitWidth(W, { type: 'FeatureCollection', features: all });
// vertical extent of the land we keep
let ymin = Infinity, ymax = -Infinity;
for (const f of all) { const [[w, s], [e, n]] = geoBounds(f); for (const p of [[w, s], [e, n], [w, n], [e, s]]) { const q = proj(p); if (q) { ymin = Math.min(ymin, q[1]); ymax = Math.max(ymax, q[1]); } } }
const boxes = all.map(f => ({ f, b: geoBounds(f) }));
const inBox = (b, lon, lat) => { const [[w, s], [e, n]] = b; return lat >= s && lat <= n && (w <= e ? lon >= w && lon <= e : lon >= w || lon <= e); };
const out = { na: [], latam: [], eu: [], me: [], af: [], apac: [] };
let rows = 0;
for (let y = Math.floor(ymin), r = 0; y <= ymax; y += DY, r++) {
  rows++;
  for (let x = (r % 2 ? DX / 2 : 0); x <= W; x += DX) {
    const ll = proj.invert([x, y]); if (!ll || !isFinite(ll[0]) || Math.abs(ll[0]) > 180 || Math.abs(ll[1]) > 90) continue;
    const back = proj(ll); if (!back || Math.abs(back[0] - x) > 0.5 || Math.abs(back[1] - y) > 0.5) continue;   // outside the projected sphere
    for (const { f, b } of boxes) {
      if (!inBox(b, ll[0], ll[1])) continue;
      if (geoContains(f, ll)) { out[region(f.properties.name, ll[0])].push([Math.round(x), Math.round(y - ymin)]); break; }
    }
  }
}
const H = Math.ceil(ymax - ymin) + DY;
mkdirSync(new URL('../src/gen/', import.meta.url), { recursive: true });
writeFileSync(new URL('../src/gen/world-hex.json', import.meta.url), JSON.stringify({ W, H, DX, DY, regions: out }));
console.log('size', W, H, 'rows', rows, Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v.length])), 'total', Object.values(out).reduce((a, v) => a + v.length, 0));
