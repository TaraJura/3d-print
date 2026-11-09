#!/usr/bin/env python3
"""Inspect actual G-code at both horizontal mounting-hole crowns; no printer I/O."""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib,json,re,math
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
N=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
def parse(text):
    out={};role='Custom';pos=dict(X=0.,Y=0.,Z=0.,E=0.);rel=True;absolute=True;layer=-1
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

cad=json.loads((HERE.parent/'kontrola-modelu.json').read_text());p=cad['parameters_mm']
manifest=json.loads((HERE/'manifest.json').read_text());plate=manifest['plates'][0];part=plate['parts'][0]
project=HERE/'podlozka-01-kobra-x-pla-projekt.3mf'
with ZipFile(project) as z:gcode=z.read('Metadata/plate_1.gcode')
layers=parse(gcode.decode());t=part['translation_mm']
centres=[t[0]+p['MountInset'],t[0]+p['Length']-p['MountInset']]
ymax=part['placed_max_mm'][1];miny=ymax-p['TabDepth'];cy=p['MountY']
targets=[cy,cy+1.8,cy+2,cy+2.2,cy+2.4,cy+2.6,cy+2.8,cy+3]
chosen=sorted({min(layers,key=lambda z:abs(z-target)) for target in targets})
font=ImageFont.truetype(F,18);title=ImageFont.truetype(F,23);records=[]
for number,cx in enumerate(centres,1):
    lo=[cx-8,miny-1.5];hi=[cx+8,ymax+1.5];cols=4;tilew=370;tileh=235;scale=21
    im=Image.new('RGB',(cols*tilew,70+math.ceil(len(chosen)/cols)*tileh),'#fafbfc');draw=ImageDraw.Draw(im)
    draw.text((18,12),f'Montážní otvor {number:02d} · skutečné dráhy u vrcholu Ø{p["MountHole"]:g} mm',font=title,fill='#18343d')
    rows=[]
    for index,z in enumerate(chosen):
        col=index%cols;row=index//cols
        def xy(x,y):return (18+col*tilew+(x-lo[0])*scale,60+row*tileh+(hi[1]-y)*scale)
        def within(s):return all(lo[a]<=val<=hi[a] for point in ((s[0],s[1]),(s[2],s[3])) for a,val in enumerate(point))
        before=max((a for a in layers if a<z),default=None)
        if before is not None:
            for s in layers[before]:
                if within(s):draw.line((xy(s[0],s[1]),xy(s[2],s[3])),fill='#cbd5d9',width=10)
        current=[s for s in layers[z] if within(s)]
        for x,y,x2,y2,role in current:
            colr='#e29236' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#273d47'
            draw.line((xy(x,y),xy(x2,y2)),fill=colr,width=4)
        roles=Counter(s[4] for s in current)
        bridge=[s for s in current if s[4]=='Bridge']
        rows.append({'z_mm':z,'roles':dict(roles),'bridge_stroke_count':len(bridge),'maximum_bridge_stroke_mm':max((math.hypot(s[2]-s[0],s[3]-s[1]) for s in bridge),default=0)})
        draw.text((18+col*tilew,60+row*tileh+160),f'Z {z:g} mm · most {len(bridge)} tahů',font=font,fill='#18343d')
    out=f'detail-otvor-{number:02d}-mostky.png';im.save(HERE/out)
    records.append({'hole':number,'centre_print_x_mm':cx,'hole_axis_z_mm':cy,'preview':out,'layers':rows})
# Clip real strokes for a detailed look at the open transition and its foot.
def clip(segment,lo,hi):
    x,y,x2,y2,role=segment;dx=x2-x;dy=y2-y;low=0.;high=1.
    for pp,qq in [(-dx,x-lo[0]),(dx,hi[0]-x),(-dy,y-lo[1]),(dy,hi[1]-y)]:
        if abs(pp)<1e-14:
            if qq<0:return None
        else:
            tt=qq/pp
            if pp<0:low=max(low,tt)
            else:high=min(high,tt)
            if low>high:return None
    return x+low*dx,y+low*dy,x+high*dx,y+high*dy,role
