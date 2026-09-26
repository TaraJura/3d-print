#!/usr/bin/env python3
"""Create local experimental profiles and slice; never connects to a printer.

Overwrites the experimental files beside this script, preserving geometry-only 3MF.
The machine profile is copied unmodified from installed system resources.
The filament and process settings are design choices, not physically calibrated.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sample', action='store_true', help='Slice the separate two-part test plate')
args = parser.parse_args()
SYSTEM = Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
CONFIG = HERE / 'experimentalni-profily'
CONFIG.mkdir(exist_ok=True)
OUT = HERE / ('experimentalni-TEST-slice' if args.sample else 'experimentalni-slice')
OUT.mkdir(exist_ok=True)

machine = json.loads((SYSTEM / 'machine/Anycubic Kobra X 0.4 nozzle.json').read_text())
process = json.loads((SYSTEM / 'process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json').read_text())
filament = json.loads((SYSTEM / 'filament/Anycubic TPU 95A @Anycubic Kobra X 0.4 nozzle.json').read_text())
process_name = 'EXPERIMENT prepazka 575 snap TPU95A 0.20mm Kobra X 0.4'
filament_name = 'EXPERIMENT 575 snap Alzament TPU95A Gray Kobra X 0.4 225C bed60C'
process.update({
    'from': 'user', 'name': process_name, 'setting_id': process_name, 'print_settings_id': process_name,
    'curr_bed_type': 'Textured PEI Plate',
    'layer_height': '0.2', 'initial_layer_print_height': '0.2',
    'wall_loops': '4', 'top_shell_layers': '5', 'bottom_shell_layers': '5',
    'top_shell_thickness': '1', 'bottom_shell_thickness': '1',
    'sparse_infill_density': '100%', 'sparse_infill_pattern': 'rectilinear',
    'initial_layer_speed': '20', 'initial_layer_infill_speed': '20',
    'outer_wall_speed': '30', 'inner_wall_speed': '40', 'small_perimeter_speed': '20',
    'sparse_infill_speed': '40', 'internal_solid_infill_speed': '40', 'top_surface_speed': '30',
    'gap_infill_speed': '30', 'bridge_speed': '30', 'internal_bridge_speed': '30',
    'overhang_1_4_speed': '40', 'overhang_2_4_speed': '30', 'overhang_3_4_speed': '20',
    'overhang_4_4_speed': '10', 'overhang_totally_speed': '10',
    'support_speed': '40', 'support_interface_speed': '30', 'skirt_speed': '20',
    'travel_speed': '150', 'default_acceleration': '1000', 'outer_wall_acceleration': '500',
    'inner_wall_acceleration': '1000', 'sparse_infill_acceleration': '1000',
    'internal_solid_infill_acceleration': '1000', 'top_surface_acceleration': '500',
    'bridge_acceleration': '500', 'initial_layer_acceleration': '300', 'travel_acceleration': '2000',
    'enable_support': '0', 'brim_type': 'outer_only', 'brim_width': '5', 'brim_object_gap': '0.1',
    'skirt_loops': '0', 'raft_layers': '0', 'enable_prime_tower': '0',
    'filename_format': 'EXPERIMENT-prepazka-575-snap-TPU95A-plate{plate_number}.gcode',
})
filament.update({
    'from': 'user', 'is_custom_defined': '1', 'name': filament_name, 'setting_id': filament_name,
    'filament_settings_id': [filament_name], 'filament_id': 'EXPERIMENT-575-snap-Alzament-TPU95A-Gray',
    'filament_vendor': ['Alzament'], 'filament_type': ['TPU'], 'default_filament_colour': ['#9A9A9A'],
    'filament_colour': ['#9A9A9A'], 'nozzle_temperature': ['225'], 'nozzle_temperature_initial_layer': ['225'],
    'nozzle_temperature_BRASS': ['225'], 'nozzle_temperature_HS': ['225'],
    'nozzle_temperature_range_low': ['220'], 'nozzle_temperature_range_high': ['230'],
    'textured_plate_temp': ['60'], 'textured_plate_temp_initial_layer': ['60'],
    'hot_plate_temp': ['60'], 'hot_plate_temp_initial_layer': ['60'],
    'filament_max_volumetric_speed': ['3.2'], 'filament_flow_ratio': ['1'],
    'filament_density': ['1.24'],
    'filament_notes': ['EXPERIMENT ONLY. No physical calibration. Alzament TDS nozzle220-240 bed60-80; Gray product nozzle190-230 bed30-50: bed recommendations conflict. 225C/60C are provisional design choices, not a verified Alzament profile. Density1.24g/cm3 is inherited from Anycubic and unverified for Alzament; weight is only a slicer estimate. No physical waterproofness or fit validation.'],
})
paths = {}
for name, data in [('machine', machine), ('process', process), ('filament', filament)]:
    paths[name] = CONFIG / f'{name}.json'
    paths[name].write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

with tempfile.TemporaryDirectory(prefix='prepazka-slicer-') as temporary:
    command = [
        '/usr/bin/AnycubicSlicerNext', '--datadir', temporary, '--debug', '2',
        '--load-settings', f"{paths['machine']};{paths['process']}",
        '--load-filaments', str(paths['filament']),
        '--arrange', '0', '--orient', '0', '--slice', '0',
        '--metadata-name', 'Title;Description',
        '--metadata-value', f"{'TEST ' if args.sample else ''}EXPERIMENT prepazka 575 snap TPU95A;Local sliced experiment with geometry, profiles and G-code. Physical settings and sealing unverified. Bed temperature source conflict remains unresolved.",
        '--outputdir', str(OUT),
        '--export-3mf', '../TEST-EXPERIMENT-575-snap-Alzament-TPU95A.3mf' if args.sample else '../EXPERIMENT-prepazka-575-snap-Alzament-TPU95A.3mf',
        '--export-settings', str(OUT / 'effective-settings.json'),
        str(HERE / ('TEST-575-snap-pracovni-geometrie.3mf' if args.sample else 'prepazka-575-snap-pracovni-geometrie.3mf')),
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(result.stdout[-16000:])
    print('Slicer exit:', result.returncode)
    raise SystemExit(result.returncode)
