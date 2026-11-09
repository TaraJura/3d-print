#!/usr/bin/env python3
"""Reprodukovatelna podlozka testu TPU; zapisuje pouze do teto slozky.
Cte pet ../stl/*.stl; prepise vlastni 3MF, profily, PNG a kontrolni JSON.
Jen mistni CLI Anycubic Slicer Next; zadne spojeni s tiskarnou.
"""
from collections import Counter
import argparse, hashlib, json, math, os, re, struct, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
CACHE=HERE/'.cache'
BED,EDGE=260.,8.
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PNS='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
XMLNS={'m':NS}
IDENTITY=[1,0,0,0,1,0,0,0,1]
SYSTEM=Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
MACHINE=SYSTEM/'machine/Anycubic Kobra X 0.4 nozzle.json'
PROCESS=SYSTEM/'process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json'
FILAMENT=SYSTEM/'filament/Anycubic TPU 95A @Anycubic Kobra X 0.4 nozzle.json'
CLI='/usr/bin/AnycubicSlicerNext'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GEOMETRY=HERE/'podlozka-01-geometrie.3mf'
DELIVERED=HERE/'podlozka-01-kobra-x-alzament-tpu95a-projekt.3mf'
PARTS=[
 ('pasek-08','01 Pasek 0.8 mm',[69,96],[70,14,.8]),
 ('pasek-16','02 Pasek 1.6 mm',[69,122],[70,14,1.6]),
 ('pasek-32','03 Pasek 3.2 mm',[69,148],[70,14,3.2]),
 ('krouzek-08','04 Krouzek stena 0.8 mm',[159,96],[32,32,12]),
 ('krouzek-16','05 Krouzek stena 1.6 mm',[159,142],[32,32,12]),
]
ET.register_namespace('',NS)
def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def read_mesh(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0] if len(raw) >= 84 else 0
    if len(raw) == 84 + count * 50:
        points = []
        for i in range(count):
            values = struct.unpack_from('<12fH', raw, 84 + 50*i)
            points.extend(tuple(values[j:j+3]) for j in (3, 6, 9))
    else:
        points = [tuple(map(float, p)) for p in re.findall(
            rb'\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)', raw)]
    require(len(points) >= 12 and len(points) % 3 == 0, f'Neplatná STL: {path}')
    vertices, lookup, faces = [], {}, []
    for i in range(0, len(points), 3):
        face = []
        for point in points[i:i+3]:
            require(all(math.isfinite(v) for v in point), 'Nekonečná souřadnice')
            key = tuple(round(v, 6) for v in point)
            if key not in lookup:
                lookup[key] = len(vertices)
                vertices.append(point)
            face.append(lookup[key])
        require(len(set(face)) == 3, f'Degenerovaný trojúhelník: {path}')
        faces.append(tuple(face))
    edges = Counter()
    parent = list(range(len(faces)))
    first = {}
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, face in enumerate(faces):
        a, b, c = (vertices[n] for n in face)
        cross = ((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),
                 (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),
                 (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
        require(sum(v*v for v in cross) > 1e-12, f'Nulová plocha: {path}')
        for j in range(3):
            edge = tuple(sorted((face[j], face[(j+1)%3])))
            edges[edge] += 1
            if edge in first:
                parent[root(i)] = root(first[edge])
            else:
                first[edge] = i
    require(all(n == 2 for n in edges.values()), f'Neuzavřená STL: {path}')
    require(len({root(i) for i in range(len(faces))}) == 1, f'Více komponent STL: {path}')
    lo = [min(p[i] for p in vertices) for i in range(3)]
    hi = [max(p[i] for p in vertices) for i in range(3)]
    size = [hi[i]-lo[i] for i in range(3)]
    require(all(v > 0 for v in size), f'Nulový rozměr: {path}')
    require(size[0] <= BED-2*EDGE and size[1] <= BED-2*EDGE and size[2] < BED,
            f'Díl se nevejde s okraji na Kobra X: {path}: {size}')
    return {'vertices': vertices, 'faces': faces, 'lo': lo, 'hi': hi, 'size': size}


def geometry():
    root=ET.Element(f'{{{NS}}}model',unit='millimeter')
    ET.SubElement(root,'metadata',name='Title').text='TPU test pruznosti – podlozka 01, pouze geometrie'
    ET.SubElement(root,'metadata',name='Description').text='5 samostatnych vzorku 1:1. Bez tiskovych, materialovych presetu a G-code.'
    resources,build=ET.SubElement(root,'resources'),ET.SubElement(root,'build')
    records=[]
    for number,(ident,name,xy,expected) in enumerate(PARTS,1):
        file=HERE.parent/'stl'/f'{ident}.stl';m=read_mesh(file)
        require(all(abs(a-b)<.01 for a,b in zip(m['size'],expected)),f'Unexpected size {ident}: {m["size"]}')
        obj=ET.SubElement(resources,'object',id=str(number),type='model',name=name)
        mesh=ET.SubElement(obj,'mesh');vertices=ET.SubElement(mesh,'vertices');faces=ET.SubElement(mesh,'triangles')
        for p in m['vertices']:ET.SubElement(vertices,'vertex',**{a:format(v,'.12g') for a,v in zip('xyz',p)})
        for f in m['faces']:ET.SubElement(faces,'triangle',**{f'v{i+1}':str(v) for i,v in enumerate(f)})
        t=[xy[0]-m['lo'][0],xy[1]-m['lo'][1],-m['lo'][2]]
        ET.SubElement(build,'item',objectid=str(number),transform=' '.join(map(str,IDENTITY+t)))
        records.append({'id':ident,'name':name,'number':number,'source_stl':f'../stl/{ident}.stl','source_sha256':sha(file),
            'translation_mm':t,'min_mm':[m['lo'][i]+t[i] for i in range(3)],'max_mm':[m['hi'][i]+t[i] for i in range(3)],
            'size_mm':m['size'],'vertices':len(m['vertices']),'triangles':len(m['faces']),'watertight':True,'connected_components':1})
    types=ET.Element('Types',xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
    ET.SubElement(types,'Default',Extension='rels',ContentType='application/vnd.openxmlformats-package.relationships+xml')
    ET.SubElement(types,'Default',Extension='model',ContentType='application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
    rels=ET.Element('Relationships',xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
    ET.SubElement(rels,'Relationship',Target='/3D/3dmodel.model',Id='rel0',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    with ZipFile(GEOMETRY,'w',ZIP_DEFLATED) as z:
        for name,node in [('[Content_Types].xml',types),('_rels/.rels',rels),('3D/3dmodel.model',root)]:
            z.writestr(name,ET.tostring(node,encoding='utf-8',xml_declaration=True))
    gap=min(math.hypot(*[max(a['min_mm'][i]-b['max_mm'][i],b['min_mm'][i]-a['max_mm'][i],0) for i in (0,1)]) for n,a in enumerate(records) for b in records[n+1:])
    margin=min(v for p in records for v in p['min_mm'][:2]+[BED-p['max_mm'][i] for i in (0,1)])
    require(gap>=12 and margin>=EDGE,'Insufficient gap or margin')
    canvas=Image.new('RGB',(1200,900),'#f5f5f0');d=ImageDraw.Draw(canvas)
    title=ImageFont.truetype(FONT,30);font=ImageFont.truetype(FONT,22)
    d.text((48,24),'01 / TPU 95A · pět samostatných vzorků',fill='#24343b',font=title)
    origin=(48,100);scale=2.7
    xy=lambda x,y:(origin[0]+x*scale,origin[1]+(260-y)*scale)
    d.rectangle((xy(0,260),xy(260,0)),fill='#dfe6e4',outline='#648079',width=3)
    for p in records:
        m=read_mesh(HERE/p['source_stl']);t=p['translation_mm']
        for f in sorted(m['faces'],key=lambda f:sum(m['vertices'][i][2] for i in f)):
            pts=[m['vertices'][i] for i in f]
            d.polygon([xy(v[0]+t[0],v[1]+t[1]) for v in pts],fill='#63767b')
        cx=(p['min_mm'][0]+p['max_mm'][0])/2;cy=(p['min_mm'][1]+p['max_mm'][1])/2
        px,py=xy(cx,cy);d.ellipse((px-16,py-16,px+16,py+16),fill='#f5f5f0');d.text((px-7,py-14),str(p['number']),font=font,fill='#24343b')
    legend=['1  Pásek 70 × 14 × 0,8 mm','2  Pásek 70 × 14 × 1,6 mm','3  Pásek 70 × 14 × 3,2 mm','4  Kroužek Ø32 / stěna 0,8','5  Kroužek Ø32 / stěna 1,6','Kroužky: výška 12 mm','','Kobra X · tryska 0,4 mm','Bez podpor · bez brimu','1× otevřít jako projekt']
    for i,label in enumerate(legend):d.text((790,160+48*i),label,fill='#24343b',font=font)
    d.text((48,831),'Pohled shora ze skutečné STL geometrie · podložka 260 × 260 mm',fill='#506966',font=font)
    canvas.save(HERE/'podlozka-01.png')
    result={'physical_pieces':5,'geometry_file':GEOMETRY.name,'geometry_sha256':sha(GEOMETRY),'parts':records,
        'minimum_bbox_gap_mm':gap,'minimum_geometry_bed_margin_mm':margin,'supports_required':False,'printer_operation':False}
    write_json(HERE/'kontrola-rozlozeni.json',result)
    return result


def profiles():
    process=json.loads(PROCESS.read_text());name='EXPERIMENT TPU test 0.20 mm @Kobra X'
    process.update({'from':'user','name':name,'print_settings_id':name,'setting_id':name,
        'curr_bed_type':'Textured PEI Plate','layer_height':'0.2','initial_layer_print_height':'0.2',
        'wall_loops':'2','wall_generator':'arachne','sparse_infill_density':'100%','sparse_infill_pattern':'rectilinear',
        'top_shell_layers':'4','bottom_shell_layers':'4','top_shell_thickness':'0.8','bottom_shell_thickness':'0.8',
        'line_width':'0.4','outer_wall_line_width':'0.4','inner_wall_line_width':'0.4','initial_layer_line_width':'0.4',
        'internal_solid_infill_line_width':'0.4','top_surface_line_width':'0.4','sparse_infill_line_width':'0.4',
        'elefant_foot_compensation':'0','initial_layer_speed':'15','initial_layer_infill_speed':'15',
        'outer_wall_speed':'25','inner_wall_speed':'25','small_perimeter_speed':'20','sparse_infill_speed':'25',
        'internal_solid_infill_speed':'25','top_surface_speed':'25','gap_infill_speed':'20','bridge_speed':'20',
        'internal_bridge_speed':'20','overhang_1_4_speed':'25','overhang_2_4_speed':'20','overhang_3_4_speed':'15',
        'overhang_4_4_speed':'10','overhang_totally_speed':'10','support_speed':'25','support_interface_speed':'20',
        'travel_speed':'120','default_acceleration':'500','outer_wall_acceleration':'500','inner_wall_acceleration':'500',
        'sparse_infill_acceleration':'500','internal_solid_infill_acceleration':'500','top_surface_acceleration':'500',
        'initial_layer_acceleration':'300','travel_acceleration':'1000','bridge_acceleration':'500',
        'brim_type':'no_brim','brim_width':'0','skirt_loops':'0','raft_layers':'0','enable_support':'0',
        'support_on_build_plate_only':'0','enable_prime_tower':'0','arc_fitting':'0','print_sequence':'by layer',
        'filename_format':'TPU-test-Alzament95A-plate{plate_number}.gcode'})
    filament=json.loads(FILAMENT.read_text());name='EXPERIMENT Alzament TPU95A Gray 225C bed60C @Kobra X'
    filament.update({'from':'user','is_custom_defined':'1','name':name,'setting_id':name,'filament_settings_id':[name],
        'filament_id':'EXPERIMENT-Alzament-TPU95A-test','filament_vendor':['Alzament'],'filament_type':['TPU'],
        'filament_colour':['#949A9C'],'default_filament_colour':['#949A9C'],
        'filament_max_volumetric_speed':['2.0'],'filament_flow_ratio':['1'],'filament_density':['1.24'],
        'nozzle_temperature':['225'],'nozzle_temperature_initial_layer':['225'],
        'nozzle_temperature_BRASS':['225'],'nozzle_temperature_HS':['225'],
        'nozzle_temperature_initial_layer_BRASS':['225'],'nozzle_temperature_initial_layer_HS':['225'],
        'nozzle_temperature_range_low':['220'],'nozzle_temperature_range_high':['240'],
        'hot_plate_temp':['60'],'hot_plate_temp_initial_layer':['60'],'textured_plate_temp':['60'],'textured_plate_temp_initial_layer':['60'],
        'filament_notes':['Experimental uncalibrated Alzament TPU95A. User confirmed material on 2026-10-24. TDS https://dwn.alza.cz/manual/161249: nozzle220-240 bed60-80; Gray product190-230/30-50 conflicts with TDS. 225/60 is provisional choice based on TDS. Density1.24 inherited from Anycubic, unverified for Alzament. No physical print verified.']})
    paths=[]
    for filename,data in [('proces-kobra-x-tpu-navrh.json',process),('filament-alzament-tpu95a-navrh.json',filament)]:
        path=HERE/filename;write_json(path,data);paths.append(path)
    return paths


def run_cli(command,log):
    with log.open('w') as stream:
        r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'DISPLAY':''},timeout=1200)
    require(r.returncode==0,f'Slicer exit {r.returncode}, log {log}')


def inspect_project(path,layout,has_gcode):
    def transform(value):
        m=list(map(float,value.split())) if value else IDENTITY+[0,0,0]
        require(m[:9]==IDENTITY,'Changed orientation/scale');return m[9:]
    with ZipFile(path) as z:
        require(z.testzip() is None,'Corrupt3MF')
        root=ET.fromstring(z.read('3D/3dmodel.model'));items=root.findall('m:build/m:item',XMLNS)
        require(root.get('unit')=='millimeter' and len(items)==5,'Wrong units/count')
        cfg=json.loads(z.read('Metadata/project_settings.config'));config=ET.fromstring(z.read('Metadata/model_settings.config'))
        expected={'printer_model':'Anycubic Kobra X','nozzle_diameter':['0.4'],'layer_height':'0.2','wall_loops':'2',
            'sparse_infill_density':'100%','enable_support':'0','brim_type':'no_brim','wall_generator':'arachne',
            'nozzle_temperature':['225'],'nozzle_temperature_initial_layer':['225'],'textured_plate_temp':['60'],
            'filament_max_volumetric_speed':['2'],'enable_prime_tower':'0'}
        for k,v in expected.items():require(cfg.get(k)==v,f'Changed setting {k}={cfg.get(k)} vs {v}')
        repairs=[p.attrib for p in config.findall('.//mesh_stat')]
        require(all(all(int(v)==0 for v in p.values()) for p in repairs),'Mesh repairs')
        byname={p['name']:p for p in layout['parts']};checked=[]
        for item in items:
            obj=root.find(f'm:resources/m:object[@id="{item.get("objectid")}"]',XMLNS)
            oc=config.find(f'object[@id="{item.get("objectid")}"]')
            name=oc.find('metadata[@key="name"]').get('value');exp=byname[name]
            components=obj.findall('m:components/m:component',XMLNS);require(len(components)==1,'Multiple components')
            c=components[0];nested=ET.fromstring(z.read(c.get(f'{{{PNS}}}path').lstrip('/')))
            mesh=nested.find(f'm:resources/m:object[@id="{c.get("objectid")}"]/m:mesh',XMLNS)
            offset=[a+b for a,b in zip(transform(item.get('transform')),transform(c.get('transform')))]
            verts=[[float(v.get(a))+offset[i] for i,a in enumerate('xyz')] for v in mesh.findall('m:vertices/m:vertex',XMLNS)]
            faces=mesh.findall('m:triangles/m:triangle',XMLNS)
            require(len(verts)==exp['vertices'] and len(faces)==exp['triangles'],'Mesh count changed')
            source=read_mesh(HERE/exp['source_stl'])
            delta=max(abs(source['vertices'][i][a]+exp['translation_mm'][a]-verts[i][a]) for i in range(len(verts)) for a in range(3))
            require(delta<.001,'Changed geometry or placement')
            checked.append({'id':exp['id'],'max_vertex_delta_mm':delta,'preserved_geometry_and_placement':True})
        require(('Metadata/plate_1.gcode' in z.namelist())==has_gcode,'Wrong slicing state')
        report={'file':path.name,'sha256':sha(path),'physical_parts':5,'objects':checked,'mesh_repairs':repairs,'has_gcode':has_gcode,
            'settings':{k:cfg.get(k) for k in expected}}
        if has_gcode:
            data=z.read('Metadata/plate_1.gcode');report['gcode_sha256']=hashlib.sha256(data).hexdigest()
            info=ET.fromstring(z.read('Metadata/slice_info.config'))
            report['slice_metadata']={m.get('key'):m.get('value') for m in info.iter('metadata') if m.get('key') in ('prediction','weight','outside','support_used')}
            report['warnings']=[w.attrib for w in info.iter('warning')]
            require(report['slice_metadata']['outside']=='false','Outside bed')
            reviewed_warnings={'not_support_traditional_timelapse','bed_temperature_too_high_than_filament'}
            require(not [w for w in report['warnings'] if w.get('msg') not in reviewed_warnings],'Unexpected slicing warning')
            report['warning_review']='Bed60C is an explicit uncalibrated choice from Alzament TDS60-80C; product page30-50C conflicts. The inherited material glass-transition parameter is unchanged; warning is retained. Traditional timelapse is unsupported.'
            report['paths']=inspect_paths(data.decode(),layout)
        return report


def inspect_paths(gcode,layout):
    layer=-1;role='Custom';absolute=True;relative_e=True;feed=0.
    pos=dict(X=0.,Y=0.,Z=0.,E=0.);layers={};roles=Counter();owners=set();max_speed=0.;max_flow=0.;max_raw_flow=0.
    samples={p['id']:{} for p in layout['parts']};volumes=Counter();first_layer_parts=set()
    num=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):layer+=1
        elif line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        elif line.startswith('EXCLUDE_OBJECT_START NAME='):owners.add(line.split('NAME=',1)[1])
        command=line.split(';',1)[0].strip()
        if not command:continue
        kind=command.split()[0];values={k:float(v) for k,v in num.findall(command)}
        if kind=='G90':absolute=True
        elif kind=='G91':absolute=False
        elif kind=='M83':relative_e=True
        elif kind=='M82':relative_e=False
        elif kind=='G92':pos.update({k:v for k,v in values.items() if k in pos})
        elif kind in ('G0','G1'):
            old=pos.copy()
            for a in 'XYZ':
                if a in values:pos[a]=values[a] if absolute else pos[a]+values[a]
            extrusion=values.get('E',0) if relative_e else values.get('E',pos['E'])-pos['E']
            if 'E' in values:pos['E']=pos['E']+values['E'] if relative_e else values['E']
            if 'F' in values:feed=values['F']/60
            length=math.hypot(pos['X']-old['X'],pos['Y']-old['Y'])
            if extrusion<=0 or length<1e-8 or role=='Custom':continue
            require(layer>=0,'Extrusion before layer')
            mid=[(old[a]+pos[a])/2 for a in 'XY']
            matches=[p for p in layout['parts'] if all(p['min_mm'][i]-.05<=mid[i]<=p['max_mm'][i]+.05 for i in (0,1))]
            require(len(matches)==1,f'Extrusion outside objects {mid}')
            p=matches[0];ident=p['id'];roles[role]+=1
            require(not any(s in role.lower() for s in ('support','bridge','overhang','brim','skirt')),'Unwanted support/bridge/adhesion')
            if layer==0:first_layer_parts.add(ident)
            for point in ((old['X'],old['Y']),(pos['X'],pos['Y'])):require(all(0<v<260 for v in point),'Outside bed')
            rec=layers.setdefault(layer,{'z':pos['Z'],'segments':[]});rec['segments'].append((old['X'],old['Y'],pos['X'],pos['Y'],ident,role))
            samples[ident].setdefault(layer,set())
            steps=max(1,math.ceil(length/.15))
            for i in range(steps+1):
                t=i/steps;samples[ident][layer].add((round(4*(old['X']+(pos['X']-old['X'])*t)),round(4*(old['Y']+(pos['Y']-old['Y'])*t))))
            volume=extrusion*math.pi*(1.75/2)**2;volumes[ident]+=volume
            flow=volume*feed/length;max_raw_flow=max(max_raw_flow,flow)
            if length>=.1:max_flow=max(max_flow,flow)
            max_speed=max(max_speed,feed)
        elif kind in ('G2','G3') and values.get('E',0)>0:raise RuntimeError('Arc extrusion not audited')
    require(len(owners)==5 and len(first_layer_parts)==5,'Missing object or first-layer extrusion')
    require(len(layers)==60 and set(layers)==set(range(60)),'Missing layer')
    require(max_speed<=25.001 and max_flow<2.12,f'Speed or flow limit {max_speed}/{max_flow}')
    require('G9111 bedTemp=60 extruderTemp=225' in gcode,'Wrong start temperature')
    part_reports=[];unsupported=[]
    near=[(dx,dy) for dx in range(-2,3) for dy in range(-2,3) if dx*dx+dy*dy<=4]
    for p in layout['parts']:
        ident=p['id'];expected_layers=round(p['size_mm'][2]/.2);actual=samples[ident]
        require(set(actual)==set(range(expected_layers)),f'Missing part layers {ident}: {len(actual)}')
        for n,current in actual.items():
            if n==0:continue
            prev=actual[n-1]
            for x,y in current:
                if not any((x+dx,y+dy) in prev for dx,dy in near):unsupported.append((ident,n+1,x/4,y/4))
        info={'id':ident,'layer_count':expected_layers,'all_expected_layers_present':True,'extruded_volume_mm3':volumes[ident]}
        if ident.startswith('krouzek'):
            wall=.8 if ident.endswith('08') else 1.6;cx=p['min_mm'][0]+16;cy=p['min_mm'][1]+16
            counts=[];radii=[]
            for n,rec in layers.items():
                bands=[set(),set()];radial=[]
                for x,y,xx,yy,which,r in rec['segments']:
                    if which!=ident:continue
                    steps=max(1,math.ceil(math.hypot(xx-x,yy-y)/.2))
                    for i in range(steps+1):
                        t=i/steps;px=x+(xx-x)*t-cx;py=y+(yy-y)*t-cy;radius=math.hypot(px,py)
                        radial.append(radius);angle=int((math.atan2(py,px)%(2*math.pi))/(2*math.pi)*72)%72
                        bands[int(radius>16-wall/2)].add(angle)
                require(all(len(b)==72 for b in bands),f'Incomplete inner/outer ring wall {ident} layer{n+1}: {list(map(len,bands))}')
                require(min(radial)>16-wall-.05 and max(radial)<16.05,'Ring paths out of geometry')
                counts.append(list(map(len,bands)));radii.append([min(radial),max(radial)])
            info['ring_wall_check']={'layers_checked':60,'inner_and_outer_radial_bands_have_all_72_angular_bins_every_layer':True,
                'minimum_path_radius_mm':min(v[0] for v in radii),'maximum_path_radius_mm':max(v[1] for v in radii),
                'note':'Checks actual inner/outer deposition around all360degrees. This is not proof of physical bonding.'}
        part_reports.append(info)
    require(not unsupported,f'Paths lack preceding layer contact: {unsupported[:8]}')
    # Actual G-code strokes on key layers, including final layer of each thickness.
    chosen=[0,3,7,15,29,59];tile=500;canvas=Image.new('RGB',(1500,1120),'#f5f5f0');d=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(FONT,21);title=ImageFont.truetype(FONT,29)
    d.text((24,16),'TPU test / skutečné extruzní dráhy z předávaného 3MF',fill='#24343b',font=title)
    lo=[min(p['min_mm'][i] for p in layout['parts'])-3 for i in (0,1)];hi=[max(p['max_mm'][i] for p in layout['parts'])+3 for i in (0,1)]
    scale=450/max(hi[i]-lo[i] for i in (0,1))
    for k,n in enumerate(chosen):
        col,row=k%3,k//3;xy=lambda x,y:(24+col*tile+(x-lo[0])*scale,90+row*510+(hi[1]-y)*scale)
        for x,y,xx,yy,ident,role in layers[n]['segments']:d.line((xy(x,y),xy(xx,yy)),fill='#21555c' if 'wall' in role.lower() else '#ac6e43',width=1)
        d.text((24+col*tile,500+row*510),f'Vrstva {n+1} / Z {layers[n]["z"]:g} mm',fill='#24343b',font=font)
    d.text((24,1070),'Modrá: stěny · hnědá: plné plochy · bez podpor a brimu',fill='#506966',font=font)
    canvas.save(HERE/'podlozka-01-vrstvy.png')
    # Ring close-up records geometry-defining wall toolpaths at three heights.
    canvas=Image.new('RGB',(1440,1040),'#f5f5f0');d=ImageDraw.Draw(canvas)
    d.text((24,15),'Kroužky / zachované tenké stěny v řezu',fill='#24343b',font=title)
    for row,p in enumerate(layout['parts'][3:]):
        for col,n in enumerate((0,29,59)):
            xy=lambda x,y:(30+480*col+(x-p['min_mm'][0])*12,80+470*row+(p['max_mm'][1]-y)*12)
            for x,y,xx,yy,ident,role in layers[n]['segments']:
                if ident==p['id']:d.line((xy(x,y),xy(xx,yy)),fill='#21555c',width=2)
            d.text((24+480*col,490+470*row),f'{p["name"]} / Z {layers[n]["z"]:g}',fill='#24343b',font=font)
    canvas.save(HERE/'krouzky-detail-drah.png')
    mass=re.search(r'^; total filament used \[g\] = ([0-9.]+)$',gcode,re.M)
    time=re.search(r'^; estimated printing time \(normal mode\) = (.+)$',gcode,re.M)
    return {'layer_count':60,'all_5_objects_on_first_layer':True,'part_layers':part_reports,'extrusion_roles':dict(roles),
        'interlayer_contact':{'method':'Path samples every0.15mm rounded to0.25mm grid; previous-layer radius0.5mm','unanchored_sample_count':0},
        'max_commanded_extrusion_speed_mm_s':max_speed,'max_volumetric_flow_mm3_s_segments_ge_0_1mm':max_flow,
        'max_raw_segment_flow_mm3_s':max_raw_flow,'flow_note':'Very short segments are affected by XYZ/E rounding; flow limit check uses length>=0.1mm.',
        'estimated_filament_g':float(mass.group(1)) if mass else None,'estimated_print_time':time.group(1) if time else None,
        'physical_print_verified':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--geometry-only',action='store_true');args=parser.parse_args()
    layout=geometry()
    if args.geometry_only:return
    process,filament=profiles();CACHE.mkdir(exist_ok=True)
    configured=CACHE/'configured.3mf';slice_dir=CACHE/'slice';slice_dir.mkdir(exist_ok=True)
    run_cli([CLI,'--datadir',str(CACHE/'export-profile'),'--load-settings',str(MACHINE)+';'+str(process),
        '--load-filaments',str(filament),'--arrange','0','--orient','0','--export-3mf',configured.name,'--outputdir',str(CACHE),str(GEOMETRY)],CACHE/'export.log')
    c=inspect_project(configured,layout,False)
    run_cli([CLI,'--datadir',str(CACHE/'slice-profile'),'--arrange','0','--orient','0','--slice','0',
        '--export-3mf',DELIVERED.name,'--outputdir',str(slice_dir),str(configured)],CACHE/'slice.log')
    DELIVERED.write_bytes((slice_dir/DELIVERED.name).read_bytes())
    final=inspect_project(DELIVERED,layout,True)
    report={'status':'Locally sliced and toolpaths checked; physical print unverified','date':'2026-10-24',
        'geometry':layout,'machine_profile_sha256':sha(MACHINE),'process_profile_sha256':sha(process),'filament_profile_sha256':sha(filament),
        'configured_project':c,'delivered_project':final,'printer_contact':False}
    write_json(HERE/'kontrola-rezani.json',report)
    print(json.dumps({'result':'TPU_PLATE_VALIDATED','time':final['paths']['estimated_print_time'],'mass_g':final['paths']['estimated_filament_g']},ensure_ascii=False))


if __name__=='__main__':main()