heel=cad['heel_x_mm']+t[0];handle=cad['handle_x_mm']+t[0]
require_mirrored=handle<heel;assert require_mirrored,'V04: handle seat must be left of the blade seat'
lo=[handle-20,part['placed_min_mm'][1]-1];hi=[heel+15,part['placed_max_mm'][1]+1]
check_z=[.2,p['FootHeight'],p['FootHeight']+.2,8.8,13,17,20,23,25,27,30,35,38,40]
transition_z=sorted({min(layers,key=lambda z:abs(z-target)) for target in check_z})
cols=4;tilew=430;tileh=445;scale=min(390/(hi[0]-lo[0]),370/(hi[1]-lo[1]))
im=Image.new('RGB',(cols*tilew,60+math.ceil(len(transition_z)/cols)*tileh),'#fafbfc');d=ImageDraw.Draw(im)
d.text((18,12),'Otevřený 10mm přechod mezi sedly · skutečné dráhy',font=title,fill='#18343d')
transition=[]
for i,z in enumerate(transition_z):
    col=i%cols;row=i//cols
    def xy(x,y):return 18+col*tilew+(x-lo[0])*scale,60+row*tileh+(hi[1]-y)*scale
    before=max((a for a in layers if a<z),default=None)
    if before is not None:
        for seg in layers[before]:
            c=clip(seg,lo,hi)
            if c:d.line((xy(c[0],c[1]),xy(c[2],c[3])),fill='#cbd5d9',width=4)
    current=[c for seg in layers[z] if (c:=clip(seg,lo,hi))]
    for x,y,x2,y2,role in current:
        color='#e29236' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#273d47'
        if role=='Brim':color='#51a080'
        d.line((xy(x,y),xy(x2,y2)),fill=color,width=2)
    # Dotted X boundaries mark the open neck gap, not synthetic toolpaths.
    for xx in (heel,handle):
        u,v=xy(xx,hi[1]);u2,v2=xy(xx,lo[1]);
        for yy in range(int(v),int(v2),12):d.line((u,yy,u,min(yy+4,v2)),fill='#b7c4ca',width=1)
    d.text((18+col*tilew,60+row*tileh+385),f'Z {z:g} mm',font=font,fill='#18343d')
    transition.append({'z_mm':z,'clipped_roles':dict(Counter(c[4] for c in current))})
im.save(HERE/'detail-prechod-drahy.png')
gap_lo=[handle+.3,part['placed_min_mm'][1]-1];gap_hi=[heel-.3,part['placed_max_mm'][1]+1]
unexpected=[]
for z,segs in layers.items():
    if z<=p['FootHeight']+.01:continue
    material=[seg for seg in segs if seg[4]!='Brim' and clip(seg,gap_lo,gap_hi)]
    if material:unexpected.append({'z_mm':z,'segments':len(material)})
assert not unexpected,unexpected
transition_report={'preview':'detail-prechod-drahy.png','open_gap_x_print_mm':[handle,heel],'tested_interior_gap_x_print_mm':[gap_lo[0],gap_hi[0]],'foot_top_z_mm':p['FootHeight'],'all_layers_above_foot_have_zero_extruded_strokes_in_interior_gap':True,'selected_layers':transition}
# Every bridge/overhang stroke of the whole print, grouped by whether it belongs to a hole crown.
hole_lo=miny-.5;hole_hi=ymax+.5;special=[]
for z,segs in sorted(layers.items()):
    for x,y,x2,y2,role in segs:
        if 'bridge' in role.lower() or 'overhang' in role.lower():
            near=any(abs((x+x2)/2-cx)<=p['TabWidth']/2+.5 for cx in centres) and hole_lo<=(y+y2)/2<=hole_hi and z>=cy
            special.append((z,role,near,x,y,x2,y2))
