#!/usr/bin/env python3
"""Verify combined project, copy provenance and actual per-object extrusion envelopes."""
import hashlib,importlib.util,json,re,sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import numpy as np
from shapely.geometry import MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
HERE=Path(__file__).resolve().parent;LAYOUT=HERE.parent
sys.argv.append('unused')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
reader=module('read3mf',LAYOUT/'overit-import.py')
previous=module('previous',LAYOUT/'stojate-cepy-2026-09-20/overit.py')
NUM=re.compile(r'([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')

def parse(text):
 absolute=True;erel=False;pos=dict(X=0.,Y=0.,Z=0.,E=0.);role='Custom';owner=None;width=.5
 groups=defaultdict(lambda:defaultdict(list));widths=defaultdict(float)
 for line in text.splitlines():
  if line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
  if line.startswith(';WIDTH:'):width=float(line.split(':',1)[1])
  if line.startswith('EXCLUDE_OBJECT_START NAME='):owner=line.split('NAME=',1)[1].split('_id_',1)[0]
  if line.startswith('EXCLUDE_OBJECT_END'):owner=None
  code=line.split(';',1)[0].strip()
  if not code:continue
  cmd=code.split()[0];a={k:float(v) for k,v in NUM.findall(code)}
  if cmd=='G90':absolute=True
  elif cmd=='G91':absolute=False
  elif cmd=='M83':erel=True
  elif cmd=='M82':erel=False
  elif cmd=='G92':pos.update(a)
  elif cmd in ('G0','G1'):
   old=dict(pos)
   for k in ('X','Y','Z'):
    if k in a:pos[k]=a[k] if absolute else pos[k]+a[k]
   de=a.get('E',0) if erel else a.get('E',pos['E'])-pos['E']
   if 'E' in a:pos['E']=pos['E']+a['E'] if erel else a['E']
   if de>0 and (old['X']!=pos['X'] or old['Y']!=pos['Y']) and role!='Custom':
    assert owner is not None,('Unassigned extrusion',line,role)
    groups[owner][role].append([[old[k] for k in ('X','Y','Z')],[pos[k] for k in ('X','Y','Z')]]);widths[owner]=max(widths[owner],width)
  elif cmd in ('G2','G3') and role!='Custom':raise ValueError('Arc not supported by audit')
 return {n:{r:np.array(v) for r,v in d.items()} for n,d in groups.items()},widths

