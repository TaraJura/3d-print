from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import numpy as np, json
z=ZipFile('/home/novakj/Downloads/trash-bag-holder-d60-l200_g.3mf')
r=ET.fromstring(z.read('3D/3dmodel.model'));ns={'m':r.tag.split('}')[0][1:]}
v=np.array([[float(a.attrib[c]) for c in 'xyz'] for a in r.findall('.//m:vertex',ns)])
f=np.array([[int(a.attrib[c]) for c in ('v1','v2','v3')] for a in r.findall('.//m:triangle',ns)])
print('bounds',v.min(0),v.max(0))
from collections import Counter
for ax in range(3): print('planes',ax,Counter(np.round(v[:,ax],4)).most_common(16))
sections={}
for h in [0,50,80,96,98,99,-96,-98,-99]:
 ts=v[f];ts=ts[(ts[:,:,2].min(1)<h)&(ts[:,:,2].max(1)>h)]
 segs=[]
 for t in ts:
  pts=[]
  for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:
   if (a[2]<h<b[2]) or (b[2]<h<a[2]): pts.append((a+(b-a)*(h-a[2])/(b[2]-a[2]))[:2].tolist())
  if len(pts)==2:segs.append(pts)
 sections[str(h)]=segs
 print('section',h,len(segs))
 if h==0:
  for a,b in segs:
   if np.linalg.norm(np.array(a)-b)>2:print('long segment',np.round(a,4),np.round(b,4))
(Path(__file__).parent/'vstup/rezy.json').write_text(json.dumps(sections))
