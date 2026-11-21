"""Images for the site: the globe banner in black and forest green and the forest photograph, written into the site folder.
The other photographs (rails, warehouse) already live in the site folder; anything the pages do not use is removed."""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(os.environ.get('TREKSTONE_SITE', '/home/claude/artusweb'), 'assets/img')
KEEP = {'hero-globe-1920.webp', 'hero-globe-m.webp', 'forest-1600.webp', 'forest-800.webp', 'earth-1920.webp', 'earth-960.webp', 'warehouse-scan.webp', 
        'rails-640.webp', 'rails-1000.webp', 'rails-1400.webp', 'trekstone-logo-ink.svg', 'share.jpg', 'sprite.svg'}
for name in ('1920', 'm'):
    shutil.copy(os.path.join(HERE, f'images/hero-globe-forest-{name}.webp'), os.path.join(IMG, f'hero-globe-{name}.webp'))
from PIL import Image
src_forest = os.path.join(HERE, 'images/forest-bw.webp')
fim = Image.open(src_forest).convert('L').convert('RGB')
fim.save(os.path.join(IMG, 'forest-1600.webp'), 'WEBP', quality=46, method=6)
fim.resize((800, 450), Image.LANCZOS).save(os.path.join(IMG, 'forest-800.webp'), 'WEBP', quality=52, method=6)
# the earth from orbit, toned in the site's forest greens: space stays black, the planet runs from deep forest to a pale mint in the clouds
import numpy as np
STOPS = [(0.00, (4, 7, 6)), (0.16, (11, 24, 18)), (0.40, (31, 61, 47)), (0.60, (46, 94, 69)), (0.80, (111, 168, 138)), (1.00, (214, 236, 224))]
lum = np.asarray(Image.open(os.path.join(HERE, 'images/earth-bw.webp')).convert('L')).astype(np.float32) / 255.0
xs = np.array([s[0] for s in STOPS], np.float32)
earth = Image.fromarray(np.clip(np.stack([np.interp(lum, xs, np.array([s[1][c] for s in STOPS], np.float32)) for c in range(3)], axis=-1) + .5, 0, 255).astype(np.uint8))
earth.resize((1920, 1080), Image.LANCZOS).save(os.path.join(IMG, 'earth-1920.webp'), 'WEBP', quality=74, method=6)
earth.resize((960, 540), Image.LANCZOS).save(os.path.join(IMG, 'earth-960.webp'), 'WEBP', quality=72, method=6)
removed = []
for f in sorted(os.listdir(IMG)):
    if f not in KEEP: os.remove(os.path.join(IMG, f)); removed.append(f)
print('kept', sorted(os.listdir(IMG))); print('removed', removed)
