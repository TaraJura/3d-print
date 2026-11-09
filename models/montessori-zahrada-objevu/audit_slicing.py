#!/usr/bin/env python3
"""Audit lower-edge growth from final project G-code; no slicing or printer I/O.

Writes only rozlozeni/kontrola-spodnich-hran.json. Samples actual outer-wall
strokes and compares them with preceding deposited strokes from the same part.
This is a geometric extrusion-footprint check, not a strength or print test.
"""
from collections import defaultdict
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent / 'rozlozeni'
NUM = re.compile(r'([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')


def parse(gcode, max_layer=7):
    pos = dict(X=0., Y=0., Z=0., E=0.)
    absolute = relative_e = True
    role = 'Custom'
    owner = None
    width = .42
    layer = -1
    layers = defaultdict(list)
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):
            layer += 1
            if max_layer is not None and layer > max_layer:
                break
        elif line.startswith(';TYPE:'):
            role = line.split(':', 1)[1].strip()
        elif line.startswith(';WIDTH:'):
            width = float(line.split(':', 1)[1])
        elif line.startswith('EXCLUDE_OBJECT_START NAME='):
            owner = line.split('NAME=', 1)[1]
        elif line.startswith('EXCLUDE_OBJECT_END'):
            owner = None
        command = line.split(';', 1)[0].strip()
        if not command:
            continue
        kind = command.split()[0]
        vals = {a: float(v) for a, v in NUM.findall(command)}
        if kind == 'G90':
            absolute = True
        elif kind == 'G91':
            absolute = False
        elif kind == 'M83':
            relative_e = True
        elif kind == 'M82':
            relative_e = False
        elif kind == 'G92':
            pos.update({a: v for a, v in vals.items() if a in pos})
        elif kind in ('G0', 'G1'):
            old = pos.copy()
            for a in 'XYZ':
                if a in vals:
                    pos[a] = vals[a] if absolute else pos[a] + vals[a]
            e = vals.get('E', 0) if relative_e else vals.get('E', pos['E']) - pos['E']
            if 'E' in vals:
                pos['E'] = pos['E'] + vals['E'] if relative_e else vals['E']
            if e > 0 and math.hypot(pos['X'] - old['X'], pos['Y'] - old['Y']) > 1e-7 and layer >= 0 and role not in ('Custom', 'Brim'):
                assert owner
                layers[layer].append((old['X'], old['Y'], pos['X'], pos['Y'], width, role, owner, pos['Z']))
        elif kind in ('G2', 'G3') and vals.get('E', 0) > 0:
            raise RuntimeError('Unexpected arc extrusion')
    return layers


