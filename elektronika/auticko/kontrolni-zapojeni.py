#!/usr/bin/env python3
"""Generate the dated wiring reference; never accesses hardware or network."""
from pathlib import Path
from html import escape
import json

HERE = Path(__file__).resolve().parent
W, H = 1800, 1840
C = dict(ink='#172b3a', muted='#526573', edge='#cbd5dd', panel='#f7f9fb',
         signal='#145e96', ground='#354854', power='#9c1b28', amber='#915300',
         orange='#a85800', blue='#2469aa')
parts = []


def add(s):
    parts.append(s)


def text(x, y, value, size=22, color='ink', weight=400, anchor='start'):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{C.get(color,color)}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def lines(x, y, rows, size=22, color='ink', step=30, weight=400):
    for i, row in enumerate(rows):
        text(x, y+i*step, row, size, color, weight)


def rect(x, y, w, h, fill='white', stroke='edge', r=8, dash=False):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
        f'fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="2"'
        + (' stroke-dasharray="8 6"' if dash else '') + '/>')


def wire(points, color='ink', width=3, dash=False):
    add(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" '
        f'stroke="{C.get(color,color)}" stroke-width="{width}" stroke-linejoin="round"'
        + (' stroke-dasharray="10 7"' if dash else '') + '/>')


def dot(x,y,color='ink',open_=False):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="{"white" if open_ else C.get(color,color)}" '
        f'stroke="{C.get(color,color)}" stroke-width="2"/>')


def ground(x,y,label=True):
    wire([(x,y),(x,y+14)],'ground')
    for d,half in [(14,15),(21,10),(28,5)]:
        wire([(x-half,y+d),(x+half,y+d)],'ground')
    if label:
        text(x,y+53,'GND',18,'ground',600,'middle')


def net(x,y,name,side='right',color='power',width=155):
    if side=='right':
        wire([(x,y),(x+20,y)],color)
        rect(x+20,y-17,width,34,'white',color,3)
        text(x+20+width/2,y+7,name,18,color,600,'middle')
    else:
        wire([(x,y),(x-20,y)],color)
        rect(x-20-width,y-17,width,34,'white',color,3)
        text(x-20-width/2,y+7,name,18,color,600,'middle')


PINOUT = {
    1: ('EN 1,2','EN_D5'), 2: ('IN 1','IN1_D7'), 3: ('OUT 1','M_A'),
    4: ('GND','GND'), 5: ('GND','GND'), 6: ('OUT 2','M_B'),
    7: ('IN 2','IN2_D8'), 8: ('VS','MOTOR_PLUS'), 9: ('EN 3,4','GND'),
    10: ('IN 3','GND'), 11: ('OUT 3','NC'), 12: ('GND','GND'),
    13: ('GND','GND'), 14: ('OUT 4','NC'), 15: ('IN 4','GND'),
    16: ('VSS','ARDUINO_5V'),
}
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
add('<title id="title">Autíčko: kontrolní zapojení UNO R4 WiFi, L293D a SG90</title>')
add('<desc id="desc">Referenční funkční spoje, nikoli potvrzení fyzické montáže. '
    'Všechny symboly GND jsou společná zem, stejné síťové štítky značí stejné uzly. '
    'D5 na L293D pin 1 s odporem 10 kiloohm na GND, D7 na pin 2, D8 na pin 7, '
    'D9 přímo na servo. Pin 16 je Arduino 5V, pin 8 samostatné motorové plus. '
    'Servo bylo zkoušeno přímo na 6,4V, nad uváděným rozsahem. Poslední odpojení '
    'USB ani plus serva není potvrzené. Přístupný úplný seznam spojů je v kontrolni-zapojeni.md.</desc>')
