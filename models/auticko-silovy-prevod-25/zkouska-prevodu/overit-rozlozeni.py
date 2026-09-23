#!/usr/bin/env python3
"""Independently rebuild all convex XY envelopes from source STL coordinates."""
import argparse,io,json,zipfile,math,hashlib
from pathlib import Path
from collections import Counter
import numpy as np,trimesh
from shapely import MultiPoint,Polygon,box
p=argparse.ArgumentParser();p.add_argument('input_zip');p.add_argument('layout_json');p.add_argument('output_json');a=p.parse_args()
d=json.loads(Path(a.layout_json).read_text());proof={'source_zip_sha256':hashlib.sha256(Path(a.input_zip).read_bytes()).hexdigest(),'all_passed':False,'plates':[],'objects':[]};groups={}
assert proof['source_zip_sha256']==d['source_zip_sha256']
with zipfile.ZipFile(a.input_zip) as z:
 expected=sorted(n for n in z.namelist() if n.endswith('.stl'));actual=sorted(i['name'] for i in d['items']);assert expected==actual;assert len(expected)==d['count'];assert len(set(actual))==len(actual)
 for i in d['items']:
  data=z.read(i['name']);assert hashlib.sha256(data).hexdigest()==i['source_sha256'];m=trimesh.load(io.BytesIO(data),file_type='stl',process=False);assert abs(m.bounds[0,2])<1e-5
  assert i['scale']==1 and i['dz_mm']==0
  angle=math.radians(i['angle_deg']);rot=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]]);assert np.allclose(rot.T@rot,np.eye(3));assert abs(np.linalg.det(rot)-1)<1e-12
  moved=m.vertices@rot.T+[i['dx_mm'],i['dy_mm'],0];assert np.array_equal(m.vertices[:,2],moved[:,2]);h=MultiPoint(np.unique(moved[:,:2],axis=0)).convex_hull
  assert h.hausdorff_distance(Polygon(i['placed_hull_xy']))<1e-8
  groups.setdefault(i['plate'],[]).append((i['name'],h));proof['objects'].append({'name':i['name'],'plate':i['plate'],'source_sha256':hashlib.sha256(data).hexdigest(),'triangle_count':len(m.faces),'mesh_z_bounds_mm':m.bounds[:,2].tolist(),'transform_determinant':float(np.linalg.det(rot))})
assert sorted(groups)==list(range(1,len(groups)+1))
for plate,parts in sorted(groups.items()):
 distances=[{'a':an,'b':bn,'clearance_mm':ah.distance(bh)} for j,(an,ah) in enumerate(parts) for bn,bh in parts[j+1:]]
 minimum=min((x['clearance_mm'] for x in distances),default=float('inf'));edge=min(min(h.bounds[0],h.bounds[1],260-h.bounds[2],260-h.bounds[3]) for _,h in parts)
 assert minimum>=11-1e-8;assert edge>=6-1e-8
 total_bounds=MultiPoint([c for _,h in parts for c in h.exterior.coords]).bounds;center=[(total_bounds[0]+total_bounds[2])/2,(total_bounds[1]+total_bounds[3])/2];assert np.allclose(center,[130,130])
 proof['plates'].append({'plate':plate,'objects':len(parts),'all_within_6mm_edge':all(box(6-1e-8,6-1e-8,254+1e-8,254+1e-8).covers(h) for _,h in parts),'minimum_hull_clearance_mm':minimum,'minimum_brim_envelope_clearance_mm':minimum-2*5.1,'minimum_edge_clearance_mm':edge,'minimum_brim_to_bed_edge_mm':edge-5.1,'group_bbox_center_mm':center,'pair_checks':len(distances),'pair_distances':distances})
proof['count']=len(expected);proof['all_passed']=True;proof['method']='All original STL vertices, all-height convex XY hulls, pairwise Euclidean distances, no hole nesting; rigid Z rotations and XY translations only. Brim assumption width5mm + objectgap0.1mm. Does not prove support toolpath envelope or sliced layers.'
Path(a.output_json).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k not in ['objects','plates']},indent=2));print([(p['plate'],p['objects'],p['minimum_hull_clearance_mm']) for p in proof['plates']])
