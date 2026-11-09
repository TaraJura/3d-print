#!/usr/bin/env python3
"""Zdobené pouzdro V05: tisk naležato na dlouhém boku s podporami.

Geometrie se nemění: stl/pouzdro-zdobene.stl se jen tuhě otočí a uloží jako
stl/pouzdro-zdobene-nalezato.stl. Svislé STL, FCStd a svislý projekt zůstávají beze změny.
Přepisuje jen ten nový STL a vlastní soubory v rozlozeni/nalezato-s-podporami/. Tiskárnu neovládá.

Rámce:
  díl    = rámec svislého STL: X 0–78 podél stěny, Y 0–33,8 k stěně (deska Y 29,8–33,8), Z 0–248 od konce k ústí.
  tisk   = tisková výška je X dílu; poté dlouhá osa o 45° v rovině podložky.
"""
import argparse
import json
import math
import re
import struct
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

MODEL = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(MODEL))
import build_print_projects as B  # noqa: E402

SOURCE = MODEL/'stl/pouzdro-zdobene.stl'
SOURCE_SHA = '52272f11c1da5100c33756c3c9fe94aa64b06f5f66380c752142e7aab70269b5'
FCSTD_SHA = '60896561b73ba786734fc74abd816cced1274a5c87541a244740688f988c6f35'
VERTICAL_3MF_SHA = 'db2a8a1a438cf909530de85f0b264cc8427ed5da4bbfd6591d66397f0398f401'
TARGET = MODEL/'stl/pouzdro-zdobene-nalezato.stl'
OUT = MODEL/'rozlozeni/nalezato-s-podporami'
BED, BRIM = 260., 8.
C = S = math.sqrt(.5)
NAME = 'pouzdro-zdobene-nalezato'
BEIGE, INK, MUTED = '#f4f1ec', '#26343a', '#5d6b70'
COL = {'model': '#3b4448', 'Support': '#2f9e6e', 'Support interface': '#0f6fbf', 'Support transition': '#7a5cc4',
       'Brim': '#c9a227', 'Bridge': '#e0562b', 'Overhang wall': '#e0902b', 'Internal Bridge': '#9c7a6a'}

# Hlavní rozměry dílu, stejné jako v print-manifest.json a v tabulce Parameters modelu.
BLADE_X, BLADE_Y = 22.5, 1.5
CAV_X, CAV_Y = 23.5, 2.2
LEAD_X, LEAD_Y = 25.7, 4.4
CX, CY = 39., 9.8
FLOOR_Z, LEAD_Z, MOUTH_Z = 16., 222., 234.
SEAT_TIP_Z = 24.  # špička dosednutého nože: dno + rezerva 8 mm
PLATE_Y = (29.8, 33.8)
HOLES = ({'x': 71., 'z': 241.}, {'x': 7., 'z': 7.})
HOLE_R = 2.75

# Modifikátory v rámci dílu: (název, typ, X, Y, Z). Nejsou tisknutelné a nejsou to další kusy.
MODIFIERS = (
    ('blok-dutina-a-nabeh', 'support_blocker', (CX-26., CX+26.), (CY-4.6, CY+4.6), (FLOOR_Z-.2, MOUTH_Z+.5)),
    ('blok-otvor-horni', 'support_blocker', (67.8, 74.2), (29.5, 34.1), (237.8, 245.2)),
    ('blok-otvor-dolni', 'support_blocker', (3.8, 10.2), (29.5, 34.1), (3.8, 11.2)),
    ('blok-nad-listou-u-konce', 'support_blocker', (20., 37.), (14., 19.2), (28., 58.)),
    ('blok-nad-listou-u-usti', 'support_blocker', (20., 37.), (14., 19.2), (182., 214.)),
    ('vynutit-pod-telem-a-limcem', 'support_enforcer', (.01, 15.3), (-1., 19.2), (-1., 249.)),
    ('vynutit-pod-deskou', 'support_enforcer', (10., 26.4), (29.2, 34.5), (27., 224.)),
    ('vynutit-sraz-horniho-ucha', 'support_enforcer', (63.6, 66.), (29.2, 34.5), (235.5, 248.5)),
)

PROCESS = {
    'enable_support': '1', 'support_type': 'normal(auto)', 'support_style': 'snug',
    'support_on_build_plate_only': '0', 'support_threshold_angle': '30', 'support_remove_small_overhang': '0',
    'support_critical_regions_only': '0', 'support_expansion': '0',
    'support_top_z_distance': '0.2', 'support_bottom_z_distance': '0', 'support_object_xy_distance': '0.4',
    'support_object_first_layer_gap': '0.2', 'support_interface_top_layers': '2', 'support_interface_bottom_layers': '0',
    'support_base_pattern': 'rectilinear', 'support_base_pattern_spacing': '2.5', 'support_interface_spacing': '0.5',
    'support_speed': '60', 'support_interface_speed': '40', 'independent_support_layer_height': '0',
    'detect_thin_wall': '1', 'bridge_no_support': '0', 'max_bridge_length': '10', 'bridge_angle': '0',
    'brim_type': 'outer_only', 'brim_width': format(BRIM, 'g'), 'brim_object_gap': '0', 'elefant_foot_compensation': '0',
}


def rot(x, y, z):
    """Tuhé otočení: X dílu do výšky tisku, konec s dnem nahoře v půdorysu, pak 45° v rovině podložky."""
    u, v, w = 248.-z, y, x
    return (C*u-S*v, S*u+C*v, w)


def unrot(px, py, pz):
    u, v = C*px+S*py, -S*px+C*py
    return (pz, v, 248.-u)


