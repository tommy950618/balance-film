"""crop sequence: python seq.py frames_dir out.jpg x0 y0 x1 y1 scale cols f1,f2,..."""
import sys, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7]); k = float(sys.argv[7]); cols = int(sys.argv[8]); fr = [int(v) for v in sys.argv[9].split(',')]
ims = []
for n in fr:
    im = Image.open(os.path.join(d, 'f_%04d.jpg' % n)).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    dr = ImageDraw.Draw(im); dr.rectangle([0, 0, 96, 18], fill=(0, 0, 0)); dr.text((4, 3), 'f%03d %.2fs' % (n, (n - 1) / 24), fill=(255, 255, 0))
    ims.append(im)
w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
s = Image.new('RGB', (cols * w + (cols + 1) * 6, rows * h + (rows + 1) * 6), (255, 255, 255))
for i, im in enumerate(ims):
    s.paste(im, (6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 6)))
s.save(out, quality=92); print(out, s.size)
