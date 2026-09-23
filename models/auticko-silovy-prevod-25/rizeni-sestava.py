def rotatez(a,angle):
    a.Placement.Rotation=App.Rotation(App.Vector(0,0,1),0);a.setExpression('Placement.Rotation.Angle',angle)
kin=[]
for side,tag in [(-1,'L'),(1,'R')]:
    y=f'{side} * '+s('HalfTrack')
    caplink=link('AssemblyForkCap'+tag,cap,s('KingpinX'),y,38,App.Rotation(App.Vector(0,0,1),0 if side==1 else 180))
    link('AssemblyKingpin'+tag,king,s('KingpinX'),y,45.3,App.Rotation(App.Vector(1,0,0),180))
    link('AssemblyKingClip'+tag,gearclip,s('KingpinX'),y,11.6,App.Rotation(App.Vector(0,0,1),-side*90))
    a=link('AssemblyKnuckle'+tag,knuckles[side],s('KingpinX'),y,28);rotatez(a,s('WheelAngle'));kin.append(a)
    # Transform wheel plane around Z through kingpin; quaternion via attachment wrapper group.
    group=D.addObject('App::Part','WheelCarrier'+tag);pos(group,s('KingpinX'),y,28);rotatez(group,s('WheelAngle'));assembly.addObject(group)
    wheel=link('AssemblySteeringWheel'+tag,frontwheel,'-'+s('Trail'),side*21,0,rxn if side==-1 else rxp);assembly.removeObject(wheel);group.addObject(wheel)
    wc=link('AssemblyWheelClip'+tag,gearclip,'-'+s('Trail'),side*21.4,0,rxn if side==1 else rxp);assembly.removeObject(wc);group.addObject(wc)
    kin+=[group]
    # Čep kloubu od horní příruby dolů; stejné dolní jištění Z39.6..40.9.
    long=side==-1;z=57.6 if long else 54.2
    jl=link('AssemblyJointPin'+tag,jointlong if long else jointshort,s('EndX'),y+' + '+s('Arm')+' * sin('+s('WheelAngle')+')',z,App.Rotation(App.Vector(1,0,0),180));kin.append(jl)
    cl=link('AssemblyJointClip'+tag,jointclip,s('EndX'),y+' + '+s('Arm')+' * sin('+s('WheelAngle')+')',43.6);kin.append(cl)
tiel=link('AssemblyTie',tie,s('EndX'),s('EndLeftY'),s('TieBottom'));kin.append(tiel)
dl=link('AssemblyDrag',drag,s('HornX'),s('HornY'),s('DragBottom'));rotatez(dl,s('DragAngle'));kin.append(dl)
hs=link('AssemblyHornSpacer',horn_spacer,s('HornX'),s('HornY'),50.2);kin.append(hs)
# Nominální reference SG90. Posun osy proti krabičce neznámý; explicitní parametr.
servo=cyl('ServoShaftReference',2.3,3.3,(s('ServoX'),0,s('ServoFloor')+' + '+s('ServoHeight')))
body=box('ServoBodyReference',(s('ServoWidth'),s('ServoLength'),s('ServoHeight')),(s('ServoX')+' - '+s('ServoWidth')+'/2','-'+s('CaseAxisOffset'),s('ServoFloor')))
ears=box('ServoEarsReference',(s('ServoWidth'),32.3,3),(s('ServoX')+' - '+s('ServoWidth')+'/2','-'+s('CaseAxisOffset')+' - 4.8 mm',s('ServoFloor')+' + 17 mm'))
ref=fuse('ServoReference',[body,servo,ears]);ref.Label='SG90 — nominální reference, fit těla/páčky NEOVĚŘEN';assembly.addObject(ref)
# Horn je pouze návrhová prostorová obálka, netiskne se a nenahrazuje originální spline.
hraw=fuse('HornReferenceMaterial',[cyl('HornHubReference',3.5,s('HornThickness')),box('HornArmReference',(s('HornRadius'),4,s('HornThickness')),('-'+s('HornRadius'),-2,0)),cyl('HornEyeReference',3,s('HornThickness'),('-'+s('HornRadius'),0,0))])
# Původní malý otvor není základem nového spoje; jeho průměr není známý.
horn=D.addObject('App::Link','AssemblyHornReference');horn.setLink(hraw);pos(horn,s('ServoX'),0,s('HornBottom'));assembly.addObject(horn);rotatez(horn,s('ServoAngle'));horn.Label='ORIGINÁLNÍ páčka: r15 potvrzen, ostatní obálka návrhová';kin.append(horn)

for tag,part in [('Tray',horn_tray),('Lid',horn_lid)]:
    a=link('AssemblyHorn'+tag,part,s('ServoX'),0,0);rotatez(a,s('ServoAngle'));kin.append(a)
# Příčný zamykací čep objímky se otáčí v pomocném nosiči spolu s původní páčkou.
hc=D.addObject('App::Part','HornLockCarrier');pos(hc,s('ServoX'),0,0);rotatez(hc,s('ServoAngle'));assembly.addObject(hc)
for name,part,y in [('Pin',horn_lock_pin,-12.2),('Clip',smallclip,10.4)]:
    a=link('AssemblyHornLock'+name,part,-21,y,46.5,ry);assembly.removeObject(a);hc.addObject(a)
kin.append(hc)
a=link('AssemblyHornPivotClip',gearclip,s('HornX'),s('HornY'),55.5);kin.append(a)
link('AssemblyServoCap',servo_cap,s('ServoX'),0,0)
for side in (-1,1):
    link('AssemblyServoMountPin'+str(side+2),servo_mount_pin,s('ServoX')+f' + {side*10} mm',-18.4,37.4,ry)
    link('AssemblyServoMountClip'+str(side+2),smallclip,s('ServoX')+f' + {side*10} mm',29.9,37.4,ry)
