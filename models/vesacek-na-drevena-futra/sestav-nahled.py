#!/usr/bin/env python3
"""Sestaví přehledovou tabuli výhradně ze skutečných FreeCAD CAD PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

OUT = Path(__file__).resolve().parent
W, H = 1920, 1200
BG = (244, 242, 237)
INK = (25, 49, 55)
MUTED = (91, 107, 107)
TEAL = (34, 93, 103)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
font_title = ImageFont.truetype(BOLD, 64)
font_sub = ImageFont.truetype(FONT, 29)
font_card = ImageFont.truetype(BOLD, 25)
font_note = ImageFont.truetype(FONT, 23)
font_kicker = ImageFont.truetype(BOLD, 17)

canvas = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(canvas)
draw.text((56, 29), "KONCEPT 02  /  DŘEVĚNÁ FUTRA", font=font_kicker, fill=TEAL)
draw.text((54, 54), "Věšáček na jeden vrut", font=font_title, fill=INK)
draw.text((58, 139), "Hlavní háček prodloužen z 30 na 50 mm a zesílen v kořeni na Ø 24 mm", font=font_sub, fill=MUTED)

cards = [
    (56, 212, 586, 827, "NA FUTRECH  ·  ILUSTRACE", "nahled-na-futrech-cad.png"),
    (667, 212, 586, 827, "SAMOTNÝ MODEL  ·  ŠIKMÝ POHLED", "nahled-sikmy-cad.png"),
    (1278, 212, 586, 827, "TVAR HÁČKŮ  ·  BOČNÍ POHLED", "nahled-bocni-cad.png"),
]
for x, y, w, h, label, filename in cards:
    draw.rounded_rectangle((x, y, x+w, y+h), radius=24, fill=WHITE,
                           outline=(225, 231, 229), width=2)
    draw.text((x+25, y+20), label, font=font_card, fill=TEAL)
    source = Image.open(OUT / filename).convert("RGB")
    diff = ImageChops.difference(source, Image.new("RGB", source.size, WHITE))
    bounds = diff.getbbox()
    if bounds is None:
        raise RuntimeError("Prázdný CAD náhled: " + filename)
    pad = 22
    bounds = (max(0, bounds[0]-pad), max(0, bounds[1]-pad),
              min(source.width, bounds[2]+pad), min(source.height, bounds[3]+pad))
    object_image = source.crop(bounds)
    max_w, max_h = w-60, h-98
    factor = min(max_w / object_image.width, max_h / object_image.height)
    target = object_image.resize((round(object_image.width*factor),
                                  round(object_image.height*factor)),
                                 Image.Resampling.LANCZOS)
    px = x + (w-target.width)//2
    py = y+71 + (max_h-target.height)//2
    canvas.paste(target, (px, py))

draw.rounded_rectangle((55, 1070, 1865, 1156), radius=18,
                       fill=(228, 235, 232))
draw.text((82, 1089), "NÁVRHOVÉ ROZMĚRY", font=font_kicker, fill=TEAL)
draw.text((82, 1117), "Destička 44 × 86 mm  ·  hloubka 58 mm  ·  jediný zapuštěný vrut",
          font=font_note, fill=INK)
draw.text((1190, 1096), "Futra a vrut jsou jen ilustrační.", font=font_note,
          fill=MUTED)
draw.text((1190, 1125), "Před tiskem je potřeba je změřit.", font=font_note,
          fill=MUTED)

target = OUT / "vizualizace-vesacek-na-futra.png"
canvas.save(target, optimize=True)
print(target)
