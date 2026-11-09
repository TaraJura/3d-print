#!/usr/bin/env python3
"""Create the local handoff ZIP from already verified outputs; no slicing/I/O."""
from pathlib import Path
import zipfile, json, hashlib
root=Path(__file__).resolve().parent
report=json.loads((root/'nezavisla-kontrola.json').read_text())
assert report['all_passed']
assert hashlib.sha256((root/'orbit.FCStd').read_bytes()).hexdigest()==report['input_cad_sha256']
files=[root/n for n in ['README.md','orbit.FCStd','orbit.FCMacro','print-manifest.json','kontrola-modelu.json','nezavisla-kontrola.json','nezavisla-kontrola.FCMacro','kontrola-predani.json','nahled-orbit.png','nahled-cad.png','nahled-shora-design.png','nahled-rozlozeno.png']]
files+=sorted((root/'stl').glob('*.stl'))
assert len(list((root/'stl').glob('*.stl')))==9
files+=[root/'rozlozeni'/n for n in ['README.md','pripravit-podlozky.py','manifest.json','kontrola-rezani.json','podlozka-01-kobra-x-pla-projekt.3mf','podlozka-02-kobra-x-pla-projekt.3mf','podlozka-01.png','podlozka-02.png','podlozka-01-vrstvy.png','podlozka-02-vrstvy.png']]
zip_path=root/'tiskovy-balicek.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:
  assert f.is_file(),f
  z.write(f,str(f.relative_to(root)))
 z.writestr('OBSAH-BALICKU.txt','ORBIT 25 — 9 tištěných dílů na 2 podložkách.\nOtevřít každou podložku 01 a 02 samostatně jednou jako celý projekt v Anycubic Slicer Next.\nNepřidávat navíc STL: jsou alternativním formátem těch samých 9 dílů.\nFreeCAD je editovatelná sestava; README popisuje montáž, použití a omezení kontrol.\nČas měří externí časovač. Fyzický tisk a chod zatím neověřené.\nKompletní zdrojový projekt včetně rendereru a vývojových kontrol: /home/novakj/3d-print/models/pomodoro-orbit\n')
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 assert sum(n.startswith('stl/') and n.endswith('.stl') for n in z.namelist())==9
 assert sum(n.endswith('.3mf') for n in z.namelist())==2
 for f in files:assert z.read(str(f.relative_to(root)))==f.read_bytes()
print(f'{zip_path}: {zip_path.stat().st_size} bytes; 9 STL + 2 configured 3MF; all bytes checked')
