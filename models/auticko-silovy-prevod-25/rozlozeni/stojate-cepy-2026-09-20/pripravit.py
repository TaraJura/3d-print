#!/usr/bin/env python3
"""Rebuild only original plate 03, with six pins upright. No printer access.
Source geometry hashes are locked: changed geometry requires a new orientation
review. Original plates 01/02 and canonical CAD/STL/ZIP are never rewritten.
"""
import hashlib, importlib.util, json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import trimesh
from shapely.geometry import MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
HERE=Path(__file__).resolve().parent
LAYOUT=HERE.parent; MODEL=LAYOUT.parent
ARCHIVE=MODEL/'historie/pred-stojatou-orientaci-2026-09-20'
RY=np.array([[0.,0.,-1.],[0.,1.,0.],[1.,0.,0.]])
PINS={3,4,6,7,8,9}
def helper(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
core=helper('core',LAYOUT/'vytvorit-3mf.py')
reader=helper('reader',LAYOUT/'overit-import.py')

def main():
 old=json.loads((ARCHIVE/'rozlozeni.json').read_text())
 assert sha(MODEL/'tiskovy-balicek.zip')==old['source_zip_sha256'], 'Changed geometry requires a new explicit orientation review'
 previous=json.loads((LAYOUT/'rozlozeni.json').read_text())
 assert [i for i in previous['items'] if i['plate']<3]==[i for i in old['items'] if i['plate']<3]
 keep={str(p.relative_to(MODEL)):sha(p) for p in [MODEL/'auticko-silovy-prevod-25.FCStd',MODEL/'tiskovy-balicek.zip',LAYOUT/'auticko-25-podlozka-01.3mf',LAYOUT/'auticko-25-podlozka-02.3mf']}
 parts=[]
 with ZipFile(MODEL/'tiskovy-balicek.zip') as z:
  for number,row in enumerate([p for p in old['items'] if p['plate']==3],1):
   data=z.read(row['name']);assert hashlib.sha256(data).hexdigest()==row['source_sha256']
   v,f=core.stl(data);v=np.array(v);f=np.array(f);R=RY if number in PINS else np.eye(3)
   w=v@R.T
   if number==1: centre=np.array([130.,69.])
   else: centre=np.array([40.+36*((number-2)%6),160.+50*((number-2)//6)])
   t=np.r_[centre-(w[:,:2].min(0)+w[:,:2].max(0))/2,-w[:,2].min()];w+=t
   mesh=trimesh.Trimesh(w,f,process=False);source=trimesh.Trimesh(v,f,process=False)
   assert mesh.is_watertight and abs(mesh.volume-source.volume)<1e-5 and np.linalg.det(R)==1
   assert abs(w[:,2].min())<1e-8 and w[:,2].max()<=260
   h=MultiPoint(w[:,:2]).convex_hull
   p=dict(row);p.update(angle_deg=0,dx_mm=float(t[0]),dy_mm=float(t[1]),dz_mm=float(t[2]),rotation_matrix=R.tolist(),translation_mm=t.tolist(),placed_hull_xy=list(map(list,h.exterior.coords)))
   old['items'][old['items'].index(row)]=p
   contact=float(mesh.area_faces[(mesh.face_normals[:,2]<-.999999)&(mesh.triangles_center[:,2]<1e-7)].sum())
   parts.append(dict(number=number,name=row['name'],upright_pin=number in PINS,bounds_mm=mesh.bounds.tolist(),planar_contact_mm2=contact,triangles=len(f),source_sha256=row['source_sha256'],rotation_matrix=R.tolist(),translation_mm=t.tolist(),_v=w,_f=f,_source=v,_h=h))
  gap=min(a['_h'].distance(b['_h']) for i,a in enumerate(parts) for b in parts[i+1:]);edge=min(min(p['_h'].bounds[0],p['_h'].bounds[1],260-p['_h'].bounds[2],260-p['_h'].bounds[3]) for p in parts)
  assert gap>16.2 and edge>8.1,(gap,edge)
  source3mf=LAYOUT/'auticko-25-podlozka-03.3mf'
  core.write_plate(source3mf,[i for i in old['items'] if i['plate']==3],z)
 actual=reader.meshes(source3mf);assert len(actual)==13
 for p in parts:
  v,f=actual[Path(p['name']).stem];assert np.array_equal(f,p['_f'])
  inv=(v-np.array(p['translation_mm']))@np.array(p['rotation_matrix']);assert np.max(abs(inv-p['_source']))<1e-8
 old.update(transform_convention='With rotation_matrix: world = source @ R.T + translation_mm; scale 1. Legacy rows without matrix keep XY rotation/translation. Full-3D transform takes precedence over legacy compatibility fields.',orientation_revision='stojate-cepy-2026-09-20/pripravit.py',current_validation='stojate-cepy-2026-09-20/overeni-geometrie.json; old reports describe the archived XY-only revision')
 old['clearance_policy']['plate_3_override']={'minimum_hull_gap_mm':gap,'minimum_edge_mm':edge,'reserved_brim_mm':8.1,'actual_process':'See current configured Next project and overeni-projektu.json'}
 old.pop('proof',None);old['placement_revision']={'scope':'Only plate 3 changed; six pins upright, thirteen physical pieces unchanged. Plates 1/2 are historical printed plates.'}
 (LAYOUT/'rozlozeni.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
 # Actual triangles in XY and axonometry; numbers match original plate-3 BOM.
 fig=plt.figure(figsize=(16,11),facecolor='white');ax=fig.add_axes([.05,.15,.56,.76]);ax.set_aspect('equal');ax.set(xlim=(0,260),ylim=(0,260),xlabel='X [mm]',ylabel='Y [mm]');ax.grid(alpha=.15)
 colors=plt.get_cmap('tab20')
 for p in parts:
  j=p['number'];v=p['_v'];f=p['_f'];c=colors(j-1)
  pad=np.array(p['_h'].buffer(8.1).exterior.coords);ax.plot(*pad.T,':',color=c,lw=1)
  ax.add_collection(PolyCollection(v[f][:,:,:2],facecolors=[c],edgecolors='none'))
  centre=p['_h'].centroid;ax.text(centre.x,centre.y,str(j),ha='center',va='center',fontweight='bold',bbox={'facecolor':'white','edgecolor':'none'})
  fig.text(.63,.88-(j-1)*.026,f"{j:02d}  {p['name'].removesuffix('.stl')}",fontsize=9)
 side=fig.add_axes([.63,.13,.34,.36],projection='3d')
 for p in parts: side.add_collection3d(Poly3DCollection(p['_v'][p['_f']],facecolors=[colors(p['number']-1)],edgecolors=None,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=315,altdeg=45)))
 side.set(xlim=(20,240),ylim=(20,225),zlim=(0,75));side.set_box_aspect((220,205,75));side.view_init(elev=28,azim=-60);side.set_axis_off()
 fig.text(.05,.96,'Původní podložka 03 · 13 kusů · šest čepů nastojato',fontsize=21,fontweight='bold')
 fig.text(.05,.07,'Kobra X 260 × 260 mm · 100 % · plošina + 12 malých dílů · nic nekopírovat',fontsize=12)
 fig.text(.05,.035,'Číslování původního kusovníku. Skutečná geometrie; tečky = 8,1 mm rezerva. Podpory ověřeny zvlášť v řezu.',fontsize=10)
 fig.savefig(LAYOUT/'podlozka-03.png',dpi=150);plt.close(fig)
 assert all(sha(MODEL/p)==h for p,h in keep.items())
 report={'status':'pass','plate':3,'count':13,'upright_pin_numbers':sorted(PINS),'units':'mm','scale':1,'min_z':0,'max_z_mm':max(p['bounds_mm'][1][2] for p in parts),'minimum_hull_gap_mm':gap,'minimum_edge_mm':edge,'source_zip_sha256':sha(MODEL/'tiskovy-balicek.zip'),'geometry_3mf_sha256':sha(source3mf),'unchanged':keep,'items':[{k:v for k,v in p.items() if not k.startswith('_')} for p in parts]}
 (HERE/'overeni-geometrie.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('items','unchanged')},indent=2))
if __name__=='__main__': main()
