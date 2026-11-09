#!/usr/bin/env python3
"""Label real CAD renders; does not generate or alter the CAD geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BG='#f4f2ed';INK='#1a3b30';MUTED='#5e6861'
def text(d,p,s,size=28,b=False,color=INK):d.text(p,s,font=ImageFont.truetype(BOLD if b else FONT,size),fill=color)
def sides(d,y):
 """Direction labels as seen when looking at the wall; they sit above the real CAD image."""
 text(d,(100,y),'← RUKOJEŤ VLEVO',24,True)
 f=ImageFont.truetype(BOLD,24);label='ŠPIČKA VPRAVO →';d.text((1900-d.textlength(label,font=f),y),label,font=f,fill=INK)
im=Image.new('RGB',(2000,1690),BG);d=ImageDraw.Draw(im)
text(d,(100,40),'ZRCADLOVÝ V DRŽÁK',57,True)
text(d,(103,118),'Přesné zrcadlení revize 03. Stěna vzadu a vyjímání shora beze změny.',30,color=MUTED)
sides(d,178)
raw=Image.open(ROOT/'nahled-s-nozem-cad.png').convert('RGB')
im.paste(raw.crop((120,320,2280,870)).resize((1800,458)),(100,220))
text(d,(100,702),'Rukojeť 105 mm. Čepel 45 → 40 mm na úseku 100 mm. Zbytek obrysu nože je ilustrační, nikoli přesně změřený.',25,color=MUTED)
text(d,(100,787),'VOLNÝ PŘÍSTUP SHORA',28,True)
raw=Image.open(ROOT/'nahled-prazdny-cad.png').convert('RGB')
im.paste(raw.crop((120,210,2280,1080)).resize((1800,725)),(100,835))
text(d,(100,1580),'Dva vruty · jeden díl · volný přechod 10 mm · vyjmutí přímo nahoru',25)
text(d,(100,1632),'Odskok rukojeti 20 mm je předběžný výklad zadání. Skutečný fit není ověřen.',23,color=MUTED)
im.save(ROOT/'prehled-navrhu.png')

im=Image.new('RGB',(2000,1150),BG);d=ImageDraw.Draw(im)
text(d,(100,50),'BOČNÍ OBRYS NÁVRHU',52,True)
text(d,(103,130),'Pohled na stěnu · náběh 5 mm / 100 mm · rukojeť 105 mm · přechod 10 mm',29,color=MUTED)
sides(d,195)
raw=Image.open(ROOT/'nahled-profil-cad.png').convert('RGB')
im.paste(raw.crop((100,200,2300,900)).resize((1800,573)),(100,240))
text(d,(100,875),'225 mm čepele vychází z předpokladu délkového řetězce 340 − 105 − 10.',25)
text(d,(100,930),'Rovný hřbet, odskok rukojeti a její průřez jsou pracovní předpoklady.',25,color=MUTED)
text(d,(100,985),'Špička zůstává volná. Neověřeno fyzické usazení, stabilita a upevnění.',25,color=MUTED)
im.save(ROOT/'nahled-profil.png')
print('V04_PRESENTATION_OK')
