#!/usr/bin/env python3
"""Kontrola růstu stěn a čelní projekce skutečných drah z předávaného 3MF.

Čte hotový 3MF a kontrola-rezani.json. Přepíše jen tento kontrolní JSON a PNG.
Neřeže znovu a nekontaktuje tiskárnu. Nejde o fyzickou zkoušku filamentu.
"""
import json, math
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pohar_slice',HERE/'pripravit-projekt.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def sample(layer, walls_only=False):
    pts=set()
    for x,y,nx,ny,z,role,speed in layer:
        if walls_only and role not in ('Outer wall','Overhang wall','Inner wall'):continue
        if role=='Brim':continue
        n=max(1,math.ceil(math.hypot(nx-x,ny-y)/0.2))
        for i in range(n+1):
            f=i/n;pts.add((round((x+f*(nx-x))*4),round((y+f*(ny-y))*4)))
    return pts

def contact_check(layers):
    near=[(dx,dy) for dx in range(-2,3) for dy in range(-2,3) if dx*dx+dy*dy<=4]
    wide=[(dx,dy) for dx in range(-4,5) for dy in range(-4,5) if dx*dx+dy*dy<=16]
    previous=sample(layers[0]);count=0;over05=[];over1=[]
    for i,layer in enumerate(layers[1:],2):
        walls=sample(layer,True);count+=len(walls)
        for x,y in walls:
            if not any((x+dx,y+dy) in previous for dx,dy in near):
                over05.append((i,x/4,y/4))
                if not any((x+dx,y+dy) in previous for dx,dy in wide):over1.append((i,x/4,y/4))
        previous=sample(layer)
    return {'method':'Wall paths sampled every0.2mm on0.25mm grid; previous-layer material search0.5/1mm. Sparse infill and internal bridges excluded from current screen.',
        'sampled_wall_sites':count,'sites_over_0_5_mm':len(over05),'examples_over_0_5_mm':over05[:20],
        'sites_over_1_mm':len(over1),'examples_over_1_mm':over1[:30],
        'limitation':'Local geometric screening, not a physical print guarantee.'}

def details_image(layers,t):
    im=Image.new('RGB',(1800,880),'#f5f2e9');d=ImageDraw.Draw(im)
    fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    title=ImageFont.truetype(fontfile,27);small=ImageFont.truetype(fontfile,19)
    d.text((28,18),'Skutečné dráhy reliéfu · čelní projekce X/Z z předávaného G-code',font=title,fill='#453619')
    panels=[('Nápisy podstavce',(-26,26,1,22),lambda x,y,z:2.3<z<21.5 and y<t[1]-15.85,False),
            ('Dvě esa a symboly',(-20,20,20,50),lambda x,y,z:21<z<50 and y<t[1]-5.85,False),
            ('Jméno na zadní straně',(-26,26,3,22),lambda x,y,z:3<z<22 and y>t[1]+15.85,True)]
    counts={}
    for j,(caption,(x0,x1,z0,z1),accept,flip) in enumerate(panels):
        ox=j*600;top=125;scale=min(550/(x1-x0),660/(z1-z0));left=ox+(600-(x1-x0)*scale)/2
        d.text((ox+25,80),caption,font=title,fill='#453619')
        d.rectangle((ox+15,top,ox+585,815),fill='#fffdfa',outline='#d6c69d',width=2)
        n=0
        for layer in layers:
            for x,y,nx,ny,z,role,speed in layer:
                if role not in ('Outer wall','Overhang wall','Gap infill','Top surface','Inner wall','Internal solid infill','Bottom surface'):continue
                if not accept(x,y,z) or not accept(nx,ny,z):continue
                xx=x-t[0];nxx=nx-t[0]
                if flip:xx=-xx;nxx=-nxx
                xy=lambda q,zz:(left+(q-x0)*scale,top+45+(z1-zz)*scale)
                if x0<=xx<=x1 and x0<=nxx<=x1:
                    d.line((*xy(xx,z),*xy(nxx,z)),fill='#80601f',width=2);n+=1
        counts[caption]=n
        d.text((ox+25,830),f'{n} extruzních úseků',font=small,fill='#72664e')
    im.save(HERE/'nahled-reliefu-drahy.png')
    return {'file':'nahled-reliefu-drahy.png','projected_segments':counts,'note':'Projection of relief front-face extrusions only; not a simulated physical surface.'}

def main():
    report=json.loads((HERE/'kontrola-rezani.json').read_text())
    with ZipFile(module.PROJECT) as z:gcode=z.read('Metadata/plate_1.gcode').decode()
    layers=module.parse_paths(gcode)
    contact=contact_check(layers);details=details_image(layers,report['translation_mm'])
    report['wall_contact_screen']=contact;report['relief_toolpath_preview']=details
    module.save_json(HERE/'kontrola-rezani.json',report)
    print(json.dumps({'contact':contact,'details':details},ensure_ascii=False))
    if contact['sites_over_1_mm']:raise RuntimeError('Review wall sites over1mm from prior-layer paths')

if __name__=='__main__':main()