add('<g font-family="DejaVu Sans, sans-serif">')
rect(0,0,W,H,'white','white',0)
text(65,64,'Autíčko — kontrolní zapojení',38,weight=700)
text(65,104,'UNO R4 WiFi · ST L293D DIP16 · DC motor · SG90     |     stav hlášení 22. 9. 2026',23,'muted')
rect(65,132,1670,94,'#fff4ed','amber')
text(88,166,'PŘED KONTROLOU ODPOJIT USB A PLUS OBOU EXTERNÍCH ZDROJŮ.',23,'amber',700)
text(88,203,'Poslední odpojení USB a plus serva není potvrzené. Obrázek neznamená, že je obvod nyní vypnutý.',22,'ink')

# Main electrical reference. Named supply nets keep crossing lines out of the pinout.
rect(65,245,1670,800,'panel')
text(85,278,'FUNKČNÍ SPOJE · stejné štítky = stejný elektrický uzel · GND = společná zem',21,'muted',600)
rect(95,325,285,660,'white','ink')
text(237,365,'Arduino',28,weight=700,anchor='middle')
text(237,400,'UNO R4 WiFi',25,weight=700,anchor='middle')
rect(115,430,80,110,'panel','edge',5)
lines(155,465,['USB-C','napájení'],16,'muted',24)
wire([(95,478),(78,478),(78,315)],'muted')
text(105,308,'USB z PC / powerbanky',18,'muted')
for name,y in [('5V',575),('D5',430),('D7',480),('D8',730),('D9',895),('GND',955)]:
    text(350,y+7,name,23,weight=600,anchor='end')
    wire([(360,y),(380,y)],'signal' if name.startswith('D') else 'ground' if name=='GND' else 'power')
    dot(380,y,'signal' if name.startswith('D') else 'ground' if name=='GND' else 'power')
net(380,575,'+5V LOGIKA',width=155)

# L293D body, notch at top. Exact top-view numbering.
rect(845,390,250,420,'white','ink',4)
add('<path d="M 945 390 A 25 25 0 0 0 995 390" fill="none" stroke="#172b3a" stroke-width="3"/>')
text(970,334,'ST L293D · DIP16',27,weight=700,anchor='middle')
text(970,365,'shora · výřez nahoře',20,'muted',anchor='middle')
# Chip identity is already above; keep the pin labels unobstructed.
for pin,(label,netname) in PINOUT.items():
    left=pin<=8; row=pin-1 if left else 16-pin; y=430+50*row
    x=845 if left else 1095; tip=x-30 if left else x+30
    add(f'<g id="l293d-pin-{pin}" data-net="{netname}">')
    wire([(x,y),(tip,y)])
    text(x+14 if left else x-14,y+7,str(pin),21,weight=700,anchor='start' if left else 'end')
    text(x+55 if left else x-55,y+6,label,15,'muted',anchor='start' if left else 'end')
    add('</g>')

# Control lines: no series resistor on D5; resistor is a separate branch.
wire([(380,430),(815,430)],'signal')
text(403,421,'D5 → 1',19,'signal')
wire([(380,480),(815,480)],'signal')
text(403,471,'D7 → 2',19,'signal')
wire([(380,730),(815,730)],'signal')
text(403,721,'D8 → 7',19,'signal')
dot(690,430,'signal')
wire([(690,430),(690,397)],'signal')
rect(680,345,20,52,'white','ink',0)
wire([(690,345),(690,310),(745,310)])
ground(745,310,False)
text(665,340,'10 kΩ',20,'ink',600,'end')
text(660,368,'EN → GND',17,'muted',anchor='end')
text(770,327,'GND',17,'ground',600)

# Motor between the two active bridge outputs. Neither terminal is GND.
wire([(815,530),(730,530),(730,571)],'ink')
wire([(815,680),(730,680),(730,639)],'ink')
add('<circle cx="730" cy="605" r="34" fill="white" stroke="#172b3a" stroke-width="3"/>')
text(730,615,'M',28,weight=700,anchor='middle')
text(650,603,'DC motor',19,anchor='end')
text(705,526,'kontakt A',17,'muted',anchor='end')
text(705,680,'kontakt B',17,'muted',anchor='end')
wire([(815,580),(795,580),(795,630),(815,630)],'ground')
dot(795,630,'ground')
ground(795,630,False)
net(815,780,'MOTOR +',side='left',width=135)

