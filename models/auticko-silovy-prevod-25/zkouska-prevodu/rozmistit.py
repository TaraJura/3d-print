#!/usr/bin/env python3
"""Pack unchanged STL hulls using only planar rotations and translations.
Transforms rotate counterclockwise about STL origin, then translate dx,dy.
"""
import argparse,io,zipfile,json,math,time,hashlib,random
from pathlib import Path
import numpy as np
import trimesh
from shapely import MultiPoint,Polygon,box
from shapely.affinity import rotate,translate
from scipy.spatial import ConvexHull

parser=argparse.ArgumentParser();parser.add_argument('input_zip');parser.add_argument('output_dir');parser.add_argument('--attempts',type=int,default=30);parser.add_argument('--large-threshold',type=float,default=175);parser.add_argument('--target-plates',type=int,default=2)
args=parser.parse_args();out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
raw={}; meshes={}
with zipfile.ZipFile(args.input_zip) as z:
 for n in z.namelist():
  if not n.lower().endswith('.stl'):continue
  data=z.read(n); m=trimesh.load(io.BytesIO(data),file_type='stl',process=False)
  hull=MultiPoint(np.unique(m.vertices[:,:2],axis=0)).convex_hull
  raw[n]={'hull':hull,'sha':hashlib.sha256(data).hexdigest(),'bounds':m.bounds.tolist()};meshes[n]=m
N=list(raw); GAP=11.05;EDGE=6;SIZE=260
assert N and len({Path(n).stem for n in N})==len(N),'STL names must be unique'
assert all(abs(raw[n]['bounds'][0][2])<1e-5 for n in N),'Sources must start at Z=0'
variants={};varids={};pid=0
for n in N:
 variants[n]=[]
 for a in [0,90,180,270]:
  h=rotate(raw[n]['hull'],a,origin=(0,0));minx,miny,x1,y1=h.bounds
  h=translate(h,-minx,-miny)
  # Canonicalize equivalent repeated geometry to reuse pairwise no-fit polygons.
  key=tuple(np.round(np.array(h.exterior.coords).flatten(),6))
  if key not in varids:varids[key]=pid;pid+=1
  v={'angle':a,'hull':h,'minx':minx,'miny':miny,'w':x1-minx,'h':y1-miny,'id':varids[key]}
  variants[n].append(v)
cache={}
def nfp(va,vb):
 key=(va['id'],vb['id'])
 if key in cache:return cache[key]
 aa=np.asarray(va['hull'].exterior.coords)[:-1];bb=-np.asarray(vb['hull'].exterior.coords)[:-1]
 pts=(aa[:,None,:]+bb[None,:,:]).reshape(-1,2)
 ch=ConvexHull(pts);poly=Polygon(pts[ch.vertices]).buffer(GAP,quad_segs=10)
 cache[key]=poly;return poly

