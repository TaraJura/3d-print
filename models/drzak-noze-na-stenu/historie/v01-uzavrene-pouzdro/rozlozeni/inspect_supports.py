#!/usr/bin/env python3
"""Render only actual G-code at critical support interfaces; no printer I/O."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib,json,re,math
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
N=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
def parse(text):
    out={};z=0.;role='Custom';pos=dict(X=0.,Y=0.,Z=0.,E=0.);rel=True;absolute=True;layer=-1
    for raw in text.splitlines():
        if raw.startswith(';LAYER_CHANGE'):layer+=1
        if raw.startswith(';TYPE:'):role=raw.split(':',1)[1].strip()
        cmd=raw.split(';',1)[0].strip()
        if not cmd:continue
        code=cmd.split()[0];v={a:float(b) for a,b in N.findall(cmd)}
        if code=='M83':rel=True
        elif code=='M82':rel=False
        elif code=='G90':absolute=True
        elif code=='G91':absolute=False
        elif code=='G92':pos.update({a:b for a,b in v.items() if a in pos})
        elif code in ('G0','G1'):
            old=pos.copy()
            for a in 'XYZ':
                if a in v:pos[a]=v[a] if absolute else pos[a]+v[a]
            e=v.get('E',0) if rel else v.get('E',pos['E'])-pos['E']
            if 'E' in v:pos['E']=pos['E']+v['E'] if rel else v['E']
            if e>0 and math.hypot(pos['X']-old['X'],pos['Y']-old['Y'])>1e-8 and role!='Custom' and layer>=0:
                out.setdefault(round(pos['Z'],4),[]).append((old['X'],old['Y'],pos['X'],pos['Y'],role))
    return out

def render(n,targets,bounds,title,outname):
    path=HERE/f'podlozka-{n:02d}-kobra-x-pla-projekt.3mf'
    with ZipFile(path) as archive:gcode=archive.read('Metadata/plate_1.gcode')
    layers=parse(gcode.decode());low,high=bounds
    scale=4.;w=int((high[0]-low[0])*scale)+40;h=int((high[1]-low[1])*scale)+65
    c=Image.new('RGB',(w*2,h*math.ceil(len(targets)/2)+72),'#fafbfc');d=ImageDraw.Draw(c)
    font=ImageFont.truetype(F,16);bold=ImageFont.truetype(F,20)
    d.text((18,15),title,font=bold,fill='#18343d')
    report=[]
    for i,target in enumerate(targets):
        z=min(layers,key=lambda val:abs(val-target));col=i%2;row=i//2
        def pt(x,y):return (col*w+20+(x-low[0])*scale,60+row*h+(high[1]-y)*scale)
        roles=Counter();support=[];model=[]
        for x,y,x2,y2,role in layers[z]:
            if not all(low[a]<=val<=high[a] for p in ((x,y),(x2,y2)) for a,val in enumerate(p)):continue
            color='#36a076' if 'support' in role.lower() else '#e29a42' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#273d47'
            if role=='Brim':color='#93bdb2'
            d.line((pt(x,y),pt(x2,y2)),fill=color,width=2);roles[role]+=1
            (support if 'support' in role.lower() else model).append((x,y,x2,y2))
        d.text((col*w+18,60+row*h+h-45),f'Z {z:g} mm · podpory {len(support)} úseků',font=font,fill='#18343d')
        report.append({'z_mm':z,'region_xy_mm':bounds,'roles_segments':dict(roles)})
    c.save(HERE/outname)
    return {'project':path.name,'gcode_sha256':hashlib.sha256(gcode).hexdigest(),'preview':outname,'layers':report}

manifest=json.loads((HERE/'manifest.json').read_text())
cad=json.loads((HERE.parent/'kontrola-modelu.json').read_text())
parameters=cad['parameters_mm']
by_id={part['id']:(plate['number'],part) for plate in manifest['plates'] for part in plate['parts']}
def part_box(id):
    n,p=by_id[id]
    return n,[[p['placed_min_mm'][0]-1,p['placed_min_mm'][1]-1],[p['placed_max_mm'][0]+1,p['placed_max_mm'][1]+1]]
n,left=by_id['vanicka-leva'];floor=parameters['FloorLevel'];back=parameters['BackThickness'];lip=back+parameters['HandleThickness']+parameters['DepthClearance']
left_bounds=[[left['placed_min_mm'][0]-1,left['translation_mm'][1]+floor-6],[left['placed_max_mm'][0]+1,left['translation_mm'][1]+floor+parameters['RetainerHeight']+3]]
r=[render(n,[back,back+.2,back+.4,lip-.4,lip-.2,lip,lip+.2,lip+.4],left_bounds,'Vanička levá · podpora pod záchytným lemem','podpory-01-levy-lem.png')]
n,bounds=part_box('vanicka-prava')
r.append(render(n,[0.2,1.0,1.2,1.6,1.8,back],bounds,'Vanička pravá · stupňový spoj','podpory-01-pravy-spoj.png'))
n,bounds=part_box('kryt-pravy');seam=parameters['WallThickness']-1.4
r.append(render(n,[0.2,seam-.8,seam-.4,seam-.2,seam,seam+.2],bounds,'Pravý kryt · podpora pod přesahem','podpory-02-pravy-kryt.png'))
summary=[]
manifest=json.loads((HERE/'manifest.json').read_text())
for plate in manifest['plates']:
    project=HERE/f'podlozka-{plate["number"]:02d}-kobra-x-pla-projekt.3mf'
    with ZipFile(project) as archive:all_layers=parse(archive.read('Metadata/plate_1.gcode').decode())
    for part in plate['parts']:
        lo=[v-4 for v in part['placed_min_mm'][:2]];hi=[v+4 for v in part['placed_max_mm'][:2]]
        support=[(z,seg) for z,segs in all_layers.items() for seg in segs if 'support' in seg[4].lower() and all(lo[a]<=val<=hi[a] for point in ((seg[0],seg[1]),(seg[2],seg[3])) for a,val in enumerate(point))]
        assert bool(support)==part['supports'],(part['name'],len(support),part['supports'])
        summary.append({'name':part['name'],'support_required_by_cad_manifest':part['supports'],'support_segments_near_part':len(support),'support_z_range_mm':[min(z for z,s in support),max(z for z,s in support)] if support else None})
(HERE/'kontrola-podpor-detail.json').write_text(json.dumps({'support_region_summary':summary,'evidence':'Actual extruded G-code line segments at critical support interfaces; green=support, orange=bridge/overhang, dark=model','parts':r,'physical_removal_unverified':True},ensure_ascii=False,indent=2)+'\n')
print('SUPPORT_DETAIL_OK')
