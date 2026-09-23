# Návrhové obálky SG90, nikoli fyzicky změřený fit. Všechny spoje tištěné.
# Výstupní spline a jeho jediný potvrzený šroubek jsou ORIGINÁLNÍ, netisknou se.
for i,(n,v) in enumerate([('HornHubDiameter',7),('HornArmWidth',6),('HornPocketHeight',3.4),('ServoEarTop',34.7)],60):
    T.set('A'+str(i),n);T.set('B'+str(i),f'={v} mm');T.setAlias('B'+str(i),n);T.set('C'+str(i),'Návrhový fit: nejdříve změřit/ověřit malým výtiskem, není potvrzený rozměr kusu')
steermat.append(box('ServoFloor',(20,29,s('ServoFloor')+' - 4 mm'),(s('ServoX')+' - 10 mm',-8,4)))
# Střed těla zůstává otevřený, zadní vývod kabelu není sevřen páskou.
for side in (-1,1):
    steermat.append(box('ServoSideGuide'+str(side),(3.7,23,17),(s('ServoX')+f' + {6.3 if side==1 else -10} mm',-5.2,s('ServoFloor'))))
    for tag,y in [('Front',-16.2),('Rear',26.6)]:
        steermat.append(box('ServoLockEar'+tag+str(side),(7,3,36.5),(s('ServoX')+f' + {side*10-3.5} mm',y,4)))
        steervoids.append(cyl('ServoLockHole'+tag+str(side),p('StaticLockBore')+'/2',5,(s('ServoX')+f' + {side*10} mm',y-1,37.4),ry))
servo_cap=box('ServoCapBlank',(28,39.2,5),(-14,-12.9,34.9))
servo_cap_voids=[box('ServoCapBodyClearance',(12.6,23.1,7),(-6.3,-5.2,33.9))]
for side in (-1,1):servo_cap_voids.append(cyl('ServoCapPinHole'+str(side),p('StaticLockBore')+'/2',42,(side*10,-14,37.4),ry))
servo_cap=reg('servo-viko',cut('ServoCap',servo_cap,fuse('ServoCapVoids',servo_cap_voids)))
servo_mount_pin=reg('servo-cep-4x51_2',pin('ServoMountPin',4,51.2,8,3),'round_pin')
# Pouzdro páčky: dolní sedlo, zasouvací víko v podélných drážkách a příčný čep.
# Reference horn má náboj7 a široký konec6: tyto dva rozměry nejsou měřené.
# Původní šroubek je přístupný průchozím oknem, jeho upínaná tloušťka se nezvětší.
horn_tray=box('HornTrayBlank',(32,20,8.6),(-24,-10,42.8))
tray_voids=[box('HornLidSlide',(34,18,2.2),(-25,-9,48.2)),box('HornTopOpening',(32,16,3),(-24,-8,50.4)),
    box('HornArmPocket',(15.5,s('HornArmWidth')+' + 0.4 mm',s('HornPocketHeight')),(-18.5,'-('+s('HornArmWidth')+' + 0.4 mm)/2',44.8)),
    cyl('HornHubPocket',s('HornHubDiameter')+'/2 + 0.3 mm',5,(0,0,44.8)),
    cyl('HornScrewAccess',4,12,(0,0,41.8)),box('HornLockTonguePocket',(5.8,16,3.4),(-24,-8,44.8)),
    cyl('HornTrayLockHole',p('StaticLockBore')+'/2',22,(-21,-11,46.5),ry)]
horn_tray=reg('objimka-packy-spodek',cut('HornTray',horn_tray,fuse('HornTrayVoids',tray_voids)))
lidmat=[box('HornLidPlate',(32,17.6,2),(-24,-8.8,48.2)),box('HornLidTongue',(5,15.6,3.3),(-23.7,-7.8,44.9)),
    cyl('HornPrintedPivot',4,8.2,('-'+s('HornRadius'),0,50.2))]
lidgroove=cut('HornPivotGroove',cyl('HornPivotGrooveOuter',6,1.5,('-'+s('HornRadius'),0,55.4)),cyl('HornPivotGrooveCore',3.4,3.5,('-'+s('HornRadius'),0,54.4)))
lidvoids=[cyl('HornLidScrewAccess',4,4,(0,0,47.2)),cyl('HornLidLockHole',p('StaticLockBore')+'/2',18,(-21,-9,46.5),ry),lidgroove]
horn_lid=reg('objimka-packy-viko',cut('HornLid',fuse('HornLidMaterial',lidmat),fuse('HornLidVoids',lidvoids)))
horn_lock_pin=reg('objimka-cep-4x25_5',pin('HornLockPin',4,25.5,7,3),'round_pin')
# Krátká distanční podložka pod táhlem: zachycuje kloub bez jeho sevření.
horn_spacer=reg('podlozka-packy-1_8',cut('HornPrintedSpacer',cyl('HornSpacerOuter',6,1.8),cyl('HornSpacerBore',4.3,3.8,(0,0,-1))))
# C táhlo vede před celou objímkou, nikoli skrz ni. Středy kloubů se nemění.
tie_mat=[cyl('NewTieEyeL',6,3),cyl('NewTieEyeR',6,3,(0,s('TieLength'),0)),
    box('NewTieBeam',(6,s('TieLength'),3),(28,0,0)),box('NewTieEndL',(31,6,3),(0,-3,0)),box('NewTieEndR',(31,6,3),(0,s('TieLength')+' - 3 mm',0))]
tie=cut('TieBarFinal',fuse('TieMaterialFinal',tie_mat),fuse('TieVoidsFinal',[cyl('NewTieHoleL',3.25,5,(0,0,-1)),cyl('NewTieHoleR',3.25,5,(0,s('TieLength'),-1))]))