def main():
 manifest=json.loads((HERE/'rozlozeni.json').read_text());job=json.loads((HERE/'evidence/prikazy.json').read_text());source=Path(job['geometry']);project=Path(job['project']);sliced=Path(job['sliced'])
 original=json.loads((LAYOUT/'rozlozeni.json').read_text());expected={}
 selections={1:{8,11,12,13,14,17,19},2:{4,11,12,16,22,23},3:set(range(1,14))}
 for plate,numbers in selections.items():
  for i,p in enumerate((r for r in original['items'] if r['plate']==plate),1):
   if i in numbers:expected[Path(p['name']).stem]=(plate,i,p['source_sha256'])
 assert len(expected)==manifest['count']==26
 assert {p['copy_id'] for p in manifest['items']}==expected.keys()
 assert manifest['source_zip_sha256']==hashlib.sha256((LAYOUT.parent/'tiskovy-balicek.zip').read_bytes()).hexdigest()
 with ZipFile(LAYOUT.parent/'tiskovy-balicek.zip') as z:
  for p in manifest['items']:
   assert (p['source_plate'],p['source_number'],p['source_sha256'])==expected[p['copy_id']]
   assert hashlib.sha256(z.read(p['name'])).hexdigest()==p['source_sha256']
 assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['geometry_sha256']
 assert hashlib.sha256(project.read_bytes()).hexdigest()==job['project_sha256']
 with ZipFile(project) as z:
  assert not any(n.endswith('.gcode') for n in z.namelist());cfg=json.loads(z.read('Metadata/project_settings.config'));ocfg=previous.objcfg(z)
 with ZipFile(sliced) as z:
  gcode=z.read('Metadata/plate_1.gcode');after=json.loads(z.read('Metadata/project_settings.config'));assert ocfg==previous.objcfg(z)
  meta=E.fromstring(z.read('Metadata/slice_info.config'));info={m.get('key'):m.get('value') for m in meta.iter('metadata') if m.get('key') in ('prediction','weight','outside','support_used')};warnings=[w.attrib for w in meta.iter('warning')]
 diffs={k:[cfg.get(k),after.get(k)] for k in cfg.keys()|after.keys() if cfg.get(k)!=after.get(k)}
 assert diffs=={'machine_max_junction_deviation':[['0','0'],['0','0','0']]},diffs
 assert cfg['printer_model']=='Anycubic Kobra X' and cfg['nozzle_diameter']==['0.4'] and cfg['print_sequence']=='by layer'
 expected_supported={'plosina-170x60__01','osa-zadni-12x150_6__01','tehlice-prava__01','tehlice-leva__01'}
 assert {n for n,v in ocfg.items() if v['enable_support']=='1'}==expected_supported
 assert cfg['layer_height']=='0.12' and cfg['wall_loops']=='2' and cfg['sparse_infill_density']=='15%'
 for name,v in ocfg.items():
  if not name.startswith('plosina-'):assert v['wall_loops']=='4' and v['sparse_infill_density']=='100%'
 models=reader.meshes(source);assert len(models)==manifest['count'];delta=0
 for file in (project,sliced):
  actual=reader.meshes(file);assert actual.keys()==models.keys()
  for n,(v,f) in models.items():
   w,fs=actual[n];assert np.array_equal(f,fs);delta=max(delta,float(abs(v-w).max()));assert delta<2e-5
 groups,widths=parse(gcode.decode());assert groups.keys()==models.keys(),(groups.keys(),models.keys())
 records=[];footprints={};aggregate=defaultdict(list)
 for p in manifest['items']:
  name=p['copy_id'];roles=groups[name];pts=np.concatenate(list(roles.values())).reshape(-1,3)
  assert len(roles.get('Brim',[]))>0,name
  model_roles=[v for k,v in roles.items() if k!='Brim' and not k.startswith('Support')]
  assert model_roles,name
  model_pts=np.concatenate(model_roles).reshape(-1,3)
  assert abs(float(model_pts[:,2].max())-float(models[name][0][:,2].max()))<=float(cfg['layer_height'])+.02,(name,model_pts[:,2].max(),models[name][0][:,2].max())
  h=MultiPoint(pts[:,:2]).convex_hull.buffer(widths[name]/2);footprints[name]=h
  assert min(h.bounds[0],h.bounds[1],260-h.bounds[2],260-h.bounds[3])>1,name
  support=[v for k,v in roles.items() if k.startswith('Support')]
  assert bool(support)==(ocfg[name]['enable_support']=='1'),name
  record={'copy_id':name,'number':p['number'],'source_plate':p['source_plate'],'source_number':p['source_number'],'purpose':p['purpose'],'settings':ocfg[name],'brim_segments':len(roles['Brim']),'max_extrusion_width_mm':widths[name],'all_extrusion_bounds_mm':[pts.min(0).tolist(),pts.max(0).tolist()],'footprint_includes_model_brim_supports_and_half_line_width':True,'support_roles':{k:{'segments':len(v),'bounds_mm':[v.reshape(-1,3).min(0).tolist(),v.reshape(-1,3).max(0).tolist()]} for k,v in roles.items() if k.startswith('Support')}}
  record['model_extrusion_max_z_mm']=float(model_pts[:,2].max());record['model_extrusion_segments']=sum(len(v) for v in model_roles)
  records.append(record)
  for role,v in roles.items():aggregate[role].append(v)
 distances=[]
 names=list(footprints)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   d=footprints[a].distance(footprints[b]);assert d>1,(a,b,d)
   distances.append({'a':a,'b':b,'gap_mm':d})
 nearest=min(distances,key=lambda r:r['gap_mm'])
 fig,axs=plt.subplots(1,2,figsize=(16,10));colors=plt.get_cmap('tab20')
 for p in manifest['items']:
  n=p['copy_id'];h=footprints[n];coords=np.array(h.exterior.coords);axs[0].fill(*coords.T,color=colors(p['number']-1),alpha=.35);axs[0].plot(*coords.T,color=colors(p['number']-1));c=h.centroid;axs[0].text(c.x,c.y,str(p['number']),ha='center',va='center',fontsize=9)
  for role,v in groups[n].items():
   color='#e67514' if role.startswith('Support') else '#22834f' if role=='Brim' else '#688999'
   axs[1].add_collection(LineCollection(v[:,:,:2],colors=color,linewidths=.3,alpha=.6 if role.startswith('Support') or role=='Brim' else .15,rasterized=True))
 for ax in axs:ax.set(xlim=(0,260),ylim=(0,260),xlabel='X mm',ylabel='Y mm');ax.set_aspect('equal');ax.grid(alpha=.15)
 axs[0].set_title('Obálky všech skutečných drah + polovina šířky čáry');axs[1].set_title('Model modře / podpory oranžově / brim zeleně')
 fig.suptitle(f"Kombinovaná 03 · {manifest['count']} kusů · nejmenší mezera drah {nearest['gap_mm']:.2f} mm")
 fig.tight_layout(rect=(0,0,1,.95));fig.savefig(HERE/'evidence/drahy-a-odstupy.png',dpi=150);plt.close(fig)
 # Critical local layers per support-bearing object, full role inspection in report.
 supported=[n for n in names if ocfg[n]['enable_support']=='1']
 fig,axs=plt.subplots(len(supported),3,figsize=(15,4*len(supported)))
 for row,name in enumerate(supported):
  targets=[(3.92,4.16),(67.60,67.88),(68.84,69.08)] if name.startswith('plosina') else [(19.16,19.4),(52.92,53.16),(54.2,54.44)] if name.startswith('osa') else [(7.04,7.28),(10.88,11.12),(16.52,16.76)]
  szall=np.unique(np.concatenate([v for k,v in groups[name].items() if k.startswith('Support')])[:,1,2])
  mzall=np.unique(np.concatenate([v for k,v in groups[name].items() if k!='Brim' and not k.startswith('Support')])[:,1,2])
  for ax,(starget,mtarget) in zip(np.atleast_2d(axs)[row],targets):
   sz=float(szall[np.argmin(abs(szall-starget))]);mz=float(mzall[np.argmin(abs(mzall-mtarget))])
   for role,v in groups[name].items():
    if role=='Brim':continue
    issupport=role.startswith('Support');z=sz if issupport else mz
    selected=v[abs(v[:,1,2]-z)<.002]
    if len(selected):ax.add_collection(LineCollection(selected[:,:,:2],colors='#e67514' if issupport else '#527387',linewidths=.8))
   ax.autoscale();ax.margins(.1);ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title(f'{name}\npodpora Z={sz:.2f} / model Z={mz:.2f} mm',fontsize=9)
 fig.tight_layout();fig.savefig(HERE/'evidence/kriticke-vrstvy.png',dpi=150);plt.close(fig)
 report={'status':'pass_with_recorded_profile_warnings','count':manifest['count'],'source_geometry_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'sliced_sha256':hashlib.sha256(sliced.read_bytes()).hexdigest(),'gcode_sha256':hashlib.sha256(gcode).hexdigest(),'no_gcode_in_delivered_project':True,'maximum_mesh_vertex_delta_mm':delta,'metadata':info,'warnings':warnings,'normalization':diffs,'actual_path_envelopes_disjoint':True,'nearest_actual_extrusion_envelopes':nearest,'minimum_actual_extrusion_edge_mm':min(min(h.bounds[0],h.bounds[1],260-h.bounds[2],260-h.bounds[3]) for h in footprints.values()),'settings':{k:cfg[k] for k in previous.parser.KEYS if k in cfg},'objects':records,'limits':'All extrusion XY convex envelopes include model/support/brim paths and half maximum extrusion width. Startup/custom G-code excluded. Physical stability, removability, surface fit and machine performance not proven.'}
 (HERE/'overeni.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','count','metadata','nearest_actual_extrusion_envelopes','minimum_actual_extrusion_edge_mm')},indent=2))
if __name__=='__main__':main()
