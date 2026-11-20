"""Cut a shot sheet into pieces of two columns for viewing. Usage: split.py PAGE WIDTH"""
import sys
from PIL import Image
page, W = sys.argv[1], int(sys.argv[2]); per = int(sys.argv[3]) if len(sys.argv) > 3 else 2
im = Image.open(f'shots/{page}-{W}-sheet.png'); col = W + 14; n = (im.width - 14) // col
for k, i in enumerate(range(0, n, per)):
    part = im.crop((i * col, 0, min(im.width, (i + per) * col + 14), im.height)); part.save(f'shots/{page}-{W}-p{k}.png'); print(f'shots/{page}-{W}-p{k}.png', part.size)
