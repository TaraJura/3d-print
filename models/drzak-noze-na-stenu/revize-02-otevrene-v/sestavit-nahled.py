#!/usr/bin/env python3
"""Labels and layout of actual CAD images; no generated illustration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
INK='#1a3b30';MUTED='#5e6861';BG='#f4f2ed'
def txt(d,p,t,size=28,b=False,color=INK):d.text(p,t,font=ImageFont.truetype(BOLD if b else FONT,size),fill=color)
# Two complementary views, both from the same final parametric CAD model.
im=Image.new('RGB',(2000,1580),BG);d=ImageDraw.Draw(im)
txt(d,(100,50),'OTEVŘENÝ V DRŽÁK',58,True)
txt(d,(103,130),'Položit ostřím dolů. Vzít jedním pohybem.',31,color=MUTED)
txt(d,(1510,63),'2 body uchycení',29,True)
txt(d,(1510,107),'1 tištěný díl',25,color=MUTED)
raw=Image.open(ROOT/'nahled-s-nozem-cad.png').convert('RGB')
im.paste(raw.crop((120,320,2280,850)).resize((1800,442)),(100,225))
txt(d,(100,690),'Nůž 340 mm je ilustrační; přesný obrys a rozdělení čepele neznáme.',25,color=MUTED)
txt(d,(100,780),'VOLNÝ PŘÍSTUP SHORA',28,True)
raw=Image.open(ROOT/'nahled-prazdny-cad.png').convert('RGB')
im.paste(raw.crop((120,240,2280,1050)).resize((1800,675)),(100,835))
txt(d,(100,1530),'Délka držáku 230 mm  ·  rozevření V 34 mm  ·  rozteč vrutů 160 mm',25)
im.save(ROOT/'prehled-navrhu.png')

im=Image.new('RGB',(1800,1250),BG);d=ImageDraw.Draw(im)
txt(d,(85,45),'PROFIL V A DVA VRUTY',48,True)
txt(d,(87,115),'Otevřené konce, zaoblené dno. Bez víka a bez rozebírání.',27,color=MUTED)
raw=Image.open(ROOT/'nahled-profil-cad.png').convert('RGB')
im.paste(raw.resize((1600,1000)),(100,175))
txt(d,(85,1190),'Špička a přečnívající ostří zůstávají volné. Skutečný fit a stabilita neověřeny.',24,color=MUTED)
im.save(ROOT/'nahled-profil.png')
print('OPEN_V_PRESENTATION_OK')