def distance(x, y, stroke):
    x1, y1, x2, y2 = stroke[:4]
    dx, dy = x2 - x1, y2 - y1
    t = max(0., min(1., ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - x1 - t * dx, y - y1 - t * dy)


def audit(project, report):
    raw = project.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report['delivered']['sha256']
    with ZipFile(project) as z:
        gcode = z.read('Metadata/plate_1.gcode')
    assert hashlib.sha256(gcode).hexdigest() == report['delivered']['gcode_sha256']
    layers = parse(gcode.decode())
    records = []
    for layer in range(1, 8):
        previous = [s for s in layers[layer - 1] if s[5] in ('Outer wall', 'Overhang wall')]
        grid = defaultdict(list)
        for stroke in previous:
            x1, y1, x2, y2 = stroke[:4]
            for x in range(math.floor(min(x1, x2) - 1), math.floor(max(x1, x2) + 1) + 1):
                for y in range(math.floor(min(y1, y2) - 1), math.floor(max(y1, y2) + 1) + 1):
                    grid[(stroke[6], x, y)].append(stroke)
        owners = sorted({s[6] for s in layers[layer]})
        for owner in owners:
            outer = [s for s in layers[layer] if s[6] == owner and s[5] in ('Outer wall', 'Overhang wall')]
            assert outer, (owner, layer)
            maximum_distance = 0.
            minimum_overlap = math.inf
            samples = 0
            for stroke in outer:
                x1, y1, x2, y2, width = stroke[:5]
                n = max(1, math.ceil(math.hypot(x2 - x1, y2 - y1) / .15))
                for k in range(n + 1):
                    x, y = x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n
                    near = grid[(owner, math.floor(x), math.floor(y))]
                    assert near, (owner, layer, x, y)
                    nearest = min(near, key=lambda s: distance(x, y, s))
                    d = distance(x, y, nearest)
                    overlap = (width + nearest[4]) / 2 - d
                    maximum_distance = max(maximum_distance, d)
                    minimum_overlap = min(minimum_overlap, overlap)
                    samples += 1
            records.append({'object': owner, 'layer_one_based': layer + 1, 'z_mm': outer[0][7],
                'outer_wall_samples': samples, 'sample_spacing_at_most_mm': .15,
                'maximum_distance_to_previous_deposition_centerline_mm': maximum_distance,
                'minimum_nominal_stroke_overlap_mm': minimum_overlap,
                'all_outer_samples_overlap_previous_nominal_strokes': minimum_overlap >= 0})
    return {'project': project.name, 'sha256': hashlib.sha256(raw).hexdigest(),
        'gcode_sha256': hashlib.sha256(gcode).hexdigest(), 'checks': records,
        'passed': all(r['all_outer_samples_overlap_previous_nominal_strokes'] for r in records)}


def audit_microstrokes():
    report = json.loads((HERE / 'kontrola-podlozky-01.json').read_text())
    with ZipFile(HERE / report['project']) as z:
        gcode = z.read('Metadata/plate_1.gcode')
        settings = json.loads(z.read('Metadata/project_settings.config'))
    assert hashlib.sha256(gcode).hexdigest() == report['delivered']['gcode_sha256']
    layers = parse(gcode.decode(), max_layer=52)
    original = [(195.022, 210.768, 195.066, 210.615), (186.599, 216.816, 186.751, 216.808)]
    checks = []
    image = Image.new('RGB', (1200, 710), '#fafbfc')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
    title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23)
    draw.text((20, 15), 'Základna: skutečné dráhy Z 10,6 mm v místech původních mikročar', font=title, fill='#18343d')
    for index, target in enumerate(original):
        found = [s for s in layers[52] if max(abs(s[k] - target[k]) for k in range(4)) < .002]
        cx, cy = (target[0] + target[2]) / 2, (target[1] + target[3]) / 2
        lo, hi = (cx - 3, cy - 3), (cx + 3, cy + 3)
        intersects = lambda s: max(s[0], s[2]) >= lo[0] and min(s[0], s[2]) <= hi[0] and max(s[1], s[3]) >= lo[1] and min(s[1], s[3]) <= hi[1]
        project = lambda x, y: ((x - lo[0]) * 88, (hi[1] - y) * 88)
        tile = Image.new('RGB', (528, 528), '#fafbfc')
        tile_draw = ImageDraw.Draw(tile)
        for layer, colour in ((51, '#cad3d7'), (52, '#264750')):
            for s in layers[layer]:
                if not intersects(s):
                    continue
                tile_draw.line((project(s[0], s[1]), project(s[2], s[3])), fill=colour, width=max(1, round(s[4] * 88)))
        x, y = project(cx, cy)
        tile_draw.ellipse((x - 9, y - 9, x + 9, y + 9), outline='#cd684b', width=2)
        image.paste(tile, (30 + index * 600, 70))
        draw.text((30 + index * 600, 615), f'Původní místo {index + 1}: X {cx:.3f}, Y {cy:.3f}', font=font, fill='#18343d')
        draw.text((30 + index * 600, 643), 'Původní mikročára: ' + ('zůstává' if found else 'nenalezena'), font=font, fill='#18343d')
        checks.append({'original_xy': target, 'original_stroke_found_in_final_gcode': bool(found),
            'matching_strokes': found})
    draw.text((20, 680), 'Šedá: předchozí vrstva • tmavá: současná, skutečné WIDTH • oranžový kruh: původní místo', font=font, fill='#536871')
    image.save(HERE / 'kriticka-vrstva-01-mikrovypln.png')
    output = {'final_gcode_sha256': hashlib.sha256(gcode).hexdigest(),
        'process': {k: settings[k] for k in ('detect_narrow_internal_solid_infill', 'filter_out_gap_fill', 'wall_loops', 'sparse_infill_density', 'sparse_infill_pattern')},
        'checks': checks, 'preview': 'kriticka-vrstva-01-mikrovypln.png',
        'both_original_microstrokes_removed': all(not c['original_stroke_found_in_final_gcode'] for c in checks),
        'limitation': 'Absence of the two identified strokes is not a certification of all deposition order or physical support. Full-layer graph and separate lower-edge checks are recorded independently.'}
    (HERE / 'kontrola-mikrocarek-finalni.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'original_microstrokes_removed': output['both_original_microstrokes_removed']}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revalidate-paths', action='store_true',
        help='Recheck saved candidate G-code with current variable-width graph, without slicing')
    args = parser.parse_args()
    if args.revalidate_paths:
        source = HERE.parent / 'build_print_projects.py'
        spec = importlib.util.spec_from_file_location('print_builder', source)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        for number in (1, 2):
            report_file = HERE / f'kontrola-podlozky-{number:02d}.json'
            report = json.loads(report_file.read_text())
            project = HERE / report['project']
            candidate = HERE / '.cache' / f'podlozka-{number:02d}' / 'candidate.3mf'
            assert hashlib.sha256(candidate.read_bytes()).hexdigest() == report['delivered']['sha256']
            for part in report['plate']['parts']:
                assert hashlib.sha256((HERE / part['file']).read_bytes()).hexdigest() == part['source_sha256']
            with ZipFile(candidate) as z:
                gcode = z.read('Metadata/plate_1.gcode')
            assert hashlib.sha256(gcode).hexdigest() == report['delivered']['gcode_sha256']
            old = report['toolpath_audit']['deposition_island_test']
            if not old['passed']:
                report['superseded_fixed_width_audit'] = old
            paths = builder.check_paths(gcode.decode(), report['plate'])
            assert paths['deposition_island_test']['passed']
            report['toolpath_audit'] = paths
            report['revalidation_without_reslicing'] = True
            report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            project.write_bytes(candidate.read_bytes())
            print(f'Plate {number}: actual-width graph passed; same G-code SHA256', flush=True)
    plates = []
    for number in (1, 2):
        report = json.loads((HERE / f'kontrola-podlozky-{number:02d}.json').read_text())
        plates.append(audit(HERE / report['project'], report))
    result = {'method': 'Sampled actual exterior extrusion paths in layers 2 through 8, spacing <=0.15 mm; same-object preceding exterior-wall strokes, actual G-code WIDTH values. Nominal circular-stroke footprint only, not proof of physical bonding or full overhang print quality.',
        'plates': plates, 'passed': all(p['passed'] for p in plates),
        'resliced': False, 'printer_io': False, 'physical_print_verified': False}
    (HERE / 'kontrola-spodnich-hran.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'checks': sum(len(p['checks']) for p in plates),
        'minimum_overlap_mm': min(c['minimum_nominal_stroke_overlap_mm'] for p in plates for c in p['checks'])}))
    assert result['passed'], 'Nominal unsupported lower-edge stroke detected'
    audit_microstrokes()


if __name__ == '__main__':
    main()
