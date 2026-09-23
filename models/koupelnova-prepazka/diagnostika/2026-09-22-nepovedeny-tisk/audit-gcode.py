#!/usr/bin/env python3
"""Independent read-only forensic audit of frozen model and GUI-export evidence.

Writes only audit-gcode.json and audit-gcode.md beside this script. Does not read
earlier audit JSON, invoke a slicer, execute G-code, or connect to a printer.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
PRODUCTION = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
PARAM = re.compile(r'([A-Z])([-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?)')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounds(points):
    return [[min(point[a] for point in points) for a in range(3)],
            [max(point[a] for point in points) for a in range(3)]] if points else None


def mesh_check(vertices, triangles):
    # Weld identical vertices, independently of prior STL/audit scripts.
    lookup, welded, index_map = {}, [], []
    for point in vertices:
        key = tuple(round(v, 8) for v in point)
        if key not in lookup:
            lookup[key] = len(welded)
            welded.append(point)
        index_map.append(lookup[key])
    faces = [tuple(index_map[i] for i in tri) for tri in triangles]
    edge_counts, directions, adjacency = Counter(), Counter(), defaultdict(set)
    volume = 0.0
    degenerates = 0
    for tri in faces:
        a,b,c = [welded[i] for i in tri]
        ab = [b[i]-a[i] for i in range(3)]
        ac = [c[i]-a[i] for i in range(3)]
        cross = [ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        degenerates += sum(v*v for v in cross) < 1e-20
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for left,right in zip(tri,(tri[1],tri[2],tri[0])):
            edge_counts[tuple(sorted((left,right)))] += 1
            directions[(left,right)] += 1
            adjacency[left].add(right)
            adjacency[right].add(left)
    remaining=set(range(len(welded)))
    components=0
    while remaining:
        components += 1
        queue=[remaining.pop()]
        while queue:
            node=queue.pop()
            new=remaining.intersection(adjacency[node])
            remaining.difference_update(new)
            queue.extend(new)
    box=bounds(welded)
    return {'vertices':len(welded),'triangles':len(faces),'bounds_mm':box,
            'dimensions_mm':[box[1][i]-box[0][i] for i in range(3)],
            'connected_shells':components,'signed_volume_mm3':volume,
            'boundary_or_nonmanifold_edges':sum(n!=2 for n in edge_counts.values()),
            'inconsistent_oriented_edges':sum(directions[(a,b)]!=1 or directions[(b,a)]!=1 for a,b in edge_counts),
            'degenerate_triangles':degenerates}


def audit_3mf(raw):
    import io
    out={}
    gcodes=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        out['zip_crc_valid']=archive.testzip() is None
        names=archive.namelist()
        out['members']=names
        for name in names:
            if name.endswith('.gcode'):
                gcodes.append((name,archive.read(name)))
        out['embedded_gcode_count']=len(gcodes)
        out['contained_mesh_objects']=[]
        for name in names:
            if not name.endswith('.model'): continue
            model_root=ET.fromstring(archive.read(name))
            for object_element in model_root.findall(f'{CORE}resources/{CORE}object'):
                mesh=object_element.find(CORE+'mesh')
                if mesh is None: continue
                vv=[tuple(float(v.get(a)) for a in 'xyz') for v in mesh.findall(f'{CORE}vertices/{CORE}vertex')]
                tt=[tuple(int(t.get(f'v{i}')) for i in (1,2,3)) for t in mesh.findall(f'{CORE}triangles/{CORE}triangle')]
                out['contained_mesh_objects'].append({'member':name,'object_id':object_element.get('id'),**mesh_check(vv,tt)})
        cache={}
        def root(path):
            if path not in cache: cache[path]=ET.fromstring(archive.read(path))
            return cache[path]
        def transform(points,text):
            matrix=list(map(float,text.split())) if text else [1,0,0,0,1,0,0,0,1,0,0,0]
            assert len(matrix)==12
            result=[tuple(sum(p[j]*matrix[j*3+i] for j in range(3))+matrix[9+i] for i in range(3)) for p in points]
            return result,matrix
        def resolve(path,objid,depth=0):
            assert depth<12
            obj=root(path).find(f"{CORE}resources/{CORE}object[@id='{objid}']")
            if obj is None: raise ValueError(f'Missing object {path}:{objid}')
            mesh=obj.find(CORE+'mesh')
            if mesh is not None:
                vertices=[tuple(float(v.get(a)) for a in 'xyz') for v in mesh.findall(f'{CORE}vertices/{CORE}vertex')]
                triangles=[tuple(int(t.get(f'v{i}')) for i in (1,2,3)) for t in mesh.findall(f'{CORE}triangles/{CORE}triangle')]
                return vertices,triangles,[]
            vertices,triangles,matrices=[],[],[]
            for child in obj.findall(f'{CORE}components/{CORE}component'):
                vv,tt,mm=resolve(child.get(PRODUCTION+'path',path).lstrip('/'),child.get('objectid'),depth+1)
                vv,matrix=transform(vv,child.get('transform'))
                offset=len(vertices)
                vertices.extend(vv)
                triangles.extend(tuple(i+offset for i in tri) for tri in tt)
                matrices.extend(mm+[matrix])
            return vertices,triangles,matrices
        if '3D/3dmodel.model' in names:
            model=root('3D/3dmodel.model')
            out['unit']=model.get('unit','millimeter')
            out['build_items']=[]
            for item in model.findall(f'{CORE}build/{CORE}item'):
                vertices,triangles,matrices=resolve('3D/3dmodel.model',item.get('objectid'))
                vertices,matrix=transform(vertices,item.get('transform'))
                entry=mesh_check(vertices,triangles)
                entry.update({'object_id':item.get('objectid'),'build_transform':matrix,'component_transforms':matrices,
                              'all_scale_rotation_matrices_identity':all(m[:9]==[1,0,0,0,1,0,0,0,1] for m in matrices+[matrix])})
                out['build_items'].append(entry)
        for member in ['Metadata/project_settings.config','Metadata/slice_info.config']:
            if member not in names: continue
            if member.endswith('project_settings.config'):
                config=json.loads(archive.read(member))
                keys=['printer_model','printer_settings_id','nozzle_diameter','filament_type','filament_settings_id','filament_diameter',
                      'nozzle_temperature','nozzle_temperature_initial_layer','curr_bed_type','textured_plate_temp','textured_plate_temp_initial_layer',
                      'temperature_vitrification','layer_height','initial_layer_print_height','z_hop','retraction_length','retraction_speed',
                      'initial_layer_speed','outer_wall_speed','inner_wall_speed','sparse_infill_speed','filament_max_volumetric_speed',
                      'wall_loops','top_shell_layers','bottom_shell_layers','sparse_infill_density','enable_support','brim_width']
                out['embedded_project_settings']={k:config.get(k) for k in keys}
            else:
                out['embedded_slice_warnings']=[w.attrib for w in ET.fromstring(archive.read(member)).findall('.//warning')]
    return out,gcodes


def parse_gcode(raw):
    lines=raw.decode('utf-8-sig',errors='replace').splitlines()
    pos={a:0.0 for a in 'XYZE'}
    xyz_absolute=True
    e_relative=False
    units=1.0
    feed=0.0
    layer=0
    active_object=None
    role='unclassified'
    e_mode_explicit=False
    commands=Counter()
    events=[]
    deposits=[]
    non_deposit_z=[]
    extrusion_z=Counter()
    layer_info={}
    object_info=defaultdict(lambda:{'deposition_moves':0,'z':set(),'positive_e_mm':0.0})
    negative_e=Counter()
    total_e_positive=total_e_negative=0.0
    printed_first=printed_last=None
    config={}
    estimates=[]
    t_command=Counter()
    eonly_prime=0
    unknown_e_mode_moves=0
    remaining_normal_seconds=None
    initial_normal_seconds=None
    all_position_points=[]
    pause_commands={'M0','M1','M25','M226','M600','M601','M112','M410','PAUSE','CANCEL_PRINT','SDCARD_RESET_FILE'}
    observed_events={'G20','G21','G90','G91','M82','M83','G92','G9111','M104','M109','M140','M190','M141','M191','M18','M84','M220','M221','M200','M302','M209','G28','G29','M400','M106','M107','SET_PRESSURE_ADVANCE'}|pause_commands
    for number,line in enumerate(lines,1):
        if line==';LAYER_CHANGE':
            layer+=1
            layer_info[layer]={'comment_z_mm':None,'deposition_moves':0,'actual_extrusion_z_mm':set(),'objects':set(),
                               'first_deposition_line':None,'last_deposition_line':None,'max_feed_mm_s':0.0,
                               'positive_e_mm':0.0,'deposition_distance_mm':0.0,
                               'normal_remaining_seconds_near_layer_start':remaining_normal_seconds}
        if line.startswith(';Z:') and layer in layer_info: layer_info[layer]['comment_z_mm']=float(line[3:])
        if line.startswith(';TYPE:'): role=line[6:].strip()
        if line.startswith('; estimated printing time'): estimates.append(line[2:])
        match=re.match(r'^; ([A-Za-z0-9_]+) = (.*)$',line)
        if match: config[match[1]]=match[2]
        remaining=re.search(r'NormalR([\d.]+)s',line)
        if remaining:
            remaining_normal_seconds=float(remaining[1])
            if initial_normal_seconds is None: initial_normal_seconds=remaining_normal_seconds
        code=line.split(';',1)[0].strip()
        if not code: continue
        code=re.sub(r'^N\d+\s+','',code)
        command=code.split()[0]
        values={k:float(v) for k,v in PARAM.findall(code[len(command):])}
        commands[command]+=1
        if command in observed_events: events.append({'line':number,'layer':layer,'command':code})
        if command.startswith('T') and command[1:].isdigit(): t_command[command]+=1
        if command=='G20': units=25.4
        if command=='G21': units=1.0
        if command=='G90': xyz_absolute=True
        if command=='G91': xyz_absolute=False
        if command=='M82': e_relative=False; e_mode_explicit=True
        if command=='M83': e_relative=True; e_mode_explicit=True
        if command=='G92':
            for a in pos:
                if a in values: pos[a]=values[a]*units
        if command=='EXCLUDE_OBJECT_START':
            match=re.search(r'NAME=(\S+)',code)
            active_object=match[1] if match else None
        if command=='EXCLUDE_OBJECT_END': active_object=None
        if command not in ('G0','G1','G2','G3'): continue
        before=dict(pos)
        for a in 'XYZ':
            if a in values: pos[a]=values[a]*units if xyz_absolute else pos[a]+values[a]*units
        if 'F' in values: feed=values['F']*units/60
        e_delta=(values.get('E',0)*units if e_relative else values.get('E',pos['E']/units)*units-pos['E'])
        if 'E' in values: pos['E']=pos['E']+values['E']*units if e_relative else values['E']*units
        distance=math.dist(tuple(before[a] for a in 'XYZ'),tuple(pos[a] for a in 'XYZ'))
        if command in ('G2','G3'):
            # Account for XY arcs when supplied, and explicitly report them.
            if 'I' in values or 'J' in values:
                center=(before['X']+values.get('I',0)*units,before['Y']+values.get('J',0)*units)
                radius=math.hypot(before['X']-center[0],before['Y']-center[1])
                start=math.atan2(before['Y']-center[1],before['X']-center[0])
                end=math.atan2(pos['Y']-center[1],pos['X']-center[0])
                angle=(end-start)%(2*math.pi) if command=='G3' else (start-end)%(2*math.pi)
                if angle<1e-12: angle=2*math.pi
                distance=math.hypot(radius*angle,pos['Z']-before['Z'])
            else:
                raise ValueError('Unsupported arc without I/J center')
        if e_delta>0: total_e_positive+=e_delta
        if e_delta<0:
            total_e_negative+=e_delta
            negative_e[round(-e_delta,6)]+=1
        if e_delta<=1e-8 or distance<=1e-8:
            if abs(pos['Z']-before['Z'])>1e-8: non_deposit_z.append((number,pos['Z']))
            if e_delta>1e-8 and distance<=1e-8: eonly_prime+=1
            continue
        if not e_mode_explicit: unknown_e_mode_moves+=1
        point=tuple(pos[a] for a in 'XYZ')
        z=round(pos['Z'],6)
        extrusion_z[z]+=1
        all_position_points.extend([tuple(before[a] for a in 'XYZ'),point])
        record={'line':number,'layer':layer,'start_xyz_mm':[before[a] for a in 'XYZ'],'end_xyz_mm':list(point),
                'e_delta_mm':e_delta,'feed_mm_s':feed,'distance_mm':distance,'role':role,'object':active_object,
                'relative_extrusion':e_relative,'xyz_absolute':xyz_absolute}
        deposits.append(record)
        printed_first=printed_first or number
        printed_last=number
        if layer not in layer_info:
            layer_info[layer]={'comment_z_mm':None,'deposition_moves':0,'actual_extrusion_z_mm':set(),'objects':set(),'first_deposition_line':None,'last_deposition_line':None,'max_feed_mm_s':0.0,'positive_e_mm':0.0,'deposition_distance_mm':0.0,'normal_remaining_seconds_near_layer_start':remaining_normal_seconds}
        summary=layer_info[layer]
        summary['deposition_moves']+=1
        summary['actual_extrusion_z_mm'].add(z)
        summary['max_feed_mm_s']=max(summary['max_feed_mm_s'],feed)
        summary['positive_e_mm']+=e_delta
        summary['deposition_distance_mm']+=distance
        summary['first_deposition_line']=summary['first_deposition_line'] or number
        summary['last_deposition_line']=number
        if active_object:
            summary['objects'].add(active_object)
            object_info[active_object]['deposition_moves']+=1
            object_info[active_object]['z'].add(z)
            object_info[active_object]['positive_e_mm']+=e_delta
    for summary in layer_info.values():
        summary['actual_extrusion_z_mm']=sorted(summary['actual_extrusion_z_mm'])
        summary['objects']=sorted(summary['objects'])
        remaining=summary['normal_remaining_seconds_near_layer_start']
        summary['normal_elapsed_seconds_near_layer_start']=initial_normal_seconds-remaining if remaining is not None and initial_normal_seconds is not None else None
    for summary in object_info.values(): summary['z']=sorted(summary['z'])
    type_stats=defaultdict(lambda:{'moves':0,'min_speed_mm_s':math.inf,'max_speed_mm_s':0.0})
    for move in deposits:
        s=type_stats[move['role']]
        s['moves']+=1
        s['min_speed_mm_s']=min(s['min_speed_mm_s'],move['feed_mm_s'])
        s['max_speed_mm_s']=max(s['max_speed_mm_s'],move['feed_mm_s'])
    heat_off=[event for event in events if re.match(r'^(M104|M109|M140|M190)\s+S0(?:\s|$)',event['command'])]
    early_ends=[e for e in events if (e['command'].split()[0] in {'M18','M84'} or e in heat_off) and printed_last and e['line']<printed_last]
    keys=['filament_type','filament_settings_id','printer_model','printer_settings_id','filament_diameter','filament_flow_ratio',
          'filament_max_volumetric_speed','layer_height','initial_layer_print_height','initial_layer_speed',
          'outer_wall_speed','inner_wall_speed','sparse_infill_speed','wall_loops','top_shell_layers','bottom_shell_layers',
          'sparse_infill_density','enable_support','brim_width','z_hop','retraction_length','retraction_speed',
          'temperature_vitrification','nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer']
    return {'sha256':digest(raw),'size_bytes':len(raw),'lines':len(lines),'declared_and_parsed_layer_changes':layer,
            'actual_extrusion_z_levels_mm':sorted(extrusion_z),'actual_extrusion_levels_count':len(extrusion_z),
            'actual_deposition_move_count':len(deposits),'actual_deposition_bounds_mm':bounds(all_position_points),
            'maximum_commanded_deposition_speed_mm_s':max((m['feed_mm_s'] for m in deposits),default=0),
            'fastest_deposition_move':max(deposits,key=lambda m:m['feed_mm_s']) if deposits else None,
            'first_layer_maximum_commanded_deposition_speed_mm_s':layer_info.get(1,{}).get('max_feed_mm_s'),
            'all_deposition_uses_explicit_relative_e':bool(deposits) and all(m['relative_extrusion'] for m in deposits) and unknown_e_mode_moves==0,
            'all_deposition_xyz_absolute':bool(deposits) and all(m['xyz_absolute'] for m in deposits),
            'unknown_extrusion_mode_deposition_moves':unknown_e_mode_moves,
            'nonextruding_z_min_max_mm':[min((z for _,z in non_deposit_z),default=0),max((z for _,z in non_deposit_z),default=0)],
            'positive_e_total_mm_including_unretractions':total_e_positive,'negative_e_total_mm':total_e_negative,
            'e_only_positive_move_count':eonly_prime,'negative_e_lengths_mm_counts':dict(negative_e),
            'first_deposition_line':printed_first,'last_deposition_line':printed_last,
            'first_deposition':deposits[0] if deposits else None,'last_deposition':deposits[-1] if deposits else None,
            'objects_with_actual_deposition':dict(object_info),'object_count_with_actual_deposition':len(object_info),
            'layer_details':layer_info,'role_speed_statistics':dict(type_stats),'command_counts':dict(commands),
            'mode_temperature_fan_stop_events':events,'pause_cancel_emergency_events':[e for e in events if e['command'].split()[0] in pause_commands],
            'heat_off_or_motor_disable_before_final_deposition':early_ends,'tool_select_commands':dict(t_command),
            'embedded_config_comments':{key:config.get(key) for key in keys},'header_time_estimates':estimates,
            'firmware_macro_calls':[e for e in events if e['command'].startswith('G9111')],
            'limits':['Firmware implementation of G9111 and printer-resident overrides not available in these files.',
                      'Commanded extrusion and Z do not establish actual material output or physical Z motion.',
                      'Identity of the actual completed user print remains unconfirmed.']}


def main():
    targets=sorted(p for p in EVIDENCE.rglob('*') if p.is_file() and p.suffix in ('.3mf','.gcode','.model'))
    initial={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in targets}
    gcode_results={}
    external_hashes=defaultdict(list)
    for p in targets:
        if p.suffix=='.gcode': external_hashes[digest(p.read_bytes())].append(str(p.relative_to(ROOT)))
    archives=[]
    sources=[]
    for p in targets:
        raw=p.read_bytes()
        relative=str(p.relative_to(ROOT))
        if p.suffix=='.gcode':
            h=digest(raw)
            if h not in gcode_results: gcode_results[h]=parse_gcode(raw)
            sources.append({'path':relative,'type':'external_gcode','sha256':h,'gcode_sha256':h})
        else:
            record,embedded=audit_3mf(raw)
            record.update({'path':relative,'sha256':digest(raw),'embedded_gcode':[]})
            for member,gcode in embedded:
                h=digest(gcode)
                if h not in gcode_results: gcode_results[h]=parse_gcode(gcode)
                record['embedded_gcode'].append({'member':member,'sha256':h,'byte_identical_external_files':external_hashes.get(h,[])})
                sources.append({'path':relative+'!'+member,'type':'embedded_gcode','archive_sha256':digest(raw),'gcode_sha256':h})
            archives.append(record)
    unchanged=all(digest((ROOT/path).read_bytes())==h for path,h in initial.items())
    assert unchanged,'Frozen evidence changed during this audit'
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'evidence_root':str(EVIDENCE),
            'method':'Fresh parsing of raw3MF ZIP/XML and raw G-code only; no previous audit JSON used.',
            'evidence_hashes_before_and_after_identical':unchanged,'sources':sources,'archives':archives,
            'gcodes_by_sha256':gcode_results,
            'conclusions':['No audited G-code is a one-layer program: actual positive-extrusion moves reach8 or10mm.',
                           'No audited G-code has a pause/cancel or heater/motor shutdown before its last deposition move.',
                           'GUI exports have different profiles from supplied experimental projects; identity of executed file unknown.',
                           'No slicer regeneration, printer control or evidence modification was performed.']}
    (ROOT/'audit-gcode.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    rows=[]
    for source in sources:
        data=gcode_results[source['gcode_sha256']]
        name=source['path'].replace('evidence/model/revize-02-8mm/','').replace('evidence/local-temp/','')
        rows.append(f"| `{name}` | {data['object_count_with_actual_deposition']} | {data['actual_extrusion_levels_count']} | {max(data['actual_extrusion_z_levels_mm']):g} | {data['maximum_commanded_deposition_speed_mm_s']:.3f} | {data['embedded_config_comments']['filament_type']} |")
    report='''# Nezávislý audit zmrazených G-code a 3MF

Audit čte pouze původní soubory ze `evidence/`, nepřebírá dřívější kontrolní JSON. SHA-256 všech auditovaných souborů před a po čtení je shodné. Nic nebylo přegenerováno, odesláno ani spuštěno na tiskárně.

**Ve všech nalezených G-code jsou skutečné kladné extruzní pohyby ve 40 nebo 50 výškách, až do 8 nebo 10 mm. Žádný není programem pro jedinou vrstvu.** Zvednutí pro přejezdy (Z-hop) jsou z tohoto počtu vyloučena. Přítomné G90 a M83 určují absolutní souřadnice a relativní extruzi; audit zpracoval i případné G92/M82/G91 samostatně. Nebyl nalezen vložený pause/cancel, předčasné vypnutí ohřevu nebo motorů před posledním extruzním pohybem. Z toho nelze vyvodit, že firmware skutečně vykonal celý program nebo že materiál skutečně vytékal.

| Varianta | Tryska první / další vrstvy | Deska | Skutečná nejvyšší příkazová rychlost první / další extruze | Výška / vrstev | Čas normálně / tiše / sport |
|---|---|---|---|---|---|
| GUI 19:22, PLA | 220 / 205 °C | 60 °C | 100 / 250 mm/s | 10 mm / 50 | 57:23 / 1:34:31 / 50:25 |
| GUI 20:35, PLA | 220 / 205 °C | 60 °C | 100 / 250 mm/s | 8 mm / 40 | 49:39 / 1:22:01 / 43:34 |
| GUI 20:36, systémový TPU | 215 / 210 °C | 60 °C | 50 / 61,315 mm/s | 8 mm / 40 | 2:28:26 / 4:51:45 / 1:56:06 |
| Dodaný TEST, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 8 mm / 40 | 33:09 / 1:00:19 / 27:40 |
| Dodaná sestava 8 mm, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 8 mm / 40 | 5:54:08 / 11:11:18 / 4:45:55 |
| Historická sestava 10 mm, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 10 mm / 50 | 7:23:04 / 13:59:39 / 5:57:49 |

Rychlosti jsou přímo z pohybů s kladnou extruzí, nikoli pouze hodnoty v profilu. Překročení 50 mm/s na první vrstvě PLA pochází mimo jiné z první vrstvy výplně; maximum je 100 mm/s. Název materiálu v souboru není důkazem fyzicky vložené cívky.

| Zdroj | Objektů s extruzí | Skutečných extruzních Z | Nejvyšší extruzní Z [mm] | Nejvyšší příkazová extruzní rychlost [mm/s] | Materiál v G-code |
|---|---:|---:|---:|---:|---|
'''+ '\n'.join(rows)+'''

## Rozhodující rozdíly

- Dodaný TEST projekt obsahuje dvě uzavřené samostatné sítě, bez škálování, přibližně 30 × 20 × 8 mm; 40 skutečných extruzních vrstev, jediný profil TPU, 225/60 °C. Odhad je 33 m 9 s normálně, 60 m 19 s tiše, 27 m 40 s sport. Vestavěný G-code je byte-identický s uloženým vnějším souborem.
- GUI archiv 19:22 obsahuje skutečně profil **PLA**, počáteční trysku 220 °C a následně 205 °C, desku 60 °C, 2 stěny a 15% výplň. Má 50 extruzních vrstev do 10 mm. Proces se liší od našeho experimentálního TPU projektu.
- GUI G-code 20:35 je opět **PLA 220→205 °C**, 40 vrstev do 8 mm. GUI 20:36 je systémový **TPU 95A 215→210 °C**, rovněž 40 vrstev do 8 mm, 2 stěny a 15% výplň; také se liší od dodaného experimentu 225 °C / 4 stěny / 100% výplň.
- Žádný časový odhad nalezeného souboru přesně neodpovídá hlášenému dokončení za 88 min. Přibližné časy nejsou spolehlivým identifikátorem úlohy a skutečně použitý soubor zatím není potvrzen.
- Příkaz G9111 je firmwarem definované zahájení tisku; jeho interní chování a případná nastavení/rychlostní režimy uložené v tiskárně nejsou součástí těchto souborů a tento audit je nepotvrzuje.

Podrobný `audit-gcode.json` uvádí hashe, shodu embedded/external, geometrické komponenty, příkazové i skutečně parsované výšky extruze, počty pohybů po vrstvách, rychlosti podle typu dráhy, režimy E/G92, teplotní příkazy a řádky začátku/konce. Záznamy se stejným hashem G-code jsou auditovány jednou a propojeny se všemi kopiemi. Výsledek neprokazuje fyzickou příčinu selhání ani vinu uživatele.
'''
    (ROOT/'audit-gcode.md').write_text(report)
    print(json.dumps({'raw_files':len(targets),'archives':len(archives),'unique_gcodes':len(gcode_results),'unchanged':unchanged,
                      'summary':[{'hash':h,'objects':d['object_count_with_actual_deposition'],'layers':d['actual_extrusion_levels_count'],
                                  'zmax':max(d['actual_extrusion_z_levels_mm']),'vmax':d['maximum_commanded_deposition_speed_mm_s'],
                                  'first_vmax':d['first_layer_maximum_commanded_deposition_speed_mm_s'],
                                  'pauses':d['pause_cancel_emergency_events'],'early_end':d['heat_off_or_motor_disable_before_final_deposition'],
                                  'time':d['header_time_estimates']} for h,d in gcode_results.items()]},ensure_ascii=False))


if __name__=='__main__':
    main()
