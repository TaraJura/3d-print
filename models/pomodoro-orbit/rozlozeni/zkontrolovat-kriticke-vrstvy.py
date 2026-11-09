#!/usr/bin/env python3
"""Render critical detail from the existing verified 01 G-code. No reslicing/I/O."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,re
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
REPORT=HERE/'kontrola-podlozky-01.json'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def main():
    report=json.loads(REPORT.read_text());project=HERE/report['project']
    assert hashlib.sha256(project.read_bytes()).hexdigest()==report['delivered']['sha256']
    with ZipFile(project) as z:data=z.read('Metadata/plate_1.gcode')
    assert hashlib.sha256(data).hexdigest()==report['delivered']['gcode_sha256']
    gcode=data.decode();pos=dict(X=0.,Y=0.,Z=0.,E=0.);absolute=True;relative_e=True
    role='Custom';owner=None;layers={};index=-1
    number=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):index+=1
        elif line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        elif line.startswith('EXCLUDE_OBJECT_START NAME='):owner=line.split('NAME=',1)[1]
        elif line.startswith('EXCLUDE_OBJECT_END'):owner=None
        command=line.split(';',1)[0].strip()
        if not command:continue
        kind=command.split()[0];values={a:float(v) for a,v in number.findall(command)}
        if kind=='G90':absolute=True
        elif kind=='G91':absolute=False
        elif kind=='M83':relative_e=True
        elif kind=='M82':relative_e=False
        elif kind=='G92':pos.update({k:v for k,v in values.items() if k in pos})
        elif kind in ('G0','G1'):
            old=pos.copy()
            for axis in 'XYZ':
                if axis in values:pos[axis]=values[axis] if absolute else pos[axis]+values[axis]
            extrusion=values.get('E',0) if relative_e else values.get('E',pos['E'])-pos['E']
            if 'E' in values:pos['E']=pos['E']+values['E'] if relative_e else values['E']
            length=math.hypot(pos['X']-old['X'],pos['Y']-old['Y'])
            if extrusion<=0 or length<1e-8 or role=='Custom' or index<0:continue
            assert owner is not None
            layer=layers.setdefault(index,{'z':pos['Z'],'segments':[]})
            layer['segments'].append((old['X'],old['Y'],pos['X'],pos['Y'],role,owner))
        elif kind in ('G2','G3') and values.get('E',0)>0:raise RuntimeError('Unexpected arc extrusion')
    report_parts={p['id']:p for p in report['plate']['parts']}
    checks=[]
    for part_id,targets in [('Screw',[12.4,12.6,15,20,21.64,21.8,21.96]),('Crown',[1.64,1.8,1.96,2.12])]:
        part=report_parts[part_id];lo=[part['placed_min_mm'][i]-1 for i in (0,1)];hi=[part['placed_max_mm'][i]+1 for i in (0,1)]
        def for_part(l):
            return [s for s in l['segments'] if all(lo[i]<=v<=hi[i] for point in (s[:2],s[2:4]) for i,v in enumerate(point))]
        choices=sorted({min(layers,key=lambda k:abs(layers[k]['z']-v)) for v in targets})
        cols=3 if part_id=='Screw' else 2;rows=math.ceil(len(choices)/cols);tile=490
        canvas=Image.new('RGB',(cols*tile,rows*(tile+38)+100),'#fafbfc');draw=ImageDraw.Draw(canvas)
        title=ImageFont.truetype(FONT,26);font=ImageFont.truetype(FONT,18)
        draw.text((20,12),part_id+' – kritické skutečné vrstvy',fill='#18343d',font=title)
        scale=(tile-45)/max(hi[i]-lo[i] for i in (0,1))
        records=[]
        def axis_distance(segment):
            x,y,x2,y2=segment[:4];cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2
            dx,dy=x2-x,y2-y;t=max(0,min(1,((cx-x)*dx+(cy-y)*dy)/(dx*dx+dy*dy)))
            return math.hypot(cx-x-t*dx,cy-y-t*dy)
        for n,k in enumerate(choices):
            col,row=n%cols,n//cols
            xy=lambda x,y:(20+col*tile+scale*(x-lo[0]),56+row*(tile+38)+scale*(hi[1]-y))
            old=for_part(layers[k-1]);current=for_part(layers[k])
            for x,y,x2,y2,role,owner in old:draw.line((xy(x,y),xy(x2,y2)),fill='#c4cdd0',width=3)
            for x,y,x2,y2,role,owner in current:
                colour='#c77239' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#173b46'
                draw.line((xy(x,y),xy(x2,y2)),fill=colour,width=1)
            draw.text((20+col*tile,56+row*(tile+38)+tile-10),f"Z {layers[k]['z']:g} mm / předchozí {layers[k-1]['z']:g} mm",fill='#18343d',font=font)
            records.append({'layer_one_based':k+1,'z_mm':layers[k]['z'],'previous_z_mm':layers[k-1]['z'],
                'current_roles_segments':dict(Counter(s[4] for s in current)),
                'previous_segments':len(old),'current_segments':len(current),
                'minimum_current_path_distance_from_axis_mm':min(axis_distance(segment) for segment in current)})
        draw.text((20,canvas.height-30),'Šedá: předchozí vrstva · tmavá: současná · oranžová: most/převis',fill='#536871',font=font)
        path=HERE/f'kriticke-vrstvy-{part_id.lower()}.png';canvas.save(path)
        checks.append({'part':part_id,'image':path.name,'layers':records})
    result={'project':project.name,'project_sha256':report['delivered']['sha256'],
        'gcode_sha256':report['delivered']['gcode_sha256'],'source':'Existing final sliced project; no reslice',
        'checks':checks,'new_slice_performed':False,'printer_io_performed':False,'physical_print_verified':False}
    (HERE/'kontrola-kritickych-vrstev.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
