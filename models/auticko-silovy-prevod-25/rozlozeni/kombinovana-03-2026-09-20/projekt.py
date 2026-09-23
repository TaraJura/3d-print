#!/usr/bin/env python3
"""Prepare and slice exact combined 26-object project, no printer access."""
import hashlib,importlib.util,json,os,subprocess
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as E
HERE=Path(__file__).resolve().parent;LAYOUT=HERE.parent;REPO=HERE.parents[3]
CACHE=REPO/'.cache/kombinovana-03-2026-09-20'
s=importlib.util.spec_from_file_location('upright',LAYOUT/'stojate-cepy-2026-09-20/projekty.py');upright=importlib.util.module_from_spec(s);s.loader.exec_module(upright)

def main():
 CACHE.mkdir(parents=True,exist_ok=True)
 common=json.loads((LAYOUT/'dotisk-prvni-varky-2026-09-20/doporucene-nastaveni.json').read_text())['common_overrides']
 process=json.loads(upright.PROCESS.read_text())
 process.update({k:v for k,v in common.items() if k.startswith(('support_', 'brim_', 'initial_layer_')) or k in ('enable_prime_tower','gcode_comments','print_sequence')})
 process.update({'enable_support':'0','support_object_xy_distance':'0.35','support_critical_regions_only':'0','bridge_no_support':'0','support_expansion':'0','default_acceleration':'500','outer_wall_acceleration':'500','inner_wall_acceleration':'500','travel_acceleration':'500'})
 process['name']=process['print_settings_id']='V3 kombinovana 03 - 26 kusu - stojate cepy - lokalni podpory'
 cfg=CACHE/'process.json';cfg.write_text(json.dumps(process,indent=2))
 geometry=HERE/'auticko-25-kombinovana-03-geometrie.3mf';project=HERE/'auticko-25-kombinovana-03-nastaveny-projekt.3mf'
 cmd=['/usr/bin/AnycubicSlicerNext','--datadir',str(CACHE/'export-profile'),'--arrange','0','--orient','0','--debug','3','--load-settings',str(upright.MACHINE)+';'+str(cfg),'--load-filaments',str(upright.FILAMENT),'--export-3mf','export.3mf','--outputdir',str(CACHE),str(geometry)]
 upright.runcli(cmd,CACHE/'export.log')
 with ZipFile(CACHE/'export.3mf') as z:files={n:z.read(n) for n in z.namelist()}
 root=E.fromstring(files['Metadata/model_settings.config']);overrides={}
 for o in root.findall('object'):
  name=o.find('metadata[@key="name"]').get('value');isdeck=name.startswith('plosina-');isaxis=name.startswith('osa-zadni-');isknuckle=name.startswith('tehlice-')
  v={'enable_support':'1' if (isdeck or isaxis or isknuckle) else '0'}
  if not isdeck:
   v.update({k:common[k] for k in ('wall_loops','sparse_infill_density','sparse_infill_pattern','outer_wall_speed','inner_wall_speed','small_perimeter_speed','small_perimeter_threshold','top_surface_speed','sparse_infill_speed','internal_solid_infill_speed','gap_infill_speed')})
  if isaxis:v.update({'brim_width':'12','outer_wall_speed':'20','inner_wall_speed':'30','small_perimeter_speed':'15','outer_wall_acceleration':'300','support_speed':'30','support_interface_speed':'20'})
  overrides[name]=v
  for k,value in v.items():E.SubElement(o,'metadata',key=k,value=value)
 assert len(overrides)==26 and sum(v['enable_support']=='1' for v in overrides.values())==4
 files['Metadata/model_settings.config']=E.tostring(root,encoding='utf-8',xml_declaration=True)
 assert not any(n.endswith('.gcode') for n in files)
 with ZipFile(project,'w',ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 out=CACHE/'slice';out.mkdir(exist_ok=True)
 cmdslice=['/usr/bin/AnycubicSlicerNext','--datadir',str(CACHE/'slice-profile'),'--arrange','0','--orient','0','--debug','3','--slice','0','--export-3mf','sliced.3mf','--outputdir',str(out),str(project)]
 upright.runcli(cmdslice,CACHE/'slice.log')
 report={'project':str(project),'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'sliced':str(out/'sliced.3mf'),'geometry':str(geometry),'object_overrides':overrides,'commands':[cmd,cmdslice],'exit_codes':[0,0]}
 (HERE/'evidence/prikazy.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['project'])
if __name__=='__main__':main()
