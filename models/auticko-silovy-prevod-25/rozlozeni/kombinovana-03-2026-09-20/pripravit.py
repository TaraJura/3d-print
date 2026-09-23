#!/usr/bin/env python3
"""Single combined plate: original plate 3 (13) + first repairs (7) + second repairs (6).
Uses exact existing orientations; no changes to CAD/STL or source-copy counts.
"""
import hashlib,importlib.util,json
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
HERE=Path(__file__).resolve().parent;LAYOUT=HERE.parent;MODEL=LAYOUT.parent
SECOND_REPLACEMENTS={4,11,12,16,22,23}
CENTRES=[(130,60),(83,210),(50,178.5),(82,178.5),(114,178.5),(146,178.5),(178,178.5),(210,178.5),(242,178.5),(18,210),(50,210),(18,178.5),(114,210),(154,139),(37,139),(146,210),(178,210),(210,210),(242,210),(18,241.5),(96,139),(50,241.5),(114,241.5),(82,241.5),(146,241.5),(178,241.5)]

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
core=module('core',LAYOUT/'vytvorit-3mf.py');reader=module('reader',LAYOUT/'overit-import.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 manifest=json.loads((LAYOUT/'rozlozeni.json').read_text());repair=json.loads((LAYOUT/'dotisk-prvni-varky-2026-09-20/overeni-dotisku.json').read_text())
 assert sha(MODEL/'tiskovy-balicek.zip')==manifest['source_zip_sha256']==repair['source_zip_sha256']
 rows=[dict(r,source_plate=3,source_number=i+1,purpose='original_remaining') for i,r in enumerate(p for p in manifest['items'] if p['plate']==3)]
 rows += [dict(r,source_plate=1,source_number=r['original_number'],purpose='first_batch_replacement') for r in repair['items']]
 rows += [dict(r,source_plate=2,source_number=i,purpose='second_batch_replacement',rotation_matrix=[[0,0,-1],[0,1,0],[1,0,0]]) for i,r in enumerate((p for p in manifest['items'] if p['plate']==2),1) if i in SECOND_REPLACEMENTS]
 assert len(rows)==26 and len({r['name'] for r in rows})==26 and len([r for r in rows if r['purpose']=='original_remaining'])==13
 parts=[]
 with ZipFile(MODEL/'tiskovy-balicek.zip') as z:
  for num,row in enumerate(rows,1):
   name=row['name'];data=z.read(name);assert hashlib.sha256(data).hexdigest()==row['source_sha256']
   v,f=core.stl(data);v=np.array(v);f=np.array(f);R=np.array(row['rotation_matrix']);w=v@R.T
   centre=CENTRES[num-1]
   t=np.r_[np.array(centre)-(w[:,:2].min(0)+w[:,:2].max(0))/2,-w[:,2].min()];w+=t
   mesh=trimesh.Trimesh(w,f,process=False);src=trimesh.Trimesh(v,f,process=False);assert mesh.is_watertight and np.linalg.det(R)==1 and abs(mesh.volume-src.volume)<1e-5
   assert abs(w[:,2].min())<1e-8 and w[:,2].max()<260
   hull=MultiPoint(w[:,:2]).convex_hull;brim=12 if name.startswith('osa-zadni') else 8
   row.update(copy_id=Path(name).stem,number=num,plate=1,angle_deg=0,rotation_matrix=R.tolist(),translation_mm=t.tolist(),dx_mm=float(t[0]),dy_mm=float(t[1]),dz_mm=float(t[2]),scale=1,bounds_mm=mesh.bounds.tolist(),brim_mm=brim,placed_hull_xy=list(map(list,hull.exterior.coords)),triangles=len(f),_v=w,_f=f,_src=v,_h=hull)
   parts.append(row)
  gap=min(a['_h'].buffer(a['brim_mm']+.1).distance(b['_h'].buffer(b['brim_mm']+.1)) for i,a in enumerate(parts) for b in parts[i+1:])
  edge=min(min(p['_h'].bounds[0],p['_h'].bounds[1],260-p['_h'].bounds[2],260-p['_h'].bounds[3])-p['brim_mm']-.1 for p in parts)
  assert gap>2 and edge>3,(gap,edge)
  core.write_plate(HERE/'auticko-25-kombinovana-03-geometrie.3mf',parts,z)
 actual=reader.meshes(HERE/'auticko-25-kombinovana-03-geometrie.3mf');assert len(actual)==26
 for p in parts:
  v,f=actual[p['copy_id']];assert np.array_equal(f,p['_f']);assert abs((v-np.array(p['translation_mm']))@np.array(p['rotation_matrix'])-p['_src']).max()<1e-8
 report={'status':'geometry_pass_actual_support_paths_in_separate_overeni_json','description':'One print instead of original 03 and the first-batch repair plates, plus six second-batch replacements; never add those copies again. Frame and incomplete inventory remain separate unresolved questions.','units':'mm','scale':1,'count':26,'original_remaining':13,'first_batch_replacements':7,'second_batch_replacements':6,'second_batch_quality':'photos 20260920_185846 and 20260920_192335; see inventar-druhe-varky.json','source_zip_sha256':sha(MODEL/'tiskovy-balicek.zip'),'geometry_sha256':sha(HERE/'auticko-25-kombinovana-03-geometrie.3mf'),'min_brim_envelope_gap_mm':gap,'min_brim_envelope_edge_mm':edge,'items':[{k:v for k,v in p.items() if not k.startswith('_')} for p in parts]}
 (HERE/'rozlozeni.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 fig=plt.figure(figsize=(16,12),facecolor='white');ax=fig.add_axes([.05,.17,.56,.73]);ax.set_aspect('equal');ax.set(xlim=(0,260),ylim=(0,260),xlabel='X [mm]',ylabel='Y [mm]');ax.grid(alpha=.15);colors=plt.get_cmap('tab20')
 for p in parts:
  n=p['number'];c=colors(n-1);pad=np.array(p['_h'].buffer(p['brim_mm']+.1).exterior.coords);ax.plot(*pad.T,':',color=c,lw=1)
  ax.add_collection(PolyCollection(p['_v'][p['_f']][:,:,:2],facecolors=[c],edgecolors='none'))
  centre=p['_h'].centroid;ax.text(centre.x,centre.y,str(n),ha='center',va='center',fontweight='bold',bbox={'facecolor':'white','edgecolor':'none'})
  fig.text(.63,.895-(n-1)*.019,f"{n:02d}  {p['copy_id']}"+('  [náhrada]' if n>13 else ''),fontsize=8.5)
 side=fig.add_axes([.63,.11,.34,.27],projection='3d')
 for p in parts:side.add_collection3d(Poly3DCollection(p['_v'][p['_f']],facecolors=[colors(p['number']-1)],edgecolors=None,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=315,altdeg=45)))
 side.set(xlim=(0,250),ylim=(10,245),zlim=(0,152));side.set_box_aspect((250,235,152));side.view_init(elev=27,azim=-60);side.set_axis_off()
 fig.text(.05,.955,'Kombinovaná 03 · 13 původních + 7 + 6 náhrad = 26 kusů',fontsize=20,fontweight='bold')
 fig.text(.05,.09,'Jedna podložka Kobra X · tisknout jednou NAMÍSTO původní 03 a celé opravné sady',fontsize=13,fontweight='bold')
 fig.text(.05,.05,'100 % měřítko · všechny čepy a osa nastojato · skutečná geometrie; podpory se kontrolují v řezu',fontsize=11)
 fig.savefig(HERE/'podlozka.png',dpi=160);plt.close(fig)
 print(json.dumps({k:v for k,v in report.items() if k!='items'},indent=2))
if __name__=='__main__':main()
