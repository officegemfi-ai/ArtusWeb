"""Recolour TREKSTONE's globe banner: same picture, the night blue swapped for the site's black, with the dots in forest green.
Reads images/brand-protection-banner.jpg (from trekstone.net) and writes the two hero images that assets2.py copies into the site."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = np.asarray(Image.open(HERE + '/images/brand-protection-banner.jpg').convert('RGB')).astype(np.float32)
H, W, _ = src.shape
lum = lambda a: 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
# background per row, from the empty left quarter of the banner
bg = np.median(src[:, :420, :], axis=1)                      # (H, 3)
bg_l = lum(bg)                                                # (H,)
# how much "dot" a pixel holds: its blue above the row's background, against the brightest dots
d = (src[..., 2] - bg[:, None, 2])
t = np.clip(d / np.percentile(d, 99.7), 0, 1)
def variant(dot_rgb, bg_top, bg_bottom, gain=1.0):
    k = (bg_l - bg_l.min()) / max(1e-6, bg_l.max() - bg_l.min())          # 1 at the lightest row, 0 at the darkest
    base = bg_bottom[None, :] + (bg_top - bg_bottom)[None, :] * k[:, None]  # (H, 3) neutral ground with the same fall-off
    out = base[:, None, :] + (np.array(dot_rgb, np.float32)[None, None, :] - base[:, None, :]) * np.clip(t * gain, 0, 1)[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))
im = variant((70, 134, 100), np.array([22, 22, 22], np.float32), np.array([10, 10, 10], np.float32))
im.save(f'{HERE}/images/hero-globe-forest-1920.webp', 'WEBP', quality=82, method=6)
im.crop((760, 0, 1680, 980)).save(f'{HERE}/images/hero-globe-forest-m.webp', 'WEBP', quality=80, method=6)
print('forest', os.path.getsize(f'{HERE}/images/hero-globe-forest-1920.webp'), os.path.getsize(f'{HERE}/images/hero-globe-forest-m.webp'))