def read_stl(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    B.require(len(raw) == 84+50*count, f'Není binární STL: {path}')
    return [struct.unpack_from('<12f', raw, 84+50*i)[3:] for i in range(count)]


def volume(tris):
    return sum((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
               for a, b, c in ((t[:3], t[3:6], t[6:9]) for t in tris))


def make_stl():
    B.require(B.sha(SOURCE) == SOURCE_SHA, 'Změněné zdrojové STL')
    source = read_stl(SOURCE)
    points = [rot(*t[i:i+3]) for t in source for i in (0, 3, 6)]
    lo = [min(p[i] for p in points) for i in range(3)]
    out = bytearray(b'Pouzdro V05 - rigid print orientation of pouzdro-zdobene.stl'.ljust(80, b' '))
    out += struct.pack('<I', len(source))
    for i in range(len(source)):
        tri = [[points[3*i+k][a]-lo[a] for a in range(3)] for k in range(3)]
        u = [tri[1][a]-tri[0][a] for a in range(3)]
        v = [tri[2][a]-tri[0][a] for a in range(3)]
        n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        m = math.sqrt(sum(q*q for q in n)) or 1.
        out += struct.pack('<12fH', n[0]/m, n[1]/m, n[2]/m, *tri[0], *tri[1], *tri[2], 0)
    TARGET.write_bytes(bytes(out))
    return lo


def rigid_check(lo):
    """Vrchol po vrcholu zpět do rámce svislého STL. Stejné pořadí trojúhelníků, stejná topologie."""
    source, target = read_stl(SOURCE), read_stl(TARGET)
    B.require(len(source) == len(target), 'Jiný počet trojúhelníků')
    worst = 0.
    for s, t in zip(source, target):
        for i in (0, 3, 6):
            back = unrot(t[i]+lo[0], t[i+1]+lo[1], t[i+2]+lo[2])
            worst = max(worst, max(abs(back[a]-s[i+a]) for a in range(3)))
    B.require(worst < 5e-5, f'Není tuhé otočení: {worst}')
    volumes = abs(volume(source)), abs(volume(target))
    B.require(abs(volumes[0]-volumes[1]) < .05, f'Jiný objem: {volumes}')
    mesh = B.read_mesh(TARGET)  # uzavřenost, 1 komponenta, nenulové plochy a limit podložky
    probe = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    axes = [[rot(*p)[a]-rot(0, 0, 0)[a] for a in range(3)] for p in probe]
    det = (axes[0][0]*(axes[1][1]*axes[2][2]-axes[1][2]*axes[2][1])
           - axes[0][1]*(axes[1][0]*axes[2][2]-axes[1][2]*axes[2][0])
           + axes[0][2]*(axes[1][0]*axes[2][1]-axes[1][1]*axes[2][0]))
    B.require(abs(det-1) < 1e-12, 'Otočení zrcadlí díl')
    return mesh, {'triangles': len(target), 'volume_source_mm3': volumes[0], 'volume_rotated_mm3': volumes[1],
                  'max_vertex_deviation_back_in_source_frame_mm': worst, 'rotation_determinant': det,
                  'closed_single_component': True, 'size_mm': mesh['size'], 'source_sha256': SOURCE_SHA,
                  'rotated_sha256': B.sha(TARGET)}


def box_mesh(xr, yr, zr, to_local):
    corners = [(x, y, z) for z in zr for y in yr for x in xr]
    faces = ((0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5))
    return [to_local(*p) for p in corners], faces


def add_modifiers(configured, frame, modifiers):
    """Přidá modifikátory jako další součásti TÉHOŽ objektu: subtype support_blocker / support_enforcer."""
    with ZipFile(configured) as z:
        entries = [(n, z.read(n)) for n in z.namelist()]
    data = dict(entries)
    root = ET.fromstring(data['3D/3dmodel.model'])
    item = root.find('m:build/m:item', B.XMLNS)
    tr = [float(v) for v in item.get('transform').split()]
    B.require(tr[:9] == B.IDENTITY, 'Položka není jen posunutá')
    obj = root.find(f'm:resources/m:object[@id="{item.get("objectid")}"]', B.XMLNS)
    comps = obj.find('m:components', B.XMLNS)
    first = comps.findall('m:component', B.XMLNS)[0]
    path = first.get(f'{{{B.PNS}}}path')
    inner_name = path.lstrip('/')
    ET.register_namespace('p', B.PNS)
    inner = ET.fromstring(data[inner_name])
    resources = inner.find('m:resources', B.XMLNS)
    next_id = max(int(o.get('id')) for o in resources.findall('m:object', B.XMLNS))+1
    config = ET.fromstring(data['Metadata/model_settings.config'])
    cobj = config.find(f'object[@id="{item.get("objectid")}"]')
    part_id = max(int(p.get('id')) for p in cobj.findall('part'))+1

    def to_local(x, y, z):
        p = rot(x, y, z)
        return tuple(p[a]-frame['lo'][a]+frame['t'][a]-tr[9+a] for a in range(3))
    for name, subtype, xr, yr, zr in modifiers:
        verts, faces = box_mesh(xr, yr, zr, to_local)
        o = ET.SubElement(resources, f'{{{B.NS}}}object', id=str(next_id), type='model')
        mesh = ET.SubElement(o, f'{{{B.NS}}}mesh')
        vs, ts = ET.SubElement(mesh, f'{{{B.NS}}}vertices'), ET.SubElement(mesh, f'{{{B.NS}}}triangles')
        for p in verts:
            ET.SubElement(vs, f'{{{B.NS}}}vertex', x=format(p[0], '.9g'), y=format(p[1], '.9g'), z=format(p[2], '.9g'))
        for f in faces:
            ET.SubElement(ts, f'{{{B.NS}}}triangle', v1=str(f[0]), v2=str(f[1]), v3=str(f[2]))
        ET.SubElement(comps, f'{{{B.NS}}}component', {f'{{{B.PNS}}}path': path, 'objectid': str(next_id),
                                                       'transform': '1 0 0 0 1 0 0 0 1 0 0 0'})
        part = ET.SubElement(cobj, 'part', id=str(part_id), subtype=subtype)
        ET.SubElement(part, 'metadata', key='name', value=name)
        ET.SubElement(part, 'metadata', key='matrix', value='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
        ET.SubElement(part, 'mesh_stat', edges_fixed='0', degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
        next_id += 1
        part_id += 1
    data[inner_name] = ET.tostring(inner, encoding='utf-8', xml_declaration=True)
    data['3D/3dmodel.model'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    data['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    with ZipFile(configured, 'w', B.ZIP_DEFLATED) as z:
        for name, _ in entries:
            z.writestr(name, data[name])


def read_project(path):
    """Přečte finální 3MF: 1 položka, 1 tisknutelná součást, modifikátory zachované, geometrie a nastavení."""
    with ZipFile(path) as z:
        B.require(z.testzip() is None, 'Poškozený ZIP')
        root = ET.fromstring(z.read('3D/3dmodel.model'))
        items = root.findall('m:build/m:item', B.XMLNS)
        B.require(len(items) == 1, 'Projekt nemá 1 položku')
        tr = [float(v) for v in items[0].get('transform').split()]
        B.require(tr[:9] == B.IDENTITY, 'Slicer změnil orientaci nebo měřítko')
        obj = root.find(f'm:resources/m:object[@id="{items[0].get("objectid")}"]', B.XMLNS)
        comps = obj.findall('m:components/m:component', B.XMLNS)
        config = ET.fromstring(z.read('Metadata/model_settings.config'))
        parts = [(p.get('id'), p.get('subtype'), {m.get('key'): m.get('value') for m in p.findall('metadata')},
                  (p.find('mesh_stat').attrib if p.find('mesh_stat') is not None else {})) for p in config.findall('.//object/part')]
        B.require(sum(p[1] == 'normal_part' for p in parts) == 1, 'Není právě 1 tisknutelná součást')
        B.require(len(comps) == len(parts), 'Počet komponent neodpovídá součástem')
        volumes = []
        for comp, part in zip(comps, parts):
            inner = ET.fromstring(z.read(comp.get(f'{{{B.PNS}}}path').lstrip('/')))
            mesh = inner.find(f'm:resources/m:object[@id="{comp.get("objectid")}"]/m:mesh', B.XMLNS)
            ctr = [float(v) for v in comp.get('transform').split()]
            B.require(ctr[:9] == B.IDENTITY, 'Komponenta není jen posunutá')
            vs = [[float(v.get(a))+ctr[9+i]+tr[9+i] for i, a in enumerate('xyz')] for v in mesh.findall('m:vertices/m:vertex', B.XMLNS)]
            tris = mesh.findall('m:triangles/m:triangle', B.XMLNS)
            volumes.append({'part_id': part[0], 'subtype': part[1], 'name': part[2].get('name'), 'vertices': vs, 'triangles': len(tris),
                            'bbox_mm': [[min(p[i] for p in vs) for i in range(3)], [max(p[i] for p in vs) for i in range(3)]],
                            'mesh_stat': part[3]})
        cfg = json.loads(z.read('Metadata/project_settings.config'))
        info = {'items': len(items), 'volumes': volumes, 'cfg': cfg}
        if 'Metadata/plate_1.gcode' in z.namelist():
            gcode = z.read('Metadata/plate_1.gcode')
            info['gcode_sha256'] = B.hashlib.sha256(gcode).hexdigest()
            info['gcode_bytes'] = len(gcode)
            si = ET.fromstring(z.read('Metadata/slice_info.config'))
            info['slice_metadata'] = {v.get('key'): v.get('value') for v in si.iter('metadata') if v.get('key') in ('prediction', 'weight', 'outside', 'support_used')}
            info['warnings'] = [v.attrib for v in si.iter('warning')]
        return info


def parse_strokes(gcode):
    """Všechny extruze po vrstvách: konce v souřadnicích podložky, role, šířka, E. Druhá hodnota je celkové E včetně čištění."""
    layers, role, width, layer = {}, 'Custom', .42, -1
    pos = dict(X=0., Y=0., Z=0.)
    total = 0.
    num = re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):
            layer += 1
        elif line.startswith(';TYPE:'):
            role = line.split(':', 1)[1].strip()
        elif line.startswith(';WIDTH:'):
            width = float(line.split(':', 1)[1])
        cmd = line.split(';', 1)[0].strip()
        if not cmd or cmd.split()[0] not in ('G0', 'G1'):
            continue
        vals = {a: float(v) for a, v in num.findall(cmd)}
        old = pos.copy()
        for a in 'XYZ':
            if a in vals:
                pos[a] = vals[a]
        e = vals.get('E', 0)
        total += max(e, 0.)
        if e > 0 and role != 'Custom' and layer >= 0 and (pos['X'] != old['X'] or pos['Y'] != old['Y']):
            rec = layers.setdefault(layer, {'z': pos['Z'], 'strokes': []})
            rec['strokes'].append((old['X'], old['Y'], pos['X'], pos['Y'], role, width, e))
    return layers, total


class Frame:
    def __init__(self, frame):
        self.lo, self.t = frame['lo'], frame['t']

    def part(self, bx, by, bz):
        return unrot(bx-self.t[0]+self.lo[0], by-self.t[1]+self.lo[1], bz+self.lo[2])


def void_at(x, y, z, margin=0.):
    """Je bod dílu ve funkční dutině nebo náběhu (zmenšených o margin)?"""
    dx, dy = abs(x-CX), abs(y-CY)
    if z < FLOOR_Z+margin or z > MOUTH_Z:
        return False
    if z <= LEAD_Z:
        return dx < CAV_X-margin and dy < CAV_Y-margin
    s = (z-LEAD_Z)/(MOUTH_Z-LEAD_Z)
    return dx < CAV_X+s*(LEAD_X-CAV_X)-margin and dy < CAV_Y+s*(LEAD_Y-CAV_Y)-margin


def is_support(role):
    return 'support' in role.lower()


def support_region(y, z):
    if z > 234.5 and y >= 28.:
        return 'vez-pod-hornim-uchem'
    if y >= 29.3:
        return 'pod-zadni-deskou'
    if y >= 19.:
        return 'kanal-pod-zebrem'
    if z >= 180.:
        return 'pod-limcem'
    if z <= 56.:
        return 'pod-koncovkou'
    return 'pod-telem'


def support_scan(layers, frame):
    """Kde jsou podpory v rámci dílu a jestli je nějaká v dutině, náběhu nebo otvoru."""
    F = Frame(frame)
    regions = {}
    in_void = in_hole = 0
    for l in layers.values():
        for s in l['strokes']:
            if not is_support(s[4]):
                continue
            length = math.hypot(s[2]-s[0], s[3]-s[1])
            steps = max(1, int(length/.5))
            void = hole = False
            for k in range(steps+1):
                t = k/steps
                x, y, z = F.part(s[0]+t*(s[2]-s[0]), s[1]+t*(s[3]-s[1]), l['z']-.1)
                void = void or void_at(x, y, z)
                hole = hole or any(PLATE_Y[0] <= y <= PLATE_Y[1] and math.hypot(x-h['x'], z-h['z']) < HOLE_R for h in HOLES)
            in_void += void
            in_hole += hole
            x, y, z = F.part((s[0]+s[2])/2, (s[1]+s[3])/2, l['z']-.1)
            r = regions.setdefault(support_region(y, z), {'strokes': 0, 'interface_strokes': 0, 'length_mm': 0., 'print_z_mm': [l['z'], l['z']],
                                                          'part_y_mm': [y, y], 'part_z_mm': [z, z]})
            r['strokes'] += 1
            r['interface_strokes'] += 'interface' in s[4].lower()
            r['length_mm'] += length
            r['print_z_mm'] = [min(r['print_z_mm'][0], l['z']), max(r['print_z_mm'][1], l['z'])]
            r['part_y_mm'] = [min(r['part_y_mm'][0], y), max(r['part_y_mm'][1], y)]
            r['part_z_mm'] = [min(r['part_z_mm'][0], z), max(r['part_z_mm'][1], z)]
    for r in regions.values():
        r['length_mm'] = round(r['length_mm'])
        r['part_y_mm'] = [round(q, 1) for q in r['part_y_mm']]
        r['part_z_mm'] = [round(q, 1) for q in r['part_z_mm']]
    return {'regions': regions, 'strokes_in_cavity_or_lead_in': in_void, 'strokes_in_mount_holes': in_hole}


def tower_report(layers, frame):
    F = Frame(frame)
    per_layer = Counter()
    ys, zs = [], []
    for l in layers.values():
        if l['z'] < 15. or l['z'] > 62.:
            continue
        for s in l['strokes']:
            if not is_support(s[4]):
                continue
            a, b = F.part(s[0], s[1], l['z']-.1), F.part(s[2], s[3], l['z']-.1)
            if min(a[2], b[2]) > 234.5 and min(a[1], b[1]) >= 28.:
                per_layer[l['z']] += 1
                ys += [a[1], b[1]]
                zs += [a[2], b[2]]
    return {'print_z_mm': [min(per_layer), max(per_layer)], 'footprint_y_mm': [round(min(ys), 2), round(max(ys), 2)], 'footprint_z_mm': [round(min(zs), 2), round(max(zs), 2)],
            'average_strokes_per_layer': round(sum(per_layer.values())/len(per_layer), 1)}


class LayerIndex:
    """Tahy po vrstvách v mřížce 1 mm, zvlášť model a podpory, pro dotaz: co leží přesně nad bodem."""

    def __init__(self, layers, z_keep):
        self.tops = sorted(l['z'] for l in layers.values())
        self.model, self.support = {}, {}
        for l in layers.values():
            if not z_keep(l['z']):
                continue
            for s in l['strokes']:
                if s[4] == 'Brim':
                    continue
                store = self.support if is_support(s[4]) else self.model
                seg = math.hypot(s[2]-s[0], s[3]-s[1])
                steps = max(1, int(seg))
                for k in range(steps+1):
                    key = (round(l['z'], 2), int((s[0]+k/steps*(s[2]-s[0]))//1), int((s[1]+k/steps*(s[3]-s[1]))//1))
                    store.setdefault(key, []).append(s)

    @staticmethod
    def near(store, z, x, y, r):
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                for s in store.get((round(z, 2), int(x//1)+a, int(y//1)+b), ()):
                    dx, dy = s[2]-s[0], s[3]-s[1]
                    m = dx*dx+dy*dy
                    t = max(0., min(1., ((x-s[0])*dx+(y-s[1])*dy)/m)) if m else 0.
                    if math.hypot(x-s[0]-t*dx, y-s[1]-t*dy) <= r:
                        return s
        return None


def sample_ceilings(frame, spacing=1.):
    """Body na dolních plochách STL, které potřebují podepřít: ploché stropy a 45° plochy ve vynucené zóně."""
    out = []
    for t in read_stl(SOURCE):
        a, b, c = t[:3], t[3:6], t[6:9]
        u = [b[i]-a[i] for i in range(3)]
        v = [c[i]-a[i] for i in range(3)]
        n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        m = math.sqrt(sum(q*q for q in n))
        if not m or n[0]/m >= -1e-6:
            continue
        slope = math.degrees(math.acos(min(1., -n[0]/m)))
        mx, my, mz = [(a[i]+b[i]+c[i])/3 for i in range(3)]
        flat = slope < 12.
        low45 = slope < 46. and mx <= 15.3 and my <= 19.2
        if not (flat or low45):
            continue
        area = m/2
        count = max(1, int(math.sqrt(area)/spacing))
        for i in range(count):
            for j in range(count-i):
                r1, r2 = (i+1/3)/count, (j+1/3)/count
                r3 = 1-r1-r2
                x, y, z = [r1*a[k]+r2*b[k]+r3*c[k] for k in range(3)]
                out.append((x, y, z, area/(count*(count+1)/2), slope))
    return out


def ceiling_group(x, y, z, slope):
    if x < .1:
        return 'kontakt-s-podlozkou'
    if abs(y-CY) <= LEAD_Y+.01 and FLOOR_Z-.01 <= z <= MOUTH_Z+.01 and CX-LEAD_X-.01 <= x <= CX+LEAD_X+.01 and x > 16:
        return 'strop-dutiny-a-nabehu'
    for h in HOLES:
        if PLATE_Y[0] <= y <= PLATE_Y[1] and math.hypot(x-h['x'], z-h['z']) < HOLE_R+1.2:
            return 'montazni-otvor'
    if y > 29.7 and z > 234.5 and x > 60:
        return 'horni-ucho'
    if y > 29.7:
        return 'zadni-deska'
    if abs(x-36.) < .3:
        return 'zebro-strop'
    if abs(x-25.) < .3:
        return 'blok-u-konce-strop'
    if abs(x-17.) < .3:
        return 'blok-u-usti-strop'
    if x <= 16.5 and z >= 180:
        return 'limec-a-telo-u-usti'
    if x <= 16.5 and z <= 56:
        return 'koncovka-a-telo-u-konce'
    if x <= 16.5:
        return 'hreben-tela'
    return 'ostatni'


def ceiling_reach(layers, frame):
    """Pro body stropů: nejnižší stopa modelu nad bodem a nejvyšší podpora těsně pod ní. Na plochých stropech je rozdíl skutečný vzduch."""
    samples = sample_ceilings(frame)
    want = set()
    for s in samples:
        h = round(s[0]*5)/5
        for k in range(-7, 7):
            want.add(round(h+k*.2, 1))
    index = LayerIndex(layers, lambda z: round(z, 1) in want)
    tops = index.tops
    groups = {}
    for x, y, z, area, slope in samples:
        p = rot(x, y, z)
        bx, by = p[0]-frame['lo'][0]+frame['t'][0], p[1]-frame['lo'][1]+frame['t'][1]
        g = groups.setdefault(ceiling_group(x, y, z, slope), {'area': 0., 'supported': 0., 'flat': 0., 'hist': Counter(), 'none_y': [], 'tops': Counter()})
        g['area'] += area
        model_top = next((t for t in tops if x-.05 <= t <= x+1.05 and index.near(index.model, t, bx, by, .3)), None)
        ref = model_top if model_top is not None else x+.2
        support_top = next((t for t in reversed(tops) if ref-1.25 <= t <= ref-.15 and index.near(index.support, t, bx, by, .55)), None)
        if model_top is not None:
            g['tops'][round(model_top, 1)] += area
        if support_top is not None:
            g['supported'] += area
        else:
            g['none_y'].append(y)
        if slope < 12. and model_top is not None and support_top is not None:
            g['flat'] += area
            g['hist'][format(round(model_top-.2-support_top, 2), '.1f')] += area
    return {k: {'area_mm2': round(v['area'], 1), 'supported_area_mm2': round(v['supported'], 1),
                'air_gap_mm_by_area_on_flat_ceilings': {a: round(b, 1) for a, b in sorted(v['hist'].items())},
                'first_model_layer_tops_mm': dict(v['tops'].most_common(3)),
                'unsupported_part_y_mm': [round(min(v['none_y']), 1), round(max(v['none_y']), 1)] if v['none_y'] else None} for k, v in sorted(groups.items())}


def ridge_gap(layers, frame):
    """Osa dlouhého hřebene těla (Y = rovina čepele, Z 56–180): první stopa modelu a rozhraní pod ní."""
    keep = {round(9.+k*.2, 1) for k in range(20)}
    index = LayerIndex(layers, lambda z: round(z, 1) in keep)
    tops = [t for t in index.tops if round(t, 1) in keep]
    first, close, wide = Counter(), Counter(), Counter()
    planes = 0
    for z in range(56, 181):
        p = rot(9.91, CY, float(z))
        bx, by = p[0]-frame['lo'][0]+frame['t'][0], p[1]-frame['lo'][1]+frame['t'][1]
        model = next((t for t in tops if index.near(index.model, t, bx, by, .25)), None)
        planes += 1
        first[str(model)] += 1
        ref = model if model is not None else 99.
        close[str(next((t for t in reversed(tops) if t <= ref-.15 and index.near(index.support, t, bx, by, .3)), None))] += 1
        wide[str(next((t for t in reversed(tops) if t <= ref-.15 and index.near(index.support, t, bx, by, .6)), None))] += 1
    return {'planes': planes, 'first_model_layer_top_mm': dict(first), 'support_top_mm_within_0_3_mm_of_axis': dict(close), 'support_top_mm_within_0_6_mm_of_axis': dict(wide),
            'note': 'Rozhraní má rozteč 0,5 mm a na 45° plochách schody. Do 0,3 mm je přímo pod stopou, do 0,6 mm zahrnuje i sousední schod.'}


def height_field(frame, cell=.5):
    """Nejnižší plocha modelu nad každou buňkou podložky: co leží nad ní, má pod sebou volno až k podložce."""
    field = {}
    for t in read_stl(TARGET):
        a, b, c = [(t[i]+frame['t'][0], t[i+1]+frame['t'][1], t[i+2]) for i in (0, 3, 6)]
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-9:
            continue
        x0, x1 = min(a[0], b[0], c[0]), max(a[0], b[0], c[0])
        y0, y1 = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
        for ix in range(int(x0/cell), int(x1/cell)+2):
            x = (ix+.5)*cell
            for iy in range(int(y0/cell), int(y1/cell)+2):
                y = (iy+.5)*cell
                u = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
                v = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
                w = 1-u-v
                if u < -1e-9 or v < -1e-9 or w < -1e-9:
                    continue
                z = u*a[2]+v*b[2]+w*c[2]
                if z < field.get((ix, iy), 1e9):
                    field[(ix, iy)] = z
    return field, cell


def on_model(layers, frame, field, cell):
    """Podpůrné tahy, pod kterými leží model. Tři buňky tolerance kvůli tahům těsně u stěny."""
    F = Frame(frame)
    groups = {}
    free = hit = 0
    points = []
    for l in layers.values():
        for bx, by, bx2, by2, role, *_ in l['strokes']:
            if not is_support(role):
                continue
            seg = math.hypot(bx2-bx, by2-by)
            steps = max(1, int(seg))
            for k in range(steps+1):
                x, y = bx+k/steps*(bx2-bx), by+k/steps*(by2-by)
                ix, iy = int(x/cell), int(y/cell)
                low = max(field.get((ix+a, iy+b), 1e9) for a in (-1, 0, 1) for b in (-1, 0, 1))
                if l['z']-.2 > low+.25:
                    hit += 1
                    p = F.part(x, y, l['z']-.1)
                    points.append(p)
                    key = (round(p[1]/4)*4, round(p[2]/12)*12)
                    g = groups.setdefault(key, {'n': 0, 'z': [l['z'], l['z']], 'land': 1e9})
                    g['n'] += 1
                    g['z'] = [min(g['z'][0], l['z']), max(g['z'][1], l['z'])]
                    g['land'] = min(g['land'], low)
                else:
                    free += 1
    return {'points': points, 'samples_free_to_bed': free, 'samples_above_model': hit,
            'groups_y_z': {f'Y{k[0]} Z{k[1]}': {'samples': v['n'], 'print_z': v['z'], 'model_below_mm': round(v['land'], 1)} for k, v in sorted(groups.items())}}


def build(work, process_over=None, modifiers=MODIFIERS):
    """STL, geometrie, export nastavení, modifikátory, řez. Vrací projekt a rámec. Nic nekontroluje nad rámec zápisu."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    lo = make_stl()
    mesh, rigid = rigid_check(lo)
    t = [(BED-mesh['size'][0])/2, (BED-mesh['size'][1])/2, 0.]
    frame = {'lo': lo, 't': t}
    meta = {'file': '../../stl/pouzdro-zdobene-nalezato.stl', 'source_sha256': rigid['rotated_sha256'], 'supports': True,
            'support_note': 'viz README.md', 'critical_z_mm': [.2, 4.4, 9.8, 10., 14., 15.6, 15.8, 17.2, 25.2, 26.2, 36.2, 39., 62.4, 62.6, 64.2, 70., 78.],
            'blade_path': {}, 'mount_holes': [], 'mount_hole_diameter_mm': 5.5, 'wall_plate_y_mm': list(PLATE_Y)}
    mesh.update(meta)
    meshes = {NAME: mesh}
    B.HERE = work
    B.BRIM = BRIM
    plate = B.make_geometry(1, {'items': [{'id': NAME, 'name': f'01_{NAME}_01', 'xy': t[:2]}], 'colour': '#B3141D'}, meshes)
    profile = {'kind': 'cervena', 'mvs': '8', 'nozzle': '205', 'initial_nozzle': '215', 'bed': '50'}
    plate.update({'colour': '#B3141D', 'material_name': 'cervena', 'profile': profile, 'supports_enabled': True})
    process_path, filament_path = B.create_profiles(1, plate['colour'], plate['material_name'], profile, True)
    process = json.loads(process_path.read_text())
    name = 'Zdobené pouzdro V05 naležato s podporami 0.20 mm navrh @Kobra X'
    process.update({'name': name, 'print_settings_id': name, **PROCESS, **(process_over or {})})
    process_path.write_text(json.dumps(process, ensure_ascii=False, indent=2)+'\n')
    configured, sliced = work/'configured.3mf', work/'sliced.3mf'
    B.run_cli([B.CLI, '--datadir', str(work/'datadir-export'), '--load-settings', f'{B.MACHINE};{process_path}', '--load-filaments', str(filament_path),
               '--arrange', '0', '--orient', '0', '--export-3mf', configured.name, '--outputdir', str(work), str(work/plate['geometry'])], work/'export.log')
    if modifiers:
        add_modifiers(configured, frame, modifiers)
    B.run_cli([B.CLI, '--datadir', str(work/'datadir-slice'), '--arrange', '0', '--orient', '0', '--slice', '0',
               '--export-3mf', sliced.name, '--outputdir', str(work), str(configured)], work/'slice.log')
    return {'work': work, 'sliced': sliced, 'frame': frame, 'plate': plate, 'meshes': meshes, 'rigid': rigid,
            'process_path': process_path, 'filament_path': filament_path}


def openings_lying(L, frame):
    """Dutina, náběh a oba otvory ve skutečných tazích. Kontroly svislého builderu převedené do rámce dílu."""
    F = Frame(frame)
    blade = (CY-BLADE_Y, FLOOR_Z, CY+BLADE_Y, 300.)
    seated = (CY-BLADE_Y, SEAT_TIP_Z, CY+BLADE_Y, 300.)
    cavity = (CY-CAV_Y, FLOOR_Z, CY+CAV_Y, LEAD_Z)
    closure = (CY-BLADE_Y, 14.5, CY+BLADE_Y, FLOOR_Z)
    centre = (CY-1.5, 30., CY+1.5, 210.)
    near = lambda s, r, m=3.: max(s[0], s[2]) >= r[0]-m and min(s[0], s[2]) <= r[2]+m and max(s[1], s[3]) >= r[1]-m and min(s[1], s[3]) <= r[3]+m
    crossing = cav_cross = 0
    min_blade = min_cav = math.inf
    blade_layers = cav_layers = closed = 0
    void_hits = Counter()
    slot_closed = {}
    holes = [{'x_mm': h['x'], 'z_mm': h['z'], 'layers_checked': 0, 'strokes_inside_inscribed_circle': 0, 'minimum_stroke_distance_mm': math.inf} for h in HOLES]
    for l in L.values():
        top, x = l['z'], l['z']-.1
        in_blade = top-.2 < CX+BLADE_X-1e-6 and top > CX-BLADE_X+1e-6
        in_cav = CX-CAV_X+1e-6 < x < CX+CAV_X-1e-6
        in_lead = abs(x-CX) < LEAD_X
        blade_layers += in_blade
        cav_layers += in_cav
        is_closed = False
        is_slot_closed = False
        windows = []
        for h, rec in zip(HOLES, holes):
            if abs(x-h['x']) < HOLE_R:
                c = math.sqrt(HOLE_R**2-(x-h['x'])**2)
                windows.append((rec, (PLATE_Y[0], h['z']-c, PLATE_Y[1], h['z']+c)))
                rec['layers_checked'] += 1
        for s in l['strokes']:
            if s[4] == 'Brim':
                continue
            a, b = F.part(s[0], s[1], x), F.part(s[2], s[3], x)
            seg = (a[1], a[2], b[1], b[2])
            model = not is_support(s[4])
            half = s[5]/2
            if in_blade and near(seg, blade):
                d = B.rect_distance(*seg, blade)
                crossing += d == 0.
                min_blade = min(min_blade, B.rect_distance(*seg, seated)-half)
            if in_blade and model and not is_closed and near(seg, closure, 0.) and B.rect_distance(*seg, closure) == 0.:
                is_closed = True
            if model and not is_slot_closed and near(seg, centre, 0.) and B.rect_distance(*seg, centre) == 0.:
                is_slot_closed = True
            if in_cav and near(seg, cavity):
                d = B.rect_distance(*seg, cavity)
                cav_cross += d == 0.
                min_cav = min(min_cav, d-half)
            if in_lead and near(seg, (CY-LEAD_Y, FLOOR_Z, CY+LEAD_Y, MOUTH_Z)):
                length = math.hypot(s[2]-s[0], s[3]-s[1])
                steps = max(1, int(length/.25))
                if any(void_at(x, seg[0]+k/steps*(seg[2]-seg[0]), seg[1]+k/steps*(seg[3]-seg[1])) for k in range(steps+1)):
                    void_hits['support' if not model else 'model'] += 1
            for rec, win in windows:
                if near(seg, win):
                    d = B.rect_distance(*seg, win)
                    rec['strokes_inside_inscribed_circle'] += d == 0.
                    rec['minimum_stroke_distance_mm'] = min(rec['minimum_stroke_distance_mm'], d)
        closed += in_blade and is_closed
        slot_closed[round(top, 2)] = is_slot_closed
    open_tops = sorted(t for t, c in slot_closed.items() if not c and 14. < t < 64.)
    first_open, last_open = open_tops[0], open_tops[-1]
    B.require(all(not slot_closed.get(round(first_open+k*.2, 2), True) for k in range(int(round((last_open-first_open)/.2))+1)), 'Dutina není souvisle otevřená')
    return {'strokes_crossing_blade_rect_floor_to_mouth': crossing, 'layers_checked_floor_to_mouth': blade_layers, 'minimum_stroke_edge_distance_to_blade_rect_mm': min_blade,
            'strokes_crossing_cavity_rect': cav_cross, 'cavity_layers_checked': cav_layers, 'minimum_stroke_edge_distance_to_cavity_rect_mm': min_cav,
            'strokes_in_cavity_or_lead_in_by_kind': {'model': void_hits['model'], 'support': void_hits['support']},
            'closed_end_layers_with_strokes_under_blade': closed, 'mount_holes': holes,
            'printed_slot': {'first_open_layer_top_mm': first_open, 'last_open_layer_top_mm': last_open, 'floor_mm': round(first_open-.2, 2), 'ceiling_mm': last_open,
                             'printed_width_mm': round(last_open-first_open+.2, 2), 'clearance_blade_low_side_mm': round(CX-BLADE_X-(first_open-.2), 2), 'clearance_blade_high_side_mm': round(last_open-(CX+BLADE_X), 2)},
            'method': 'Tahy z G-code převedené inverzní tuhou transformací do rámce svislého dílu. Vrstva je v rovině X dílu, obdélníky v rovině Y, Z. Odstupy jsou od hrany tahu podle jeho WIDTH.'}


def bridges(L, frame):
    """Směr mostů nad hlavní dutinou a uzavírání náběhu: úhel od krátké osy Y dílu."""
    F = Frame(frame)
    main, connectors = [], []
    lead = Counter()
    lead_angle = lead_len = 0.
    closing_layers = set()
    for l in L.values():
        if not 62. <= l['z'] <= 65.:
            continue
        x = l['z']-.1
        for s in l['strokes']:
            a, b = F.part(s[0], s[1], x), F.part(s[2], s[3], x)
            my, mz = (a[1]+b[1])/2, (a[2]+b[2])/2
            length = math.hypot(b[1]-a[1], b[2]-a[2])
            angle = math.degrees(math.atan2(abs(b[2]-a[2]), abs(b[1]-a[1])))
            if s[4] == 'Bridge' and FLOOR_Z-.5 <= mz <= LEAD_Z and abs(my-CY) <= CAV_Y+1.2:
                # Spojky do 0,6 mm mezi konci mostů leží na stěnách vedle dutiny, nepřeklenují ji.
                if length >= 1.:
                    main.append((length, angle, l['z'], mz))
                else:
                    connectors.append(abs(my-CY))
            if s[4] == 'Overhang wall' and LEAD_Z-1 <= mz <= MOUTH_Z+.2:
                half = CAV_Y+max(0., mz-LEAD_Z)/(MOUTH_Z-LEAD_Z)*(LEAD_Y-CAV_Y)
                if abs(my-CY) <= half+.6 and length >= 1.:
                    lead['segments'] += 1
                    closing_layers.add(l['z'])
                    lead_angle = max(lead_angle, angle)
                    lead_len = max(lead_len, length)
    B.require(main, 'Nad dutinou není most')
    return {'main_cavity_bridge_segments': len(main), 'main_cavity_bridge_layer_tops_mm': sorted({m[2] for m in main}),
            'main_cavity_bridge_max_stroke_length_mm': round(max(m[0] for m in main), 3), 'main_cavity_bridge_max_angle_from_short_axis_deg': round(max(m[1] for m in main), 4),
            'main_cavity_bridge_part_z_range_mm': [round(min(m[3] for m in main), 2), round(max(m[3] for m in main), 2)],
            'main_cavity_nominal_span_mm': 2*CAV_Y, 'connector_stubs_on_side_walls': len(connectors), 'connector_stubs_min_distance_from_blade_plane_mm': round(min(connectors), 2) if connectors else None, 'lead_in_closing_overhang_segments': lead['segments'], 'lead_in_closing_layer_tops_mm': sorted(closing_layers),
            'lead_in_max_angle_from_short_axis_deg': round(lead_angle, 4), 'lead_in_max_stroke_length_mm': round(lead_len, 3), 'lead_in_nominal_span_at_mouth_mm': 2*LEAD_Y}


def centroid(tris):
    vol = 0.
    acc = [0., 0., 0.]
    for t in tris:
        a, b, c = t[:3], t[3:6], t[6:9]
        v = (a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        vol += v
        for i in range(3):
            acc[i] += v*(a[i]+b[i]+c[i])/4
    return [q/vol for q in acc]


def hull(points):
    pts = sorted(set(points))
    def half(seq):
        out = []
        for p in seq:
            while len(out) > 1 and (out[-1][0]-out[-2][0])*(p[1]-out[-2][1])-(out[-1][1]-out[-2][1])*(p[0]-out[-2][0]) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]
    return half(pts)+half(pts[::-1])


def hull_margin(poly, p):
    """Kladná vzdálenost bodu od nejbližší hrany konvexního obalu, záporná když leží mimo."""
    best = math.inf
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        m = math.hypot(b[0]-a[0], b[1]-a[1])
        best = min(best, ((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))/m)
    return best


def first_layer(L, frame):
    F = Frame(frame)
    strokes = L[0]['strokes']
    area = Counter()
    ends = {k: {'wall': 0., 'attached': 0., 'brim_area': 0., 'model_area': 0., 'gap': 9.} for k in ('u-konce', 'u-usti')}
    brim = [s for s in strokes if s[4] == 'Brim']
    for s in strokes:
        length = math.hypot(s[2]-s[0], s[3]-s[1])
        area['brim' if s[4] == 'Brim' else 'podpora' if is_support(s[4]) else 'model'] += length*s[5]
        z = F.part((s[0]+s[2])/2, (s[1]+s[3])/2, .1)[2]
        end = ends['u-konce' if z < 124 else 'u-usti']
        if s[4] == 'Brim':
            end['brim_area'] += length*s[5]
        elif not is_support(s[4]):
            end['model_area'] += length*s[5]
        if s[4] == 'Outer wall':
            steps = max(1, int(length/.5))
            for k in range(steps):
                x, y = s[0]+(k+.5)/steps*(s[2]-s[0]), s[1]+(k+.5)/steps*(s[3]-s[1])
                end['wall'] += length/steps
                for q in brim:
                    dx, dy = q[2]-q[0], q[3]-q[1]
                    m = dx*dx+dy*dy
                    t = max(0., min(1., ((x-q[0])*dx+(y-q[1])*dy)/m)) if m else 0.
                    gap = math.hypot(x-q[0]-t*dx, y-q[1]-t*dy)-(s[5]+q[5])/2
                    end['gap'] = min(end['gap'], gap)
                    if gap <= .02:
                        end['attached'] += length/steps
                        break
    com = centroid(read_stl(SOURCE))
    p = rot(*com)
    cp = (p[0]-frame['lo'][0]+frame['t'][0], p[1]-frame['lo'][1]+frame['t'][1])
    ends_pts = lambda test: [q for s in strokes if test(s) for q in ((s[0], s[1]), (s[2], s[3]))]
    margin_all = hull_margin(hull(ends_pts(lambda s: s[4] != 'Brim')), cp)
    margin_model = hull_margin(hull(ends_pts(lambda s: s[4] != 'Brim' and not is_support(s[4]))), cp)
    return {'extruded_area_mm2': {k: round(v, 1) for k, v in area.items()}, 'cad_contact_area_mm2': 67.2,
            'ends': {k: {'model_area_mm2': round(v['model_area'], 1), 'brim_area_mm2': round(v['brim_area'], 1), 'outer_wall_with_touching_brim_share': round(v['attached']/v['wall'], 3), 'smallest_wall_to_brim_edge_gap_mm': round(v['gap'], 3)} for k, v in ends.items()},
            'centre_of_mass_part_frame_mm': [round(q, 2) for q in com], 'centre_of_mass_print_mm': [round(cp[0], 2), round(cp[1], 2), round(p[2], 2)],
            'com_margin_inside_first_layer_with_supports_mm': round(margin_all, 2), 'com_margin_inside_model_contact_only_mm': round(margin_model, 2)}


def ray_free(tris, x0, y0, z0, sign):
    """Volná cesta z bodu podél osy Y dílu ven z modelu?"""
    for t in tris:
        a, b, c = t[:3], t[3:6], t[6:9]
        den = (b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
        if abs(den) < 1e-12:
            continue
        u = ((b[2]-c[2])*(x0-c[0])+(c[0]-b[0])*(z0-c[2]))/den
        v = ((c[2]-a[2])*(x0-c[0])+(a[0]-c[0])*(z0-c[2]))/den
        w = 1-u-v
        if u < 0 or v < 0 or w < 0:
            continue
        if sign*(u*a[1]+v*b[1]+w*c[1]-y0) > 0:
            return False
    return True


def removal(L, frame, field, cell):
    """Odstranitelnost jako geometrie: každý vzorek podpory má volno dolů k podložce, nebo volný výstup podél Y dílu."""
    report = on_model(L, frame, field, cell)
    points = report.pop('points')
    tris = read_stl(SOURCE)
    sample = points[::max(1, len(points)//40)]
    free = [p for p in sample if ray_free(tris, p[0], p[1], p[2], 1.) or ray_free(tris, p[0], p[1], p[2], -1.)]
    report.update({'above_model_samples_tested_along_part_y': len(sample), 'above_model_samples_with_free_exit_along_part_y': len(free)})
    total = report['samples_free_to_bed']+report['samples_above_model']
    report['share_free_to_bed'] = round(report['samples_free_to_bed']/total, 4)
    return report


def legend_fix(path, text):
    im = Image.open(path).convert('RGB')
    d = ImageDraw.Draw(im)
    d.rectangle((0, im.height-34, im.width, im.height), fill='#fafbfc')
    d.text((20, im.height-27), text, fill='#536871', font=ImageFont.truetype(B.FONT, 17))
    im.save(path)


def section_strokes(L, frame, z0, half=.3):
    F = Frame(frame)
    out = []
    for l in L.values():
        x = l['z']-.1
        for s in l['strokes']:
            a, b = F.part(s[0], s[1], x), F.part(s[2], s[3], x)
            lo_z, hi_z = min(a[2], b[2]), max(a[2], b[2])
            if hi_z < z0-half or lo_z > z0+half:
                continue
            if abs(b[2]-a[2]) < 1e-9:
                y0, y1 = a[1], b[1]
            else:
                t0 = max(0., min(1., (z0-half-a[2])/(b[2]-a[2])))
                t1 = max(0., min(1., (z0+half-a[2])/(b[2]-a[2])))
                y0, y1 = a[1]+t0*(b[1]-a[1]), a[1]+t1*(b[1]-a[1])
            out.append((min(y0, y1), max(y0, y1), l['z'], s[4]))
    return out


def render_overview(L, frame, facts, path):
    font = lambda n, bold=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else B.FONT, n)
    W, H = 1820, 1650
    im = Image.new('RGB', (W, H), '#fafbfc')
    d = ImageDraw.Draw(im)
    d.text((40, 24), 'Zdobené pouzdro V05 · tisk naležato s podporami · 1 kus', fill=INK, font=font(34, True))
    d.text((42, 70), 'Kobra X 0,4 mm. Dlouhý bok dole, dlouhá osa vodorovně a 45° v rovině podložky. Vše je z G-code uloženého v projektu.', fill=MUTED, font=font(20))
    # A: podložka shora
    s, ox, oy = 2.3, 40, 150
    xy = lambda x, y: (ox+s*x, oy+s*(BED-y))
    d.text((ox, oy-34), 'Podložka shora, 1. vrstva', fill=INK, font=font(22, True))
    d.rectangle((xy(0, BED), xy(BED, 0)), fill='#edf0f2', outline='#55717b', width=3)
    d.line((xy(0, 0), xy(BED, 0)), fill='#b85042', width=5)
    d.text((xy(92, 0)[0], xy(0, 0)[1]+8), 'předek tiskárny', fill='#b85042', font=font(17))
    t = frame['t']
    for q in read_stl(TARGET):
        d.polygon([xy(q[i]+t[0], q[i+1]+t[1]) for i in (0, 3, 6)], fill='#e7c4c4')
    for q in L[0]['strokes']:
        d.line((xy(q[0], q[1]), xy(q[2], q[3])), fill=COL.get(q[4], COL['model']), width=1)
    place = lambda x, y, z: (rot(x, y, z)[0]-frame['lo'][0]+t[0], rot(x, y, z)[1]-frame['lo'][1]+t[1])
    cx, cy = xy(*place(39, 12, 124))
    d.rounded_rectangle((cx-24, cy-20, cx+24, cy+20), radius=6, fill='white', outline=INK)
    d.text((cx-14, cy-14), '01', fill=INK, font=font(23, True))
    for label, p, dx, dy in (('ústí', place(39, 8, 262), -28, 0), ('uzavřený konec', place(39, 8, -22), -235, -70)):
        x, y = xy(*p)
        d.text((x+dx, y+dy), label, fill=INK, font=font(18, True))
    # B: bokorys
    s2, bx, by = 4., 680, 150+78*4.+14
    d.text((bx, 116), 'Bokorys: skutečné podpory pod dílem', fill=INK, font=font(22, True))
    Y = lambda z: by-z*s2
    for q in read_stl(SOURCE):
        d.polygon([(bx+q[i+2]*s2, Y(q[i])) for i in (0, 3, 6)], fill='#ecdcdc')
    F = Frame(frame)
    for l in L.values():
        x = l['z']-.1
        for q in l['strokes']:
            if not is_support(q[4]):
                continue
            a, b = F.part(q[0], q[1], x), F.part(q[2], q[3], x)
            d.line((bx+a[2]*s2, Y(l['z']), bx+b[2]*s2, Y(l['z'])), fill=COL.get(q[4], COL['Support']), width=1)
    d.line((bx-8, by, bx+248*s2+8, by), fill='#55717b', width=3)
    d.text((bx, by+6), 'uzavřený konec', fill=INK, font=font(17))
    d.text((bx+248*s2-40, by+6), 'ústí', fill=INK, font=font(17))
    d.text((bx+390, by+6), 'podložka', fill='#55717b', font=font(17))
    ty = by+44
    for row in facts:
        d.text((bx, ty), row, fill=INK, font=font(19))
        ty += 29
    # C: příčné řezy
    s3, sy = 7.2, 850
    d.text((40, sy-30), 'Příčné řezy skutečnými tahy (deska vpravo, tisková výška nahoru)', fill=INK, font=font(22, True))
    panels = [(7, 'Z 7: dolní otvor'), (30, 'Z 30: koncovka'), (120, 'Z 120: střed délky'), (226, 'Z 226: náběh'), (241, 'Z 241: horní ucho a otvor')]
    pw = 350
    base = sy+78*s3+40
    for n, (z0, title) in enumerate(panels):
        px = 40+n*pw
        d.text((px, sy), title, fill=INK, font=font(19, True))
        d.line((px, base, px+38*s3, base), fill='#55717b', width=2)
        P = lambda y, h: (px+(y+2.)*s3, base-h*s3)
        for y0, y1, h, role in section_strokes(L, frame, z0):
            x0, yy = P(y0, h)
            x1, _ = P(y1, h)
            d.line((x0, yy, max(x1, x0+1.5), yy), fill=COL.get(role, COL['model']), width=2)
        if FLOOR_Z < z0 < MOUTH_Z:
            f = max(0., z0-LEAD_Z)/(MOUTH_Z-LEAD_Z)
            hx, hy = CAV_X+f*(LEAD_X-CAV_X), CAV_Y+f*(LEAD_Y-CAV_Y)
            d.rectangle((P(CY-hy, CX+hx), P(CY+hy, CX-hx)), outline='#d81b2c', width=2)
        for h in HOLES:
            if abs(z0-h['z']) < 1:
                d.rectangle((P(PLATE_Y[0], h['x']+HOLE_R), P(PLATE_Y[1], h['x']-HOLE_R)), outline='#d81b2c', width=2)
    lx, ly = 40, base+18
    for name, key in (('model', 'model'), ('podpora', 'Support'), ('rozhraní podpory', 'Support interface'), ('most', 'Bridge'), ('převisová stěna', 'Overhang wall'), ('brim', 'Brim')):
        d.rectangle((lx, ly+4, lx+22, ly+18), fill=COL[key])
        d.text((lx+28, ly), name, fill=INK, font=font(18))
        lx += 60+int(font(18).getlength(name))
    d.rectangle((lx, ly+4, lx+22, ly+18), outline='#d81b2c', width=2)
    d.text((lx+28, ly), 'jmenovitá dutina nebo otvor', fill=INK, font=font(18))
    d.text((40, ly+34), 'Digitální řez a kontrola drah. Fyzický tisk, odstranění podpor ani fit nože nejsou ověřené.', fill=MUTED, font=font(19))
    im.save(path)


def write_readme(result):
    r = result
    op, br, fl, rm = r['openings'], r['bridges'], r['first_layer'], r['removal']
    cz = lambda v, d=1: f'{v:.{d}f}'.replace('.', ',')
    rg = r['support_regions']
    names = {'pod-telem': 'Pod hřebenem a za tělem', 'pod-limcem': 'Pod límcem a tělem u ústí', 'pod-koncovkou': 'Pod koncovkou a tělem u dna',
             'kanal-pod-zebrem': 'Kanál mezi deskou a tělem, pod žebrem a bloky', 'pod-zadni-deskou': 'Pod zadní deskou', 'vez-pod-hornim-uchem': 'Pod horním uchem a kolem dolního ucha'}
    rows = '\n'.join(f"| {names[k]} | {v['strokes']} | {cz(v['length_mm']/1000)} m | {cz(v['print_z_mm'][0])}–{cz(v['print_z_mm'][1])} mm |" for k, v in sorted(rg.items(), key=lambda kv: -kv[1]['length_mm']))
    reach = r['ceiling_reach']
    ps = op['printed_slot']
    ridge = r['ridge']
    close = ridge['support_top_mm_within_0_3_mm_of_axis']
    ends = fl['ends']
    text = f"""# Kobra X — pouzdro V05 naležato s podporami

**Preferovaný tisk V05. Digitálně ověřený návrh, fyzický tisk ani odstranění podpor ověřené nejsou.**

Projekt: **[pouzdro-nalezato-kobra-x-pla-projekt.3mf](pouzdro-nalezato-kobra-x-pla-projekt.3mf)**, 1 kus. Otevřít jednou jako celek a nepřerovnávat. Pět blokátorů a tři vynucovače podpor jsou součástí téhož objektu, nejsou to další kusy.

[Přehled orientace, podpor a řezů](nahled-orientace-a-podpor.png) · [očíslovaná podložka](podlozka-01.png) · [skutečné vrstvy](podlozka-01-vrstvy.png) · [detail drah]({r['detail_preview']}) · [protokol](kontrola-nalezato.json)

## Proč tato varianta

Hlášení Jiřího, předané 3. 11. 2026 přes koordinátora:

- Ručně otočený tisk naležato bez podpor „propadal na visícím přechodu“.
- Původní svislá varianta: „na výšku to nevyšlo“. Konkrétní příčina není známá.

Který G-code se skutečně tiskl, není známé. Tyto zápisy nejsou důkaz příčiny.

## Orientace

- [STL naležato](../../stl/pouzdro-zdobene-nalezato.stl) je tuhé otočení svislého STL, otočení je v [generátoru](../../build_nalezato.py). Geometrie se nemění, odchylka vrcholů nejvýše {cz(r['rigid']['max_vertex_deviation_back_in_source_frame_mm'], 6)} mm.
- Dolů je dlouhý bok na straně spodního otvoru (X dílu = tisková výška), tisková výška {r['toolpaths']['maximum_extrusion_z_mm']:g} mm.
- Dlouhá osa je vodorovně a o 45° natočená v rovině podložky. Půdorys {cz(r['rigid']['size_mm'][0])} × {cz(r['rigid']['size_mm'][1])} mm se tak vejde i s plným brimem 8 mm. Rezerva všech extruzí od okraje je {cz(r['toolpaths']['minimum_extrusion_edge_margin_mm'])} mm.
- Strop dutiny přemosťuje jen krátkou osu 4,4 mm, u ústí až 8,8 mm. Díl má na podložce jen {cz(fl['cad_contact_area_mm2'])} mm² ve dvou koncích zadní desky, tělo začíná ve výšce 9,9 mm. Podpory jsou proto nosné.

## Podpory

{r['role_counts']['Support']} tahů podpory a {r['role_counts']['Support interface']} tahů rozhraní, odhadem {r['estimates']['support_mass_g']:.0f} g.

| Oblast | Tahy | Délka | Tisková výška |
|---|---:|---:|---|
{rows}

- **V dutině a náběhu {op['strokes_in_cavity_or_lead_in_by_kind']['support']} tahů podpory, v otvorech {sum(h['strokes_inside_inscribed_circle'] for h in op['mount_holes'])}.** Bez blokátoru dutiny by jich v dutině bylo {r['control_without_cavity_blocker']['strokes_in_cavity_or_lead_in']}, blokátor tedy skutečně pracuje.
- **Hřeben těla:** zapnutý tisk tenkých stěn posunul první stopu ze 10,4 na 10,2 mm, vzduch nad rozhraním je tak 0,2 mm místo 0,4 mm. Na {ridge['planes']} rovinách délky je přímo pod stopou rozhraní s vrchem 9,8 mm na {close.get('9.8', 0)} z nich, jinde leží nejbližší tah rozhraní dál, protože má rozteč 0,5 mm. Plochy 45° pod tělem a límcem jsou podepřené do výšky 15,3 mm.
- **Ploché stropy:** žebro ve výšce 36 mm, bloky 17 a 25 mm, deska 26 mm a horní ucho 64 mm mají podporu s mezerou nad rozhraním převážně 0,2 mm, viz protokol. Nejvýš 4,8 mm široký pruh žebra u těla podporu záměrně nemá a překlene ho most od těla.
- **Odstranění:** {cz(rm['share_free_to_bed']*100)} % vzorků podpor má volnou cestu k bývalé podložce. Zbytek je hlavně věž pod horním uchem na výstupku dolního ucha, z té má volný výstup podél Y {rm['above_model_samples_with_free_exit_along_part_y']} z {rm['above_model_samples_tested_along_part_y']} testovaných bodů. Věž má dolní mezeru 0 a řídkou patu na okraji desky, aby nespadla. Je přístupná zezadu i od ústí, ale patu může být nutné odstřihnout a začistit. Čisté odlomení bez stop se neslibuje.

## Tisk

Kobra X 0,4 mm, návrhový nekalibrovaný červený PLA: 0,20 mm, 4 stěny, 15 % gyroid, tryska 215/205 °C, podložka 50 °C, brim 8 mm, max. průtok 8 mm³/s. Podpory normal snug, nad rozhraním 0,2 mm, od stěn 0,4 mm. Červená je jen barva v projektu, při odeslání vybrat skutečnou cívku. Brim leží těsně u pásků modelu, bez mezery a bez kompenzace první vrstvy, aby se s nimi spojil. Odhad sliceru **{cz(r['estimates']['filament_g'])} g / {r['estimates']['printing_time']}**.

Po tisku: odstranit brim a koberec podpor, vylomit podpory z kanálu směrem k bývalé podložce, věž pod uchem odstřihnout u paty a místo začistit. Dutinu a otvory projet až po začištění.

## Kontrola tohoto řezu

| Kontrola | Výsledek |
|---|---|
| Vrstvy, kusy | {r['toolpaths']['layers']} vrstev, {r['toolpaths']['physical_parts']} kus, 1 tisknutelná součást, opravy sítě {r['project']['mesh_repairs']} |
| Objem proti svislému STL | {cz(r['rigid']['volume_source_mm3'], 2)} a {cz(r['rigid']['volume_rotated_mm3'], 2)} mm³, uzavřená jedna komponenta |
| Nové ostrovy | {r['islands']['unsupported']} nepodepřených |
| Dráha čepele 45 × 3 mm přes ústí | {op['strokes_crossing_blade_rect_floor_to_mouth']} tahů v {op['layers_checked_floor_to_mouth']} vrstvách, boční odstup hrany tahu nejméně {cz(op['minimum_stroke_edge_distance_to_blade_rect_mm'], 2)} mm |
| Dutina v tisku | otevřená od výšky {cz(ps['floor_mm'])} do {cz(ps['ceiling_mm'])} mm, tedy {cz(ps['printed_width_mm'])} mm; od čepele {cz(ps['clearance_blade_low_side_mm'])} a {cz(ps['clearance_blade_high_side_mm'])} mm |
| Most nad dutinou | {br['main_cavity_bridge_segments']} tahů do {cz(br['main_cavity_bridge_max_stroke_length_mm'])} mm včetně kotvení, odchylka od krátké osy nejvýš {cz(br['main_cavity_bridge_max_angle_from_short_axis_deg'], 3)}° |
| Uzavření náběhu | {br['lead_in_closing_overhang_segments']} převisových tahů, odchylka nejvýš {cz(br['lead_in_max_angle_from_short_axis_deg'], 3)}°, délka do {cz(br['lead_in_max_stroke_length_mm'])} mm |
| Montážní otvory | {', '.join(str(h['strokes_inside_inscribed_circle']) for h in op['mount_holes'])} tahů uvnitř kružnice Ø5,5 mm, po {', '.join(str(h['layers_checked']) for h in op['mount_holes'])} vrstvách |
| Brim | {fl['extruded_area_mm2']['brim']:.0f} mm²; dotýká se {ends['u-konce']['outer_wall_with_touching_brim_share']*100:.0f} % obvodu pásku u dna a {ends['u-usti']['outer_wall_with_touching_brim_share']*100:.0f} % u ústí, zbytek obvodu brim nemá |
| První vrstva | model {fl['extruded_area_mm2']['model']:.0f} mm², podpory {fl['extruded_area_mm2']['podpora']:.0f} mm²; těžiště {cz(fl['com_margin_inside_first_layer_with_supports_mm'])} mm uvnitř obalu s podporami, mimo samotný kontakt modelu |
| Největší průtok | {cz(r['toolpaths']['maximum_commanded_volumetric_flow_mm3_s_segments_at_least_0_1mm'], 3)} mm³/s |
| Svislé STL, FCStd a svislý projekt | bitově beze změny, hashe v protokolu |

Uložená varování sliceru: {', '.join(sorted(set(x.get('msg', '') for x in r['project']['warnings']))) or 'žádná'}. CLI hlášky: {'; '.join(r['cli_error_messages']) or 'žádné'}.

## Omezení

- Neověřeno: tisk, přilnavost, odstranění podpor a povrch po nich, kvalita mostů a stropu náběhu, fit nože, pevnost. Vrstvy jsou teď rovnoběžně s rovinou X = konst., pevnost se proti svislému tisku liší. Slicer ani graf drah to neprokážou.
- Těžiště leží mimo kontakt modelu, díl tedy nese koberec podpor a rozhraní bez pevného spoje. Přilnavost je největší riziko.
- Věž pod horním uchem je vysoká asi 50 mm a v osách tahů {cz(r['tower']['footprint_y_mm'][1]-r['tower']['footprint_y_mm'][0])} × {cz(r['tower']['footprint_z_mm'][1]-r['tower']['footprint_z_mm'][0])} mm v půdorysu. Je to nejštíhlejší podpora řezu, sledovat ji od výšky asi 40 mm.
- Před tiskem změřit na noži vzdálenost od špičky k začátku širší rukojeti, jak uvádí [README revize](../../README.md).
- Projekt nebyl otevřen v GUI sliceru. Tiskárna nebyla ovládána.

Starší nesoulad, který tato varianta neřeší: `rozlozeni/podlozka-01-geometrie.3mf` má už před touto úlohou hash `e0d2d8ce…` místo hodnoty ve starém manifestu. Soubor ani `stl/pouzdro-zdobene.3mf` nebyly obnoveny ani změněny.

Regenerace: `python3 ../../build_nalezato.py`. Přepíše jen `stl/pouzdro-zdobene-nalezato.stl` a tuto složku.
"""
    (OUT/'README.md').write_text(text)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    fixed = {SOURCE: SOURCE_SHA, MODEL/'pouzdro.FCStd': FCSTD_SHA, MODEL/'rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf': VERTICAL_3MF_SHA}
    for path, value in fixed.items():
        B.require(B.sha(path) == value, f'Změněný soubor: {path}')
    OUT.mkdir(parents=True, exist_ok=True)
    work = OUT/'.cache'
    control = build(work/'kontrola-bez-blokeru', None, tuple(m for m in MODIFIERS if m[0] != 'blok-dutina-a-nabeh'))
    with ZipFile(control['sliced']) as z:
        control_layers, _ = parse_strokes(z.read('Metadata/plate_1.gcode').decode(errors='replace'))
    control_report = support_scan(control_layers, control['frame'])
    built = build(work/'finalni')
    frame, plate, meshes = built['frame'], built['plate'], built['meshes']
    delivered = OUT/'pouzdro-nalezato-kobra-x-pla-projekt.3mf'
    entries = []
    with ZipFile(built['sliced']) as zin:
        for name in zin.namelist():
            data = zin.read(name)
            if name == '3D/3dmodel.model':
                data = data.decode().replace('podlozka-01, pouze geometrie', 'naležato s podporami, PLA prototyp, nastavený projekt').replace(
                    'Pouze geometrie 1:1; bez procesu, filamentu a G-code. Alternativa téže podložky.',
                    'Kobra X 0,4 mm, lokálně nařezaný prototyp z návrhového červeného PLA se skutečnými podporami. Fyzický tisk, fit nože a montáž neověřeny.').encode()
            entries.append((name, data))
    if delivered.exists():
        delivered.unlink()
    B.write_zip_if_changed(delivered, entries)
    info = read_project(delivered)
    cfg = info.pop('cfg')
    bad = {k: (cfg.get(k), v) for k, v in PROCESS.items() if str(cfg.get(k)) != v}
    B.require(not bad, f'Projekt nemá finální nastavení: {bad}')
    checks = {'printer_model': 'Anycubic Kobra X', 'layer_height': '0.2', 'wall_loops': '4', 'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
              'top_shell_layers': '5', 'bottom_shell_layers': '5', 'seam_position': 'back', 'enable_prime_tower': '0', 'nozzle_diameter': ['0.4'], 'filament_colour': ['#B3141D'],
              'nozzle_temperature': ['205'], 'nozzle_temperature_initial_layer': ['215'], 'textured_plate_temp': ['50'], 'filament_max_volumetric_speed': ['8']}
    bad = {k: cfg.get(k) for k, v in checks.items() if cfg.get(k) != v}
    B.require(not bad, f'Změněný proces: {bad}')
    B.require(info['slice_metadata'].get('outside') == 'false', 'Slicer hlásí přesah podložky')
    B.require(not [w for w in info['warnings'] if w.get('msg') != 'not_support_traditional_timelapse'], f"Varování: {info['warnings']}")
    volumes = info.pop('volumes')
    normal = [v for v in volumes if v['subtype'] == 'normal_part']
    B.require(len(normal) == 1 and len(volumes) == 1+len(MODIFIERS), 'Jiný počet součástí')
    B.require([v['name'] for v in volumes[1:]] == [m[0] for m in MODIFIERS] and [v['subtype'] for v in volumes[1:]] == [m[1] for m in MODIFIERS], 'Změněné modifikátory')
    source = meshes[NAME]
    tr = plate['parts'][0]['translation_mm']
    B.require(len(source['vertices']) == len(normal[0]['vertices']), 'Změněné vrcholy')
    delta = max(abs(source['vertices'][i][a]+tr[a]-normal[0]['vertices'][i][a]) for i in range(len(source['vertices'])) for a in range(3))
    B.require(delta < .001, f'Změněná geometrie v projektu: {delta}')
    stats = normal[0]['mesh_stat']
    repairs = sum(int(v) for v in stats.values())
    B.require(repairs == 0, f'Slicer opravil síť: {stats}')
    with ZipFile(delivered) as z:
        gcode = z.read('Metadata/plate_1.gcode').decode(errors='replace')
    L, total_e = parse_strokes(gcode)
    openings = openings_lying(L, frame)
    B.require(not openings['strokes_crossing_blade_rect_floor_to_mouth'], 'Extruze v dráze čepele')
    B.require(not openings['strokes_crossing_cavity_rect'], 'Extruze v dutině')
    B.require(not any(openings['strokes_in_cavity_or_lead_in_by_kind'].values()), 'Extruze v dutině nebo náběhu')
    B.require(all(h['layers_checked'] and not h['strokes_inside_inscribed_circle'] for h in openings['mount_holes']), 'Extruze v otvoru')
    B.require(openings['closed_end_layers_with_strokes_under_blade'] == openings['layers_checked_floor_to_mouth'], 'Otevřený konec')
    bridge = bridges(L, frame)
    B.require(bridge['main_cavity_bridge_max_angle_from_short_axis_deg'] < 1 and bridge['lead_in_max_angle_from_short_axis_deg'] < 1, 'Most podél dutiny')
    B.HERE = OUT
    B.functional_openings = lambda layers, part: openings
    plate['parts'][0]['file'] = '../../stl/pouzdro-zdobene-nalezato.stl'
    paths = B.check_paths(gcode, plate)
    layers_flagged = paths['deposition_island_test']['disconnected_new_islands']
    on_support, unsupported = [], []
    for row in layers_flagged:
        below = L[row['layer_one_based']-3]['strokes'] if row['layer_one_based'] >= 3 else []
        for island in row['islands']:
            (x0, y0), (x1, y1) = island['xy_bbox_mm']
            near = [s for s in below if is_support(s[4]) and max(s[0], s[2]) >= x0-.8 and min(s[0], s[2]) <= x1+.8 and max(s[1], s[3]) >= y0-.8 and min(s[1], s[3]) <= y1+.8]
            (on_support if near else unsupported).append({'layer_one_based': row['layer_one_based'], 'z_mm': row['z_mm'], 'segments': island['segment_count'], 'roles': island['roles'], 'xy_bbox_mm': island['xy_bbox_mm']})
    legend_fix(OUT/paths['preview'], 'Zelená: brim a podpory · oranžová: most/převis · tmavá: model')
    B.require(not unsupported, f'Ostrov bez podpory: {unsupported[:5]}')
    shutil.copy2(work/'finalni/podlozka-01.png', OUT/'podlozka-01.png')
    shutil.copy2(built['process_path'], OUT/'proces-nalezato-kobra-x-pla-navrh.json')
    shutil.copy2(built['filament_path'], OUT/'filament-nalezato-pla-cervena-navrh.json')
    field, cell = height_field(frame)
    regions = support_scan(L, frame)
    B.require(not regions['strokes_in_cavity_or_lead_in'] and not regions['strokes_in_mount_holes'], 'Podpora v dutině nebo otvoru')
    reach = ceiling_reach(L, frame)
    B.require(not reach['strop-dutiny-a-nabehu']['supported_area_mm2'] and not reach['montazni-otvor']['supported_area_mm2'], 'Podpora pod stropem dutiny nebo otvoru')
    rm = removal(L, frame, field, cell)
    B.require(rm['above_model_samples_with_free_exit_along_part_y'] == rm['above_model_samples_tested_along_part_y'], 'Podpora bez volného výstupu')
    mass = float(re.search(r'^; total filament used \[g\] = ([0-9.]+)$', gcode, re.M).group(1))
    e_support = sum(s[6] for l in L.values() for s in l['strokes'] if is_support(s[4]))
    role_counts = Counter(s[4] for l in L.values() for s in l['strokes'])
    cli_errors = sorted(set(line.split('[error]', 1)[1].strip() for name in ('export.log', 'slice.log') for line in (work/'finalni'/name).read_text(errors='replace').splitlines() if '[error]' in line))
    result = {
        'revision': '05', 'variant': 'naležato s podporami', 'physical_print_verified': False, 'printer_io': False,
        'orientation': 'X dílu je tisková výška, Z dílu leží v rovině podložky, konec s dnem k zadní straně tiskárny. Otočení je v build_nalezato.py a v STL. Položka 3MF je jen posunutá.',
        'yaw_in_bed_plane_deg': 45, 'rigid': built['rigid'], 'placement': {'translation_mm': frame['t'], 'rotated_min_mm': frame['lo']},
        'user_reports': [
            {'recorded': '2026-11-03', 'origin': 'Hlášení Jiřího předané koordinátorem', 'variant': 'Ručně otočený tisk naležato bez podpor', 'report': 'propadal na visícím přechodu', 'printed_gcode_sha256': None},
            {'recorded': '2026-11-03', 'origin': 'Hlášení Jiřího předané koordinátorem', 'variant': 'Původní svislá varianta', 'report': 'na výšku to nevyšlo', 'cause': 'neznámá', 'printed_gcode_sha256': None}],
        'project': {'file': delivered.name, 'sha256': B.sha(delivered), 'gcode_sha256': info['gcode_sha256'], 'gcode_bytes': info['gcode_bytes'], 'build_items': info['items'], 'printable_parts': 1,
                    'normal_part_max_vertex_delta_mm': delta, 'mesh_repairs': repairs, 'modifiers': [{'name': v['name'], 'subtype': v['subtype'], 'triangles': v['triangles'], 'print_bbox_mm': v['bbox_mm']} for v in volumes[1:]],
                    'slice_metadata': info['slice_metadata'], 'warnings': info['warnings'], 'support_settings': {k: cfg.get(k) for k in PROCESS}},
        'cli_error_messages': cli_errors, 'role_counts': dict(role_counts),
        'support_regions': regions.pop('regions'), 'support_totals': regions,
        'control_without_cavity_blocker': {'strokes_in_cavity_or_lead_in': control_report['strokes_in_cavity_or_lead_in'], 'note': 'Stejný řez bez blokátoru dutiny, není součástí předání.'},
        'openings': openings, 'bridges': bridge, 'ridge': ridge_gap(L, frame), 'ceiling_reach': reach, 'removal': rm, 'tower': tower_report(L, frame), 'first_layer': first_layer(L, frame),
        'islands': {'unsupported': len(unsupported), 'flagged_on_support': len(on_support), 'flagged_on_support_examples': on_support[:12], 'note': 'Ostrov, který vidí nejbližší podporu o dvě vrstvy níž, je start modelu nad podporou s nastavenou mezerou 0,2 mm.'},
        'toolpaths': {k: paths[k] for k in ('physical_parts', 'layers', 'maximum_extrusion_z_mm', 'extrusion_min_xy_mm', 'extrusion_max_xy_mm', 'minimum_extrusion_edge_margin_mm', 'role_ranges', 'support_segments', 'maximum_commanded_volumetric_flow_mm3_s_segments_at_least_0_1mm', 'maximum_commanded_extrusion_speed_mm_s', 'selected_z_mm')},
        'estimates': {'filament_g': mass, 'printing_time': paths['estimated_printing_time'], 'support_mass_g': e_support*mass/total_e},
        'unchanged': {'stl/pouzdro-zdobene.stl': SOURCE_SHA, 'pouzdro.FCStd': FCSTD_SHA, 'rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf': VERTICAL_3MF_SHA},
        'pre_existing_difference_not_resolved': {'file': 'rozlozeni/podlozka-01-geometrie.3mf', 'sha256_found': B.sha(MODEL/'rozlozeni/podlozka-01-geometrie.3mf'), 'note': 'Hash se liší od starého manifestu už před touto úlohou. Soubor nebyl obnoven ani změněn.'},
        'not_verified': ['fyzický tisk', 'přilnavost a stabilita', 'odstranění podpor a povrch po nich', 'kvalita mostů a stropu náběhu', 'fit nože', 'pevnost při této orientaci vrstev', 'otevření projektu v GUI sliceru'],
        'detail_preview': paths['detail_previews'][0],
    }
    B.write_json(OUT/'kontrola-nalezato.json', result)
    facts = [f"{paths['layers']} vrstev, tisková výška {paths['maximum_extrusion_z_mm']:g} mm, 1 kus",
             f"Podpory: {role_counts['Support']} tahů, rozhraní {role_counts['Support interface']} tahů, odhadem {result['estimates']['support_mass_g']:.0f} g",
             f"V dutině a náběhu {openings['strokes_in_cavity_or_lead_in_by_kind']['support']} tahů podpory, v otvorech {sum(h['strokes_inside_inscribed_circle'] for h in openings['mount_holes'])}",
             f"Rezerva extruzí od okraje podložky {paths['minimum_extrusion_edge_margin_mm']:.1f} mm",
             f"Odhad sliceru {mass:.1f} g / {paths['estimated_printing_time']}"]
    render_overview(L, frame, facts, OUT/'nahled-orientace-a-podpor.png')
    write_readme(result)
    shutil.rmtree(work)
    names = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != 'predani.sha256')
    lines = [f'{B.sha(OUT/n)}  {n}' for n in names]
    lines += [f'{B.sha(MODEL/n)}  ../../{n}' for n in ('stl/pouzdro-zdobene-nalezato.stl', 'stl/pouzdro-zdobene.stl', 'build_nalezato.py', 'build_print_projects.py')]
    (OUT/'predani.sha256').write_text('\n'.join(lines)+'\n')
    for path, value in fixed.items():
        B.require(B.sha(path) == value, f'Změněný soubor: {path}')
    print('V05_LYING_PROJECT_OK', json.dumps({'project': result['project']['sha256'], 'gcode': info['gcode_sha256'], 'stl': built['rigid']['rotated_sha256'], 'g': mass, 'time': paths['estimated_printing_time']}), flush=True)


if __name__ == '__main__':
    main()
