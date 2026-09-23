#!/usr/bin/env python3
"""Build configured Next projects, slice those exact files in repo cache.
No user profiles or printer IO. Only original 03 and repair 01 are rebuilt.
"""
import json, os, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent; LAYOUT=HERE.parent; REPO=HERE.parents[3]
REPAIR=LAYOUT/'dotisk-prvni-varky-2026-09-20'
CACHE=REPO/'.cache/stojate-2026-09-20'
PROFILES=Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
MACHINE=PROFILES/'machine/Anycubic Kobra X 0.4 nozzle.json'
PROCESS=PROFILES/'process/0.12mm High Quality @Anycubic Kobra X 0.4 nozzle.json'
FILAMENT=PROFILES/'filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json'
JOBS={
 'puvodni-03':{'geometry':LAYOUT/'auticko-25-podlozka-03.3mf','project':HERE/'auticko-25-03-stojate-nastaveny-projekt.3mf','title':'V3 puvodni 03 - stojate cepy - podpora plosiny - 0.12 mm','overrides':{'enable_support':'0'},'objects':True},
 'dotisk-01':{'geometry':REPAIR/'dotisk-25-podlozka-01.3mf','project':REPAIR/'projekty-next/dotisk-25-01-nastaveny-projekt.3mf','title':'V3 dotisk 01 - stojata osa - podpory - 0.12 mm','overrides':{'enable_support':'1','brim_width':'12','default_acceleration':'500','outer_wall_acceleration':'300','inner_wall_acceleration':'500','travel_acceleration':'500','outer_wall_speed':'20','inner_wall_speed':'30','small_perimeter_speed':'15','support_speed':'30','support_interface_speed':'20'},'objects':False}}
def runcli(cmd,log):
 with log.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,DISPLAY=''),timeout=900)
 assert r.returncode==0,(r.returncode,str(log));return r.returncode

def run(name):
 job=JOBS[name];cache=CACHE/name;cache.mkdir(parents=True,exist_ok=True)
 process=json.loads(PROCESS.read_text());common=json.loads((REPAIR/'doporucene-nastaveni.json').read_text())['common_overrides']
 if job['objects']:
  # Platform retains the public 0.12mm process: 15% 3D honeycomb, two walls.
  # Only supports, adhesion and first-layer controls are shared with repair.
  process.update({k:v for k,v in common.items() if k.startswith(('support_', 'brim_', 'initial_layer_')) or k in ('enable_prime_tower','gcode_comments','print_sequence')})
 else:process.update(common)
 process.update({'support_object_xy_distance':'0.35','support_critical_regions_only':'0','bridge_no_support':'0','support_expansion':'0'})
 process.update(job['overrides']);process['name']=process['print_settings_id']=job['title']
 cfg=cache/'process.json';cfg.write_text(json.dumps(process,indent=2))
 cmd=['/usr/bin/AnycubicSlicerNext','--datadir',str(cache/'export-profile'),'--arrange','0','--orient','0','--debug','3','--load-settings',str(MACHINE)+';'+str(cfg),'--load-filaments',str(FILAMENT),'--export-3mf','export.3mf','--outputdir',str(cache),str(job['geometry'])]
 runcli(cmd,cache/'export.log')
 with ZipFile(cache/'export.3mf') as z:files={n:z.read(n) for n in z.namelist()}
 root=E.fromstring(files['Metadata/model_settings.config']);overrides={}
 if job['objects']:
  for o in root.findall('object'):
   oname=o.find('metadata[@key="name"]').get('value')
   enabled=oname=='plosina-170x60__01';overrides[oname]={'enable_support':'1' if enabled else '0'}
   if not enabled:
    overrides[oname].update({k:common[k] for k in ('wall_loops','sparse_infill_density','sparse_infill_pattern','outer_wall_speed','inner_wall_speed','small_perimeter_speed','small_perimeter_threshold','top_surface_speed','sparse_infill_speed','internal_solid_infill_speed','gap_infill_speed')})
   for k,v in overrides[oname].items():E.SubElement(o,'metadata',key=k,value=v)
  assert len(overrides)==13 and sum(v['enable_support']=='1' for v in overrides.values())==1
  files['Metadata/model_settings.config']=E.tostring(root,encoding='utf-8',xml_declaration=True)
 assert not any(n.endswith('.gcode') for n in files)
 with ZipFile(job['project'],'w',ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 out=cache/'slice';out.mkdir(exist_ok=True)
 cmdslice=['/usr/bin/AnycubicSlicerNext','--datadir',str(cache/'slice-profile'),'--arrange','0','--orient','0','--debug','3','--slice','0','--export-3mf','sliced.3mf','--outputdir',str(out),str(job['project'])]
 runcli(cmdslice,cache/'slice.log')
 return {'job':name,'geometry':str(job['geometry']),'project':str(job['project']),'project_sha256':hashlib.sha256(job['project'].read_bytes()).hexdigest(),'sliced':str(out/'sliced.3mf'),'object_overrides':overrides,'commands':[cmd,cmdslice],'exit_codes':[0,0]}

def main():
 with ThreadPoolExecutor(max_workers=2) as ex:records=list(ex.map(run,JOBS))
 (HERE/'evidence/prikazy.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(records,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
