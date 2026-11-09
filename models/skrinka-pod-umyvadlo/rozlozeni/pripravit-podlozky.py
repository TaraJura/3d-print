#!/usr/bin/env python3
"""Reprodukovatelné podložky skříňky, lokální řezání a kontrola skutečných drah.

Čte ../dily.json: parts=[{id,file,count,supports,support_note}]. STL již musí
mít určenou tiskovou orientaci. Zapisuje jen do této složky a ignorované
.cache/ uvnitř této složky. Žádná komunikace s tiskárnou ani tisk.
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
MANIFEST = MODEL / 'dily.json'
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


def inventory():
    data = json.loads(MANIFEST.read_text())
    parts = data['parts'] if isinstance(data, dict) else data
    require(parts and len({p['id'] for p in parts}) == len(parts), 'Duplicitní/žádné typy')
    meshes, copies = {}, []
    for part in parts:
        require(isinstance(part['count'], int) and part['count'] > 0, 'Neplatný počet')
        require(isinstance(part.get('supports'), bool), f'Chybí rozhodnutí podpor: {part["id"]}')
        require(part.get('support_note'), f'Chybí zdůvodnění podpor: {part["id"]}')
        path = (MODEL / part['file']).resolve()
        require(MODEL.resolve() in path.parents, 'STL musí být uvnitř složky modelu')
        mesh = read_mesh(path)
        mesh.update({'file': part['file'], 'source_sha256': sha(path),
                     'supports': part['supports'], 'support_note': part['support_note'].replace('brim zajistí přilnavost','brim pomáhá přilnavosti'),
                     'critical_z_mm': part.get('critical_z_mm', [])})
        # Actual hinge-axis and 45° roof heights of this cabinet revision.
        # Read as additional layer selections; geometry remains source-authoritative.
        if part['id']=='bok-segment':
            mesh['critical_z_mm']=sorted(set(mesh['critical_z_mm']+[4.2,14,16,17.2,18.4]))
        elif part['id'].startswith('dvere-'):
            mesh['critical_z_mm']=sorted(set(mesh['critical_z_mm']+[4.2,8,10,11.2,12.2]))
        meshes[part['id']] = mesh
        for number in range(1, part['count']+1):
            copies.append({'id': part['id'], 'name': f'{part["id"]}-{number:02d}',
                           'size': mesh['size']})
    return parts, meshes, copies


def pack(copies):
    plates = []
    for item in sorted(copies, key=lambda p: p['size'][0]*p['size'][1], reverse=True):
        width, depth = item['size'][:2]
        placed = False
        for plate in plates:
            for row in plate['rows']:
                if depth <= row['depth'] and row['x']+width <= BED-EDGE:
                    record = {**item, 'xy': [row['x'], row['y']]}
                    plate['items'].append(record)
                    row['x'] += width+GAP
                    placed = True
                    break
            if placed:
                break
            top = max(r['y']+r['depth'] for r in plate['rows'])+GAP
            if top+depth <= BED-EDGE:
                plate['rows'].append({'x': EDGE+width+GAP, 'y': top, 'depth': depth})
                plate['items'].append({**item, 'xy': [EDGE, top]})
                placed = True
                break
        if not placed:
            plates.append({'rows': [{'x': EDGE+width+GAP, 'y': EDGE, 'depth': depth}],
                           'items': [{**item, 'xy': [EDGE, EDGE]}]})
    for plate in plates:
        items = plate['items']
        high = [max(p['xy'][i]+p['size'][i] for p in items) for i in range(2)]
        offset = [(BED-high[i]-EDGE)/2 for i in range(2)]
        for p in items:
            p['xy'] = [p['xy'][i]+offset[i] for i in range(2)]
    return plates


def make_geometry(number, plate, meshes):
    stem = f'podlozka-{number:02d}'
    path = HERE / f'{stem}-geometrie.3mf'
    model = ET.Element(f'{{{NS}}}model', unit='millimeter')
    ET.SubElement(model, 'metadata', name='Title').text = f'Skříňka pod umyvadlo – {stem}, pouze geometrie'
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
            draw.polygon([xy(p[0]+t[0],p[1]+t[1]) for p in points], fill=(tone,tone+3,tone+5))
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
    draw.text((65,1020), f'{len(records)} fyzických dílů · skutečná STL · 1:1', fill='#263f49', font=font)
    for row,text in enumerate(textwrap.wrap(summary,width=85)):
        draw.text((65,1052+24*row), text, fill='#536871', font=font)
    canvas.save(HERE/f'podlozka-{number:02d}.png')


def create_profiles(supports):
    process = json.loads(PROCESS.read_text())
    process.update({'name': 'Skrinka 0.20 mm cerne PLA navrh Kobra X',
                    'print_settings_id': 'Skrinka 0.20 mm cerne PLA navrh Kobra X',
                    'layer_height': '0.2', 'wall_loops': '4', 'sparse_infill_density': '25%',
                    'sparse_infill_pattern': 'gyroid', 'brim_type': 'outer_only',
                    'brim_width': '5', 'brim_object_gap': '0.1', 'enable_support': '1' if supports else '0',
                    'support_type': 'normal(auto)', 'support_style': 'snug',
                    'support_on_build_plate_only': '0', 'support_object_xy_distance': '0.35',
                    'initial_layer_speed': '25', 'initial_layer_infill_speed': '40',
                    'outer_wall_speed': '50', 'inner_wall_speed': '75', 'top_surface_speed': '50',
                    'sparse_infill_speed': '75', 'internal_solid_infill_speed': '75',
                    'gap_infill_speed': '50', 'default_acceleration': '1000',
                    'outer_wall_acceleration': '500', 'inner_wall_acceleration': '800',
                    'top_surface_acceleration': '500', 'print_sequence': 'by layer',
                    'enable_prime_tower': '0'})
    filament = json.loads(FILAMENT.read_text())
    name = 'NAVRH Alzament PLA Basic cerna @Kobra X 0.4'
    filament.update({'name': name, 'setting_id': name,
                     'filament_settings_id': [name], 'filament_vendor': ['Alzament'],
                     'filament_colour': ['#17191B'], 'default_filament_colour': ['#17191B'],
                     'filament_notes': ['Navrhovy profil; bez fyzicke kalibrace; overit skutecnou cernou civku.']})
    for key,value in {'nozzle_temperature':'205','nozzle_temperature_initial_layer':'215',
                      'nozzle_temperature_BRASS':'205','nozzle_temperature_HS':'205',
                      'nozzle_temperature_initial_layer_BRASS':'215','nozzle_temperature_initial_layer_HS':'215',
                      'hot_plate_temp':'50','hot_plate_temp_initial_layer':'50',
                      'textured_plate_temp':'50','textured_plate_temp_initial_layer':'50'}.items():
        filament[key] = [value]
    process_path = HERE / ('proces-kobra-x-pla-podpory.json' if supports else 'proces-kobra-x-pla.json')
    filament_path = HERE / 'filament-cerna-pla-navrh.json'
    write_json(process_path, process)
    write_json(filament_path, filament)
    return process_path, filament_path


def run_cli(command, log):
    with log.open('w') as stream:
        r = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                           env={**os.environ,'DISPLAY':''}, timeout=1800)
    require(r.returncode == 0, f'Slicer exit {r.returncode}: {log}')


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
        require(cfg['brim_type'] == 'outer_only' and float(cfg['brim_width']) == 5, 'Chybí brim')
        require(cfg['filament_colour'] == ['#17191B'], 'Změněná barva profilu')
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
                'settings':{k:cfg.get(k) for k in ('printer_model','printer_settings_id','print_settings_id','filament_settings_id','nozzle_diameter','layer_height','wall_loops','sparse_infill_density','sparse_infill_pattern','enable_support','support_on_build_plate_only','brim_type','brim_width','nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','outer_wall_speed','inner_wall_speed','filament_colour')},
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


def slice_plate(plate, meshes):
    stem=f'podlozka-{plate["number"]:02d}'
    work=CACHE/stem
    work.mkdir(parents=True,exist_ok=True)
    supports={p['supports'] for p in plate['parts']}
    # Separate support-bearing parts from unsupported parts when packing is used.
    require(len(supports)==1, 'Smíšené podpory na podložce: rozdělit podložku podle potřeby podpor')
    process,filament=create_profiles(True in supports)
    configured=work/'configured.3mf'
    run_cli([CLI,'--datadir',str(work/'datadir-export'),'--load-settings',f'{MACHINE};{process}',
             '--load-filaments',str(filament),'--arrange','0','--orient','0',
             '--export-3mf',configured.name,'--outputdir',str(work),str(HERE/plate['geometry'])],work/'export.log')
    configured_info=project_check(configured,plate,meshes,False)
    run_cli([CLI,'--datadir',str(work/'datadir-slice'),'--arrange','0','--orient','0','--slice','0',
             '--export-3mf','sliced.3mf','--outputdir',str(work),str(configured)],work/'slice.log')
    sliced=work/'sliced.3mf'
    sliced_info=project_check(sliced,plate,meshes,True)
    delivered=HERE/f'{stem}-kobra-x-cerny-pla-projekt.3mf'
    with ZipFile(sliced) as source,ZipFile(delivered,'w',ZIP_DEFLATED) as output:
        for name in source.namelist():
            content=source.read(name)
            if name=='3D/3dmodel.model':
                text=content.decode().replace('pouze geometrie','nastavený a lokálně nařezaný projekt')
                text=text.replace('Pouze geometrie 1:1; bez procesu, filamentu a G-code. Alternativa téže podložky.',
                                  'Kobra X 0,4 mm; černý PLA, návrhový profil. Fyzický tisk, montáž a uchycení neověřeny.')
                content=text.encode()
            output.writestr(name,content)
    final=project_check(delivered,plate,meshes,True)
    require(final['gcode_sha256']==sliced_info['gcode_sha256'],'Předání změnilo G-code')
    with ZipFile(delivered) as z:
        paths=check_paths(z.read('Metadata/plate_1.gcode').decode(errors='replace'),plate)
    log_messages=sorted(set(line.split('[error]',1)[1].strip() for name in ('export.log','slice.log')
                            for line in (work/name).read_text(errors='replace').splitlines()
                            if '[error]' in line))
    return {**plate,'project':delivered.name,'process_sha256':sha(process),'filament_sha256':sha(filament),
            'configured':configured_info,'delivered':final,'toolpath_audit':paths,
            'cli_exit_codes':[0,0],'cli_error_messages':log_messages,
            'status':'Nastaveno a lokálně nařezáno; skutečné dráhy zkontrolovány; fyzický tisk neověřen'}


def check_paths(gcode,plate):
    number=plate['number']
    # First, feature-level and upper layers, selected from actual maximum height.
    max_height=max(p['size_mm'][2] for p in plate['parts'])
    targets=[0.2,round(max_height/2/0.2)*0.2,round((max_height-0.1)/0.2)*0.2]
    targets.extend(z for p in plate['parts'] for z in p.get('critical_z_mm',[]))
    target_z=sorted(set(round(max(0.2,round(z/0.2)*0.2),1) for z in targets if z <= max_height))
    segments={z:[] for z in target_z}
    layer=-1;role='Custom';owner=None;xyz_absolute=True;e_relative=True
    pos=dict(X=0.0,Y=0.0,Z=0.0,E=0.0)
    roles=Counter();layers=Counter();owners=set();first_owners=set()
    min_xy=[math.inf,math.inf];max_xy=[-math.inf,-math.inf];max_z=0.0
    num=re.compile(r'([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    support_layers=Counter();bridge_layers=Counter()
    maximum_bridge_segment=0.0;maximum_external_bridge_segment=0.0
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'): layer+=1
        elif line.startswith(';TYPE:'): role=line.split(':',1)[1].strip()
        elif line.startswith('EXCLUDE_OBJECT_START NAME='):
            owner=line.split('NAME=',1)[1];owners.add(owner)
        elif line.startswith('EXCLUDE_OBJECT_END'):owner=None
        command=line.split(';',1)[0].strip()
        if not command: continue
        kind=command.split()[0];values={a:float(v) for a,v in num.findall(command)}
        if kind=='G90':xyz_absolute=True
        elif kind=='G91':xyz_absolute=False
        elif kind=='M83':e_relative=True
        elif kind=='M82':e_relative=False
        elif kind=='G92':pos.update(values)
        elif kind in ('G0','G1'):
            old=pos.copy()
            for axis in 'XYZ':
                if axis in values:pos[axis]=values[axis] if xyz_absolute else pos[axis]+values[axis]
            extrusion=values.get('E',0) if e_relative else values.get('E',pos['E'])-pos['E']
            if 'E' in values:pos['E']=pos['E']+values['E'] if e_relative else values['E']
            if extrusion<=0 or (old['X'],old['Y'])==(pos['X'],pos['Y']) or role=='Custom':continue
            require(owner is not None and layer>=0,'Extruze modelu mimo objekt/vrstvu')
            roles[role]+=1;layers[layer]+=1;max_z=max(max_z,pos['Z'])
            if layer==0:first_owners.add(owner)
            if 'support' in role.lower():support_layers[layer]+=1
            if 'bridge' in role.lower() or 'overhang' in role.lower():bridge_layers[layer]+=1
            if 'bridge' in role.lower():
                maximum_bridge_segment=max(maximum_bridge_segment,math.hypot(old['X']-pos['X'],old['Y']-pos['Y']))
                if 'internal' not in role.lower():
                    maximum_external_bridge_segment=max(maximum_external_bridge_segment,math.hypot(old['X']-pos['X'],old['Y']-pos['Y']))
            for xy in ((old['X'],old['Y']),(pos['X'],pos['Y'])):
                require(all(0<v<BED for v in xy),f'Dráha mimo podložku: {xy}')
                min_xy=[min(min_xy[i],xy[i]) for i in range(2)]
                max_xy=[max(max_xy[i],xy[i]) for i in range(2)]
            for z in target_z:
                if abs(pos['Z']-z)<0.101:segments[z].append((old['X'],old['Y'],pos['X'],pos['Y'],role))
        elif kind in ('G2','G3') and values.get('E',0)>0:raise RuntimeError('Nezpracovaná oblouková extruze')
    require(len(owners)==plate['physical_parts'],'G-code má jiný počet objektů')
    require(first_owners==owners,'Některý díl nemá kontakt s první vrstvou')
    require(set(layers)==set(range(layer+1)),'Vrstva bez extruze')
    require(abs(max_z-max_height)<0.21,f'Výška drah {max_z} nesouhlasí s modelem {max_height}')
    require(roles['Brim']>0,'Chybí skutečný brim')
    require(bool(support_layers)==any(p['supports'] for p in plate['parts']),'Rozhodnutí podpor nesouhlasí s drahami')
    require('G9111 bedTemp=50 extruderTemp=215' in gcode,'Start G-code má jiné první teploty')
    preview=HERE/f'podlozka-{number:02d}-vrstvy.png'
    columns=min(4,len(target_z));rows=math.ceil(len(target_z)/columns)
    canvas=Image.new('RGB',(columns*540,rows*590+110),'#fafbfc');draw=ImageDraw.Draw(canvas)
    title,font=ImageFont.truetype(FONT,25),ImageFont.truetype(FONT,18)
    draw.text((25,15),f'Podložka {number:02d} · skutečné dráhy z předávaného G-code',fill='#18343d',font=title)
    for index,z in enumerate(target_z):
        column,row=index%columns,index//columns
        xy=lambda x,y: (25+540*column+1.85*x,70+590*row+1.85*(BED-y))
        draw.rectangle((xy(0,BED),xy(BED,0)),fill='#e8edef',outline='#55717b',width=2)
        require(segments[z],f'Prázdný náhled vybrané vrstvy {z}')
        for x,y,x2,y2,r in segments[z]:
            color='#55a483' if 'support' in r.lower() or r=='Brim' else '#c77239' if 'bridge' in r.lower() or 'overhang' in r.lower() else '#263c45'
            draw.line((xy(x,y),xy(x2,y2)),fill=color,width=1)
        draw.text((25+540*column,566+590*row),f'Z ≈ {z:g} mm',fill='#18343d',font=font)
    draw.text((25,canvas.height-35),'Tmavě model · zeleně brim/podpory · oranžově most/převis',fill='#536871',font=font)
    canvas.save(preview)
    weight=re.search(r'^; total filament used \[g\] = ([0-9.]+)$',gcode,re.M)
    time=re.search(r'^; estimated printing time \(normal mode\) = (.+)$',gcode,re.M)
    return {'physical_parts':len(owners),'all_objects_on_first_layer':True,'layers':layer+1,
            'all_layers_have_extrusion':True,'maximum_extrusion_z_mm':max_z,'roles_segments':dict(roles),
            'support_segments':sum(support_layers.values()),'bridge_overhang_segments':sum(bridge_layers.values()),
            'maximum_bridge_extrusion_segment_mm':maximum_bridge_segment,
            'maximum_external_bridge_extrusion_segment_mm':maximum_external_bridge_segment,
            'internal_bridge_note':'Internal Bridge crosses sparse infill; segment length is not unsupported free span.',
            'support_layer_range':[min(support_layers),max(support_layers)] if support_layers else None,
            'bridge_layer_range':[min(bridge_layers),max(bridge_layers)] if bridge_layers else None,
            'extrusion_min_xy_mm':min_xy,'extrusion_max_xy_mm':max_xy,
            'minimum_extrusion_edge_margin_mm':min(min_xy+[BED-v for v in max_xy]),
            'preview':preview.name,'selected_z_mm':target_z,
            'estimated_filament_g':float(weight.group(1)) if weight else None,
            'estimated_printing_time':time.group(1) if time else None,
            'first_layer_gcode_temperature_c':{'bed':50,'nozzle':215},
            'physical_print_fit_support_removal':'Neověřeno'}


def write_documentation(result):
    sliced='delivered' in result['plates'][0]
    lines=['# Připravené tiskové podložky skříňky','',
           f"**{len(result['plates'])} podložek / {result['physical_parts']} skutečných fyzických dílů.** "
           'Každý nastavený projekt otevřít samostatně jednou jako celý projekt v Anycubic Slicer Next. '
           'Všechny kopie jsou již vložené; nerozmísťovat automaticky ani nenásobit počty.','',
           'Tiskárna: **Anycubic Kobra X, tryska 0,4 mm, plocha 260 × 260 mm**. '
           'Návrhový profil pro černý Alzament PLA Basic: vrstva 0,20 mm, 4 stěny, '
           '25 % gyroid, 5mm vnější brim. Tryska 215 °C první / 205 °C další vrstvy, '
           'texturovaná podložka 50 °C. První vrstva 25 mm/s, vnější stěny 50 mm/s, '
           'vnitřní stěny a výplň 75 mm/s. Jde o počáteční nastavení, nikoli fyzicky '
           'kalibrovaný profil. Ověřit skutečnou černou cívku a její přiřazení.','',
           'Podložka 50 °C byla zvolena po prvním místním řezu s 60 °C: ten hlásil '
           '`bed_temperature_too_high_than_filament`, protože profil Anycubic PLA dědí '
           '`temperature_vitrification=54 °C`. Hodnota 50 °C je uvnitř dokumentovaného '
           'dodavatelského rozsahu 45–60 °C. Všechny předávané projekty a G-code '
           'byly následně vytvořeny se stejnými 50 °C; materiálová kalibrace je neověřená.','',
           '| Podložka | Nastavený projekt | Kusy | Díly | Odhad PLA | Odhad času |',
           '|---|---|---:|---|---:|---|']
    total_mass,total_seconds=0.0,0
    warnings=[]
    for p in result['plates']:
        number=p['number'];summary=', '.join(f'{n}× {k}' for k,n in Counter(a['id'] for a in p['parts']).items())
        project=f'[{p["project"]}]({p["project"]})' if sliced else 'Řezání dosud neověřeno'
        mass=p.get('toolpath_audit',{}).get('estimated_filament_g')
        time=p.get('toolpath_audit',{}).get('estimated_printing_time')
        total_mass+=mass or 0
        seconds=int(p.get('delivered',{}).get('slice_metadata',{}).get('prediction','0'))
        total_seconds+=seconds
        mass_text=f'{mass:.2f} g' if mass is not None else '—'
        lines.append(f'| [{number:02d}](podlozka-{number:02d}.png) | {project} | {p["physical_parts"]} | {summary} | {mass_text} | {time or "—"} |')
        warnings.extend(p.get('delivered',{}).get('warnings',[]))
    lines.extend(['','## Počty dílů','',
                  *[f'- `{k}`: **{n} {"kus" if n==1 else "kusy" if 2<=n<=4 else "kusů"}**.' for k,n in result['type_counts'].items()],'',
                  'Soupis jednotlivých očíslovaných kopií, zdrojové STL, jejich hashe, '
                  'umístění a počty jsou v [manifest.json](manifest.json).','',
                  '## Tisková orientace a podpory',''])
    types={p['id']:p for plate in result['plates'] for p in plate['parts']}
    for key,p in types.items():
        note=p['support_note'].replace('brim zajistí přilnavost','brim pomáhá přilnavosti')
        lines.append(f'- `{key}` — {note} Podpory {"zapnuté" if p["supports"] else "vypnuté"}.')
    lines.extend(['','Brim zlepšuje přilnavost, nepodpírá převisy. Odstranitelnost brimů, '
                  'tisk malých otvorů a mechanická funkce pantů/čepů čekají na fyzickou zkoušku.','',
                  '## Provedené kontroly',''])
    if sliced:
        lines.extend([f'Lokální řezání všech {len(result["plates"])} podložek proběhlo v Anycubic '
                      'Slicer Next. Nastavené projekty obsahují skutečný G-code. Po exportu i řezu '
                      'byla ověřena jednotka mm, měřítko 1:1, zachované vrcholy/rozměry/umístění, '
                      'správné počty a nulové opravy sítí. Z G-code byla ověřena první vrstva '
                      'každého objektu, extruze ve všech vrstvách, celková výška, brim, podpory '
                      'a skutečné dráhy uvnitř podložky.','',
                      f'Celkový odhad sliceru: **{total_mass:.2f} g PLA / {total_seconds//3600} h '
                      f'{(total_seconds%3600)//60} min**. Jde o odhad, nikoli skutečnou spotřebu či čas.','',
                      'Podrobnosti a hashe jsou v [kontrola-rezani.json](kontrola-rezani.json). '
                      'Obrázky `podlozka-NN-vrstvy.png` zobrazují skutečné extruzní dráhy z '
                      'předávaných projektů v první, horní a vybraných kritických vrstvách.',''])
        if warnings:
            unique=sorted({w.get('msg','') for w in warnings})
            lines.append('Slicer zaznamenal tato informační varování: '+', '.join(f'`{w}`' for w in unique)+'. '
                         'Varování `not_support_traditional_timelapse` se týká režimu časosběru. '
                         'Slicer nehlásí přesah podložky; opravy sítí jsou nulové.')
        log_messages=sorted({s for p in result['plates'] for s in p.get('cli_error_messages',[])})
        if log_messages:
            lines.extend(['','CLI log zaznamenal '+', '.join(f'`{s}`' for s in log_messages)+'. '
                          'Řezání přesto skončilo s exit 0; ověřené jsou geometrii zachovávající '
                          'projekty a extruzní dráhy. Funkce vynechávání jednotlivých objektů '
                          'během fyzického tisku nebyla zkoušena.'])
    else:
        lines.append('Podložky zatím obsahují pouze geometrii. Profil, podpory a řezání čekají na ověření.')
    lines.extend(['','Fyzický tisk, montáž, rozměrový fit a dlouhodobá funkce nejsou ověřené. '
                  'Žádná tisková úloha nebyla odeslána ani spuštěna.','',
                  '## Alternativa a regenerace','',
                  'Soubory `podlozka-NN-geometrie.3mf` jsou alternativy se stejnými díly '
                  'a bez procesu/filamentu/G-code. **Netisknout navíc k nastaveným projektům**. '
                  'Pro přímé použití jsou určeny nastavené projekty z tabulky.','',
                  'Po aktualizaci `../dily.json` a odpovídajících tiskově orientovaných STL spustit '
                  '`python3 pripravit-podlozky.py` v této složce. Generátor přepíše zdejší '
                  'podložky/náhledy/kontroly/profily a do `.cache/` uloží místní logy a dočasné '
                  'datadir; nemění uživatelské globální presety a nekontaktuje tiskárnu.',''])
    lines.extend(['Pro změnu pouze vybraných podložek použít například '
                  '`python3 pripravit-podlozky.py --plates 1,2,3,4,5,6`. U všech zachovaných '
                  'podložek generátor vyžaduje přesné shodné source hash, obsazení, rozmístění '
                  'a vazbu geometrie na hotový projekt; jejich G-code se znovu nevytváří.',''])
    (HERE/'README.md').write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true')
    parser.add_argument('--plates',help='Jen určené podložky, např. 1,2,3; ostatní musí zůstat shodné')
    args=parser.parse_args()
    parts,meshes,copies=inventory()
    # Support-bearing parts are packed separately so global supports do not affect all parts.
    plates=pack([p for p in copies if not meshes[p['id']]['supports']])+pack([p for p in copies if meshes[p['id']]['supports']])
    selection=set(map(int,args.plates.split(','))) if args.plates else set(range(1,len(plates)+1))
    require(selection and selection<=set(range(1,len(plates)+1)),'Neplatný výběr podložek')
    previous_manifest=json.loads((HERE/'manifest.json').read_text()) if args.plates else None
    previous_slice=json.loads((HERE/'kontrola-rezani.json').read_text()) if args.plates and not args.geometry_only else None
    layout=[]
    for number,packed in enumerate(plates,1):
        if number in selection:
            layout.append(make_geometry(number,packed,meshes))
        else:
            require(previous_manifest is not None,'Chybí předchozí manifest')
            previous=next(p for p in previous_manifest['plates'] if p['number']==number)
            require([p['name'] for p in packed['items']]==[p['name'] for p in previous['parts']],
                    f'Podložka {number} změnila obsazení; přidat do --plates')
            for item,record in zip(packed['items'],previous['parts']):
                mesh=meshes[item['id']]
                require(mesh['source_sha256']==record['source_sha256'],
                        f'Podložka {number} změnila geometrii; přidat do --plates')
                require(all(abs(item['xy'][i]-record['placed_min_mm'][i])<0.001 for i in range(2)),
                        f'Podložka {number} změnila rozmístění; přidat do --plates')
            require(sha(HERE/previous['geometry'])==previous['geometry_sha256'],
                    f'Změněný existující 3MF podložky {number}')
            layout.append(previous)
    expected=Counter({p['id']:p['count'] for p in parts})
    actual=Counter(p['id'] for plate in layout for p in plate['parts'])
    require(actual==expected,'Podložky neodpovídají kusovníku')
    result={'source_manifest_sha256':sha(MANIFEST),'machine':'Anycubic Kobra X 0.4 nozzle',
            'bed_mm':[BED,BED,BED],'physical_parts':len(copies),'type_counts':dict(expected),
            'plates':layout,'physical_print_verified':False}
    write_json(HERE/'manifest.json',result)
    if not args.geometry_only:
        result['machine_profile_sha256']=sha(MACHINE)
        final=[]
        for plate in layout:
            if plate['number'] in selection:
                final.append(slice_plate(plate,meshes))
            else:
                require(previous_slice is not None,'Chybí původní audit řezu')
                old=next(p for p in previous_slice['plates'] if p['number']==plate['number'])
                require(sha(HERE/old['project'])==old['delivered']['sha256'],'Změněný zachovaný projekt')
                require(old['geometry_sha256']==plate['geometry_sha256'],'Projekt neodpovídá zachované geometrii')
                final.append(old)
        result['plates']=final
        write_json(HERE/'kontrola-rezani.json',result)
    write_documentation(result)
    print(json.dumps({'plates':len(layout),'parts':len(copies),'sliced':not args.geometry_only},ensure_ascii=False))


if __name__=='__main__':
    main()