outside=[s for s in special if not s[2]]
special_report={'strokes_total':len(special),'strokes_at_mount_tabs_above_hole_axis':len(special)-len(outside),'roles':dict(Counter(s[1] for s in special)),
 'z_range_at_tabs_mm':[min((s[0] for s in special if s[2]),default=None),max((s[0] for s in special if s[2]),default=None)],
 'outside_tabs':{'strokes':len(outside),'roles':dict(Counter(s[1] for s in outside)),'z_range_mm':[min((s[0] for s in outside),default=None),max((s[0] for s in outside),default=None)],
  'bbox_xy_mm':[[min((min(s[3],s[5]) for s in outside),default=None),min((min(s[4],s[6]) for s in outside),default=None)],[max((max(s[3],s[5]) for s in outside),default=None),max((max(s[4],s[6]) for s in outside),default=None)]],
  'longest_stroke_mm':max((math.hypot(s[5]-s[3],s[6]-s[4]) for s in outside),default=0)}}
# Real outer-wall paths against the mirrored paths of the delivered V03 project (read-only).
v03_project=HERE.parent.parent/'revize-03-tvarovany-dle-noze/rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf'
v03_sha_before=hashlib.sha256(v03_project.read_bytes()).hexdigest()
with ZipFile(v03_project) as z:v03_layers=parse(z.read('Metadata/plate_1.gcode').decode())
mirror_sum=2*t[0]+p['Length']
assert sorted(v03_layers)==sorted(layers),'Layer heights differ from V03'
def point_seg(px,py,a,b,c,d):
    dx,dy=c-a,d-b;q=dx*dx+dy*dy;u=max(0.,min(1.,((px-a)*dx+(py-b)*dy)/q)) if q>0 else 0.
    return math.hypot(px-a-u*dx,py-b-u*dy)
worst=0.;worst_z=None;extent_worst=0.
for z in sorted(layers):
    mine=[s for s in layers[z] if 'outer wall' in s[4].lower()]
    other=[(mirror_sum-s[0],s[1],mirror_sum-s[2],s[3]) for s in v03_layers[z] if 'outer wall' in s[4].lower()]
    if not mine or not other:
        assert bool(mine)==bool(other),('outer wall only in one revision',z)
        continue
    cells={}
    for seg in other:
        for cx_ in range(math.floor(min(seg[0],seg[2])/3),math.floor(max(seg[0],seg[2])/3)+1):
            for cy_ in range(math.floor(min(seg[1],seg[3])/3),math.floor(max(seg[1],seg[3])/3)+1):cells.setdefault((cx_,cy_),[]).append(seg)
    for s in mine:
        for px,py in ((s[0],s[1]),(s[2],s[3])):
            near=[g for i in (-1,0,1) for j in (-1,0,1) for g in cells.get((math.floor(px/3)+i,math.floor(py/3)+j),[])]
            d=min((point_seg(px,py,*g) for g in near),default=min(point_seg(px,py,*g) for g in other))
            if d>worst:worst,worst_z=d,z
    for fn,a,b in ((min,0,2),(max,0,2),(min,1,3),(max,1,3)):
        extent_worst=max(extent_worst,abs(fn(fn(s[a],s[b]) for s in mine)-fn(fn(g[a],g[b]) for g in other)))
assert hashlib.sha256(v03_project.read_bytes()).hexdigest()==v03_sha_before
path_mirror={'v03_project_sha256':v03_sha_before,'layers_compared':len(layers),'same_layer_heights':True,'mirror':f'X -> {mirror_sum:g} - X (print frame), Y unchanged','maximum_outer_wall_point_to_mirrored_v03_path_mm':worst,'at_z_mm':worst_z,'maximum_per_layer_outer_wall_extent_difference_mm':extent_worst,'note':'Outer walls only; seams, infill and gap fill are generated separately per slice and are not expected to be mirrored.'}
(HERE/'kontrola-mostku.json').write_text(json.dumps({'project':project.name,'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'bridge_overhang_strokes_all_layers':special_report,'actual_paths_vs_mirrored_v03':path_mirror,'gcode_sha256':hashlib.sha256(gcode).hexdigest(),'source_manifest_sha256':manifest['source_manifest_sha256'],'method':'Actual extruded strokes, grey = previous layer, dark = current material, orange = bridge/overhang. Reported bridge length is whole extrusion move, not unsupported gap.','holes':records,'transition':transition_report,'physical_bridge_quality_verified':False},ensure_ascii=False,indent=2)+'\n')
print('V04_BRIDGE_DETAILS_OK')
