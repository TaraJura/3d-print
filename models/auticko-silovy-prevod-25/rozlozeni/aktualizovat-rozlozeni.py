#!/usr/bin/env python3
"""Rebind existing rigid placements to a complete new STL ZIP; fail on any gap/boundary/count problem.
Only writes the explicitly supplied output JSON after all geometry checks pass.
"""
import argparse, hashlib, io, json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import trimesh
from shapely import MultiPoint, box
from shapely.affinity import rotate, translate
p=argparse.ArgumentParser()
p.add_argument('old_layout',type=Path);p.add_argument('new_zip',type=Path);p.add_argument('output',type=Path)
p.add_argument('--expected-count',type=int,required=True)
a=p.parse_args()
old=json.loads(a.old_layout.read_text()); result={k:v for k,v in old.items() if k not in ['items','proof']}
assert not any('rotation_matrix' in i for i in old['items']), 'Planar historical updater cannot modify upright revision; use stojate-cepy-2026-09-20/pripravit.py and verify new source dimensions.'
assert a.output.resolve()!=Path(__file__).resolve().parent/'rozlozeni.json', 'Canonical manifest is owned by stojate-cepy-2026-09-20/pripravit.py; historical planar updates must use a new directory.'
assert len(old['items'])==a.expected_count
items=[];changed=[];proof=[]
with ZipFile(a.new_zip) as z:
 names=[n for n in z.namelist() if n.lower().endswith('.stl')]
 assert len(set(names))==len(names)==a.expected_count
 assert sorted(names)==sorted(i['name'] for i in old['items'])
 for row in old['items']:
  assert row['scale']==1 and row['dz_mm']==0
  data=z.read(row['name']);mesh=trimesh.load(io.BytesIO(data),file_type='stl',process=False)
  bounds=mesh.bounds;assert abs(bounds[0,2])<1e-5 and bounds[1,2]<=260
  hull=MultiPoint(np.unique(mesh.vertices[:,:2],axis=0)).convex_hull
  placed=translate(rotate(hull,row['angle_deg'],origin=(0,0)),row['dx_mm'],row['dy_mm'])
  assert box(6-1e-5,6-1e-5,254+1e-5,254+1e-5).covers(placed),('Outside plate',row['name'])
  n=dict(row);n.update(source_sha256=hashlib.sha256(data).hexdigest(),source_bounds_mm=bounds.tolist(),placed_hull_xy=list(map(list,placed.exterior.coords)))
  items.append(n)
  if n['source_sha256']!=row['source_sha256']:
   changed.append({'name':row['name'],'previous_sha256':row['source_sha256'],'new_sha256':n['source_sha256'],'maximum_bbox_delta_mm':float(np.max(np.abs(bounds-np.array(row['source_bounds_mm']))))})
 for pn in sorted({i['plate'] for i in items}):
  rows=[i for i in items if i['plate']==pn]
  hulls=[MultiPoint(i['placed_hull_xy']).convex_hull for i in rows]
  gap=min((h.distance(g) for j,h in enumerate(hulls) for g in hulls[j+1:]),default=None)
  assert gap is None or gap>=11-1e-5,('Insufficient gap',pn,gap)
  edge=min(min(h.bounds[0],h.bounds[1],260-h.bounds[2],260-h.bounds[3]) for h in hulls)
  bb=np.array([h.bounds for h in hulls]);center=[float((bb[:,0].min()+bb[:,2].max())/2),float((bb[:,1].min()+bb[:,3].max())/2)]
  assert max(abs(v-130) for v in center)<1e-5,('Noncentered changed envelope',pn,center)
  proof.append({'plate':pn,'count':len(rows),'minimum_hull_clearance_mm':gap,'minimum_edge_clearance_mm':edge,'group_bbox_center_mm':center,'all_pairs_tested':len(rows)*(len(rows)-1)//2,'all_inside':True})
result.update(source_zip=str(a.new_zip.resolve()),source_zip_sha256=hashlib.sha256(a.new_zip.read_bytes()).hexdigest(),count=len(items),items=items,proof=proof,
 placement_revision={'method':'Previous rigid planar transforms retained; every hull, boundary and pair distance recomputed from current ZIP vertices.',
  'previous_layout_sha256':hashlib.sha256(a.old_layout.read_bytes()).hexdigest(),'changed_mesh_copies':changed})
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'count':len(items),'changed_mesh_copies':len(changed),'plates':proof},indent=2))
