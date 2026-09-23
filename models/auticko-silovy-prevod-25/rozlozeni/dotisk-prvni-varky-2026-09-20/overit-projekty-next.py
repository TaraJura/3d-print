#!/usr/bin/env python3
"""Verify all delivered repair projects against geometry and the recorded slices."""
import hashlib,importlib.util,json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('read3mf',HERE.parent/'overit-import.py');reader=importlib.util.module_from_spec(s);s.loader.exec_module(reader)
def main():
 sliced=json.loads((HERE/'overeni-rezani.json').read_text());result=[]
 for i,row in enumerate(sliced['plates'],1):
  project=HERE/f'projekty-next/dotisk-25-{i:02d}-nastaveny-projekt.3mf'
  with ZipFile(project) as z:
   assert not any(n.endswith('.gcode') for n in z.namelist());cfg=json.loads(z.read('Metadata/project_settings.config'))
  with ZipFile(row['sliced_archive_path']) as z:verified=json.loads(z.read('Metadata/project_settings.config'))
  differences={k:{'project':cfg.get(k),'sliced':verified.get(k)} for k in cfg.keys()|verified.keys() if cfg.get(k)!=verified.get(k)}
  assert set(differences)<=({'machine_max_junction_deviation'} if i==1 else {'print_settings_id'}),differences
  if i==1:assert differences['machine_max_junction_deviation']=={'project':['0','0'],'sliced':['0','0','0']}
  source=reader.meshes(HERE/f'dotisk-25-podlozka-{i:02d}.3mf');actual=reader.meshes(project);assert actual.keys()==source.keys() and len(actual)==(1 if i<3 else 5)
  maxdelta=0
  for name,(v,f) in source.items():
   w,g=actual[name];assert np.array_equal(f,g);delta=float(abs(v-w).max());assert delta<2e-5;maxdelta=max(delta,maxdelta)
  assert cfg['printer_model']=='Anycubic Kobra X' and cfg['nozzle_diameter']==['0.4']
  result.append({'plate':i,'file':str(project.relative_to(HERE)),'sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'objects':len(actual),'gcode_embedded':False,'maximum_vertex_delta_mm':maxdelta,'same_triangle_indices':True,'printer_model':cfg['printer_model'],'printer_settings_id':cfg['printer_settings_id'],'process':cfg['print_settings_id'],'support':cfg['enable_support'],'brim_width':cfg['brim_width'],'config_differences_from_verified_slice':differences})
 (HERE/'overeni-projektu-next.json').write_text(json.dumps({'status':'pass','note':'Full Next projects; current plate 1 upright, same physical BOM 1/1/5. Source meshes match and print configuration equals verified slice except recorded process label or zero-array padding. No G-code/printer IO.','projects':result},ensure_ascii=False,indent=2)+'\n')
 print([(p['plate'],p['objects'],p['brim_width']) for p in result])
if __name__=='__main__':main()
