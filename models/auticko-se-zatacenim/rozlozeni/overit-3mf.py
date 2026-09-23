#!/usr/bin/env python3
"""Independent geometry/clearance audit of 3MF documents against original STL."""
import argparse,hashlib,json,math,struct,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
import numpy as np
from shapely.geometry import MultiPoint,box
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('zip',type=Path);ap.add_argument('layout',type=Path);ap.add_argument('directory',type=Path);args=ap.parse_args()
 layout=json.loads(args.layout.read_text());assert layout['source_zip_sha256']==hashlib.sha256(args.zip.read_bytes()).hexdigest();items=layout['items'];assert all(x['scale']==1 and x['dz_mm']==0 for x in items);positions={Path(p['name']).stem:p for p in items};seen=[];plates=[]
 with zipfile.ZipFile(args.zip) as src:
  for f in sorted(args.directory.glob('auticko-v3-podlozka-*.3mf')):
   with zipfile.ZipFile(f) as z:
    assert sorted(z.namelist())==['3D/3dmodel.model','[Content_Types].xml','_rels/.rels'],'Unexpected configuration payload'
    root=E.fromstring(z.read('3D/3dmodel.model'));assert root.attrib['unit']=='millimeter'
    objects=root.findall('m:resources/m:object',NS);build=root.findall('m:build/m:item',NS)
    assert len(objects)==len(build);assert {x.attrib['objectid'] for x in build}=={x.attrib['id'] for x in objects}
    assert all('transform' not in x.attrib for x in build)
    shapes=[];records=[]
    for obj in objects:
     name=obj.attrib['name'];p=positions[name];seen.append(name)
     v=np.array([[float(x.attrib[c]) for c in ['x','y','z']] for x in obj.findall('m:mesh/m:vertices/m:vertex',NS)])
     t=np.array([[int(x.attrib[c]) for c in ['v1','v2','v3']] for x in obj.findall('m:mesh/m:triangles/m:triangle',NS)])
     actual=v[t]
     data=src.read(p['name']);n=struct.unpack_from('<I',data,80)[0];assert len(t)==n
     original=np.array([struct.unpack_from('<12fH',data,84+50*i)[3:12] for i in range(n)]).reshape(n,3,3)
     # Undo only the documented rigid planar placement; original 3D facets must be retained.
     back=actual.copy();back[:,:,0]-=p['dx_mm'];back[:,:,1]-=p['dy_mm']
     a=math.radians(p['angle_deg']);r=np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]])
     back[:,:,:2]=back[:,:,:2]@r.T
     err=float(abs(back-original).max());assert err<1e-6,(name,err)
     assert abs(v[:,2].min())<1e-5;assert v[:,2].max()<=260
     footprint=MultiPoint(v[:,:2]).convex_hull
     edge=float(footprint.distance(box(0,0,260,260).boundary));assert box(6-1e-5,6-1e-5,254+1e-5,254+1e-5).covers(footprint)
     shapes.append(footprint);records.append({'name':name,'facets':n,'max_facet_error_mm':err,'edge_clearance_mm':edge,'bounds_mm':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]})
    distances=[float(a.distance(b)) for i,a in enumerate(shapes) for b in shapes[i+1:]]
    assert not distances or min(distances)>=11-1e-5
    unionbounds=np.array([s.bounds for s in shapes]);center=[(unionbounds[:,0].min()+unionbounds[:,2].max())/2,(unionbounds[:,1].min()+unionbounds[:,3].max())/2]
    assert max(abs(c-130) for c in center)<1e-5,center
    plates.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'count':len(objects),'minimum_convex_hull_gap_mm':min(distances) if distances else None,'center_mm':center,'objects':records})
  expected=[Path(n).stem for n in src.namelist() if n.lower().endswith('.stl')]
  assert sorted(seen)==sorted(expected);assert len(seen)==33
 wheels=sorted(r['name'] for r in plates[0]['objects'] if r['name'].startswith('kolo-'))
 expected_wheels=sorted(['kolo-zadni-76x12-72z__01','kolo-zadni-76x12-prave__01','kolo-predni-76x12__01','kolo-predni-76x12__02']);assert wheels==expected_wheels
 report={'four_wheels_verified_on_plate_1':wheels,'status':'pass','source_zip_sha256':hashlib.sha256(args.zip.read_bytes()).hexdigest(),'objects':len(seen),'unit':'millimeter','scale':1,'rotation_only_about_z':True,'preserved_source_facets':True,'minimum_required_object_gap_mm':11,'minimum_required_edge_clearance_mm':6,'configuration_embedded':False,'plate_count':len(plates),'plates':plates}
 (args.directory/'overeni-3mf.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='plates'},indent=2))
if __name__=='__main__':main()
