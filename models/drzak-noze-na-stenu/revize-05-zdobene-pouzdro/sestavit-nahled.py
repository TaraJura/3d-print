#!/usr/bin/env python3
"""Compose labelled overviews from the real CAD renders and compare the front render with the STL.
Does not generate or alter CAD geometry. Writes prehled-navrhu.png and kontrola-nahledu.json only.
"""
from pathlib import Path
import hashlib
import json
import struct

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BG, INK, MUTED = '#f4f1ec', '#3a1014', '#6b5f5c'


def text(d, p, s, size=28, bold=False, color=INK):
    d.text(p, s, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color)


def fit(path, box):
    """Trim the white or wall margin of a render and scale it into box without distortion."""
    img = Image.open(path).convert('RGB')
    corner = Image.new('RGB', img.size, img.getpixel((2, 2)))
    bbox = ImageChops.difference(img, corner).point(lambda v: 255 if v > 12 else 0).getbbox()
    img = img.crop(bbox)
    scale = min(box[0] / img.width, box[1] / img.height)
    return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)


def paste(canvas, path, x, y, w, h, fill='#ffffff'):
    d = ImageDraw.Draw(canvas)
    d.rectangle((x, y, x + w, y + h), fill=fill)
    img = fit(ROOT / path, (w - 24, h - 24))
    canvas.paste(img, (x + (w - img.width) // 2, y + (h - img.height) // 2))


W, H = 2200, 2020
im = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(im)
text(d, (70, 40), 'ZDOBENÉ POUZDRO NA NŮŽ', 56, True)
text(d, (73, 116), 'Revize 05 · jeden díl · na stěnu · nůž se zasouvá shora · skutečná CAD geometrie, žádná textura', 28, color=MUTED)
TOP = 180
PANEL_H = 1290
paste(im, 'nahled-cad-celo.png', 70, TOP, 620, PANEL_H)
paste(im, 'nahled-cad-iso.png', 710, TOP, 760, PANEL_H, Image.open(ROOT / 'nahled-cad-iso.png').convert('RGB').getpixel((2, 2)))
paste(im, 'nahled-cad-rez.png', 1490, TOP, 640, PANEL_H)
y = TOP + PANEL_H + 12
text(d, (70, y), 'Čelo', 26, True)
text(d, (710, y), 'Šikmý pohled', 26, True)
text(d, (920, y + 2), 'stěna a hlavy vrutů jsou ilustrace', 23, color=MUTED)
text(d, (1490, y), 'Řez X = 0 s referenčním nožem a stěnou', 26, True)
y += 56
paste(im, 'nahled-cad-usti.png', 70, y, 820, 400)
facts = [
    ('Čepel (zadání)', '200 × 45 × 3 mm'),
    ('Dutina (návrh)', '218 × 47 × 4,4 mm = 200 + krček 10 + rezerva 8'),
    ('Čepel od stěny', '24 mm, za rukojetí 25 mm zbývá 11,5 mm'),
    ('Celý díl', '78 × 33,8 × 248 mm'),
    ('Dva vruty', 'Ø5,5 mm, vpravo nahoře a vlevo dole, skutečné vruty neznámé'),
    ('Tisk', 'svisle ústím nahoru, bez podpor, 1 kus'),
]
ty = y + 6
for label, value in facts:
    text(d, (920, ty), label, 25, True)
    text(d, (1290, ty), value, 25)
    ty += 56
text(d, (920, ty + 6), 'Tvar nože v řezu je ilustrace. Fit a tisk nejsou fyzicky ověřené.', 24, color=MUTED)
im.save(ROOT / 'prehled-navrhu.png')

# ---------- Front render against the STL: same silhouette, red material ----------
raw = (ROOT / 'stl/pouzdro-zdobene.stl').read_bytes()
count = struct.unpack_from('<I', raw, 80)[0]
assert len(raw) == 84 + count * 50
render = Image.open(ROOT / 'nahled-cad-celo.png').convert('RGB')
mask = render.convert('L').point(lambda v: 255 if v < 245 else 0)
x0, y0, x1, y1 = mask.getbbox()
tris = [struct.unpack_from('<9f', raw, 84 + 50 * i + 12) for i in range(count)]
xs = [t[j] for t in tris for j in (0, 3, 6)]
zs = [t[j] for t in tris for j in (2, 5, 8)]
sx, sz = (x1 - x0) / (max(xs) - min(xs)), (y1 - y0) / (max(zs) - min(zs))
drawn = Image.new('L', render.size, 0)
pen = ImageDraw.Draw(drawn)
for t in tris:
    pen.polygon([(x0 + (t[j] - min(xs)) * sx, y1 - (t[j + 2] - min(zs)) * sz) for j in (0, 3, 6)], fill=255)
area = lambda img: img.histogram()[255]
inter = area(ImageChops.multiply(mask, drawn))
union = area(ImageChops.lighter(mask, drawn))
pixels = [render.getpixel((x, y)) for x in range(0, render.width, 2) for y in range(0, render.height, 2) if mask.getpixel((x, y))]
red = sum(1 for r, g, b in pixels if r > 1.6 * g and r > 1.6 * b) / len(pixels)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = {
    'front_render': 'nahled-cad-celo.png', 'front_render_sha256': sha(ROOT / 'nahled-cad-celo.png'),
    'stl_sha256': sha(ROOT / 'stl/pouzdro-zdobene.stl'), 'fcstd_sha256': sha(ROOT / 'pouzdro.FCStd'),
    'silhouette_iou_with_stl_projection': inter / union, 'scale_px_per_mm': [sx, sz], 'red_pixel_share': red,
    'overview': 'prehled-navrhu.png', 'overview_sha256': sha(ROOT / 'prehled-navrhu.png'),
}
assert report['silhouette_iou_with_stl_projection'] > .985 and red > .9 and abs(sx - sz) / sx < .01, report
(ROOT / 'kontrola-nahledu.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('V05_PRESENTATION_OK', json.dumps({k: report[k] for k in ('silhouette_iou_with_stl_projection', 'red_pixel_share', 'scale_px_per_mm')}))
