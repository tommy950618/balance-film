"""contact sheet from extracted frames: python sheet_t.py frames_dir out.jpg step cols width"""
import sys, os, glob
from PIL import Image, ImageDraw
d, out, step, cols, wd = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
fs = sorted(glob.glob(os.path.join(d, 'f_*.jpg')))
pick = fs[::step]
ims = []
for p in pick:
    im = Image.open(p).convert('RGB'); n = int(os.path.basename(p)[2:6])
    im = im.resize((wd, int(im.height * wd / im.width)), Image.LANCZOS)
    dr = ImageDraw.Draw(im); dr.rectangle([0, 0, 92, 18], fill=(0, 0, 0)); dr.text((4, 3), 'f%03d %.2fs' % (n, (n - 1) / 24), fill=(255, 255, 0))
    ims.append(im)
h = ims[0].height; rows = (len(ims) + cols - 1) // cols
s = Image.new('RGB', (cols * wd + (cols + 1) * 6, rows * h + (rows + 1) * 6), (255, 255, 255))
for i, im in enumerate(ims):
    s.paste(im, (6 + (i % cols) * (wd + 6), 6 + (i // cols) * (h + 6)))
s.save(out, quality=90); print(out, s.size, len(ims), 'frames')