# Right-side chip pins: exact distinct net labels avoid false crossings.
net(1125,430,'+5V LOGIKA',width=155)
for pin in [15,13,12,10,9]:
    y=430+50*(16-pin)
    wire([(1125,y),(1170,y)],'ground')
    text(1180,y+7,'GND',20,'ground',600)
for pin in [14,11]:
    y=430+50*(16-pin)
    wire([(1121,y-5),(1131,y+5)],'muted',2)
    wire([(1121,y+5),(1131,y-5)],'muted',2)
    text(1145,y+6,'nezapojit',17,'muted')

# Motor supply shown as interrupted, per the user's earlier report.
rect(530,840,505,165,'white','edge')
text(550,871,'STARÝ ZDROJ MOTORU',22,weight=700)
lines(550,902,['Jeden článek vyjmutý — hlášení uživatele.',
              'Aktuální napětí a složení nejsou ověřené.'],18,'muted',25)
text(550,980,'−',25,weight=700);wire([(575,971),(600,971)]);ground(600,971,False)
text(802,980,'+',25,'power',700);net(830,971,'MOTOR +',width=135)

# Servo and its actual risky test branch. The open symbol marks the requested break,
# never a claim that the user has actually disconnected it.
rect(1360,320,350,220,'#fff4ed','amber')
text(1380,354,'NOVÝ ZDROJ SERVA',23,'ink',700)
lines(1380,391,['4 články · naměřeno 6,4 V',
                  'měření uživatele, zátěž neznámá',
                  'bez měniče · přímý pokus',
                  '6,4 V > uváděných 4,8–6 V'],18,'amber',32)
text(1410,531,'−',25,weight=700);text(1630,531,'+',25,'power',700)
wire([(1420,540),(1420,555)],'ground');ground(1420,555,False)
wire([(1640,540),(1640,592)],'power',4)
dot(1640,592,'power',True);dot(1640,639,'power',True)
wire([(1640,592),(1672,622)],'power',4)
wire([(1640,639),(1640,687),(1720,687),(1720,880),(1685,880)],'power',4)
text(1590,612,'ROZPOJIT PRO KONTROLU',19,'power',700,'end')
text(1590,638,'požadovaný stav; odpojení nepotvrzené',16,'power',400,'end')
lines(1370,718,['Přímé napájení = uskutečněný',
                 'rizikový pokus, nikoli doporučené',
                 'provozní napájení.'],17,'amber',24)
rect(1360,790,325,198,'white','ink')
text(1519,826,'SG90',27,weight=700,anchor='middle')
text(1380,861,'signál · oranžový',20,'orange')
text(1665,894,'+ · červený',20,'power',anchor='end')
text(1665,952,'GND · hnědý',20,'ground',anchor='end')
wire([(380,895),(470,895),(470,820),(1290,820),(1290,855),(1360,855)],'orange',4)
text(490,811,'UNO D9 přímo na signál serva — není to pin 9 čipu L293D',20,'orange',600)
wire([(1685,945),(1720,945),(1720,977)],'ground');ground(1720,977,False)
text(1400,980,'Táhlo od kol odpojeno, páčka zůstala¹',15,'muted')

# Common ground/breadboard reference. Not a claim of current continuity.
rect(65,1065,1670,245,'white','edge')
text(85,1102,'SPOLEČNÁ ZEM A NEPÁJIVÉ POLE',24,weight=700)
lines(85,1136,['Všechny symboly GND jsou tentýž požadovaný uzel:',
               'UNO GND · SG90 hnědý · oba zdroje − · L293D 4/5/12/13/9/10/15 · odpor 10 kΩ.'],19,'ground',30)
