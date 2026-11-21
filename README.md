# TREKSTONE website: sources and build

This branch holds the hand-written sources of the TREKSTONE website and the small script that turns them into the
finished site. The finished site itself lives on the `trekstone` branch of this repository.

## What is here

| Path | What it is |
| --- | --- |
| `src/pages/` | One file per page: home, brand protection, how it works, sustainability, buyers, contact, privacy, terms, not found |
| `src/partials/` | The header and footer shared by every page |
| `src/css/site.css`, `src/js/site.js` | The one stylesheet and the one script |
| `build.py` | Puts pages, header and footer together and writes the site |
| `icons.py`, `brand/` | The icon set: TREKSTONE's own logo, grade marks and pictograms, plus line icons from Lucide (ISC licence) |
| `hexmap.py`, `gen/map.mjs`, `src/gen/world-hex.json` | The hexagon world map on the brand protection page (land shapes: Natural Earth) |
| `recolor.py`, `assets2.py`, `images/` | The hero globe in black and forest green, made from TREKSTONE's own banner, and the forest photograph |
| `share.py` | The link-preview image |
| `sanity.py`, `interact.py`, `formtest.py`, `emu.py`, `notch.py`, `tops.py`, `shot.py`, `split.py`, `handover.py` | Checks and screenshots |
| `story.py`, `storymodes.py` | The home banner animation: frame-by-frame captures, and checks that it stays off on phones, with reduced motion, without JavaScript and in print |

Pages are plain HTML with a few `{{tokens}}`: `{{ic:name}}` for an icon, `{{hx:name}}` and `{{bx:name}}` for an icon in a
hexagon tile, `{{grade:a}}` for a grade mark, `{{logo}}`, `{{map}}`, `{{countries}}`, `{{login}}`.

## Building

```
git clone -b trekstone https://github.com/officegemfi-ai/ArtusWeb site
git clone -b trekstone-source https://github.com/officegemfi-ai/ArtusWeb builder
cd builder/vendor && npm ci && cd .. && ln -s vendor/node_modules node_modules
pip install pycountry pillow numpy playwright
TREKSTONE_SITE=../site python3 build.py            # writes the site
TREKSTONE_SITE=../site python3 build.py --preview  # also writes a self-contained copy into preview/
```

`TREKSTONE_SITE` is the folder the site is written into. The checks expect that folder served at
`http://127.0.0.1:8815/` (`python3 -m http.server 8815 --bind 127.0.0.1`).

## The home banner animation

On larger screens the home banner is held in place while the visitor scrolls: it shrinks into a square frame with the headline
split around it, then turns into the hexagon of the logo mark and the letters of the logo follow. The markup is at the top of
`src/pages/home.html` (`.hs`), the styles are under "home: on scroll the banner folds" in `site.css`, and the script is the block
with the same heading in `site.js`; its timings are the numbers in `apply()`. `{{herologo}}` writes the real logo as separate
shapes (`icons.logo_pieces`) so that the mark and each letter can appear on their own.

## The forms

The buyer sign-up and the contact form post to the `site-forms` function of the TREKSTONE Supabase project, which checks
every value and stores it in the `buyer_applications` and `enquiries` tables. The tables are closed to the public keys.
The function and the database setup are kept in that Supabase project (function `site-forms`, migration
`website_forms`). The address of the function, the site's public key and the list of web addresses that may send forms
are at the top of `build.py`; the same list of addresses is in the function and both must be changed together.
