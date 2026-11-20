import { readFileSync } from 'node:fs';
import { feature } from 'topojson-client';
import { geoCentroid } from 'd3-geo';
const topo = JSON.parse(readFileSync(new URL('../vendor/node_modules/world-atlas/countries-110m.json', import.meta.url)));
const fc = feature(topo, topo.objects.countries);
console.log(fc.features.length);
console.log(fc.features.map(f => { const c = geoCentroid(f); return `${f.properties.name}(${c[0].toFixed(0)},${c[1].toFixed(0)})`; }).join(' | '));