wire([(380,955),(440,955),(440,1010)],'ground',4)
ground(440,1010,False)
wire([(180,1207),(825,1207)],'ground',4)
ground(700,1207,False)
text(85,1252,'Servo a jeho zdroj mají podle hlášení vlastní vodiče přímo do UNO GND.',17,'muted')
text(85,1282,'Spojení lišty s touto zemí dosud není potvrzené.',19,'amber',600)
wire([(825,1207),(1090,1207)],'amber',4,True)
text(950,1191,'OVĚŘIT SPOJ',18,'amber',700,'middle')
rect(1090,1180,600,102,'panel','edge')
text(1110,1206,'Mínusová lišta nepájivého pole',20,weight=600)
wire([(1110,1240),(1320,1240)],'ground',4)
dot(1320,1240,'ground')
wire([(1320,1240),(1430,1240),(1430,1263),(1660,1263)],'blue',4)
dot(1660,1263,'blue',True)
text(1440,1248,'volný modrý: konec neurčen',15,'blue')
text(1110,1271,'Lišta může být uprostřed přerušená.',15,'muted')

# Three compact explanatory sections.
rect(65,1330,525,325,'panel','edge')
text(85,1367,'Původní otočení čipu',24,weight=700)
text(85,1399,'Shora, výřez vlevo:',21,'muted')
rect(110,1450,420,85,'white','ink',3)
add('<path d="M 110 1477 A 16 16 0 0 1 110 1509" fill="none" stroke="#172b3a" stroke-width="3"/>')
for i in range(8):
    x=144+i*51
    text(x,1439,str(16-i),21,weight=600,anchor='middle')
    wire([(x,1445),(x,1450)])
    wire([(x,1535),(x,1541)])
    text(x,1564,str(i+1),21,weight=600,anchor='middle')
lines(85,1600,['Horní zleva 16–9; dolní zleva 1–8.',
               'DIP16, nikoli 20pinový L293DD.'],19,'muted',30)

rect(610,1330,525,325,'panel','edge')
text(630,1367,'Tři oddělená kladná napájení',23,weight=700)
lines(630,1404,['Arduino 5V → jen logika, pin 16.',
                'Motorový zdroj + → pin 8.',
                'Servo zdroj + → červený vodič.'],21,'ink',37)
text(630,1534,'Tyto tři kladné větve NESPOJOVAT.',21,'power',700)
lines(630,1574,['Společná je GND, ne kladné póly.',
                'Kondenzátory 100 nF: 16–GND a 8–GND.',
                'Jen návrh; dostupnost/osazení nepotvrzené.'],18,'muted',29)

rect(1155,1330,580,325,'#fff4ed','amber')
text(1175,1367,'Co zůstává neověřené',24,weight=700)
lines(1175,1407,['Servo se podle hlášení ze změněné polohy',
                 'chvěje a bzučí; samo se neustavilo.',
                 'Příčina není zjištěná.',
                 'Volný modrý vodič není diagnóza.',
                 'Směrová tlačítka ani jízda nepotvrzeny².',
                 'Poslední odpojení napájení nepotvrzené.'],21,'ink',39)

text(65,1697,'Čáry ukazují funkční vazby, nikoli rozmístění otvorů na nepájivém poli. Barvy čar nejsou identifikací skutečných vodičů.',20,'muted')
text(65,1730,'¹ Uživatelské hlasové hlášení, bez vizuální kontroly.  ² Zkouška nebyla uživatelem potvrzená.',19,'muted')
text(65,1763,'Pinout: ST L293D datasheet str. 2. Arduino piny: zdroj v3-steering-v1, SHA256 9f7477c8…8d8760c.',18,'muted')
text(65,1795,'Úplný seznam spojů, zdroje a záznam zkoušky: kontrolni-zapojeni.md. Změna dokumentace bez zásahu do hardwaru.',18,'muted')
add('</g></svg>')
(HERE/'kontrolni-zapojeni.svg').write_text('\n'.join(parts)+'\n')
(HERE/'.cache/schema-2026-09-22').mkdir(parents=True, exist_ok=True)
(HERE/'.cache/schema-2026-09-22/pinout-generated.json').write_text(
    json.dumps({str(k):{'function':v[0],'net':v[1]} for k,v in PINOUT.items()},indent=2)+'\n')
print(HERE/'kontrolni-zapojeni.svg')
