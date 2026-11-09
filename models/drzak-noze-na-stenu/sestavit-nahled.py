#!/usr/bin/env python3
"""Compose and label real FreeCAD renders. No synthetic geometry is drawn.
Overwrites prehled-navrhu.png and nahled-montaz.png beside this script.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
INK='#183b31'; MUTED='#5f6a63'; BG='#f4f2ed'
def txt(d,xy,text,n=28,fill=INK,b=False):d.text(xy,text,font=font(n,b),fill=fill)

canvas=Image.new('RGB',(2000,1580),BG);d=ImageDraw.Draw(canvas)
txt(d,(100,55),'POUZDRO NA NŮŽ',58,b=True)
txt(d,(103,132),'Nástěnný držák s odnímatelným ochranným krytem',29,MUTED)
txt(d,(1440,64),'Pro nůž dlouhý 340 mm',29,b=True)
txt(d,(1440,108),'výška 45 mm · rukojeť max. 25 mm',23,MUTED)
for y,filename,label,subtitle in [
 (210,'nahled-zavreno-cad.png','01  ZAVŘENÉ POUZDRO','Dva kryty chrání celou délku nože.'),
 (860,'nahled-otevreno-cad.png','02  PO SEJMUTÍ KRYTŮ','Nůž je pouze ilustrační — délka čepele a skutečný obrys nejsou známé.')]:
 txt(d,(100,y),label,27,b=True)
 raw=Image.open(ROOT/filename).convert('RGB')
 # Crop empty wall only; all printable geometry stays unchanged and visible.
 crop=raw.crop((100,230,1900,730))
 canvas.paste(crop,(100,y+50))
 txt(d,(100,y+568),subtitle,24,MUTED)
txt(d,(100,1510),'360 × 90 × 41,7 mm  ·  4 tištěné díly  ·  skutečná CAD geometrie',25,INK)
canvas.save(ROOT/'prehled-navrhu.png')

canvas=Image.new('RGB',(2000,1550),BG);d=ImageDraw.Draw(canvas)
txt(d,(100,55),'JAK SE OTEVÍRÁ',56,b=True)
txt(d,(103,130),'Kryty zvednout o 7 mm a sejmout dopředu: levý, potom pravý.',30,MUTED)
raw=Image.open(ROOT/'nahled-montaz-cad.png').convert('RGB')
canvas.paste(raw.resize((1800,1091)),(100,220))
txt(d,(100,1350),'Pevný spodní lem zůstává na místě. Nůž se vyjímá za rukojeť.',28,INK)
txt(d,(100,1400),'Ilustrační nůž a vruty; skutečné rozměry čepele, usazení a montáž neověřeny.',25,MUTED)
txt(d,(100,1450),'Kryty jsou v tomto pohledu odložené pod držákem.',25,MUTED)
canvas.save(ROOT/'nahled-montaz.png')
print('NAHLED_COMPOSE_OK')
