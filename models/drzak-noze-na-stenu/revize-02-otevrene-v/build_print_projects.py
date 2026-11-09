#!/usr/bin/env python3
"""Otevřený V držák nože — revize 02: rozmístění, profily PLA a lokální řezání.
Zapisuje pouze do rozlozeni/, logy do rozlozeni/.cache/. Nepoužívá tiskárnové I/O.
Čte print-manifest.json. Přepíše pouze vlastní soubory v rozlozeni/.
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

MODEL = Path(__file__).resolve().parent
HERE = MODEL / 'rozlozeni'
HERE.mkdir(exist_ok=True)
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
    ET.SubElement(model, 'metadata', name='Title').text = f'Otevřený V držák nože — revize 02 – {stem}, pouze geometrie'
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
    preview_layout(number, records, meshes, plate.get('colour','#D5C5A4'))
    return {'number': number, 'geometry': path.name, 'geometry_sha256': sha(path),
            'preview': f'{stem}.png', 'physical_parts': len(records), 'parts': records,
            'minimum_geometry_edge_margin_mm': margin,
            'minimum_bbox_gap_mm': min_gap if math.isfinite(min_gap) else None}


def preview_layout(number, records, meshes, colour):
    canvas = Image.new('RGB', (1040,1120), '#fafbfc')
    draw = ImageDraw.Draw(canvas)
    title, font = ImageFont.truetype(FONT,28), ImageFont.truetype(FONT,19)
    draw.text((65,24), f'Podložka {number:02d} · Kobra X · 260 × 260 mm', fill='#18343d', font=title)
    rgb=tuple(int(colour[i:i+2],16) for i in (1,3,5))
    xy = lambda x,y: (65+3.5*x,90+3.5*(BED-y))
    draw.rectangle((xy(0,BED),xy(BED,0)), fill='#e8edef', outline='#55717b', width=3)
    draw.line((xy(0,0),xy(BED,0)), fill='#b85042', width=5)
    for index,record in enumerate(records,1):
        mesh = meshes[record['id']]
        t = record['translation_mm']
        for face in sorted(mesh['faces'], key=lambda f: sum(mesh['vertices'][i][2] for i in f)):
            points = [mesh['vertices'][i] for i in face]
            tone = int(34+42*(sum(p[2] for p in points)/3-mesh['lo'][2])/mesh['size'][2])
            draw.polygon([xy(p[0]+t[0],p[1]+t[1]) for p in points], fill=tuple(max(0,min(255,int(v*(.72+tone/250)))) for v in rgb))
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
    draw.text((65,1020), f'Fyzické kusy: {len(records)} · skutečná STL · 1:1', fill='#263f49', font=font)
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
        require(cfg['layer_height'] == '0.2' and cfg['wall_loops'] == '4', 'Změněný proces')
        require(cfg['sparse_infill_density']=='15%' and cfg['sparse_infill_pattern']=='gyroid', 'Změněná výplň')
        require(cfg['top_shell_layers']=='5' and cfg['bottom_shell_layers']=='5','Změněné horní/dolní vrstvy')
        require(cfg['detect_narrow_internal_solid_infill']=='1', 'Změněná úzká plná výplň')
        require(cfg['filter_out_gap_fill']=='0', 'Změněný filtr mikrovýplní')
        require(cfg['brim_type'] == 'outer_only' and float(cfg['brim_width']) == 3, 'Chybí brim')
        require(cfg['filament_colour'] == [plate['colour']], 'Změněná barva profilu')
        require(cfg['enable_prime_tower']=='0' and cfg['enable_support']==('1' if plate['supports_enabled'] else '0'),'Neočekávané podpory/věž')
        require(cfg['support_on_build_plate_only']=='0','Podpory nejsou povoleny na modelu')
        require(cfg['independent_support_layer_height']=='0','Unexpected independent support layers')
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
                'settings':{k:cfg.get(k) for k in ('printer_model','printer_settings_id','print_settings_id','filament_settings_id','nozzle_diameter','layer_height','wall_loops','sparse_infill_density','sparse_infill_pattern','enable_support','support_on_build_plate_only','support_type','support_style','support_threshold_angle','support_top_z_distance','support_bottom_z_distance','support_object_xy_distance','support_interface_top_layers','independent_support_layer_height','brim_type','brim_width','nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','outer_wall_speed','inner_wall_speed','filament_colour','filament_max_volumetric_speed','enable_prime_tower','initial_layer_print_height','top_shell_layers','bottom_shell_layers','filter_out_gap_fill','detect_narrow_internal_solid_infill')},
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



def create_profiles(number, colour, colour_name, spec, supports):
    process=json.loads(PROCESS.read_text())
    name=f'Otevřený V držák nože — revize 02 0.20 mm {spec["kind"]} navrh @Kobra X'
    process.update({'name':name,'print_settings_id':name,'from':'user',
        'layer_height':'0.2','initial_layer_print_height':'0.2','wall_loops':'4',
        'sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
        'top_shell_layers':'5','bottom_shell_layers':'5',
        'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.1',
        'enable_support':'1' if supports else '0','support_on_build_plate_only':'0',
        'support_type':'normal(auto)','support_style':'snug','support_threshold_angle':'30',
        'support_top_z_distance':'0.2','support_bottom_z_distance':'0.2',
        'support_object_xy_distance':'0.35','support_interface_top_layers':'2',
        'support_speed':'60','support_interface_speed':'40','bridge_no_support':'1',
        'independent_support_layer_height':'0',
        'initial_layer_speed':'25','initial_layer_infill_speed':'30',
        'outer_wall_speed':'40','inner_wall_speed':'70','top_surface_speed':'35',
        'sparse_infill_speed':'80','internal_solid_infill_speed':'70',
        'gap_infill_speed':'35','bridge_speed':'25','filter_out_gap_fill':'0','detect_narrow_internal_solid_infill':'1',
        'default_acceleration':'1500','outer_wall_acceleration':'800',
        'inner_wall_acceleration':'1500','top_surface_acceleration':'800',
        'print_sequence':'by layer','enable_prime_tower':'0','arc_fitting':'0'})
    filament=json.loads(FILAMENT.read_text())
    name=f'NAVRH Alzament PLA {spec["kind"]} {colour_name} @Kobra X 0.4'
    filament.update({'name':name,'setting_id':name,'filament_settings_id':[name],
        'filament_vendor':['Alzament'],'filament_colour':[colour],
        'default_filament_colour':[colour],'from':'user','is_custom_defined':'1',
        'filament_flow_ratio':['1.0'],'filament_max_volumetric_speed':[spec['mvs']],
        'nozzle_temperature_range_low':['190'],'nozzle_temperature_range_high':['220'],
        'filament_notes':[f'Pouze rozmerovy prototyp drzaku noze. Alzament PLA {spec["kind"]}, fyzicky nekalibrovany. Fyzicky fit noze, stabilita a montaz na stenu nejsou overeny. '
            'Barva navrhu nepotvrzuje skutecnou civku nebo vstup tiskarny.']})
    for key in ('nozzle_temperature','nozzle_temperature_BRASS','nozzle_temperature_HS'):
        filament[key]=[spec['nozzle']]
    for key in ('nozzle_temperature_initial_layer','nozzle_temperature_initial_layer_BRASS','nozzle_temperature_initial_layer_HS'):
        filament[key]=[spec['initial_nozzle']]
    for key in ('hot_plate_temp','hot_plate_temp_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer'):
        filament[key]=[spec['bed']]
    process_path=HERE/f'proces-{number:02d}-kobra-x-pla-navrh.json'
    filament_path=HERE/f'filament-{number:02d}-pla-basic-navrh.json'
    write_json(process_path,process);write_json(filament_path,filament)
    return process_path,filament_path


def run_cli(command,log):
    with log.open('w') as stream:
        r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,
            env={**os.environ,'DISPLAY':''},timeout=1800)
    require(r.returncode==0,f'Slicer exit {r.returncode}: {log}')


def check_paths(gcode,plate):
    roles=Counter();layers={};owner=None;owners=set();first_owners=set()
    role='Custom';width=.42;layer=-1;xyz_absolute=True;e_relative=True
    pos=dict(X=0.,Y=0.,Z=0.,E=0.);feed=0.;max_speed=0.;max_flow=0.;max_raw_flow=0.;flow_samples=[]
    min_xy=[math.inf,math.inf];max_xy=[-math.inf,-math.inf]
    num=re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):layer+=1
        elif line.startswith(';TYPE:'):role=line.split(':',1)[1].strip()
        elif line.startswith(';WIDTH:'):width=float(line.split(':',1)[1])
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
            layer_record=layers.setdefault(layer,{'z':pos['Z'],'segments':[],'widths':[]})
            layer_record['segments'].append((old['X'],old['Y'],pos['X'],pos['Y'],role))
            layer_record['widths'].append(width)
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
    support_segments=sum(n for r,n in roles.items() if 'support' in r.lower())
    require(plate['supports_enabled'] or support_segments==0,'Necekane podpory')
    require(f"G9111 bedTemp={plate['profile']['bed']} extruderTemp={plate['profile']['initial_nozzle']}" in gcode,'Jine prvni teploty')
    require(max_flow<float(plate['profile']['mvs'])+0.12,f'Prekrocen navrhovyMVS: {max_flow}')
    # Actual layer strokes with a short zoomed view, not a synthetic cross section.
    target_z=sorted(set([0.2,0.4,0.6,0.8,1.0,2.0,4.0,6.0,10.0,15.0,20.0,max_z]+[float(z) for p in plate['parts'] for z in p['critical_z_mm']]))
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
        target=[0.2,0.4,0.6,0.8,1.0,part['size_mm'][2]]+part['critical_z_mm']
        chosen_part=sorted({min(layers,key=lambda i:abs(layers[i]['z']-z)) for z in target if 0<z<=part['size_mm'][2]+0.01})
        cols=min(4,len(chosen_part));rows=math.ceil(len(chosen_part)/cols);tile=400
        detail=Image.new('RGB',(cols*tile,rows*(tile+35)+60),'#fafbfc');dd=ImageDraw.Draw(detail)
        dd.text((16,12),f"{part['name']} – skutečné dráhy",fill='#18343d',font=title)
        low=[part['placed_min_mm'][i]-4 for i in (0,1)];high=[part['placed_max_mm'][i]+4 for i in (0,1)]
        scale=(tile-35)/max(high[i]-low[i] for i in (0,1))
        for n,index in enumerate(chosen_part):
            col,row=n%cols,n//cols
            project=lambda x,y:(16+col*tile+scale*(x-low[0]),50+row*(tile+35)+scale*(high[1]-y))
            if index>0:
                for x,y,x2,y2,oldrole in layers[index-1]['segments']:
                    if all(low[i]<=v<=high[i] for pt in ((x,y),(x2,y2)) for i,v in enumerate(pt)):
                        dd.line((project(x,y),project(x2,y2)),fill='#c4cdd0',width=3)
            for x,y,x2,y2,role in layers[index]['segments']:
                if not all(low[i]<=v<=high[i] for pt in ((x,y),(x2,y2)) for i,v in enumerate(pt)):continue
                color='#51a080' if role=='Brim' or 'support' in role.lower() else '#c77239' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#303e46'
                dd.line((project(x,y),project(x2,y2)),fill=color,width=1)
            dd.text((16+col*tile,50+row*(tile+35)+tile-8),f"Vrstva {index+1}, Z {layers[index]['z']:g} mm",fill='#18343d',font=font)
        detail_path=HERE/f"detail-{plate['number']:02d}-{part['name']}-drahy.png"
        detail.save(detail_path);detail_previews.append(detail_path.name)
    mass=re.search(r'^; total filament used \[g\] = ([0-9.]+)$',gcode,re.M)
    time=re.search(r'^; estimated printing time \(normal mode\) = (.+)$',gcode,re.M)
    support_layers=[{'layer_one_based':i+1,'z_mm':l['z'],'segments':sum('support' in seg[4].lower() for seg in l['segments'])} for i,l in layers.items() if any('support' in seg[4].lower() for seg in l['segments'])]
    support_points=[pt for l in layers.values() for seg in l['segments'] if 'support' in seg[4].lower() for pt in ((seg[0],seg[1]),(seg[2],seg[3]))]
    support_bounds=([[fn(p[a] for p in support_points) for a in (0,1)] for fn in (min,max)] if support_points else None)
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
    disconnected=[];component_count=[];previous=[];previous_widths=[];prev_index={}
    previous2=[];previous2_widths=[];previous_z=None;previous2_z=None;support_gap_anchors=[]
    for i,l in layers.items():
        segments=[((x,y),(x2,y2)) for x,y,x2,y2,r in l['segments'] if r!='Brim']
        widths=[w for s,w in zip(l['segments'],l['widths']) if s[4]!='Brim']
        segment_roles=[s[4] for s in l['segments'] if s[4]!='Brim']
        search_pad=max(widths+previous_widths)+.25
        parent=list(range(len(segments)));index={}
        def root(n):
            while parent[n]!=n:parent[n]=parent[parent[n]];n=parent[n]
            return n
        anchored=[]
        for n,s in enumerate(segments):
            cells=list(bins(s,search_pad))
            for k in set(j for cell in cells for j in index.get(cell,[])):
                if distance(s,segments[k])<=(widths[n]+widths[k])/2:parent[root(n)]=root(k)
            if i>0:
                anchored.append(any(distance(s,previous[k])<=(widths[n]+previous_widths[k])/2+.25
                    for k in set(j for cell in cells for j in prev_index.get(cell,[]))))
            for cell in cells:index.setdefault(cell,[]).append(n)
        groups={}
        for n in range(len(segments)):groups.setdefault(root(n),[]).append(n)
        component_count.append(len(groups))
        if i>0:
            bad=[]
            for g in groups.values():
                if any(anchored[n] for n in g):continue
                record={'segment_count':len(g),'roles':dict(Counter(segment_roles[n] for n in g)),
                    'xy_bbox_mm':[[fun(pt[a] for n in g for pt in segments[n]) for a in range(2)] for fun in (min,max)],
                    'total_path_length_mm':sum(math.dist(*segments[n]) for n in g),
                    'minimum_previous_layer_path_distance_mm':min(distance(segments[n],old) for n in g for old in previous)}
                # A support interface deliberately starts one blank layer ABOVE a model
                # when support_bottom_z_distance = 0.2. Only support-only components
                # may use this bounded 0.4-mm layer-to-layer contact exception.
                support_only=all('support' in segment_roles[n].lower() for n in g)
                allowed_gap=bool(support_only and previous2 and previous2_z is not None
                    and l['z']-previous2_z<=0.40001
                    and any(distance(segments[n],old)<=(widths[n]+previous2_widths[k])/2+.25
                        for n in g for k,old in enumerate(previous2)))
                if allowed_gap:
                    record.update({'layer_one_based':i+1,'z_mm':l['z'],'base_layer_z_mm':previous2_z,
                        'support_only':True,'configured_bottom_z_gap_mm':.2,
                        'actual_layer_spacing_mm':round(l['z']-previous2_z,5),
                        'minimum_base_layer_path_distance_mm':min(distance(segments[n],old) for n in g for old in previous2)})
                    support_gap_anchors.append(record)
                else:bad.append(record)
            if bad:disconnected.append({'layer_one_based':i+1,'z_mm':l['z'],'islands':bad})
        previous2=previous;previous2_widths=previous_widths;previous2_z=previous_z;previous_z=l['z']
        previous=segments;previous_widths=widths;prev_index=index
        if (i+1)%25==0:print(f"Plate {plate['number']}: path connectivity {i+1}/{len(layers)} layers",flush=True)
    return {'physical_parts':plate['physical_parts'],'all_objects_on_first_layer':True,'layers':layer+1,
        'all_layers_have_extrusion':True,'maximum_extrusion_z_mm':max_z,
        'roles_segments':dict(roles),'support_segments':support_segments,'support_layers':support_layers,'support_bounds_xy_mm':support_bounds,'brim_generated':True,
        'deposition_island_test':{'method':'Actual path graph using per-stroke G-code WIDTH: same-layer connection distance <= half the sum of stroke widths; every component must contact preceding-layer strokes within half the sum of widths plus 0.25 mm allowance. Support-only components may contact the second preceding layer within 0.4 mm Z spacing, accounting for the configured 0.2 mm support bottom gap; every such exception is recorded. Does not check deposition order within a layer and does not certify full overhang support.',
            'disconnected_new_islands':disconnected,'configured_support_bottom_gap_contacts':support_gap_anchors,'passed':not disconnected,'maximum_components_per_layer':max(component_count)},
        'extrusion_min_xy_mm':min_xy,'extrusion_max_xy_mm':max_xy,
        'minimum_extrusion_edge_margin_mm':min(min_xy+[BED-v for v in max_xy]),
        'maximum_commanded_extrusion_speed_mm_s':max_speed,'maximum_commanded_volumetric_flow_mm3_s_segments_at_least_0_1mm':max_flow,
        'maximum_raw_segment_flow_mm3_s':max_raw_flow,
        'flow_quantisation_note':'XY coordinates use 0.001 mm and E uses 0.00001 mm precision; raw flow of moves below 0.1 mm is dominated by rounding. Audited flow uses segments at least 0.1 mm.',
        'preview':preview.name,'detail_previews':detail_previews,'selected_z_mm':[layers[i]['z'] for i in chosen],
        'estimated_filament_g':float(mass.group(1)) if mass else None,
        'estimated_printing_time':time.group(1) if time else None,
        'first_layer_gcode_temperature_c':{'bed':float(plate['profile']['bed']),'nozzle':float(plate['profile']['initial_nozzle'])},'physical_print_verified':False}


def arrange(parts, meshes):
    """Deterministic shelf pack; respects CAD export orientations and all copies."""
    items=[]
    n=0
    for p in parts.values():
        for copy in range(p['quantity']):
            n+=1
            items.append({'id':p['id'], 'name':f'{n:02d}_{p["id"]}_{copy+1:02d}'})
    items.sort(key=lambda x:(-meshes[x['id']]['size'][1],-meshes[x['id']]['size'][0],x['name']))
    plates=[];plate=[];x=y=EDGE;row=0.
    for item in items:
        w,h=meshes[item['id']]['size'][:2]
        if x+w>BED-EDGE+1e-6:
            x=EDGE;y+=row+GAP;row=0.
        if y+h>BED-EDGE+1e-6:
            require(plate,'Part cannot fit on bed')
            plates.append(plate);plate=[];x=y=EDGE;row=0.
        plate.append({**item,'xy':[x,y]})
        x+=w+GAP;row=max(row,h)
    if plate:plates.append(plate)
    return plates


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true')
    parser.add_argument('--only-plate',type=int)
    parser.add_argument('--reuse-slice',action='store_true',help='Reuse existing slice only after input/settings verification')
    args=parser.parse_args()
    require(SOURCE_MANIFEST.is_file(),'Missing final CAD manifest')
    source=json.loads(SOURCE_MANIFEST.read_text());source_sha=sha(SOURCE_MANIFEST)
    parts={p['id']:p for p in source['parts']}
    expected_count=sum(p['quantity'] for p in parts.values())
    require(len(parts)==len(source['parts']) and expected_count>0,'Invalid part inventory')
    meshes={}
    for name,p in parts.items():
        path=(MODEL/p['file']).resolve();require(path.is_relative_to(MODEL),'Input outside model')
        require(sha(path)==p['sha256'],'Manifest/STL SHA mismatch: '+name)
        mesh=read_mesh(path)
        require(all(abs(a-b)<.001 for a,b in zip(mesh['size'],p['bbox_mm'])),'Bounding-box mismatch: '+name)
        require('supports' in p and 'support_note' in p,'Missing reviewed support decision: '+name)
        z=mesh['size'][2]
        critical=[.2,.4,.6,.8,1,2,3,4,6,8,10,z]+p.get('critical_z_mm',[])
        mesh.update({'file':'../'+p['file'],'source_sha256':p['sha256'],
            'supports':p['supports'],'support_note':p['support_note'],
            'critical_z_mm':sorted(set(round(v,3) for v in critical if 0<v<=z+.01))})
        meshes[name]=mesh
    layouts=arrange(parts,meshes)
    plates=[];results=[]
    for number,layout in enumerate(layouts,1):
        if args.only_plate and args.only_plate!=number:continue
        plate=make_geometry(number,{'items':layout,'colour':'#334451'},meshes)
        plate.update({'colour':'#334451','material_name':'prototyp — barva návrhu',
            'profile':{'kind':'Basic','mvs':'8','nozzle':'205','initial_nozzle':'215','bed':'50'},
            'supports_enabled':any(meshes[p['id']]['supports'] for p in layout)})
        plates.append(plate)
        if args.geometry_only:continue
        process,filament=create_profiles(number,plate['colour'],plate['material_name'],plate['profile'],plate['supports_enabled'])
        work=CACHE/f'podlozka-{number:02d}';work.mkdir(parents=True,exist_ok=True)
        configured=work/'configured.3mf';sliced=work/'sliced.3mf'
        reuse=bool(args.reuse_slice and configured.exists() and sliced.exists())
        if reuse:
            try:
                project_check(configured,plate,meshes,False)
                project_check(sliced,plate,meshes,True)
            except RuntimeError as exc:
                print(f'PLATE_{number}: changed input/settings; slicing again: {exc}',flush=True)
                reuse=False
        if not reuse:
            run_cli([CLI,'--datadir',str(work/'datadir-export'),'--load-settings',f'{MACHINE};{process}',
                '--load-filaments',str(filament),'--arrange','0','--orient','0','--export-3mf',configured.name,
                '--outputdir',str(work),str(HERE/plate['geometry'])],work/'export.log')
        initial=project_check(configured,plate,meshes,False)
        if not reuse:
            run_cli([CLI,'--datadir',str(work/'datadir-slice'),'--arrange','0','--orient','0','--slice','0',
                '--export-3mf',sliced.name,'--outputdir',str(work),str(configured)],work/'slice.log')
        final=project_check(sliced,plate,meshes,True)
        print(f'PLATE_{number}_SLICED: audit real toolpaths',flush=True)
        cached_audit=work/'audit-draft.json'
        cached=json.loads(cached_audit.read_text()) if reuse and cached_audit.exists() else None
        if cached and cached.get('delivered',{}).get('gcode_sha256')==final['gcode_sha256']:
            paths=cached['toolpath_audit']
            require(paths['deposition_island_test']['passed'],'Previously failed path audit')
            require(paths['physical_parts']==plate['physical_parts'],'Changed cached object count')
            print(f'PLATE_{number}: unchanged G-code; preserving its completed path audit',flush=True)
        else:
            with ZipFile(sliced) as z:paths=check_paths(z.read('Metadata/plate_1.gcode').decode(errors='replace'),plate)
        cli_errors=sorted(set(line.split('[error]',1)[1].strip() for logfile in ('export.log','slice.log')
            for line in (work/logfile).read_text(errors='replace').splitlines() if '[error]' in line))
        result={'plate':plate,'project':f'podlozka-{number:02d}-kobra-x-pla-projekt.3mf',
            'configured':initial,'delivered':final,'toolpath_audit':paths,
            'machine_profile_sha256':sha(MACHINE),'process_sha256':sha(process),'filament_sha256':sha(filament),
            'cli_exit_codes':[0,0],'cli_error_messages':cli_errors,
            'status':'Open V holder prototype; knife fit, stability and wall anchors not physically verified',
            'physical_print_verified':False}
        write_json(work/'audit-draft.json',result)
        require(sha(SOURCE_MANIFEST)==source_sha,'CAD manifest changed during slicing')
        require(all(sha(MODEL/p['file'])==p['sha256'] for p in parts.values()),'STL changed during slicing')
        write_json(HERE/f'kontrola-podlozky-{number:02d}.json',result)
        require(paths['deposition_island_test']['passed'],'New disconnected toolpath island; inspect report')
        delivered=HERE/result['project']
        with ZipFile(sliced) as zin,ZipFile(delivered,'w',ZIP_DEFLATED) as zout:
            for name in zin.namelist():
                data=zin.read(name)
                if name=='3D/3dmodel.model':
                    data=data.decode().replace('pouze geometrie','PLA prototyp — nastavený projekt').replace(
                        'Pouze geometrie 1:1; bez procesu, filamentu a G-code. Alternativa téže podložky.',
                        'Kobra X 0,4 mm, lokálně nařezaný PLA prototyp. Fyzický fit nože, stabilita a montáž na stěnu neověřeny.').encode()
                zout.writestr(name,data)
        delivered_info=project_check(delivered,plate,meshes,True)
        require(delivered_info['gcode_sha256']==final['gcode_sha256'],'Delivery changed G-code')
        result['delivered']=delivered_info
        write_json(HERE/f'kontrola-podlozky-{number:02d}.json',result)
        results.append(result)
        print(json.dumps({'plate':number,'project':result['project'],'parts':plate['physical_parts'],
            'time':paths['estimated_printing_time'],'mass_g':paths['estimated_filament_g'],
            'supports':paths['support_segments'],'islands_passed':paths['deposition_island_test']['passed']},ensure_ascii=False),flush=True)
    write_json(HERE/'manifest.json',{'source_manifest_sha256':source_sha,'machine':'Anycubic Kobra X 0.4 nozzle','physical_parts':sum(p['physical_parts'] for p in plates),'plates':plates})
    if not args.geometry_only and not args.only_plate:
        require(sum(p['physical_parts'] for p in plates)==expected_count,'Missing physical parts')
        write_json(HERE/'kontrola-rezani.json',{'revision':source.get('revision','01'),'source_manifest_sha256':source_sha,'physical_parts':expected_count,'plates':results,'printer_io':False,'physical_print_verified':False})
        rows=[]
        for r in results:
            rows.append(f"| {r['plate']['number']:02d} | [{r['project']}]({r['project']}) | {r['plate']['physical_parts']} | {r['toolpath_audit']['estimated_printing_time']} | {r['toolpath_audit']['estimated_filament_g']:.2f} g |")
        warnings=sorted(set(x.get('msg','') for r in results for x in r['delivered']['warnings']))
        errors=sorted(set(x for r in results for x in r['cli_error_messages']))
        text='''# Kobra X — otevřený V držák nože, revize 02

**Návrhový tiskový prototyp. Skutečný fit nože, stabilita uložení, pevnost a kotvy ve stěně nejsou fyzicky ověřeny.**

Každou podložku otevřít jako celý projekt právě jednou. Obsahuje všechny fyzické kopie; nepřerovnávat ani nenásobit.

| Podložka | Projekt | Kusy | Čas sliceru | Materiál sliceru |
|---|---|---:|---|---:|
'''+ '\n'.join(rows)+'\n\nCelkový počet tištěných dílů: **'+str(expected_count)+'**. Přesný seznam, orientace a digitální rozměry dílů jsou v [manifestu](manifest.json) a [CAD manifestu](../print-manifest.json).\n\n'
        text+='''## Proces a podpory

Kobra X 0,4 mm; vrstva 0,20 mm; 4 stěny; 15 % gyroid; 5 horních/dolních vrstev. Vnější stěny 40, vnitřní 70, první vrstva 25 mm/s. Návrhový nekalibrovaný PLA Basic: první vrstva 215 °C, další 205 °C; texturovaná podložka 50 °C; maximální průtok 8 mm³/s. Vnější brim 3 mm, čisticí věž vypnutá. Barva je pouze vizualizace, nepotvrzuje skutečnou cívku.

'''
        for r in results:
            pl=r['plate'];num=pl['number']
            text+=f"Podložka {num:02d}: "+('automatické přiléhající podpory `normal(auto) / snug`, i na modelu, práh 30°, horní/dolní mezera 0,20 mm, XY odstup 0,35 mm, dvě kontaktní vrstvy. ' if pl['supports_enabled'] else 'podpory vypnuté; tisková orientace z CAD exportu se spodní patkou dolů. ')+f"Skutečně v G-code: {r['toolpath_audit']['support_segments']} segmentů podpor.\n\n"
            for p in pl['parts']:text+=f"- {p['name']}: {p['support_note']}\n"
            text+='\n'
        text+='''Brim je pro přilnavost a nenahrazuje podporu převisů. Montážní otvory a dosedací plochy před montáží zbavit brimu a otřepů.

## Digitální kontrola

Ověřeny jednotky, měřítko, orientace, počty, rozměry a skutečné vrcholy geometrie po importu i řezu; počet oprav sítě 0. Všechny objekty mají dráhy v první vrstvě a všechny vrstvy obsahují extruzi. Ověřena obálka extruzí na podložce, G-code teploty, maximální průtok a graf nových ostrovů podle skutečných šířek extruze. Graf ověřuje návaznost komponent, nikoli pořadí uvnitř vrstvy ani úplnou fyzickou podporu každého převisu. Podpory jsou v tomto projektu vypnuté; graf nepoužil žádnou výjimku kontaktu přes podporovou mezeru.

'''
        for r in results:
            n=r['plate']['number']
            text+=f"Podložka {n:02d}: [očíslovaný náhled](podlozka-{n:02d}.png), [skutečné dráhy](podlozka-{n:02d}-vrstvy.png).\n\n"
        text+='Podrobné vrstvy jednotlivých dílů jsou v souborech `detail-*-drahy.png`. [Kontrolní protokol](kontrola-rezani.json). [Záznam vizuální kontroly](kontrola-drah-vizualne.md). Detaily skutečných mostků u otvorů: [otvor 01](detail-otvor-01-mostky.png), [otvor 02](detail-otvor-02-mostky.png), [datová kontrola](kontrola-mostku.json).\n\n'
        text+=f"Uložená varování sliceru: {', '.join(warnings) if warnings else 'žádná'}. CLI hlášky: {'; '.join(errors) if errors else 'žádné'}. Neoznačovat řez za bezvarovný, pokud CLI hlášku obsahuje.\n\n"
        text+='''Geometrické 3MF jsou alternativy stejných podložek bez procesu; nepřidávají díly k sestavě. Výsledky jsou pouze kontrola digitálních souborů. Tisk, odstranění případných podpor, přesný fit nože, stabilita uložení, kotvy ve stěně a pevnost nejsou fyzicky ověřeny. Tiskárna nebyla ovládána.

Regenerace: po finálním exportu CAD spustit `python3 ../build_print_projects.py` ze složky rozložení. Přepíše pouze vlastní podložky, profily, náhledy a kontrolní soubory v této složce. `--reuse-slice` znovu ověří uložené řezy proti aktuálním zdrojům a profilům; nově řeže jen chybějící nebo změněnou podložku. U nezměněného SHA G-code zachová již dokončený audit drah.
'''
        (HERE/'README.md').write_text(text)
        subprocess.run(['python3',str(HERE/'inspect_bridges.py')],check=True)
        print('OPEN_V_PRINT_PROJECT_OK',flush=True)


if __name__=='__main__':main()
