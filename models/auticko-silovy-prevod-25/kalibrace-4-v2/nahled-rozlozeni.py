#!/usr/bin/env python3
"""Render actual XY triangle projections and their reserved hull envelopes."""
import argparse,io,json,zipfile,math
from pathlib import Path
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from shapely import Polygon

p=argparse.ArgumentParser();p.add_argument('layout_json');p.add_argument('output_dir');p.add_argument('--input-zip');p.add_argument('--title',default='Autíčko 25:1');a=p.parse_args()
d=json.loads(Path(a.layout_json).read_text());out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
colors=plt.get_cmap('tab20')
with zipfile.ZipFile(a.input_zip or d['source_zip']) as z:
 for plate in sorted({i['plate'] for i in d['items']}):
  items=[i for i in d['items'] if i['plate']==plate]
  fig=plt.figure(figsize=(15,10),facecolor='#f8f9fc');ax=fig.add_axes([.055,.15,.59,.78]);ax.set_aspect('equal')
  ax.set_xlim(-2,262);ax.set_ylim(-2,262);ax.set_xticks(range(0,261,20));ax.set_yticks(range(0,261,20));ax.grid(alpha=.16);ax.set_axisbelow(True)
  ax.add_patch(plt.Rectangle((0,0),260,260,edgecolor='#26374e',facecolor='white',lw=1.5,zorder=0))
  ax.add_patch(plt.Rectangle((6,6),248,248,edgecolor='#8492a6',facecolor='none',lw=.8,ls='--',zorder=1))
  ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]');labels=[]
  for j,i in enumerate(items,1):
   m=trimesh.load(io.BytesIO(z.read(i['name'])),file_type='stl',process=False)
   ang=math.radians(i['angle_deg']);r=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
   xy=m.vertices[:,:2]@r.T+np.array([i['dx_mm'],i['dy_mm']]);tri=xy[m.faces]
   # All triangle projections, including features overhanging upper layers. No silhouette simplification.
   ax.add_collection(PolyCollection(tri,facecolors=[colors((j-1)%20)],edgecolors='none',alpha=1,zorder=3,rasterized=True))
   hull=Polygon(i['placed_hull_xy']);pad=hull.buffer(5.1,quad_segs=32)
   coords=np.array(pad.exterior.coords);ax.fill(coords[:,0],coords[:,1],color=colors((j-1)%20),alpha=.11,zorder=2)
   ax.plot(coords[:,0],coords[:,1],color='#536479',alpha=.55,lw=.65,ls=':',zorder=4)
   c=hull.centroid;ax.text(c.x,c.y,str(j),ha='center',va='center',fontsize=9,fontweight='bold',zorder=6,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none','pad':1})
   labels.append(f"{j:02d}  {i['name'].removesuffix('.stl')}")
  fig.text(.67,.91,'DÍLY NA TÉTO PODLOŽCE',fontweight='bold',fontsize=11,color='#26374e')
  for j,l in enumerate(labels):fig.text(.67,.875-j*min(.022,.72/max(1,len(labels))),l,fontsize=min(8.5,360/max(1,len(labels))),fontfamily='monospace',color='#26374e')
  fig.text(.055,.955,f'{a.title} · podložka {plate} · {len(items)} kusů',fontsize=19,fontweight='bold',color='#1b2c43')
  fig.text(.055,.07,'Kobra X · 260 × 260 mm · měřítko 1 : 1 · pouze posun a otočení kolem svislé osy',fontsize=11,color='#26374e')
  fig.text(.055,.038,'Tečkovaná obálka: 5,1 mm rezerva pro brim. Náhled geometrie, nikoli náhled naslicovaných vrstev.',fontsize=10,color='#4c5c71')
  path=out/f'podlozka-{plate:02d}.png';fig.savefig(path,dpi=160);plt.close(fig);print(path)
