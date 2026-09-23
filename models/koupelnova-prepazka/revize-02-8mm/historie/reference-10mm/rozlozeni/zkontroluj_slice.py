#!/usr/bin/env python3
"""Audit actual experimental G-code and render selected layers from its XY paths.

Requires matplotlib only for the final PNG. No simulator or physical-test claim.
"""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
OUT = HERE / 'experimentalni-slice'
GCODE = OUT / 'plate_1.gcode'
PROJECT = HERE / 'EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    text = GCODE.read_text()
    settings = json.loads((OUT / 'effective-settings.json').read_text())
    geometry_audit = json.loads((HERE / 'kontrola-podlozky.json').read_text())
    nominal_height = geometry_audit['parts'][0]['nominal_cad_dimensions_mm'][2]
    layer_height = float(settings['layer_height'])
    expected_layers = round(nominal_height/layer_height)
    with zipfile.ZipFile(PROJECT) as archive:
        assert archive.testzip() is None
        assert archive.read('Metadata/plate_1.gcode') == GCODE.read_bytes()
        warnings = [item.attrib for item in ET.fromstring(archive.read('Metadata/slice_info.config')).findall('.//warning')]
        project_settings = json.loads(archive.read('Metadata/project_settings.config'))
        credential_keys = [key for key in project_settings if re.search(r'password|(?:access|refresh)_token|api_?key', key, re.I)]
        assert all(project_settings[key] in ('', [], {}, None) for key in credential_keys)
        assert not any(b'/home/novakj/' in archive.read(name) for name in archive.namelist() if not name.endswith('.png'))
        model_settings = ET.fromstring(archive.read('Metadata/model_settings.config'))
        objects = model_settings.findall('object')
        assert len(objects) == 3
        repaired = [{key: int(value) for key, value in stat.attrib.items()} for stat in model_settings.findall('.//mesh_stat')]
        assert all(all(value == 0 for value in stat.values()) for stat in repaired)
        for key in ['printer_model', 'printer_settings_id', 'curr_bed_type', 'filament_settings_id', 'nozzle_temperature', 'textured_plate_temp', 'wall_loops', 'sparse_infill_density', 'brim_width']:
            assert project_settings[key] == settings[key], key

    pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'E': 0.0}
    absolute_xyz = True
    relative_e = False
    feed = 0.0
    layer = 0
    layer_z = {}
    role = 'Unclassified'
    object_name = None
    width = 0.5
    segments = defaultdict(list)
    roles = defaultdict(lambda: {'segments': 0, 'maximum_speed_mm_s': 0.0})
    temperature_commands = []
    fan_commands = []
    negative_e = []
    commands = Counter()
    layer_speeds = defaultdict(float)
    layer_objects = defaultdict(set)
    extrusion_bounds = [[math.inf]*3, [-math.inf]*3]
    object_xy_bounds = defaultdict(lambda: [[math.inf]*2, [-math.inf]*2])
    max_mvs = 0.0
    max_mvs_record = None
    max_mvs_long_segments = 0.0
    max_mvs_rounding_lower_bound = 0.0
    deposition_length = 0.0
    e_positive_moving = 0.0
    for line_number, line in enumerate(text.splitlines(), 1):
        if line == ';LAYER_CHANGE':
            layer += 1
        elif line.startswith(';Z:'):
            layer_z[layer] = float(line[3:])
        elif line.startswith(';TYPE:'):
            role = line[6:].strip()
        elif line.startswith(';WIDTH:'):
            width = float(line[7:])
        code = line.split(';', 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        commands[command] += 1
        args = {match[0]: float(match[1]) for match in re.findall(r'\b([XYZEFSP])([-+]?(?:\d*\.)?\d+)', code)}
        if command.startswith('EXCLUDE_OBJECT_'):
            if command == 'EXCLUDE_OBJECT_START':
                object_name = re.search(r'NAME=(\S+)', code).group(1)
            elif command == 'EXCLUDE_OBJECT_END':
                object_name = None
        if command == 'G90': absolute_xyz = True
        if command == 'G91': absolute_xyz = False
        if command == 'M82': relative_e = False
        if command == 'M83': relative_e = True
        if command in ('M104', 'M109', 'M140', 'M190', 'G9111'):
            temperature_commands.append({'line': line_number, 'command': code})
        if command in ('M106', 'M107'):
            fan_commands.append(code)
        if command == 'G92':
            pos.update({key: value for key, value in args.items() if key in pos})
        if command not in ('G0', 'G1'):
            continue
        previous = dict(pos)
        for axis in 'XYZ':
            if axis in args:
                pos[axis] = args[axis] if absolute_xyz else pos[axis] + args[axis]
        e_delta = args.get('E', 0.0) if relative_e else args.get('E', pos['E']) - pos['E']
        if 'E' in args:
            pos['E'] = pos['E'] + args['E'] if relative_e else args['E']
        if 'F' in args: feed = args['F']
        distance = math.dist(tuple(previous[a] for a in 'XYZ'), tuple(pos[a] for a in 'XYZ'))
        if e_delta < -1e-7: negative_e.append(e_delta)
        if e_delta <= 0 or distance <= 1e-7:
            continue
        speed = feed / 60.0
        assert layer > 0, 'Unexpected extrusion before first layer'
        assert speed > 0
        current_mvs = e_delta * math.pi * (1.75/2)**2 / (distance / speed)
        if current_mvs > max_mvs:
            max_mvs = current_mvs
            max_mvs_record = {'line': line_number, 'code': code, 'distance_mm': distance, 'e_delta_mm': e_delta, 'speed_mm_s': speed, 'role': role}
        if distance >= 0.1:
            max_mvs_long_segments = max(max_mvs_long_segments, current_mvs)
        # XY coordinates are rounded to 0.001 mm and E to 0.00001 mm.
        # Each endpoint can move by half a coordinate unit; the vector error
        # between endpoints is at most sqrt(3)*0.001 mm in 3D.
        rounding_lower_bound = max(0, e_delta-0.000005) * math.pi*(1.75/2)**2 * speed / (distance + math.sqrt(3)*0.001)
        max_mvs_rounding_lower_bound = max(max_mvs_rounding_lower_bound, rounding_lower_bound)
        layer_speeds[layer] = max(layer_speeds[layer], speed)
        roles[role]['segments'] += 1
        roles[role]['maximum_speed_mm_s'] = max(roles[role]['maximum_speed_mm_s'], speed)
        if object_name:
            layer_objects[layer].add(object_name)
        for point in (previous, pos):
            for axis_index, axis in enumerate('XYZ'):
                extension = width/2 if axis != 'Z' else 0
                extrusion_bounds[0][axis_index] = min(extrusion_bounds[0][axis_index], point[axis] - extension)
                extrusion_bounds[1][axis_index] = max(extrusion_bounds[1][axis_index], point[axis] + extension)
                if object_name and axis != 'Z':
                    object_xy_bounds[object_name][0][axis_index] = min(object_xy_bounds[object_name][0][axis_index], point[axis] - extension)
                    object_xy_bounds[object_name][1][axis_index] = max(object_xy_bounds[object_name][1][axis_index], point[axis] + extension)
        segments[layer].append(((previous['X'], previous['Y']), (pos['X'], pos['Y']), role))
        deposition_length += distance
        e_positive_moving += e_delta

    assert not any(command in commands for command in ('G2', 'G3')), 'Arc G-code not supported by this audit'
    assert len(layer_z) == layer == expected_layers and all(abs(layer_z[n] - n*layer_height) < 1e-6 for n in range(1,expected_layers+1))
    assert all(len(names) == 3 for names in layer_objects.values())
    assert max(layer_speeds.values()) <= 40.001
    assert layer_speeds[1] <= 20.001
    assert max_mvs_long_segments <= 3.23, f'Volumetric cap exceeded on >=0.1mm segments: {max_mvs_long_segments}'
    assert max_mvs_rounding_lower_bound <= 3.201, f'Volumetric cap exceeded beyond serialization rounding: {max_mvs_rounding_lower_bound}'
    assert all(0 <= extrusion_bounds[0][axis] and extrusion_bounds[1][axis] <= 260 for axis in range(2))
    assert extrusion_bounds[1][2] <= nominal_height + 0.001
    assert not any('Support' in role for role in roles)
    assert roles['Brim']['segments'] > 0
    assert 'G9111 bedTemp=60 extruderTemp=225' in text

    result = {
        'status': 'EXPERIMENTAL local slice; physical settings and function unverified',
        'project': str(PROJECT.name), 'project_sha256': digest(PROJECT), 'gcode_sha256': digest(GCODE),
        'embedded_gcode_matches_external_exactly': True, 'objects': 3, 'mesh_repairs': repaired,
        'source_profile_provenance': 'Installed system profiles; slicer run uses an isolated temporary datadir, no user/cloud profile',
        'exported_project_credential_fields_empty': True,
        'exported_project_contains_no_home_path': True,
        'no_runtime_or_private_cloud_logs_in_artifacts': True,
        'machine': settings['printer_settings_id'], 'bed_type': settings['curr_bed_type'],
        'slicer_return_code': json.loads((OUT / 'result.json').read_text())['return_code'],
        'slicer_project_warnings': warnings,
        'layers': layer, 'layer_heights_mm': list(layer_z.values()),
        'every_printing_layer_contains_all_three_objects': True,
        'max_extrusion_move_speed_mm_s': max(layer_speeds.values()),
        'first_layer_max_extrusion_move_speed_mm_s': layer_speeds[1],
        'max_calculated_volumetric_flow_mm3_s': max_mvs,
        'maximum_flow_segment': max_mvs_record,
        'max_calculated_flow_for_segments_at_least_0_1mm_mm3_s': max_mvs_long_segments,
        'max_flow_lower_bound_after_serialization_rounding_mm3_s': max_mvs_rounding_lower_bound,
        'volumetric_rounding_explanation': 'Very short segments have large relative errors from XY0.001mm and E0.00001mm serialization; raw maximum is retained above. Long-segment cap checked at3.23, lower bound accounting for endpoint/E quantization at3.201.',
        'extrusion_bounds_including_half_line_width_mm': extrusion_bounds,
        'object_bounds_including_brim_and_half_line_width_mm': dict(object_xy_bounds),
        'all_extrusion_inside_plate_xy': True, 'support_extrusion_present': False, 'brim_extrusion_present': True,
        'extrusion_move_roles': dict(roles), 'temperature_commands': temperature_commands,
        'fan_commands': sorted(set(fan_commands)), 'retraction_lengths_mm': sorted(set(round(-v,5) for v in negative_e)),
        'extruding_path_length_mm': deposition_length, 'positive_filament_on_moving_extrusions_mm': e_positive_moving,
        'material_density_g_cm3': {'value': settings['filament_density'], 'evidence': 'inherited Anycubic default; unverified for Alzament'},
        'estimates': re.findall(r'^; (?:estimated printing time \(normal mode\)|filament used \[mm\]|filament used \[g\]|filament used \[cm3\]) = .*$', text, re.M),
        'limitations': [
            'Bed60C is a provisional choice: TDS60-80C conflicts with Gray product30-50C.',
            'Slicer emits bed_temperature_too_high_than_filament; this warning has not been suppressed.',
            'CLI also logs calc_exclude_triangles:Unable to create exclude triangles for the empty bed exclusion list; actual path bounds checked independently.',
            'Layer PNG is rendered from actual G-code XY segments, not a slicer GUI screenshot.',
            'No physical spool loading, print, adhesion, flexible-joint fit, water or seal test has been performed.',
        ],
    }
    (OUT / 'kontrola-gcode.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Patch
    palette = {'Brim': '#b86b32', 'Outer wall': '#165c91', 'Inner wall': '#398bab',
               'Internal solid infill': '#76a297', 'Top surface': '#8054a1', 'Bottom surface': '#76a297'}
    selected = [1, max(2, expected_layers//2), expected_layers]
    fig, axes = plt.subplots(1, 3, figsize=(16, 7), dpi=160)
    for axis, number in zip(axes, selected):
        paths = segments[number]
        lines = [segment[:2] for segment in paths]
        colors = [palette.get(segment[2], '#7b8b94') for segment in paths]
        axis.add_collection(LineCollection(lines, colors=colors, linewidths=0.45, alpha=0.9))
        axis.set(xlim=(15, 245), ylim=(55, 185), aspect='equal', xlabel='X [mm]', ylabel='Y [mm]')
        axis.set_title(f'Vrstva {number} / {expected_layers} · Z = {layer_z[number]:g} mm', fontsize=12)
        axis.grid(color='#dce0e4', linewidth=0.6)
        axis.set_axisbelow(True)
        axis.set_facecolor('#f8f9fa')
    fig.suptitle('Skutečné extruzní dráhy · přepážka B · 3 díly', fontsize=18, y=0.91)
    fig.text(0.5, 0.84, 'EXPERIMENTÁLNÍ TPU95A · 225 °C / deska 60 °C · 0,2 mm · lem 5 mm · bez podpor', ha='center', fontsize=11)
    handles = [Patch(color=color, label=role) for role,color in palette.items() if role in roles]
    fig.legend(handles=handles, loc='lower center', ncol=3, bbox_to_anchor=(0.5,0.13), fontsize=10, frameon=False)
    fig.text(0.5,0.06,'Náhled přímo z G-code; bez ruční změny drah. Teplota desky má nevyřešený rozpor ve zdrojích a varování sliceru.',ha='center',fontsize=10,color='#7d3522')
    fig.subplots_adjust(top=0.8, bottom=0.23, left=0.05, right=0.99, wspace=0.18)
    fig.savefig(OUT / 'nahled-skutecnych-vrstev.png', facecolor='white')
    plt.close(fig)
    print(json.dumps({'audit': str(OUT/'kontrola-gcode.json'), 'preview': str(OUT/'nahled-skutecnych-vrstev.png'),
                      'maximum_speed_mm_s': result['max_extrusion_move_speed_mm_s'], 'first_layer_speed_mm_s': layer_speeds[1],
                      'max_calculated_mvs': max_mvs, 'warnings': warnings},ensure_ascii=False))


if __name__ == '__main__':
    main()
