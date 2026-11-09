#!/usr/bin/env python3
"""Sestaví popsaný přehled ze skutečných FreeCAD PNG; geometrii nemění."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
BG = (242, 244, 246)
INK = (28, 35, 43)
SUB = (77, 88, 101)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def f(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

canvas = Image.new('RGB', (2600, 1730), BG)
d = ImageDraw.Draw(canvas)
d.text((90, 47), 'Černá skříňka pod umyvadlo', fill=INK, font=f(63, True))
d.text((92, 136), '370 × 180 × 550 mm  ·  dvě přední otevírací dvířka', fill=SUB, font=f(37))
d.line((90, 205, 2510, 205), fill=(212, 217, 223), width=3)
for x, filename, label in ((30,'nahled-zavreno-cad.png','ZAVŘENO'),
                           (1330,'nahled-otevreno-cad.png','OTEVŘENO 90°')):
    source = Image.open(OUT/filename).convert('RGBA')
    source.thumbnail((1240,1240), Image.Resampling.LANCZOS)
    canvas.paste(source, (x+(1240-source.width)//2, 280), source)
    d.text((x+60,229), label, fill=INK, font=f(34, True))
d.line((90, 1515, 2510, 1515), fill=(212, 217, 223), width=3)
d.text((90,1550),'Skutečná CAD geometrie skříňky. Bílý obrys umyvadla je pouze schematický.', fill=SUB,font=f(30))
d.text((90,1602),'Otevřená záda a vršek; bez polic a prostřední příčky. Spoje a panty jsou návrh k ověření.', fill=SUB,font=f(28))
canvas.save(OUT/'nahled-skrinky.png', optimize=True)

# Samostatné obrázky dostanou stejně světlé pozadí; originální pixely
# CAD zůstávají beze změny kromě vložení na neprůhledné pozadí.
for filename in ('nahled-zavreno-cad.png','nahled-otevreno-cad.png'):
    source=Image.open(OUT/filename).convert('RGBA')
    bg=Image.new('RGB',source.size,BG)
    bg.paste(source,(0,0),source)
    bg.save(OUT/filename,optimize=True)
print(OUT/'nahled-skrinky.png')
