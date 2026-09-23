T=D.addObject('Spreadsheet::Sheet','Steering');T.Label='Řízení: mm / deg; vůle návrhové'
params=[('KingpinX',190,'mm'),('HalfTrack',72,'mm'),('Arm',20,'mm'),('Trail',3.7,'mm'),('WheelOffset',15,'mm'),('HornRadius',15,'mm'),('ServoX',220,'mm'),('WheelAngle',0,'deg'),('StopAngle',27,'deg'),('WorkingAngle',25,'deg'),('PinDiameter',8,'mm'),('PinClearance',0.6,'mm'),('BodyRadius',7,'mm'),('KnuckleBottom',18.4,'mm'),('KnuckleTop',37.6,'mm'),('TieBottom',49,'mm'),('DragBottom',52.4,'mm'),('HornBottom',45,'mm'),('HornThickness',2.5,'mm'),('ServoFloor',14.7,'mm'),('ServoWidth',12.2,'mm'),('ServoLength',22.7,'mm'),('ServoHeight',27,'mm'),('CaseAxisOffset',5,'mm'),('JointDiameter',6,'mm'),('JointBore',6.5,'mm'),('TreadDepth',1,'mm'),('TreadWidth',1.6,'mm')]
rows={}
for i,(n,v,u) in enumerate(params,2):
    rows[n]=i;T.set('A'+str(i),n);T.set('B'+str(i),f'={v} {u}');T.setAlias('B'+str(i),n)
    note='Návrh, skutečný fit neověřen'
    if n in ('PinDiameter','PinClearance','BodyRadius','WheelOffset','KnuckleBottom','KnuckleTop','JointDiameter','JointBore','WorkingAngle'):note='Konstrukční informace: změna vyžaduje související úpravy makra a novou kontrolu, ne libovolnou editaci'
    if n=='HornRadius':note='Uživatel výslovně změřil střed osy → střed posledního otvoru 15 mm'
    if n in ('ServoWidth','ServoLength','ServoHeight'):note='Nominální TowerPro výkres; fyzicky neměřeno'
    if n=='CaseAxisOffset':note='NEZMĚŘENÝ návrhový offset; nastavitelné uložení, nutno ověřit'
    T.set('C'+str(i),note)
formulae=[('TieLength','2 * HalfTrack'),('EndX','KingpinX + Arm * cos(WheelAngle)'),('EndLeftY','-HalfTrack + Arm * sin(WheelAngle)'),('DragLength','sqrt((KingpinX + Arm - ServoX + HornRadius)^2 + HalfTrack^2)'),('DeltaX','EndX - ServoX'),('DeltaY','EndLeftY'),('RadiusToEnd','sqrt(DeltaX^2 + DeltaY^2)'),('ServoAngle','atan2(DeltaY, DeltaX) - acos((RadiusToEnd^2 + HornRadius^2 - DragLength^2)/(2*HornRadius*RadiusToEnd)) + 180 deg'),('HornX','ServoX - HornRadius * cos(ServoAngle)'),('HornY','-HornRadius * sin(ServoAngle)'),('DragAngle','atan2(EndLeftY-HornY, EndX-HornX)'),('SpacerHeight','DragBottom-HornBottom-HornThickness')]
for i,(n,f) in enumerate(formulae,len(params)+3):T.set('A'+str(i),n);T.set('B'+str(i),'='+f);T.setAlias('B'+str(i),n)
T.setColumnWidth('A',200);T.setColumnWidth('B',150);T.setColumnWidth('C',500);D.recompute()
def s(n):return 'Steering.'+n

rxp=rny;rxn=ry
steermat=[frame,box('FrontCrossmember',(20,'2 * '+s('HalfTrack'),4),(s('KingpinX')+' - 10 mm','-'+s('HalfTrack'),4)),box('NosePlate',(28,40,4),(206,-20,0))];steervoids=[]
# Dva spodní závěsy, horní čelisti samostatně nasazené do obdélníkových registrů.
for side,tag in [(-1,'L'),(1,'R')]:
    y=f'{side} * '+s('HalfTrack')
    steermat.append(box('OuterCrossmember'+tag,(20,s('HalfTrack')+' - 55 mm',5),(s('KingpinX')+' - 10 mm',55 if side==1 else '-'+s('HalfTrack'),8)))
    steermat.append(cyl('LowerFork'+tag,8,5,(s('KingpinX'),y,13)))
    steervoids+=[cyl('KingpinBore'+tag,s('PinDiameter')+'/2 + '+s('PinClearance')+'/2',12,(s('KingpinX'),y,7)),cyl('ClipAccess'+tag,7,6,(s('KingpinX'),y,7))]
    steermat.append(box('ForkSupport'+tag,(7,7,34),(s('KingpinX')+' - 3.5 mm',f'{side} * ('+s('HalfTrack')+' - 14.5 mm) - 3.5 mm',4)))
    steervoids.append(box('CapRegisterVoid'+tag,(4.6,4.6,3),(s('KingpinX')+' - 2.3 mm',f'{side} * ('+s('HalfTrack')+' - 14.5 mm) - 2.3 mm',36)))
    # Doraz: váleček Ø2,4 v otevřené kruhové dráze se svislými radiálními konci.
    half=s('StopAngle')+f' + {math.degrees(math.asin(1.2/6.5)):.14f} deg'
    sector=cyl('StopSector'+tag,8.2,3,(s('KingpinX'),y,15.3));sector.setExpression('Angle','2 * ('+half+')');sector.Placement.Rotation=App.Rotation(App.Vector(0,0,1),1);sector.setExpression('Placement.Rotation.Angle','-('+half+')')
    pocket=cut('StopPocket'+tag,sector,cyl('StopInner'+tag,5,5,(s('KingpinX'),y,14.3)))
    steervoids.append(pocket)