def points(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon': return list(g.exterior.coords)
 if hasattr(g,'geoms'):return [p for e in g.geoms for p in points(e)]
 if hasattr(g,'coords'):return list(g.coords)
 return []
def choose(n,placed,mode=0,randomize=False):
 opts=[]
 for v in variants[n]:
  if v['w']>SIZE-2*EDGE or v['h']>SIZE-2*EDGE:continue
  free=box(EDGE,EDGE,SIZE-EDGE-v['w'],SIZE-EDGE-v['h'])
  for item in placed:
   avoid=translate(nfp(item['variant'],v),item['x'],item['y'])
   free=free.difference(avoid)
   if free.is_empty:break
  pts=points(free)
  if not pts:continue
  # Boundary of buffered polygon can underapproximate euclidean clearance; reject against exact hull distance.
  pts=sorted(pts,key=lambda p:(round(p[1]+v['h'],5),round(p[0],5)))[:25]
  for x,y in pts:
   h=translate(v['hull'],x,y)
   if any(h.distance(i['poly'])<11.0-1e-7 for i in placed):continue
   maxy=max([y+v['h']]+[i['y']+i['variant']['h'] for i in placed])
   maxx=max([x+v['w']]+[i['x']+i['variant']['w'] for i in placed])
   if mode==0:score=y+v['h']+x*.015
   elif mode==1:score=maxy+maxx*.03+y*.01
   elif mode==2:score=y+v['h']*.4+x*.025
   else:score=maxy*maxx+y*5+x*.1
   opts.append((score,x,y,v,h));break
 if not opts:return None
 opts.sort(key=lambda a:a[0]);score,x,y,v,h=opts[0]
 return {'name':n,'x':x,'y':y,'variant':v,'poly':h}
def pack(order,mode):
 placed=[];missing=[]
 for n in order:
  c=choose(n,placed,mode)
  if c:placed.append(c)
  else:missing.append(n)
 return placed,missing

def save_layout(plates):
 result=[];proof=[]
 for pnum,placed in enumerate(plates,1):
  bb=np.array([i['poly'].bounds for i in placed]);x0,y0=np.min(bb[:,:2],axis=0);x1,y1=np.max(bb[:,2:],axis=0)
  ox=130-(x0+x1)/2;oy=130-(y0+y1)/2
  polys=[]
  for i in placed:
   v=i['variant'];dx=i['x']-v['minx']+ox;dy=i['y']-v['miny']+oy
   poly=translate(rotate(raw[i['name']]['hull'],v['angle'],origin=(0,0)),dx,dy);polys.append(poly)
   result.append({'name':i['name'],'plate':pnum,'angle_deg':v['angle'],'dx_mm':dx,'dy_mm':dy,'dz_mm':0.0,'scale':1.0,'source_sha256':raw[i['name']]['sha'],'source_bounds_mm':raw[i['name']]['bounds'],'placed_hull_xy':list(map(list,poly.exterior.coords))})
  minimum=min((p.distance(q) for k,p in enumerate(polys) for q in polys[k+1:]),default=None)
  edge=min(min(h.bounds[0],h.bounds[1],SIZE-h.bounds[2],SIZE-h.bounds[3]) for h in polys)
  proof.append({'plate':pnum,'count':len(placed),'minimum_hull_clearance_mm':minimum,'minimum_edge_clearance_mm':edge,'group_bbox_center_mm':[130,130],'all_pairs_tested':len(polys)*(len(polys)-1)//2,'all_inside':all(box(EDGE-.00001,EDGE-.00001,SIZE-EDGE+.00001,SIZE-EDGE+.00001).covers(p) for p in polys)})
 content={'units':'mm','transform_convention':'Rotate original STL about +Z counterclockwise by angle_deg (right-handed), then translate by dx_mm,dy_mm,dz_mm; scale=1. Z unchanged. Plate origin is front-left0,0.','source_zip':str(Path(args.input_zip).resolve()),'source_zip_sha256':hashlib.sha256(Path(args.input_zip).read_bytes()).hexdigest(),'plate_mm':[260,260],'clearance_policy':{'minimum_hull_gap_mm':11.0,'minimum_edge_mm':6.0,'process_assumption':'brim_width=5mm, brim_object_gap=0.1mm, no skirt; this geometry-only sample requires review of local supports. Local support toolpaths have not been sliced or verified and must fit inside the reserved envelope.'},'count':len(result),'items':result,'proof':proof,'heuristic':'convex hulls over all Z, no nesting in holes; greedy no-fit polygon search, rotations0/90/180/270; no claim global optimum'}
 (out/'rozlozeni.json').write_text(json.dumps(content,indent=2)+'\n')
 return content

# Reproducible greedy search. Keep large frame/deck on their own plate first;
# all other parts, including all four wheels, fill the first plate when possible.
# No assumptions about a fixed bill of materials, copy count or plate count.
rng=random.Random(20260919);start=time.time();best=None;bestscore=None
large=[n for n in N if max(raw[n]['bounds'][1][j]-raw[n]['bounds'][0][j] for j in [0,1])>=args.large_threshold]
target=[n for n in N if n not in large]
for attempt in range(args.attempts):
 mode=attempt%4
 order=sorted(target,key=lambda n:raw[n]['hull'].area*(1 if attempt<4 else rng.uniform(.6,1.7)),reverse=True)
 first,missing=pack(order,mode)
 plates=[first] if first else []
 remaining=sorted(large,key=lambda n:raw[n]['hull'].area,reverse=True)+missing
 while remaining:
  placed,more=pack(remaining,mode)
  if not placed:raise RuntimeError('Part cannot fit usable plate: '+repr(more))
  plates.append(placed);remaining=more
 score=(len(plates),-len(first),sum(max(i['y']+i['variant']['h'] for i in p) for p in plates))
 if bestscore is None or score<bestscore:
  best=plates;bestscore=score;save_layout(plates)
  print('BEST',list(map(len,plates)),'attempt',attempt,'seconds',round(time.time()-start,1),flush=True)
 if len(plates)<=args.target_plates and not missing:break
 if attempt%5==0:print('progress',attempt,'best',bestscore,'cache',len(cache),'seconds',round(time.time()-start,1),flush=True)
print('Done',list(map(len,best)),'seconds',round(time.time()-start,1),flush=True)
