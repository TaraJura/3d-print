#!/usr/bin/env python3
"""Pomodoro Orbit: rozmístění, profily PLA a lokální řezání.
Zapisuje pouze do této složky, logy do .cache/. Nepoužívá tiskárnové I/O.
Čte ../print-manifest.json. Přepíše pouze soubory v této složce.
"""
from collections import Counter
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import textwrap
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
CACHE = HERE / '.cache'
SOURCE_MANIFEST = MODEL / 'print-manifest.json'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PNS = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
XMLNS = {'m': NS}
BED, EDGE, GAP = 260.0, 8.0, 12.0
PROFILES = Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
MACHINE = PROFILES / 'machine/Anycubic Kobra X 0.4 nozzle.json'
PROCESS = PROFILES / 'process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json'
FILAMENT = PROFILES / 'filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json'
CLI = '/usr/bin/AnycubicSlicerNext'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
IDENTITY = [1, 0, 0, 0, 1, 0, 0, 0, 1]
ET.register_namespace('', NS)


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


def make_geometry(number, plate, meshes):
    stem = f'podlozka-{number:02d}'
    path = HERE / f'{stem}-geometrie.3mf'
    model = ET.Element(f'{{{NS}}}model', unit='millimeter')
    ET.SubElement(model, 'metadata', name='Title').text = f'Pomodoro Orbit – {stem}, pouze geometrie'
    ET.SubElement(model, 'metadata', name='Description').text = 'Pouze geometrie 1:1; bez procesu, filamentu a G-code. Alternativa téže podložky.'
    resources, build = ET.SubElement(model, 'resources'), ET.SubElement(model, 'build')
    records = []
    for index, item in enumerate(plate['items'], 1):
        mesh = meshes[item['id']]
        obj = ET.SubElement(resources, 'object', id=str(index), type='model', name=item['name'])
        node = ET.SubElement(obj, 'mesh')
        verts, faces = ET.SubElement(node, 'vertices'), ET.SubElement(node, 'triangles')
        for point in mesh['vertices']:
            ET.SubElement(verts, 'vertex', **{a: format(v, '.12g') for a,v in zip('xyz', point)})
        for face in mesh['faces']:
            ET.SubElement(faces, 'triangle', **{f'v{i+1}': str(v) for i,v in enumerate(face)})
        translation = [item['xy'][0]-mesh['lo'][0], item['xy'][1]-mesh['lo'][1], -mesh['lo'][2]]
        ET.SubElement(build, 'item', objectid=str(index), transform=' '.join(map(str, IDENTITY+translation)))
        lo = [mesh['lo'][i]+translation[i] for i in range(3)]
        hi = [mesh['hi'][i]+translation[i] for i in range(3)]
        records.append({'id': item['id'], 'name': item['name'], 'file': mesh['file'],
                        'source_sha256': mesh['source_sha256'], 'translation_mm': translation,
                        'placed_min_mm': lo, 'placed_max_mm': hi, 'size_mm': mesh['size'],
                        'triangle_count': len(mesh['faces']), 'supports': mesh['supports'],
                        'support_note': mesh['support_note'],
                        'critical_z_mm': mesh['critical_z_mm']})
    types = ET.Element('Types', xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
    ET.SubElement(types, 'Default', Extension='rels', ContentType='application/vnd.openxmlformats-package.relationships+xml')
    ET.SubElement(types, 'Default', Extension='model', ContentType='application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
    rels = ET.Element('Relationships', xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
    ET.SubElement(rels, 'Relationship', Target='/3D/3dmodel.model', Id='rel0', Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name,node in [('[Content_Types].xml', types), ('_rels/.rels', rels), ('3D/3dmodel.model', model)]:
            z.writestr(name, ET.tostring(node, encoding='utf-8', xml_declaration=True))
    margin = min(min(p['placed_min_mm'][:2]) for p in records)
    margin = min(margin, min(BED-max(p['placed_max_mm'][:2]) for p in records))
    require(margin >= EDGE-1e-4, 'Nedostatečný okraj podložky')
    min_gap = float('inf')
    for i,a in enumerate(records):
        for b in records[i+1:]:
            deltas = [max(a['placed_min_mm'][k]-b['placed_max_mm'][k],
                          b['placed_min_mm'][k]-a['placed_max_mm'][k], 0) for k in range(2)]
            distance = math.hypot(*deltas)
            require(distance >= GAP-1e-4, 'Příliš blízké díly')
            min_gap = min(min_gap, distance)
    preview_layout(number, records, meshes)
    return {'number': number, 'geometry': path.name, 'geometry_sha256': sha(path),
            'preview': f'{stem}.png', 'physical_parts': len(records), 'parts': records,
            'minimum_geometry_edge_margin_mm': margin,
            'minimum_bbox_gap_mm': min_gap if math.isfinite(min_gap) else None}


def preview_layout(number, records, meshes):
    canvas = Image.new('RGB', (1040,1120), '#fafbfc')
    draw = ImageDraw.Draw(canvas)
    title, font = ImageFont.truetype(FONT,28), ImageFont.truetype(FONT,19)
    draw.text((65,24), f'Podložka {number:02d} · Kobra X · 260 × 260 mm', fill='#18343d', font=title)
    xy = lambda x,y: (65+3.5*x,90+3.5*(BED-y))
    draw.rectangle((xy(0,BED),xy(BED,0)), fill='#e8edef', outline='#55717b', width=3)
    draw.line((xy(0,0),xy(BED,0)), fill='#b85042', width=5)
    for index,record in enumerate(records,1):
        mesh = meshes[record['id']]
        t = record['translation_mm']
        for face in sorted(mesh['faces'], key=lambda f: sum(mesh['vertices'][i][2] for i in f)):
            points = [mesh['vertices'][i] for i in face]
            tone = int(34+42*(sum(p[2] for p in points)/3-mesh['lo'][2])/mesh['size'][2])
            draw.polygon([xy(p[0]+t[0],p[1]+t[1]) for p in points], fill=(70+tone, 73+tone, 77+tone) if number == 1 else (189+tone//2, 165+tone//2, 102+tone//2))
        x,y = xy((record['placed_min_mm'][0]+record['placed_max_mm'][0])/2,
                 (record['placed_min_mm'][1]+record['placed_max_mm'][1])/2)
        if max(record['size_mm'][:2]) < 15:
            # Tiny upright pins must remain visible; labels sit beside their footprint.
            draw.line((x,y+12,x,y+26),fill='#55717b',width=1)
            y+=42
        draw.rounded_rectangle((x-18,y-16,x+18,y+16), radius=5, fill='white')
        draw.text((x-12,y-13), f'{index:02d}', fill='#18343d', font=font)
    summary = ', '.join(f'{n}× {k}' for k,n in Counter(p['id'] for p in records).items())
    # Keep labels on image concise; exact indexed names are in manifest.
    draw.text((65,1020), f'{len(records)} fyzických kusů · skutečná STL · 1:1', fill='#263f49', font=font)
    for row,text in enumerate(textwrap.wrap(summary,width=85)):
        draw.text((65,1052+24*row), text, fill='#536871', font=font)
    canvas.save(HERE/f'podlozka-{number:02d}.png')


def project_check(path, plate, meshes, has_gcode):
    def translation(value):
        matrix = list(map(float,value.split())) if value else IDENTITY+[0,0,0]
        require(matrix[:9] == IDENTITY, 'Slicer změnil orientaci/měřítko')
        return matrix[9:]
    with ZipFile(path) as z:
        require(z.testzip() is None, 'Poškozený ZIP')
        root = ET.fromstring(z.read('3D/3dmodel.model'))
        require(root.get('unit') == 'millimeter', 'Nesprávné jednotky')
        items = root.findall('m:build/m:item', XMLNS)
        require(len(items) == plate['physical_parts'], 'Změněný počet kusů')
        config = ET.fromstring(z.read('Metadata/model_settings.config'))
        cfg = json.loads(z.read('Metadata/project_settings.config'))
        require(cfg.get('printer_model') == 'Anycubic Kobra X' and cfg.get('nozzle_diameter') == ['0.4'], 'Chybná tiskárna/tryska')
        require(cfg['layer_height'] == '0.16' and cfg['wall_loops'] == '3', 'Změněný proces')
        require(cfg['brim_type'] == 'outer_only' and float(cfg['brim_width']) == 3, 'Chybí brim')
        require(cfg['filament_colour'] == [plate['colour']], 'Změněná barva profilu')
        require(cfg['enable_prime_tower']=='0' and cfg['enable_support']=='0','Neočekávané podpory/věž')
        require(cfg['filament_max_volumetric_speed']==[plate['profile']['mvs']],'Změněný limit průtoku')
        require(cfg['nozzle_temperature']==[plate['profile']['nozzle']] and cfg['nozzle_temperature_initial_layer']==[plate['profile']['initial_nozzle']],'Změněná teplota trysky')
        require(cfg['textured_plate_temp']==[plate['profile']['bed']],'Změněná teplota podložky')
        repairs = [p.attrib for p in config.findall('.//mesh_stat')]
        require(all(all(int(v)==0 for v in p.values()) for p in repairs), f'Slicer opravil síť: {repairs}')
        expected = {p['name']:p for p in plate['parts']}
        checked = []
        for item in items:
            obj = root.find(f'm:resources/m:object[@id="{item.get("objectid")}"]', XMLNS)
            object_config = config.find(f'object[@id="{item.get("objectid")}"]')
            require(object_config is not None, 'Chybí konfigurace objektu')
            name = object_config.find('metadata[@key="name"]').get('value')
            require(name in expected, f'Neočekávaný objekt {name}')
            exp = expected[name]
            components = obj.findall('m:components/m:component',XMLNS)
            require(len(components)==1, 'Nečekaná vícedílná struktura')
            component = components[0]
            nested = ET.fromstring(z.read(component.get(f'{{{PNS}}}path').lstrip('/')))
            mesh = nested.find(f'm:resources/m:object[@id="{component.get("objectid")}"]/m:mesh',XMLNS)
            offset = [a+b for a,b in zip(translation(item.get('transform')),translation(component.get('transform')))]
            vertices = [[float(v.get(axis))+offset[i] for i,axis in enumerate('xyz')] for v in mesh.findall('m:vertices/m:vertex',XMLNS)]
            faces = mesh.findall('m:triangles/m:triangle',XMLNS)
            lo,hi = [[fun(v[i] for v in vertices) for i in range(3)] for fun in (min,max)]
            require(len(faces)==exp['triangle_count'], f'Změněné trojúhelníky {name}')
            require(all(abs(lo[i]-exp['placed_min_mm'][i])<0.001 and abs(hi[i]-exp['placed_max_mm'][i])<0.001 for i in range(3)), f'Změněné umístění {name}')
            source = meshes[exp['id']]
            require(len(source['vertices']) == len(vertices), f'Změněné vrcholy {name}')
            # The exporter preserves vertex order. Quantisation must remain sub-micron.
            delta = max(abs(source['vertices'][i][a]+exp['translation_mm'][a]-vertices[i][a]) for i in range(len(vertices)) for a in range(3))
            require(delta < 0.001, f'Změněná geometrie {name}: {delta}')
            checked.append({'name':name,'preserved_geometry_and_placement':True,'maximum_vertex_delta_mm':delta})
        require(len(checked)==len(expected), 'Chybějící objekt')
        require(('Metadata/plate_1.gcode' in z.namelist()) == has_gcode, 'Neočekávaný stav řezání')
        info = {'sha256':sha(path), 'objects':checked, 'physical_parts':len(items), 'mesh_repairs':repairs,
                'settings':{k:cfg.get(k) for k in ('printer_model','printer_settings_id','print_settings_id','filament_settings_id','nozzle_diameter','layer_height','wall_loops','sparse_infill_density','sparse_infill_pattern','enable_support','support_on_build_plate_only','brim_type','brim_width','nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','outer_wall_speed','inner_wall_speed','filament_colour','filament_max_volumetric_speed','enable_prime_tower','initial_layer_print_height','top_shell_layers','bottom_shell_layers')},
                'has_gcode':has_gcode}
        if has_gcode:
            gcode=z.read('Metadata/plate_1.gcode')
            info.update({'gcode_bytes':len(gcode),'gcode_sha256':hashlib.sha256(gcode).hexdigest()})
            slice_info=ET.fromstring(z.read('Metadata/slice_info.config'))
            info['slice_metadata']={v.get('key'):v.get('value') for v in slice_info.iter('metadata') if v.get('key') in ('prediction','weight','outside','support_used')}
            info['warnings']=[v.attrib for v in slice_info.iter('warning')]
            require(info['slice_metadata'].get('outside') == 'false','Slicer hlásí přesah podložky')
            dangerous=[v for v in info['warnings'] if v.get('msg') not in ('not_support_traditional_timelapse',)]
            require(not dangerous, f'Varování sliceru vyžaduje kontrolu: {dangerous}')
        return info



def create_profiles(number, colour, colour_name, spec):
    process=json.loads(PROCESS.read_text())
    name=f'Pomodoro Orbit 0.16 mm {spec["kind"]} navrh @Kobra X'
    process.update({'name':name,'print_settings_id':name,'from':'user',
        'layer_height':'0.16','initial_layer_print_height':'0.2','wall_loops':'3',
        'sparse_infill_density':'20%','sparse_infill_pattern':'gyroid',
        'top_shell_layers':'5','bottom_shell_layers':'5',
        'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.1',
        'enable_support':'0','support_on_build_plate_only':'0',
        'initial_layer_speed':'25','initial_layer_infill_speed':'30',
        'outer_wall_speed':'40','inner_wall_speed':'70','top_surface_speed':'35',
        'sparse_infill_speed':'80','internal_solid_infill_speed':'70',
        'gap_infill_speed':'35','bridge_speed':'25',
        'default_acceleration':'1500','outer_wall_acceleration':'800',
        'inner_wall_acceleration':'1500','top_surface_acceleration':'800',
        'print_sequence':'by layer','enable_prime_tower':'0','arc_fitting':'0'})
    if spec['kind']=='Silk Gold':
        for key in ('inner_wall_speed','sparse_infill_speed','internal_solid_infill_speed'):
            process[key]='50'
    filament=json.loads(FILAMENT.read_text())
    name=f'NAVRH Alzament PLA {spec["kind"]} {colour_name} @Kobra X 0.4'
    filament.update({'name':name,'setting_id':name,'filament_settings_id':[name],
        'filament_vendor':['Alzament'],'filament_colour':[colour],
        'default_filament_colour':[colour],'from':'user','is_custom_defined':'1',
        'filament_flow_ratio':['1.0'],'filament_max_volumetric_speed':[spec['mvs']],
        'nozzle_temperature_range_low':['210' if spec['kind']=='Silk Gold' else '190'],'nozzle_temperature_range_high':['230' if spec['kind']=='Silk Gold' else '220'],
        'filament_notes':[f'Navrh pro Alzament PLA {spec["kind"]}, fyzicky nekalibrovany. '
            'Barva navrhu nepotvrzuje skutecnou civku nebo vstup tiskarny.']})
    for key in ('nozzle_temperature','nozzle_temperature_BRASS','nozzle_temperature_HS'):
        filament[key]=[spec['nozzle']]
    for key in ('nozzle_temperature_initial_layer','nozzle_temperature_initial_layer_BRASS','nozzle_temperature_initial_layer_HS'):
        filament[key]=[spec['initial_nozzle']]
    for key in ('hot_plate_temp','hot_plate_temp_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer'):
        filament[key]=[spec['bed']]
    process_path=HERE/f'proces-{number:02d}-kobra-x-pla-navrh.json'
    filament_path=HERE/f'filament-{number:02d}-{colour_name}-navrh.json'
    write_json(process_path,process);write_json(filament_path,filament)
    return process_path,filament_path


def run_cli(command,log):
    with log.open('w') as stream:
        r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,
            env={**os.environ,'DISPLAY':''},timeout=1800)
    require(r.returncode==0,f'Slicer exit {r.returncode}: {log}')


def check_paths(gcode,plate):
    roles=Counter();layers={};owner=None;owners=set();first_owners=set()
    role='Custom';layer=-1;xyz_absolute=True;e_relative=True
    pos=dict(X=0.,Y=0.,Z=0.,E=0.);feed=0.;max_speed=0.;max_flow=0.;max_raw_flow=0.;flow_samples=[]
    min_xy=[math.inf,math.inf];max_xy=[-math.inf,-math.inf]
    num=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):layer+=1
        elif line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        elif line.startswith('EXCLUDE_OBJECT_START NAME='):
            owner=line.split('NAME=',1)[1];owners.add(owner)
        elif line.startswith('EXCLUDE_OBJECT_END'):owner=None
        command=line.split(';',1)[0].strip()
        if not command:continue
        kind=command.split()[0];values={a:float(v) for a,v in num.findall(command)}
        if kind=='G90':xyz_absolute=True
        elif kind=='G91':xyz_absolute=False
        elif kind=='M83':e_relative=True
        elif kind=='M82':e_relative=False
        elif kind=='G92':pos.update({k:v for k,v in values.items() if k in pos})
        elif kind in ('G0','G1'):
            old=pos.copy()
            for axis in 'XYZ':
                if axis in values:pos[axis]=values[axis] if xyz_absolute else pos[axis]+values[axis]
            extrusion=values.get('E',0) if e_relative else values.get('E',pos['E'])-pos['E']
            if 'E' in values:pos['E']=pos['E']+values['E'] if e_relative else values['E']
            if 'F' in values:feed=values['F']/60
            length=math.hypot(pos['X']-old['X'],pos['Y']-old['Y'])
            if extrusion<=0 or length<1e-8 or role=='Custom':continue
            require(owner is not None and layer>=0,'Extruze mimo objekt/vrstvu')
            roles[role]+=1
            if layer==0:first_owners.add(owner)
            layers.setdefault(layer,{'z':pos['Z'],'segments':[]})['segments'].append((old['X'],old['Y'],pos['X'],pos['Y'],role))
            max_speed=max(max_speed,feed)
            flow=extrusion*math.pi*(1.75/2)**2*feed/length
            max_raw_flow=max(max_raw_flow,flow)
            if length>=0.1:max_flow=max(max_flow,flow)
            for xy in ((old['X'],old['Y']),(pos['X'],pos['Y'])):
                require(all(0<v<BED for v in xy),'Draha mimo podlozku')
                min_xy=[min(min_xy[i],xy[i]) for i in range(2)]
                max_xy=[max(max_xy[i],xy[i]) for i in range(2)]
        elif kind in ('G2','G3') and values.get('E',0)>0:raise RuntimeError('Nezpracovana obloukova extruze')
    require(len(owners)==plate['physical_parts'] and first_owners==owners,'Chybny pocet objektu nebo kontakt s podlozkou')
    require(set(layers)==set(range(layer+1)),'Vrstva bez extruze')
    max_z=max(l['z'] for l in layers.values())
    require(abs(max_z-max(p['size_mm'][2] for p in plate['parts']))<0.25,'Zmenena vyska drah')
    require(roles['Brim']>0,'Chybi brim')
    require(not any('support' in r.lower() for r in roles),'Necekane podpory')
    require(f"G9111 bedTemp={plate['profile']['bed']} extruderTemp={plate['profile']['initial_nozzle']}" in gcode,'Jine prvni teploty')
    require(max_flow<float(plate['profile']['mvs'])+0.12,f'Prekrocen navrhovyMVS: {max_flow}')
    # Actual layer strokes with a short zoomed view, not a synthetic cross section.
    target_z=sorted(set([0.2,0.68,1.0,2.0,4.0,6.0,10.0,15.0,20.0,max_z]+[float(z) for p in plate['parts'] for z in p['critical_z_mm']]))
    chosen=sorted({min(layers,key=lambda i:abs(layers[i]['z']-z)) for z in target_z if z<=max_z})
    columns=4;rows=math.ceil(len(chosen)/columns);size=420
    canvas=Image.new('RGB',(columns*size,rows*(size+45)+85),'#fafbfc');draw=ImageDraw.Draw(canvas)
    title=ImageFont.truetype(FONT,24);font=ImageFont.truetype(FONT,17)
    draw.text((20,12),f"Podložka {plate['number']:02d} · skutečné extruzní dráhy",fill='#18343d',font=title)
    lo=[min_xy[i]-2 for i in range(2)];hi=[max_xy[i]+2 for i in range(2)]
    factor=(size-45)/max(hi[i]-lo[i] for i in range(2))
    for n,index in enumerate(chosen):
        col,row=n%columns,n//columns
        xy=lambda x,y:(20+size*col+factor*(x-lo[0]),60+(size+45)*row+factor*(hi[1]-y))
        for x,y,x2,y2,r in layers[index]['segments']:
            colour='#51a080' if r=='Brim' or 'support' in r.lower() else '#c77239' if 'bridge' in r.lower() or 'overhang' in r.lower() else '#4c3a16'
            draw.line((xy(x,y),xy(x2,y2)),fill=colour,width=1)
        draw.text((20+size*col,60+(size+45)*row+size-10),f"Vrstva {index+1}, Z {layers[index]['z']:g} mm",fill='#18343d',font=font)
    draw.text((20,canvas.height-27),'Zelená: brim · oranžová: most/převis · tmavá: model',fill='#536871',font=font)
    preview=HERE/f"podlozka-{plate['number']:02d}-vrstvy.png";canvas.save(preview)
    # Close-ups of every object's actual paths at its engineering-critical heights.
    detail_previews=[]
    for part in plate['parts']:
        target=[0.2,part['size_mm'][2]]+part['critical_z_mm']
        chosen_part=sorted({min(layers,key=lambda i:abs(layers[i]['z']-z)) for z in target if 0<z<=part['size_mm'][2]+0.01})
        cols=min(4,len(chosen_part));rows=math.ceil(len(chosen_part)/cols);tile=400
        detail=Image.new('RGB',(cols*tile,rows*(tile+35)+60),'#fafbfc');dd=ImageDraw.Draw(detail)
        dd.text((16,12),f"{part['name']} – skutečné dráhy",fill='#18343d',font=title)
        low=[part['placed_min_mm'][i]-4 for i in (0,1)];high=[part['placed_max_mm'][i]+4 for i in (0,1)]
        scale=(tile-35)/max(high[i]-low[i] for i in (0,1))
        for n,index in enumerate(chosen_part):
            col,row=n%cols,n//cols
            project=lambda x,y:(16+col*tile+scale*(x-low[0]),50+row*(tile+35)+scale*(high[1]-y))
            for x,y,x2,y2,role in layers[index]['segments']:
                if not all(low[i]<=v<=high[i] for pt in ((x,y),(x2,y2)) for i,v in enumerate(pt)):continue
                color='#51a080' if role=='Brim' or 'support' in role.lower() else '#c77239' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#303e46'
                dd.line((project(x,y),project(x2,y2)),fill=color,width=1)
            dd.text((16+col*tile,50+row*(tile+35)+tile-8),f"Vrstva {index+1}, Z {layers[index]['z']:g} mm",fill='#18343d',font=font)
        detail_path=HERE/f"detail-{plate['number']:02d}-{part['name']}-drahy.png"
        detail.save(detail_path);detail_previews.append(detail_path.name)
    mass=re.search(r'^; total filament used \[g\] = ([0-9.]+)$',gcode,re.M)
    time=re.search(r'^; estimated printing time \(normal mode\) = (.+)$',gcode,re.M)
    # Connectivity means no complete new deposition island without contact in the preceding layer.
    def point_segment_distance(p,a,b):
        dx,dy=b[0]-a[0],b[1]-a[1]
        t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
        return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
    def distance(a,b):
        p,q=a;r,s=b
        cross=lambda x,y:x[0]*y[1]-x[1]*y[0]
        pq=(q[0]-p[0],q[1]-p[1]);rs=(s[0]-r[0],s[1]-r[1])
        rp=(r[0]-p[0],r[1]-p[1]);den=cross(pq,rs)
        if abs(den)>1e-12:
            t,u=cross(rp,rs)/den,cross(rp,pq)/den
            if 0<=t<=1 and 0<=u<=1:return 0.
        return min(point_segment_distance(p,r,s),point_segment_distance(q,r,s),
            point_segment_distance(r,p,q),point_segment_distance(s,p,q))
    def bins(segment,pad):
        p,q=segment
        for x in range(math.floor((min(p[0],q[0])-pad)/4),math.floor((max(p[0],q[0])+pad)/4)+1):
            for y in range(math.floor((min(p[1],q[1])-pad)/4),math.floor((max(p[1],q[1])+pad)/4)+1):yield(x,y)
    disconnected=[];component_count=[];previous=[];prev_index={}
    for i,l in layers.items():
        segments=[((x,y),(x2,y2)) for x,y,x2,y2,r in l['segments'] if r!='Brim']
        parent=list(range(len(segments)));index={}
        def root(n):
            while parent[n]!=n:parent[n]=parent[parent[n]];n=parent[n]
            return n
        anchored=[]
        for n,s in enumerate(segments):
            cells=list(bins(s,0.71))
            for k in set(j for cell in cells for j in index.get(cell,[])):
                if distance(s,segments[k])<=0.46:parent[root(n)]=root(k)
            if i>0:
                anchored.append(any(distance(s,previous[k])<=0.71
                    for k in set(j for cell in cells for j in prev_index.get(cell,[]))))
            for cell in cells:index.setdefault(cell,[]).append(n)
        groups={}
        for n in range(len(segments)):groups.setdefault(root(n),[]).append(n)
        component_count.append(len(groups))
        if i>0:
            bad=[{'segment_count':len(g),'xy_bbox_mm':[[fun(pt[a] for n in g for pt in segments[n]) for a in range(2)] for fun in (min,max)],'total_path_length_mm':sum(math.dist(*segments[n]) for n in g),'minimum_previous_layer_path_distance_mm':min(distance(segments[n],old) for n in g for old in previous)} for g in groups.values() if not any(anchored[n] for n in g)]
            if bad:disconnected.append({'layer_one_based':i+1,'z_mm':l['z'],'islands':bad})
        previous=segments;prev_index=index
        if (i+1)%25==0:print(f"Plate {plate['number']}: path connectivity {i+1}/{len(layers)} layers",flush=True)
    return {'physical_parts':plate['physical_parts'],'all_objects_on_first_layer':True,'layers':layer+1,
        'all_layers_have_extrusion':True,'maximum_extrusion_z_mm':max_z,
        'roles_segments':dict(roles),'support_segments':0,'brim_generated':True,
        'deposition_island_test':{'method':'Actual path graph: deposited strokes connect within 0.46 mm nominal width; every component must contact preceding-layer strokes within 0.71 mm (width plus 0.25 mm allowance). Does not certify full overhang support.',
            'disconnected_new_islands':disconnected,'passed':not disconnected,'maximum_components_per_layer':max(component_count)},
        'extrusion_min_xy_mm':min_xy,'extrusion_max_xy_mm':max_xy,
        'minimum_extrusion_edge_margin_mm':min(min_xy+[BED-v for v in max_xy]),
        'maximum_commanded_extrusion_speed_mm_s':max_speed,'maximum_commanded_volumetric_flow_mm3_s_segments_at_least_0_1mm':max_flow,
        'maximum_raw_segment_flow_mm3_s':max_raw_flow,
        'flow_quantisation_note':'XY coordinates use 0.001 mm and E uses 0.00001 mm precision; raw flow of moves below 0.1 mm is dominated by rounding. Audited flow uses segments at least 0.1 mm.',
        'preview':preview.name,'detail_previews':detail_previews,'selected_z_mm':[layers[i]['z'] for i in chosen],
        'estimated_filament_g':float(mass.group(1)) if mass else None,
        'estimated_printing_time':time.group(1) if time else None,
        'first_layer_gcode_temperature_c':{'bed':float(plate['profile']['bed']),'nozzle':float(plate['profile']['initial_nozzle'])},'physical_print_verified':False}

def arrange_items(parts, meshes):
    """Stable shelf placement in 260 mm bed; no rotation or scale changes."""
    expanded=[]
    for part in parts:
        count=int(part.get('count',1))
        require(count>0,'Počet kusů musí být kladný')
        for copy in range(count):
            item={'id':part['id'],'name':f"{part['id']}_{copy+1:02d}"}
            if 'xy' in part:
                xy=part['xy']
                item['xy']=xy[copy] if isinstance(xy[0],(list,tuple)) else xy
                require(count==1 or isinstance(xy[0],(list,tuple)), 'Opakované kusy vyžadují jednotlivé xy')
            expanded.append(item)
    require(all('xy' in p for p in expanded) or all('xy' not in p for p in expanded), 'Nelze míchat ruční a automatické rozmístění na jedné podložce')
    if all('xy' in p for p in expanded):return expanded
    expanded.sort(key=lambda p:(-meshes[p['id']]['size'][1],-meshes[p['id']]['size'][0],p['name']))
    x=y=EDGE;rowheight=0
    for item in expanded:
        w,h=meshes[item['id']]['size'][:2]
        if x+w>BED-EDGE:
            x=EDGE;y+=rowheight+GAP;rowheight=0
        require(y+h<=BED-EDGE,'Díly se nevejdou do 2 podložek; upravit rozdělení nebo rozmístění')
        item['xy']=[x,y];x+=w+GAP;rowheight=max(rowheight,h)
    hi=[max(p['xy'][i]+meshes[p['id']]['size'][i] for p in expanded) for i in (0,1)]
    shift=[(BED-hi[i]-EDGE)/2 for i in (0,1)]
    for p in expanded:p['xy']=[p['xy'][i]+shift[i] for i in (0,1)]
    return expanded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true',help='Vytvořit jen alternativu bez tiskových nastavení')
    parser.add_argument('--only-plate',type=int,choices=[1,2])
    parser.add_argument('--reuse-verified',action='store_true',help='Zachovat hotové podložky pouze pokud souhlasí hashe geometrie, rozmístění a projekt')
    args=parser.parse_args()
    source_hash=sha(SOURCE_MANIFEST)
    source=json.loads(SOURCE_MANIFEST.read_text())
    parts=source['parts'];meshes={}
    require(len(parts)>0,'Prázdný kusovník')
    require(set(p['plate'] for p in parts)=={1,2},'Očekávány právě 2 barevné podložky')
    for p in parts:
        require(p['id'] not in meshes,'Duplicitní ID typu dílu')
        require(not p.get('supports',False),'Díl vyžaduje samostatné nastavení a posouzení podpor')
        path=(MODEL/p['file']).resolve()
        require(path.is_relative_to(MODEL),'STL mimo model')
        mesh=read_mesh(path)
        mesh.update({'file':'../'+p['file'],'source_sha256':sha(path),'supports':False,
            'support_note':p.get('support_note','Navržen tisk bez podpor; fyzický tisk neověřen.'),
            'critical_z_mm':p.get('critical_z_mm',[])})
        meshes[p['id']]=mesh
    results=[];plates=[]
    materials=source.get('materials',{'1':{'name':'cerna','colour':'#17191B'},'2':{'name':'zlata','colour':'#D4AF37'}})
    for number in (1,2):
        if args.only_plate and args.only_plate!=number:continue
        entries=[p for p in parts if p['plate']==number]
        items=arrange_items(entries,meshes)
        report_path=HERE/f'kontrola-podlozky-{number:02d}.json'
        if args.reuse_verified and report_path.exists():
            previous=json.loads(report_path.read_text());oldplate=previous['plate']
            byname={p['name']:p for p in oldplate['parts']}
            same=len(items)==len(byname) and oldplate['colour']==materials[str(number)]['colour']
            for item in items:
                old=byname.get(item['name']);mesh=meshes[item['id']]
                t=[item['xy'][0]-mesh['lo'][0],item['xy'][1]-mesh['lo'][1],-mesh['lo'][2]]
                same=bool(same and old and old['id']==item['id'] and old['source_sha256']==mesh['source_sha256']
                    and old['supports']==mesh['supports'] and old['critical_z_mm']==mesh['critical_z_mm']
                    and all(abs(a-b)<1e-6 for a,b in zip(t,old['translation_mm'])))
            project=HERE/previous['project'];geometry=HERE/oldplate['geometry']
            same=bool(same and project.exists() and geometry.exists() and sha(project)==previous['delivered']['sha256']
                and sha(geometry)==oldplate['geometry_sha256'] and previous['toolpath_audit']['deposition_island_test']['passed'])
            if same:
                results.append(previous);plates.append(oldplate)
                print(json.dumps({'plate':number,'reused_verified_project':project.name,'source_meshes_and_placement_unchanged':True}),flush=True)
                continue
        plate=make_geometry(number,{'items':items},meshes)
        plate.update({'colour':materials[str(number)]['colour'],'material_name':materials[str(number)]['name']})
        plate['profile']={'kind':'Basic','mvs':'8','nozzle':'205','initial_nozzle':'215','bed':'50'} if number==1 else {'kind':'Silk Gold','mvs':'5.5','nozzle':'220','initial_nozzle':'220','bed':'50'}
        plates.append(plate)
        if args.geometry_only:continue
        process,filament=create_profiles(number,plate['colour'],plate['material_name'],plate['profile'])
        work=CACHE/f'podlozka-{number:02d}';work.mkdir(exist_ok=True,parents=True)
        configured=work/'configured.3mf'
        run_cli([CLI,'--datadir',str(work/'datadir-export'),'--load-settings',f'{MACHINE};{process}',
            '--load-filaments',str(filament),'--arrange','0','--orient','0','--export-3mf',configured.name,
            '--outputdir',str(work),str(HERE/plate['geometry'])],work/'export.log')
        initial=project_check(configured,plate,meshes,False)
        run_cli([CLI,'--datadir',str(work/'datadir-slice'),'--arrange','0','--orient','0','--slice','0',
            '--export-3mf','sliced.3mf','--outputdir',str(work),str(configured)],work/'slice.log')
        sliced=work/'sliced.3mf';check=project_check(sliced,plate,meshes,True)
        delivered=HERE/f'podlozka-{number:02d}-kobra-x-pla-projekt.3mf'
        candidate=work/'candidate.3mf'
        with ZipFile(sliced) as zin,ZipFile(candidate,'w',ZIP_DEFLATED) as zout:
            for name in zin.namelist():
                data=zin.read(name)
                if name=='3D/3dmodel.model':
                    data=data.decode().replace('pouze geometrie','nastavený a lokálně nařezaný projekt').replace(
                        'Pouze geometrie 1:1; bez procesu, filamentu a G-code. Alternativa téže podložky.',
                        f'Kobra X 0,4 mm; PLA {plate["profile"]["kind"]}, návrhový profil. Nastavený a lokálně nařezaný projekt. Fyzický tisk neověřen.').encode()
                zout.writestr(name,data)
        final=project_check(candidate,plate,meshes,True)
        require(final['gcode_sha256']==check['gcode_sha256'],'Předání změnilo G-code')
        with ZipFile(candidate) as z:paths=check_paths(z.read('Metadata/plate_1.gcode').decode(errors='replace'),plate)
        result={'plate':plate,'project':delivered.name,'configured':initial,'delivered':final,'toolpath_audit':paths,
            'machine_profile_sha256':sha(MACHINE),'process_sha256':sha(process),'filament_sha256':sha(filament),
            'cli_exit_codes':[0,0],'cli_error_messages':sorted(set(line.split('[error]',1)[1].strip()
                for name in ('export.log','slice.log') for line in (work/name).read_text(errors='replace').splitlines() if '[error]' in line))}
        require(sha(SOURCE_MANIFEST)==source_hash,'Manifest se během řezání změnil')
        require(all(sha((HERE/p['file']).resolve())==p['source_sha256'] for p in plate['parts']), 'STL se během řezání změnila')
        results.append(result)
        if paths['deposition_island_test']['passed']:
            delivered.write_bytes(candidate.read_bytes())
        write_json(HERE/f'kontrola-podlozky-{number:02d}.json',result)
        print(json.dumps({'plate':number,'project':delivered.name,'parts':plate['physical_parts'],
            'time':paths['estimated_printing_time'],'mass_g':paths['estimated_filament_g'],
            'islands_passed':paths['deposition_island_test']['passed']},ensure_ascii=False),flush=True)
    require(sha(SOURCE_MANIFEST)==source_hash,'Manifest se během zpracování změnil')
    require(sum(p['physical_parts'] for p in plates)==sum(p.get('count',1) for p in parts if not args.only_plate or p['plate']==args.only_plate),'Nesouhlasí počet kusů')
    manifest={'source_manifest_sha256':source_hash,'machine':'Anycubic Kobra X 0.4 nozzle',
        'physical_parts':sum(p['physical_parts'] for p in plates),'plates':plates}
    write_json(HERE/('manifest.json' if not args.only_plate else f'manifest-{args.only_plate:02d}.json'),manifest)
    if args.geometry_only or args.only_plate:return
    require(all(r['toolpath_audit']['deposition_island_test']['passed'] for r in results),'Nove oddelene ostruvky vyzaduji posouzeni; report ulozen, nepredavat jako hotove')
    write_json(HERE/'kontrola-rezani.json',{'machine':'Anycubic Kobra X 0.4 nozzle','plates':results,
        'physical_spool_slot_verified':False,'physical_print_verified':False,'physical_fit_verified':False,'printer_io_performed':False})
    rows=[];total_seconds=0;total_mass=0
    warnings=sorted({w['msg'] for r in results for w in r['delivered']['warnings']})
    cli_errors=sorted({e for r in results for e in r['cli_error_messages']})
    diagnostics='Varování uložená slicerem: '+(', '.join(warnings) if warnings else 'žádná')+'. '
    if cli_errors:
        diagnostics+='CLI navíc vypsalo `'+ '`, `'.join(cli_errors)+'`. Operace skončily exit 0; zachování geometrie a počtů bylo ověřeno samostatně. Funkce vynechávání objektů není fyzicky ověřená.'
    for r in results:
        p=r['plate'];t=r['toolpath_audit'];seconds=int(r['delivered']['slice_metadata']['prediction'])
        total_seconds+=seconds;total_mass+=t['estimated_filament_g']
        rows.append(f"| [{p['number']:02d} – {p['material_name']}]({r['project']}) | {p['physical_parts']} | {seconds//3600} h {(seconds%3600)//60} min | {t['estimated_filament_g']:.2f} g |")
    (HERE/'README.md').write_text('''# Pomodoro Orbit – připravené podložky

Každý nastavený projekt otevřít samostatně **jednou jako celý projekt** v Anycubic Slicer Next. Všechny kopie už jsou rozmístěné. Nemnožit, nepřerovnávat ani automaticky neorientovat.

| Nastavený projekt | Fyzické kusy | Odhad času | Odhad materiálu |
|---|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

Celkem **{manifest['physical_parts']} kusů, {total_seconds//3600} h {(total_seconds%3600)//60} min, {total_mass:.2f} g** podle lokálního sliceru. Fyzický tisk, spotřeba, hladkost pohybu a fit neověřeny.

**Anycubic Kobra X, 0,4 mm; návrhové nekalibrované profily:** vrstva 0,16 / první 0,20 mm; 3 stěny; 20 % gyroid; 5 horních a 5 dolních vrstev; vnější stěny 40 mm/s, první 25 mm/s. Černá PLA Basic: vnitřní 70 mm/s, tryska první 215 / další 205 °C, texturovaná podložka 50 °C, max. průtok 8 mm³/s. Zlatá Alzament PLA Silk Gold: vnitřní stěny i výplň nejvýše 50 mm/s, tryska 220 / podložka 50 °C, max. průtok 5,5 mm³/s. Každá podložka má jediný filament; čisticí věž vypnutá. **Podpory vypnuté podle tiskové orientace; vnější brim 3 mm je přilnavost, nikoli podpora převisů.** Brim opatrně odstranit z pracovních obvodů.

Před tiskem vybrat skutečné cívky a odpovídající fyzické vstupy tiskárny; barvy v projektu je nepotvrzují. Skladové zůstatky nejsou tímto úkolem ověřeny. Podložka 01 obsahuje odlišný profil PLA Basic, podložka 02 profil Silk Gold. Záměna materiálů vyžaduje změnu profilu.

- [Očíslovaná podložka 01](podlozka-01.png) · [skutečné dráhy 01](podlozka-01-vrstvy.png)
- [Očíslovaná podložka 02](podlozka-02.png) · [skutečné dráhy 02](podlozka-02-vrstvy.png)
- [Manifest kusů a umístění](manifest.json) · [kontrola obou řezů](kontrola-rezani.json)

Kontroly: uzavřenost a jedna komponenta každé STL, zachování vrcholů/počtů/orientace/umístění ve 3MF, správná tiskárna a nastavení, kontakt všech kusů na první vrstvě, extruze každé vrstvy a uvnitř podložky, kontrola nových oddělených ostrůvků z reálných drah. Grafická kontrola ostrůvků potvrzuje spojení alespoň některé dráhy komponenty s předchozí vrstvou; **necertifikuje plošnou podporu celého převisu**. Výsledky a skutečná varování jsou v kontrolním JSON. Brim a případné drobné mosty/převisy jsou viditelné v obrázcích drah.

{diagnostics}

Nastavené projekty obsahují skutečný lokálně vytvořený G-code. `podlozka-01-geometrie.3mf` a `podlozka-02-geometrie.3mf` jsou pouze alternativy stejného počtu kusů bez procesu, filamentu a G-code; **netisknout navíc**.

Regenerace po exportu STL: `python3 pripravit-podlozky.py`. Čte `../print-manifest.json`, přepíše zdejší podložky, profily, náhledy a kontrolní JSON. `--reuse-verified` zachová již ověřený řez jen při shodě hashů STL/projektu/geometrie a umístění; `--geometry-only` tvoří pouze alternativní geometrii; `--only-plate 1` nebo `2` je dílčí diagnostika a nenahradí závěrečnou kontrolu celku. Logy a izolované datadir zůstávají v ignorované `.cache/`. Program nepřepisuje globální presety a neprovádí tiskárnové I/O.

Žádná tisková úloha nebyla odeslána ani spuštěna.
''')

if __name__=='__main__':main()
