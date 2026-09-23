#!/usr/bin/env python3
"""Audit exact delivered projects and actual sliced paths, no machine IO."""
import hashlib,importlib.util,json,sys
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
HERE=Path(__file__).resolve().parent;LAYOUT=HERE.parent
sys.argv.append('unused')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parser=module('paths',LAYOUT/'dotisk-prvni-varky-2026-09-20/overit-drahy.py')
reader=module('reader',LAYOUT/'overit-import.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objcfg(z):
 root=E.fromstring(z.read('Metadata/model_settings.config'));return {o.find('metadata[@key="name"]').get('value'):{m.get('key'):m.get('value') for m in o.findall('metadata') if m.get('key') not in ('name','extruder')} for o in root.findall('object')}
def render(seg,name):
 groups=[('Model','#527387',.18,[v for k,v in seg.items() if k!='Brim' and not k.startswith('Support')]),('Brim','#168547',.8,[seg['Brim']]),('Podpory / rozhraní','#e87814',.9,[v for k,v in seg.items() if k.startswith('Support')])]
 fig,axs=plt.subplots(1,3,figsize=(16,8))
 for ax,dims in zip(axs,((0,1),(0,2),(1,2))):
  for label,color,alpha,values in groups:
   if not values:continue
   a=np.concatenate(values)[:,:,list(dims)];ax.add_collection(LineCollection(a,colors=color,alpha=alpha,linewidths=.3,label=label,rasterized=True))
  ax.autoscale();ax.set_aspect('equal');ax.margins(.1);ax.grid(alpha=.15);ax.set(xlabel='XYZ'[dims[0]]+' mm',ylabel='XYZ'[dims[1]]+' mm')
 axs[0].legend(fontsize=8);fig.suptitle(f'{name} · skutečné extruzní dráhy · Kobra X / 0,4 / PLA / 0,12 mm')
 fig.text(.04,.025,'Oranžová: skutečné podpory. Zelená: brim. Úspěšné řezání není fyzický výsledek.',fontsize=11)
 fig.tight_layout(rect=(0,.06,1,.95));fig.savefig(HERE/'evidence'/f'{name}-drahy.png',dpi=140);plt.close(fig)
 # Representative actual layers at critical heights, rounded to nearest layer.
 heights=([3,19.1,19.3,52.3,54.2,105.2,149.0] if name=='dotisk-01' else [2.5,4.0,30.,63.,68.,70.])
 model=np.concatenate([v for k,v in seg.items() if k!='Brim' and not k.startswith('Support')]);zs=np.unique(np.round(model[:,1,2],3))
 fig,axs=plt.subplots(2,4,figsize=(16,9));records=[]
 for ax,target in zip(axs.flat,heights):
  z=float(zs[np.argmin(abs(zs-target))]);record={'z_mm':z,'roles':{}}
  for label,color,alpha,values in groups:
   if not values:continue
   a=np.concatenate(values);a=a[np.abs(a[:,1,2]-z)<.002]
   if len(a):ax.add_collection(LineCollection(a[:,:,:2],colors=color,linewidths=.7,alpha=.85,label=label))
   record['roles'][label]=len(a)
  ax.autoscale();ax.margins(.15);ax.set_aspect('equal');ax.set_title(f'Z = {z:.2f} mm');ax.grid(alpha=.15);records.append(record)
 for ax in axs.flat[len(heights):]:ax.set_axis_off()
 fig.suptitle(f'{name} · vybrané skutečné vrstvy · model modře / podpory oranžově');fig.tight_layout(rect=(0,0,1,.95));fig.savefig(HERE/'evidence'/f'{name}-vrstvy.png',dpi=150);plt.close(fig)
 return records

def main():
 results=[]
 for job in json.loads((HERE/'evidence/prikazy.json').read_text()):
  name=job['job'];project=Path(job['project']);sliced=Path(job['sliced']);geometry=Path(job['geometry'])
  with ZipFile(project) as z:
   assert not any(n.endswith('.gcode') for n in z.namelist());config=json.loads(z.read('Metadata/project_settings.config'));objects=objcfg(z)
  with ZipFile(sliced) as z:
   after=json.loads(z.read('Metadata/project_settings.config'))
   differences={k:[config.get(k),after.get(k)] for k in config.keys()|after.keys() if config.get(k)!=after.get(k)}
   assert differences=={'machine_max_junction_deviation':[['0','0'],['0','0','0']]}, differences
   afterobj=objcfg(z);assert objects==afterobj
   g=z.read('Metadata/plate_1.gcode');meta=E.fromstring(z.read('Metadata/slice_info.config'))
   info={m.get('key'):m.get('value') for m in meta.iter('metadata') if m.get('key') in ('prediction','weight','outside','support_used')};warnings=[w.attrib for w in meta.iter('warning')]
  expected=13 if name=='puvodni-03' else 1;original=reader.meshes(geometry)
  assert len(original)==len(objects)==expected
  delta=0
  for p in (project,sliced):
   actual=reader.meshes(p);assert actual.keys()==original.keys()
   for k,(v,f) in original.items():
    w,gfaces=actual[k];assert np.array_equal(f,gfaces);d=float(abs(v-w).max());assert d<2e-5;delta=max(delta,d)
  assert config['printer_model']=='Anycubic Kobra X' and config['nozzle_diameter']==['0.4']
  if name=='puvodni-03':assert {k:v['enable_support'] for k,v in objects.items()}=={k:v['enable_support'] for k,v in job['object_overrides'].items()}
  seg=parser.paths(g.decode());allp=np.concatenate(list(seg.values())).reshape(-1,3);supports=np.concatenate([v for k,v in seg.items() if k.startswith('Support')]).reshape(-1,3)
  assert len(seg['Brim']) and info['support_used']=='true' and info['outside']=='false'
  assert allp[:,:2].min()>.5 and allp[:,:2].max()<259.5 and allp[:,2].max()<=260
  if name=='puvodni-03':assert supports[:,1].max()<120, 'Support escaped platform into pin area'
  roles={k:{'segments':len(v),'bounds_mm':[v.reshape(-1,3).min(0).tolist(),v.reshape(-1,3).max(0).tolist()]} for k,v in seg.items()}
  layers=render(seg,name)
  results.append({'job':name,'status':'pass_with_recorded_warnings','geometry_sha256':sha(geometry),'project':str(project),'project_sha256':sha(project),'sliced_sha256':sha(sliced),'gcode_sha256':hashlib.sha256(g).hexdigest(),'count':expected,'triangles':sum(len(f) for v,f in original.values()),'maximum_vertex_delta_mm':delta,'project_settings_equal_except_zero_array_padding':True,'slicer_normalization':differences,'object_settings_equal_sliced':True,'settings':{k:config[k] for k in parser.KEYS if k in config},'object_settings':objects,'roles':roles,'selected_layers':layers,'metadata':info,'warnings':warnings,'extrusion_centre_lines_inside_bed':True,'project_has_no_gcode':True})
 report={'status':'pass_with_recorded_warnings','scope':'Delivered Next projects sliced unchanged; mesh roundtrip, actual extrusion roles, object support overrides, bed bounds, representative layers. Startup/custom G-code and physical execution not checked.','physical_print_confirmed':False,'results':results}
 (HERE/'overeni-projektu.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps([{'job':r['job'],'metadata':r['metadata'],'supports':r['roles'].get('Support'),'warnings':r['warnings']} for r in results],indent=2))
if __name__=='__main__':main()
