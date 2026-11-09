#!/usr/bin/env python3
"""Build a verified handoff bundle; no printer/network operations."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json,hashlib,re
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((ROOT/'print-manifest.json').read_text())
 geometry=json.loads((ROOT/'nezavisla-kontrola-geometrie.json').read_text())
 fit=json.loads((ROOT/'nezavisla-kontrola-fitu.json').read_text())
 assert geometry['summary']['all_part_checks_passed']
 assert fit['summary']['wrong_fits_excluded_for_sampled_polygons']==20
 assert len(manifest['parts'])==6 and sum(p['count'] for p in manifest['parts'])==6
 for p in manifest['parts']:assert sha(ROOT/p['file'])==p['sha256']
 print_audit=json.loads((ROOT/'rozlozeni/kontrola-rezani.json').read_text())
 assert len(print_audit['plates'])==2
 for n in (1,2):
  p=ROOT/('rozlozeni/podlozka-%02d-kobra-x-pla-projekt.3mf'%n)
  with ZipFile(p) as z:assert z.testzip() is None and 'Metadata/plate_1.gcode' in z.namelist()
 paths=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or any(x in p.parts for x in ('.cache','__pycache__')):continue
  if p.name in ('tiskovy-balicek.zip','kontrola-predani.json'):continue
  if p.suffix not in ('.FCStd','.FCMacro','.stl','.3mf','.png','.md','.json','.py'):continue
  assert not p.is_symlink()
  paths.append(p)
 zpath=ROOT/'tiskovy-balicek.zip'
 with ZipFile(zpath,'w',ZIP_DEFLATED) as z:
  for p in paths:z.write(p,p.relative_to(ROOT))
 with ZipFile(zpath) as z:
  assert z.testzip() is None
  for p in paths:assert z.read(str(p.relative_to(ROOT)))==p.read_bytes()
 report={'physical_parts':6,'configured_print_plates':2,'stl_count_print_folder':len(list((ROOT/'stl').glob('*.stl'))),'archive':zpath.name,'archive_sha256':sha(zpath),'archive_bytes':zpath.stat().st_size,'files':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in paths],'visual_review':['nahled-zahrada.png','nahled-cad.png','rozlozeni/podlozka-01-vrstvy.png','rozlozeni/podlozka-02-vrstvy.png','rozlozeni/detail-02-Stone5_01-drahy.png'],'physical_print_verified':False,'toy_safety_certified':False}
 (ROOT/'kontrola-predani.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
