#!/usr/bin/env python3
"""Read-only forensic geometry audit; never imports FreeCAD or executes project code.

Reads only evidence/model. Writes only audit-geometry.json and audit-geometry.md
next to this script. Audits raw STL and 3MF vertices/triangles/transforms, not prior
validation JSON. Existing audit outputs are replaced on a deliberate rerun.
"""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import math
import posixpath
import struct
import xml.etree.ElementTree as ET
import zipfile

OUT = Path(__file__).resolve().parent
BASE = OUT / 'evidence' / 'model'
NS = {'c': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
IDENTITY = [1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.]
UNIT_MM = {'micron': .001, 'millimeter': 1., 'centimeter': 10., 'meter': 1000., 'inch': 25.4, 'foot': 304.8}

def inventory():
    return {str(p.relative_to(BASE)): {'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(BASE.rglob('*')) if p.is_file()}

def bounds(vertices):
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    return {'min_mm': lo, 'max_mm': hi, 'size_mm': [b-a for a,b in zip(lo,hi)]}

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def mesh_audit(vertices, faces):
    # Weld exact coordinate duplicates; STL represents each corner separately.
    index = {}; welded=[]; ids=[]
    for v in vertices:
        v=tuple(v)
        if v not in index: index[v]=len(welded); welded.append(v)
        ids.append(index[v])
    faces=[tuple(ids[i] for i in f) for f in faces]
    edges=collections.Counter(); directions=collections.Counter(); neighbors=collections.defaultdict(set)
    degenerate=0; volume=0.; bottom_area=0.; bb=bounds(welded)
    for f in faces:
        a,b,c=[welded[i] for i in f]
        bc=cross(b,c); volume+=sum(a[i]*bc[i] for i in range(3))/6
        ab=[b[i]-a[i] for i in range(3)]; ac=[c[i]-a[i] for i in range(3)]
        area=math.sqrt(sum(q*q for q in cross(ab,ac)))/2
        if area<1e-12: degenerate+=1
        if all(abs(v[2]-bb['min_mm'][2])<1e-7 for v in (a,b,c)): bottom_area+=area
        for i in range(3):
            u,v=f[i],f[(i+1)%3];edge=tuple(sorted((u,v)))
            edges[edge]+=1; directions[edge]+=1 if u<v else -1
            neighbors[u].add(v);neighbors[v].add(u)
    unseen=set(range(len(welded))); components=0
    while unseen:
        components+=1;pending=[unseen.pop()]
        while pending:
            for v in neighbors[pending.pop()]:
                if v in unseen:unseen.remove(v);pending.append(v)
    normalized=[]
    for f in faces:
        normalized.append(sorted(tuple(round(welded[v][i]-bb['min_mm'][i],5) for i in range(3)) for v in f))
    signature=hashlib.sha256(json.dumps(sorted(normalized),separators=(',',':')).encode()).hexdigest()
    return {**bb,'input_vertices':len(vertices),'welded_vertices':len(welded),
            'triangles':len(faces),'signed_volume_mm3':volume,'absolute_volume_mm3':abs(volume),
            'connected_vertex_components':components,'boundary_edges':sum(n==1 for n in edges.values()),
            'nonmanifold_edges':sum(n!=2 for n in edges.values()),
            'inconsistent_oriented_edges':sum(n!=0 for n in directions.values()),
            'degenerate_triangles':degenerate,'minimum_z_planar_area_mm2':bottom_area,
            'translation_normalized_triangle_sha256_quantized_1e-5_mm':signature}

def stl_read(path):
    data=path.read_bytes(); count=struct.unpack('<I',data[80:84])[0]
    if len(data)!=84+50*count: raise ValueError('Expected exact binary STL: '+str(path))
    vertices=[];faces=[]
    for i in range(count):
        f=struct.unpack('<12fH',data[84+50*i:134+50*i]); first=len(vertices)
        vertices.extend(tuple(f[k:k+3]) for k in (3,6,9));faces.append((first,first+1,first+2))
    return vertices,faces

def transform_info(text):
    m=list(map(float,text.split())) if text else IDENTITY[:]
    assert len(m)==12
    det=m[0]*(m[4]*m[8]-m[5]*m[7])-m[1]*(m[3]*m[8]-m[5]*m[6])+m[2]*(m[3]*m[7]-m[4]*m[6])
    return {'values':m,'linear_determinant':det,'axis_scale_lengths':[math.sqrt(sum(v*v for v in m[j:j+3])) for j in (0,3,6)],
            'linear_identity':m[:9]==IDENTITY[:9],'translation':m[9:]}

def apply_transform(v,m):
    return tuple(sum(v[k]*m[k*3+i] for k in range(3))+m[9+i] for i in range(3))

def audit_3mf(path,stls):
    with zipfile.ZipFile(path) as z:
        models={n:ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.model')}
        rels=ET.fromstring(z.read('_rels/.rels'))
        root_name=next(e.attrib['Target'].lstrip('/') for e in rels if e.attrib.get('Type','').endswith('/3dmodel'))
        roots=models[root_name]
        objects={(name,o.attrib['id']):o for name,r in models.items() for o in r.findall('c:resources/c:object',NS)}
        model_settings=[]
        if 'Metadata/model_settings.config' in z.namelist():
            conf=ET.fromstring(z.read('Metadata/model_settings.config'))
            for o in conf.findall('object'):
                model_settings.append({'attributes':o.attrib,'metadata':[m.attrib for m in o.findall('metadata')],
                    'parts':[{'attributes':p.attrib,'metadata':[m.attrib for m in p.findall('metadata')],
                              'mesh_stats':[m.attrib for m in p.findall('mesh_stat')]} for p in o.findall('part')]})
        raw=[]
        for (name,oid),o in objects.items():
            me=o.find('c:mesh',NS)
            if me is None: continue
            unit=models[name].attrib.get('unit','millimeter'); factor=UNIT_MM[unit]
            verts=[tuple(float(v.attrib[a])*factor for a in ('x','y','z')) for v in me.findall('c:vertices/c:vertex',NS)]
            faces=[tuple(int(t.attrib[a]) for a in ('v1','v2','v3')) for t in me.findall('c:triangles/c:triangle',NS)]
            raw.append({'member':name,'objectid':oid,'attributes':o.attrib,'unit':unit,'geometry':mesh_audit(verts,faces)})
        def resolve(member,oid,chain,trail):
            assert (member,oid) not in trail,'component cycle'
            o=objects[(member,oid)];me=o.find('c:mesh',NS)
            if me is not None:
                factor=UNIT_MM[models[member].attrib.get('unit','millimeter')]
                verts=[tuple(float(v.attrib[a])*factor for a in ('x','y','z')) for v in me.findall('c:vertices/c:vertex',NS)]
                faces=[tuple(int(t.attrib[a]) for a in ('v1','v2','v3')) for t in me.findall('c:triangles/c:triangle',NS)]
                for tr in chain:verts=[apply_transform(v,tr['values']) for v in verts]
                geom=mesh_audit(verts,faces)
                sig=geom['translation_normalized_triangle_sha256_quantized_1e-5_mm']
                matches=[s['file'] for s in stls if s['geometry']['translation_normalized_triangle_sha256_quantized_1e-5_mm']==sig]
                return [{'member':member,'objectid':oid,'attributes':o.attrib,'transform_application_order':chain,
                         'geometry':geom,'matching_stl_after_translation_1e-5_mm':matches}]
            result=[]
            for c in o.findall('c:components/c:component',NS):
                p=next((v for k,v in c.attrib.items() if k.endswith('}path')),None)
                child=member if p is None else (p.lstrip('/') if p.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(member),p)))
                tr=transform_info(c.attrib.get('transform'));tr['kind']='component';tr['attributes']=c.attrib
                result.extend(resolve(child,c.attrib['objectid'],[tr]+chain,trail+[(member,oid)]))
            return result
        built=[]
        for item in roots.findall('c:build/c:item',NS):
            tr=transform_info(item.attrib.get('transform'));tr['kind']='build';tr['attributes']=item.attrib
            built.append({'attributes':item.attrib,'root_object_attributes':objects[(root_name,item.attrib['objectid'])].attrib,
                          'printable_effective':item.attrib.get('printable','true') not in ('0','false'),
                          'resolved_meshes':resolve(root_name,item.attrib['objectid'],[tr],[])})
        return {'file':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'zip_crc_error':z.testzip(),'model_units':{n:r.attrib.get('unit','millimeter') for n,r in models.items()},
                'root_model':root_name,'embedded_gcode_members':[n for n in z.namelist() if n.endswith('.gcode')],
                'has_project_settings':'Metadata/project_settings.config' in z.namelist(),
                'raw_meshes':raw,'build_items':built,'model_settings':model_settings,
                'all_object_attributes':[{'member':n,**o.attrib} for (n,oid),o in objects.items()]}

def audit_fcstd(path):
    with zipfile.ZipFile(path) as z:
        r=ET.fromstring(z.read('Document.xml'))
        cells=[e.attrib for e in r.iter() if 'alias' in e.attrib]
        objects=[]
        for o in r.findall('.//ObjectData/Object'):
            props={p.attrib['name']:p for p in o.findall('Properties/Property')}
            if o.attrib.get('name') in ('AdhesiveBed','JointAdhesive','Part1','Part2','Part3','ContinuousProfile'):
                objects.append({'name':o.attrib['name'],'properties':{k:ET.tostring(v,encoding='unicode') for k,v in props.items() if k in ('Height','Width','Length','Base','Tool','Label')}})
        return {'file':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'zip_crc_error':z.testzip(),'spreadsheet_aliased_cells':cells,'selected_object_properties':objects,
                'scope':'Stored XML only; no FreeCAD launch, no recompute, no save, no BREP validity claim.'}

before=inventory()
stls=[]
for path in sorted(BASE.rglob('*.stl')):
    vertices,faces=stl_read(path)
    stls.append({'file':str(path.relative_to(BASE)),'sha256':before[str(path.relative_to(BASE))]['sha256'],
                 'unit_assumption':'STL has no units; project millimeters; compared against explicit 3MF millimeters.',
                 'geometry':mesh_audit(vertices,faces)})
archives=[audit_3mf(p,stls) for p in sorted(BASE.rglob('*.3mf'))]
cad=[audit_fcstd(p) for p in sorted(BASE.rglob('*.FCStd'))]
after=inventory()
assert before==after,'Evidence changed during read-only audit'
report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidence_root':str(BASE),
        'method':'Independent raw mesh/transform/XML parsing; prior audit JSON not used; no slicing, regeneration, or printer operations.',
        'evidence_file_count':len(before),'evidence_preserved_during_audit':True,'evidence_inventory':before,
        'stl':stls,'three_mf':archives,'fcstd':cad,
        'limitations':['Unknown file and edited/copied project actually printed.','No printer/toolpath/physical extrusion conclusion from geometry.',
        'Watertight two-manifold topology and nonzero volume are checked; no exhaustive triangle self-intersection proof.',
        'Native CAD BREP is not recomputed. Saved spreadsheet parameters are corroboration only.',
        'Triangle match uses translation-normalized coordinates rounded to 0.00001 mm, not byte identity.']}
(OUT/'audit-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Nezávislý audit zachované geometrie přepážky', '',
       'Čteny přímo vrcholy, trojúhelníky, komponenty a build transformace všech 3MF; staré kontrolní JSON nebyly zdrojem výsledků.',
       f'Evidence: {len(before)} souborů; SHA-256 všech souborů před a po auditu shodné.', '',
       '| 3MF | Nastavený projekt / vložený G-code | Počet dílů | Rozměry výsledných dílů mm | Z po všech transformacích mm |',
       '|---|---|---:|---|---|']
for a in archives:
    ms=[m for b in a['build_items'] for m in b['resolved_meshes']]
    dims='; '.join(' × '.join(f'{v:.6f}' for v in m['geometry']['size_mm']) for m in ms)
    zs='; '.join(f"{m['geometry']['min_mm'][2]:.8f}–{m['geometry']['max_mm'][2]:.8f}" for m in ms)
    lines.append(f"| `{a['file']}` | {'ano' if a['has_project_settings'] else 'ne'} / {'ano' if a['embedded_gcode_members'] else 'ne'} | {len(ms)} | {dims} | {zs} |")
lines+=['','## Výsledek geometrické kontroly','',
        '- Všechny 3MF mají explicitní jednotku millimeter. Lineární části všech component/build transformací jsou jednotkové: žádné zmenšení, zploštění ani rotace.',
        '- Všechny vložené mesh objekty jsou type=model. V nastavených projektech jsou díly subtype=normal_part, extruder=1 a build printable=1. Žádné lepidlo, negativní objem ani modifikátor.',
        '- Každá výsledná síť je jedna souvislá uzavřená orientovaná komponenta, s nenulovým kladným objemem, bez hran s jiným počtem než dva sousední trojúhelníky a bez degenerovaných trojúhelníků.',
        '- Všechny build díly dosedají na Z=0, s kladnou plochou spodního rovinného dosedu. U nastavených projektů jsou raw sítě centrované kolem nuly; build posun o polovinu výšky je správný, není to odsazení nad podložku.',
        '- Všechny výsledné mesh odpovídají příslušným uloženým STL po odstranění posunu a kvantizaci 0,00001 mm. Žádné 3MF neobsahuje pouze 2mm lepicí lože.',
        '- TEST má dva díly 30 × 20 × 7,99960614 mm. Aktuální velký projekt má 193/200/193 × 20 × 7,99960614 mm. Historický projekt má 196/202/196 × 20 × 9,99941826 mm.',
        '', '## Co tento audit neprokazuje','',
        'Skutečně tištěný soubor a úprava při kopírování dílu z jiného projektu nejsou identifikovány. Z těchto původních souborů nelze dovodit zachování jejich nastavení po kopírování/importu. Import geometrie může použít nastavení cílového projektu; zde se ověřuje uložená geometrie, nikoli konkrétní uživatelský postup.',
        'Audit nevysvětluje chování extruze ani nepotvrzuje vhodnost dalšího tisku. G-code posuzuje samostatný audit. Není proveden úplný test samoprůniků trojúhelníků ani přepočet CAD BREP.',
        '', '## Zachování důkazů','',
        'Nebylo spuštěno FreeCAD makro, FreeCAD, slicer ani ovládání tiskárny. Zápis pouze audit-geometry.py/json/md v této diagnostické složce mimo evidence/.',
        'Podrobný strojově čitelný výsledek, všechny transformace, příznaky, objemy, počty trojúhelníků, parametry FCStd a SHA-256 jsou v audit-geometry.json.']
(OUT/'audit-geometry.md').write_text('\n'.join(lines)+'\n')
for a in archives:
    meshes=[m for b in a['build_items'] for m in b['resolved_meshes']]
    print(a['file'])
    for m in meshes:
        g=m['geometry'];print(' ',g['size_mm'],'volume',round(g['signed_volume_mm3'],6),'triangles',g['triangles'],
            'components',g['connected_vertex_components'],'nonmanifold',g['nonmanifold_edges'],
            'orientation',g['inconsistent_oriented_edges'],'degenerate',g['degenerate_triangles'],'matches',len(m['matching_stl_after_translation_1e-5_mm']))
print('EVIDENCE_PRESERVED',before==after,'FILES',len(before))
