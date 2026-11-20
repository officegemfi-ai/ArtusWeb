"""Images for the site: the globe banner in black and forest green and the forest photograph, written into the site folder.
The other photographs (rails, warehouse) already live in the site folder; anything the pages do not use is removed."""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(os.environ.get('TREKSTONE_SITE', '/home/claude/artusweb'), 'assets/img')
KEEP = {'hero-globe-1920.webp', 'hero-globe-m.webp', 'forest-1600.webp', 'forest-800.webp', 'warehouse-scan.webp', 
        'rails-640.webp', 'rails-1000.webp', 'rails-1400.webp', 'trekstone-logo-ink.svg', 'share.jpg', 'sprite.svg'}
for name in ('1920', 'm'):
    shutil.copy(os.path.join(HERE, f'images/hero-globe-forest-{name}.webp'), os.path.join(IMG, f'hero-globe-{name}.webp'))
from PIL import Image
src_forest = os.path.join(HERE, 'images/forest-bw.webp')
fim = Image.open(src_forest).convert('L').convert('RGB')
fim.save(os.path.join(IMG, 'forest-1600.webp'), 'WEBP', quality=46, method=6)
fim.resize((800, 450), Image.LANCZOS).save(os.path.join(IMG, 'forest-800.webp'), 'WEBP', quality=52, method=6)
removed = []
for f in sorted(os.listdir(IMG)):
    if f not in KEEP: os.remove(os.path.join(IMG, f)); removed.append(f)
print('kept', sorted(os.listdir(IMG))); print('removed', removed)
