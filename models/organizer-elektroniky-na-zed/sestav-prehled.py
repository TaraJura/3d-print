#!/usr/bin/env python3
"""Sestaví přehled výhradně ze skutečných CAD PNG; geometrii neupravuje."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
canvas=Image.new('RGB',(2000,1430),'#f5f7f7');d=ImageDraw.Draw(canvas)
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def text(x,y,s,size=24,colour='#23424a',bold=False):d.text((x,y),s,font=font(size,bold),fill=colour)
def picture(file,box):
    im=Image.open(HERE/file).convert('RGB')
    diff=ImageChops.difference(im,Image.new('RGB',im.size,'white'))
    bounds=diff.getbbox();im=im.crop(bounds)
    im.thumbnail((box[2]-box[0]-40,box[3]-box[1]-40),Image.Resampling.LANCZOS)
    d.rounded_rectangle(box,radius=16,fill='white')
    canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))

text(56,34,'ORGANIZÉR ELEKTRONIKY',42,bold=True)
text(58,91,'Návrh ke kontrole · skutečná geometrie FreeCADu',25)
picture('nahled-perspektiva.png',(45,155,1365,1145))
picture('nahled-shora.png',(1400,155,1955,710))
text(1418,728,'POHLED SHORA',22,bold=True)
text(1418,771,'9× 57,2 × 76,5 mm',25,bold=True)
text(1418,811,'1× žlab 60 × 234,4 mm',25,bold=True)
text(1418,868,'Přístup shora, bez víka.',23)
text(1418,907,'Dlouhé vývody a nářadí',23)
text(1418,944,'patří do pravého žlabu.',23)
text(1418,1003,'4 otvory nad přihrádkami',23)
text(1418,1040,'+ záda 8 mm + dvě žebra',23)
for x,value,label in [(55,'246 × 246 mm','vnější půdorys'),(560,'100 mm','čistá výška přihrádek'),(1060,'150 mm','celková výška zad'),(1540,'1 kus','jedna podložka Kobra X')]:
    text(x,1190,value,35,bold=True);text(x,1240,label,22)
text(55,1310,'Odhad této robustní varianty: 1,07 kg / 44 h. Přesahuje jednu nominální 1kg cívku.',24)
text(55,1355,'Barva je pouze vizualizační. Tisk nespouštěn; uchycení a nosnost nejsou fyzicky ověřené.',22,colour='#576d73')
canvas.save(HERE/'prehled-navrhu.png')
print(HERE/'prehled-navrhu.png')
