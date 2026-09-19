#!/usr/bin/env python3
"""Nezávislá kontrola skutečných binárních STL a finálních souborových hashů.
Spouštět po generátoru a GUI náhledu. Zapisuje pouze overeni-exportu.json.
"""
from pathlib import Path
from collections import defaultdict
import json,struct,hashlib,zipfile,re,math
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'kontrola-modelu.json').read_text())
assert report['validation_pass'] and report['gui_validation']['saved_and_reopened']
def sha(b):return hashlib.sha256(b).hexdigest()
result={'generator_sha256':sha((ROOT/'auticko-s-prevodovkou.FCMacro').read_bytes()),'files':{},'stl':{}}
for name in ['auticko-s-prevodovkou.FCStd','tiskovy-balicek.zip','nahled.FCMacro','README.md','kontrola-modelu.json','sestava.png','prevodovka.png','rozlozena-plosina.png','tiskove-dily.png']:
    b=(ROOT/name).read_bytes();result['files'][name]={'sha256':sha(b),'bytes':len(b)}
for key,info in report['parts'].items():
    path=ROOT/info['stl'];data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+n*50
    edges=defaultdict(list);vertexids={};vertices=[];signed_volume=0.;degenerate=0;tris=[]
    for i in range(n):
        q=struct.unpack_from('<12fH',data,84+i*50);vv=[q[3:6],q[6:9],q[9:12]];ids=[]
        for v in vv:
            k=tuple(round(x,5) for x in v)
            if k not in vertexids:vertexids[k]=len(vertices);vertices.append(k)
            ids.append(vertexids[k])
        a,b,c=vv;ab=[b[j]-a[j] for j in range(3)];ac=[c[j]-a[j] for j in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        if len(set(ids))!=3 or sum(t*t for t in cross)<1e-18:degenerate+=1
        signed_volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for j,k in ((0,1),(1,2),(2,0)):edges[tuple(sorted((ids[j],ids[k])))].append((i,1 if ids[j]<ids[k] else -1))
    parent=list(range(n))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    badedges=0;badorientation=0
    for occurrences in edges.values():
        if len(occurrences)!=2:badedges+=1
        else:
            if sum(t[1] for t in occurrences)!=0:badorientation+=1
            a,b=(root(x[0]) for x in occurrences);parent[a]=b
    components=len({root(i) for i in range(n)});bb=[max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)]
    rel=abs(signed_volume-info['volume_mm3'])/info['volume_mm3']
    assert badedges==badorientation==degenerate==0 and components==1 and signed_volume>0 and rel<0.01,(key,badedges,badorientation,degenerate,components,rel)
    assert abs(min(v[2] for v in vertices))<1e-5
    result['stl'][key]={'sha256':sha(data),'triangles':n,'edge_connected_components':components,'edges_not_exactly_two_faces':badedges,'inconsistent_winding_edges':badorientation,'degenerate_triangles':degenerate,'signed_volume_mm3':signed_volume,'volume_difference_fraction':rel,'bbox_mm':bb,'minimum_z_mm':min(v[2] for v in vertices),'copies':info['copies']}
with zipfile.ZipFile(ROOT/'tiskovy-balicek.zip') as z:
    expected={f'{key}__{i+1:02d}.stl':sha((ROOT/info['stl']).read_bytes()) for key,info in report['parts'].items() for i in range(info['copies'])}
    assert set(n for n in z.namelist() if n.endswith('.stl'))==set(expected)
    assert all(sha(z.read(n))==h for n,h in expected.items())
    result['zip_verified_stl_count']=len(expected)
# Analytická kontrola skutečného překrytí evolventních profilů při zvětšené vzdálenosti.
result['analytical_gear_engagement']=[]
for z1,z2,a in ((18,54,32.6),(18,72,40.7)):
    m=0.9;alpha=math.radians(20);r1=m*z1/2;r2=m*z2/2;ra1=r1+m;ra2=r2+m;rb1=r1*math.cos(alpha);rb2=r2*math.cos(alpha)
    aw=math.acos((rb1+rb2)/a)
    contact=(math.sqrt(ra1*ra1-rb1*rb1)+math.sqrt(ra2*ra2-rb2*rb2)-a*math.sin(aw))/(math.pi*m*math.cos(alpha))
    assert contact>1 and ra1+ra2>a
    result['analytical_gear_engagement'].append({'teeth':[z1,z2],'operating_pressure_angle_deg':math.degrees(aw),'ideal_transverse_contact_ratio':contact,'tip_circle_overlap_mm':ra1+ra2-a,'limit':'Ideální evolventa před tiskovými odchylkami a deformací, nikoli měření funkce.'})
result['original_cad_unchanged']=all(Path(f).exists() and sha(Path(f).read_bytes())==h for f,h in report['original_cad_hashes'].items());assert result['original_cad_unchanged']
# Lokální markdown odkazy; internetové cíle nejsou součást této kontroly.
missing=[]
for label,target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',(ROOT/'README.md').read_text()):
    path=target.split('#')[0]
    if path and path!='overeni-exportu.json' and not re.match(r'[a-z]+:',path) and not (ROOT/path).exists():missing.append(path)
assert not missing,missing
result['markdown_links_pass']=True;result['all_passed']=True
(ROOT/'overeni-exportu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'all_passed':True,'manifold_stl':len(result['stl']),'print_count':result['zip_verified_stl_count'],'original_cad_unchanged':True,'generator_sha256':result['generator_sha256']}))
