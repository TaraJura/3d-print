#!/usr/bin/env python3
"""Native Anycubic whole-project import, without slicing or profile overrides.

The native round-trip copy is temporary. Only a small validation JSON is saved
beside the existing slice. The source project must remain byte-identical.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
sys.dont_write_bytecode=True
from zkontroluj_slice import project_meshes, mesh_deviation


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample',action='store_true')
    options=parser.parse_args()
    here=Path(__file__).resolve().parent
    source=here/('TEST-EXPERIMENT-575-snap-Alzament-TPU95A.3mf' if options.sample else 'EXPERIMENT-prepazka-575-snap-Alzament-TPU95A.3mf')
    output=here/('experimentalni-TEST-slice' if options.sample else 'experimentalni-slice')/'kontrola-nativniho-importu.json'
    original_hash=sha(source)
    keys=['printer_model','printer_settings_id','nozzle_diameter','curr_bed_type','filament_settings_id','filament_type',
          'filament_colour','filament_diameter','nozzle_temperature','nozzle_temperature_initial_layer',
          'textured_plate_temp','textured_plate_temp_initial_layer','filament_max_volumetric_speed',
          'wall_loops','sparse_infill_density','top_shell_layers','bottom_shell_layers','initial_layer_speed','inner_wall_speed','outer_wall_speed']
    with zipfile.ZipFile(source) as archive:
        source_settings=json.loads(archive.read('Metadata/project_settings.config'))
        source_meshes=project_meshes(archive)
    with tempfile.TemporaryDirectory(prefix='prepazka575-native-import-') as runtime:
        temporary=Path(runtime)
        command=['/usr/bin/AnycubicSlicerNext','--datadir',str(temporary/'data'),'--debug','2',
                 '--arrange','0','--orient','0','--outputdir',str(temporary),
                 '--export-3mf','native-reopened.3mf','--export-settings',str(temporary/'native-settings.json'),str(source)]
        run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        if run.returncode:
            raise RuntimeError(f'Native import failed,exit{run.returncode}: {run.stdout[-5000:]}')
        actual=json.loads((temporary/'native-settings.json').read_text())
        for key in keys:
            if actual.get(key)!=source_settings.get(key):
                raise ValueError(f'Native import altered{key}: {actual.get(key)!r} != {source_settings.get(key)!r}')
        assert actual['filament_type']==['TPU']
        assert len(actual['filament_settings_id'])==1 and 'Alzament TPU95A' in actual['filament_settings_id'][0]
        assert actual['nozzle_temperature']==actual['nozzle_temperature_initial_layer']==['225']
        assert actual['textured_plate_temp']==actual['textured_plate_temp_initial_layer']==['60']
        assert actual['printer_model']=='Anycubic Kobra X' and actual['nozzle_diameter']==['0.4']
        with zipfile.ZipFile(temporary/'native-reopened.3mf') as archive:
            reopened_meshes=project_meshes(archive)
            assert len(reopened_meshes)==len(source_meshes)
            deviations=[mesh_deviation(left,right) for left,right in zip(source_meshes,reopened_meshes)]
        assert sha(source)==original_hash,'Source project unexpectedly changed'
        result={'status':'Native CLI whole-project import passed; no GUI screenshot or physical print claim',
                'source_project':source.name,'source_sha256_before_and_after':original_hash,
                'native_cli_return_code':run.returncode,'no_external_profile_overrides':True,'no_reslice_performed':True,
                'mesh_count':len(source_meshes),'all_triangles_and_transforms_preserved':True,
                'maximum_vertex_deviation_mm_per_part':deviations,
                'active_native_settings':{key:actual.get(key) for key in keys},
                'warnings':[line.strip() for line in run.stdout.splitlines() if '[warning]' in line or '[error]' in line],
                'limitation':'TPU calibration, physical spool/feeding, snap fit and bed60C source conflict remain unverified.'}
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'audit':str(output),'objects':result['mesh_count'],'active_filament':result['active_native_settings']['filament_settings_id'],'source_unchanged':True},ensure_ascii=False))


if __name__=='__main__': main()