# SG90 lože doplněno v navazujícím konstrukčním bloku.
# Čelist zdroje v místních XY, pravá se při montáži zrcadlí otočením kolem Z.
capmat=[cyl('CapEye',8,5),box('CapBridge',(7,14.5,5),(-3.5,-14.5,0)),box('CapKey',(4,4,2),(-2,-16.5,-2))]
cap=cut('ForkCap',fuse('CapMaterial',capmat),cyl('CapHole',4.3,9,(0,0,-3)))
# Hlavní svislý čep35,3mm: kruhové pracovní plochy, samostatná C pojistka.
def axle(n,d,l,flange,groove,flat):
    a=fuse(n+'Blank',[cyl(n+'Rod',d/2,l),cyl(n+'Head',flange/2,2)])
    a=cut(n+'Flat',a,box(n+'FlatTool',(15,30,l+2),(flat,-15,-1)))
    gr=cut(n+'Groove',cyl(n+'GrooveOuter',10,1.5,(0,0,l-3)),cyl(n+'GrooveCore',groove/2,3.5,(0,0,l-4)))
    return cut(n,a,gr)
king=pin('Kingpin',8,35.3,13,6.8)
knuckles={}
for side,tag in [(-1,'L'),(1,'R')]:
    # pravé/levé zdroje globálně stejně orientované, osička směřuje ven.
    rot=rxn if side==1 else rxp
    shaft=cyl('Stub'+tag,4,24.3,('-'+s('Trail'),0,0),rot)
    collar=cyl('WheelCollar'+tag,6,4.3,('-'+s('Trail'),side*4.5,0),rot)
    items=[cyl('KnuckleBody'+tag,s('BodyRadius'),s('KnuckleTop')+' - '+s('KnuckleBottom'),(0,0,s('KnuckleBottom')+' - 28 mm')),shaft,collar,
      box('ArmBase'+tag,(20,8,5),(0,-4,4)),box('ArmRise'+tag,(9,8,15.6),(11,-4,5)),cyl('ArmEye'+tag,6,3.6,(s('Arm'),0,17)),cyl('StopPeg'+tag,1.2,3.3,(6.5,0,-12.3))]
    raw=fuse('KnuckleMaterial'+tag,items)
    # Kulaté pracovní osičky; vodorovný tisk s lokální podporou.
    gr=cut('StubGroove'+tag,cyl('StubGrooveOuter'+tag,7,1.5,('-'+s('Trail'),side*21.3,0),rot),cyl('StubGrooveCore'+tag,3.4,3.5,('-'+s('Trail'),side*20.3,0),rot))
    holes=[cyl('KnucklePivotHole'+tag,4.3,24,(0,0,-12)),cyl('ArmJointHole'+tag,3.25,12,(s('Arm'),0,12)),cyl('JointClipAccess'+tag,5.3,3.7,(s('Arm'),0,13.5)),gr]
    knuckles[side]=cut('Knuckle'+tag,raw,fuse('KnuckleVoids'+tag,holes))
# C táhlo před spojnicí čepů, vzdálenost144mm navázaná na HalfTrack.
tmat=[cyl('TieEyeL',6,3),cyl('TieEyeR',6,3,(0,s('TieLength'),0)),box('TieBeam',(4,s('TieLength'),3),(3.5,0,0))]
tie=cut('TieBar',fuse('TieMaterial',tmat),fuse('TieVoids',[cyl('TieHoleL',3.25,5,(0,0,-1)),cyl('TieHoleR',3.25,5,(0,s('TieLength'),-1))]))
# Servotáhlo v místní X: tištěný čepØ8 na0, tištěný čepØ6 naL.
dragmat=[cyl('DragSmallEye',7,3),cyl('DragLargeEye',6,3,(s('DragLength'),0,0)),box('DragBeam',(s('DragLength'),4,3),(0,-2,0))]
drag=cut('DragLink',fuse('DragMaterial',dragmat),fuse('DragVoids',[cyl('DragPivotHole',4.3,5,(0,0,-1)),cyl('DragJointHole',3.25,5,(s('DragLength'),0,-1))]))
# Malé čepy vkládat shora. Pojistka pod ramenem; otočný spoj se nesmí sevřít.
jointlong=pin('JointPinLong',6,15.6,10,4.8)
jointshort=pin('JointPinShort',6,12.2,10,4.8)
jointclip=cut('SmallClip',cut('SmallClipRing',cyl('SmallClipOuter',5,1.3),cyl('SmallClipBore',2.45,3.3,(0,0,-1))),box('SmallClipMouth',(8,4.1,3.3),(0,-2.05,-1)))

exec((OUT/'servo-uchyceni.py').read_text(),globals())
frame=reg('ram-25',cut('SteeringFrame',fuse('SteeringFrameMaterial',steermat),fuse('SteeringFrameVoids',steervoids)))

for key,obj,ori in [('celist-horni',cap,'cap'),('svisly-cep-8',king,'round_pin'),('tehlice-leva',knuckles[-1],'knuckle'),('tehlice-prava',knuckles[1],'knuckle'),('spojovaci-tahlo',tie,'flat'),('servo-tahlo-r15',drag,'flat'),('cep-tahla-dlouhy',jointlong,'round_pin'),('cep-tahla-kratky',jointshort,'round_pin'),('pojistka-kloubu-4_9',jointclip,'flat')]:reg(key,obj,ori)
