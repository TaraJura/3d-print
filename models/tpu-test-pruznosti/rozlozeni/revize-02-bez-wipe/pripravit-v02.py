#!/usr/bin/env python3
"""TPU V02: samostatny kandidat bez wipe s retrakci0.8mm pri20mm/s.
Cte V01 z nadrazene slozky a STL modelu. Zapisuje pouze do teto podslozky.
Nenahrava soubory a nekontaktuje tiskarnu. Prepisuje vlastni V02 vystupy.
"""
from collections import Counter
import copy, hashlib, importlib.util, json, math, re, shutil, sys
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
V01=HERE.parent
CACHE=HERE/'.cache'
DELIVERED=HERE/'podlozka-01-v02-bez-wipe-kobra-x-alzament-tpu95a.3mf'
SOURCE_PROJECT=V01/'podlozka-01-kobra-x-alzament-tpu95a-projekt.3mf'
SPEC=importlib.util.spec_from_file_location('tpu_v01_helpers',V01/'pripravit-podlozku.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
# Existing mesh/project/path audit helpers write images using HERE. Redirect only
# their in-memory globals; V01 files are read-only inputs throughout this run.
m.HERE=HERE;m.CACHE=CACHE;m.DELIVERED=DELIVERED


def audit_all_e(gcode):
    """Audit every explicit G0/G1 E move, including retraction and E-only moves.
    Firmware macro implementation is unavailable and explicitly outside this test.
    """
    pos=dict(X=0.,Y=0.,Z=0.,E=0.);absolute=True;relative_e=False;feed=0.;layer=0
    counts=Counter();max_speed=Counter();lengths=Counter();start_call=None;first_move=None
    extrema={};combined_negative=[];temperature_commands=[];tool_commands=[]
    number=re.compile(r'\b([XYZEF])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
    for lineno,line in enumerate(gcode.splitlines(),1):
        if line.startswith(';LAYER_CHANGE'):layer+=1
        c=line.split(';',1)[0].strip()
        if not c:continue
        kind=c.split()[0];values={k:float(v) for k,v in number.findall(c)}
        if kind=='G9111':start_call={'line':lineno,'command':c}
        if re.fullmatch(r'T\d+',kind) or kind in ('M603','M600','M701','M702'):tool_commands.append({'line':lineno,'command':c})
        if kind in ('M104','M109','M140','M190'):temperature_commands.append({'line':lineno,'command':c})
        if kind=='G90':absolute=True
        elif kind=='G91':absolute=False
        elif kind=='M83':relative_e=True
        elif kind=='M82':relative_e=False
        elif kind=='G92':pos.update({k:v for k,v in values.items() if k in pos})
        elif kind in ('G0','G1'):
            old=pos.copy()
            for a in 'XYZ':
                if a in values:pos[a]=values[a] if absolute else pos[a]+values[a]
            delta_e=values.get('E',0.) if relative_e else values.get('E',pos['E'])-pos['E']
            if 'E' in values:pos['E']=pos['E']+values['E'] if relative_e else values['E']
            if 'F' in values:feed=values['F']/60
            if 'E' not in values or abs(delta_e)<1e-12:continue
            m.require(start_call is not None,'E move before native startup macro')
            xyz_length=math.sqrt(sum((pos[a]-old[a])**2 for a in 'XYZ'))
            has_xyz=any(a in values for a in 'XYZ')
            category=('positive' if delta_e>0 else 'negative')+('_xyz' if xyz_length>1e-9 else '_xyz_quantized' if has_xyz else '_e_only')
            nominal_speed=abs(delta_e)/xyz_length*feed if xyz_length>1e-9 else feed
            record={'line':lineno,'layer':layer,'command':c,'e_delta_mm':delta_e,'xyz_length_mm':xyz_length,
                'commanded_feed_mm_min':feed*60,'nominal_filament_speed_mm_s':nominal_speed}
            if first_move is None:first_move=record
            counts[category]+=1;lengths[category]+=abs(delta_e)
            if nominal_speed>max_speed[category]:max_speed[category]=nominal_speed;extrema[category]=record
            if delta_e<0 and xyz_length>1e-9:combined_negative.append(record)
            if xyz_length<=1e-9 and has_xyz:
                # Slicer can round a sub-micron XY move to the current position
                # while retaining one E quantum. Audit and report it separately;
                # it is not the explicit0.8mm unretraction governed by20mm/s.
                m.require(delta_e>0 and delta_e<=.0001 and feed<=25.001,f'Unexpected coincident XYZ/E move: {record}')
            elif xyz_length<=1e-9:
                m.require(abs(delta_e)<=.80001,f'Unexpected E-only length: {record}')
                m.require(feed<=20.001,f'E-only speed exceeds20mm/s: {record}')
            elif delta_e>0:
                m.require(feed<=25.001,f'Model head speed exceeds25mm/s: {record}')
                # The existing V01 helper separately checks positive volumetric flow
                # with a length threshold to avoid tiny-segment rounding artefacts.
        elif kind in ('G2','G3') and 'E' in values:raise RuntimeError('Unexpected arc extrusion')
    m.require(start_call and start_call['command']=='G9111 bedTemp=60 extruderTemp=225','Changed start macro')
    m.require(not combined_negative,'Wipe/combined XYZ retraction remains')
    m.require(';WIPE_START' not in gcode and ';WIPE_END' not in gcode,'Wipe markers remain')
    m.require(not tool_commands,'Unexpected tool, loading or filament change command')
    m.require(counts['positive_xyz']>0 and counts['positive_e_only']>0 and counts['negative_e_only']>0,'Missing expected E categories')
    return {'method':'Every explicit G0/G1 E move with relative/absolute mode and feed tracking; includes E-only restoration and retraction.',
        'all_explicit_e_moves_checked':sum(counts.values()),'counts':dict(counts),'absolute_filament_distance_mm':dict(lengths),
        'maximum_nominal_filament_speed_mm_s':dict(max_speed),'extreme_examples':extrema,'first_explicit_e_move':first_move,
        'combined_xyz_negative_e_moves':0,'wipe_markers_present':False,'startup_macro':start_call,
        'coincident_xyz_note':'Positive_xyz_quantized contains explicit XYZ moves whose rounded endpoint equals the current position. Each has at most0.0001mm positive E and retained model feed<=25mm/s. These are reported, not omitted as retraction or purge.',
        'standalone_temperature_commands':temperature_commands,'tool_loading_commands':tool_commands,
        'macro_boundary':'G9111 is a firmware macro. Its internal heating, waits, purge, feed, retraction and jam checks are not present in this file and were not audited. Actual motor speed and temperature were not measured.',
        'error_11833_resolution_verified':False,'physical_print_verified':False}


def main():
    CACHE.mkdir(exist_ok=True)
    source_files=[SOURCE_PROJECT,V01/'podlozka-01-geometrie.3mf',V01/'pripravit-podlozku.py',
        V01/'proces-kobra-x-tpu-navrh.json',V01/'filament-alzament-tpu95a-navrh.json',V01/'kontrola-rozlozeni.json']
    hashes={str(p.relative_to(V01)):m.sha(p) for p in source_files}
    layout=json.loads((V01/'kontrola-rozlozeni.json').read_text())
    for p in layout['parts']:p['source_stl']='../'+p['source_stl']
    geometry=HERE/'podlozka-01-v02-geometrie.3mf'
    shutil.copyfile(V01/'podlozka-01-geometrie.3mf',geometry)
    m.require(m.sha(geometry)==layout['geometry_sha256'],'Geometry differs from V01')
    layout['geometry_file']=geometry.name
    m.write_json(HERE/'kontrola-rozlozeni-v02.json',layout)
    shutil.copyfile(V01/'podlozka-01.png',HERE/'podlozka-01.png')
    process=json.loads((V01/'proces-kobra-x-tpu-navrh.json').read_text())
    process['filename_format']='TPU-test-Alzament95A-V02-bez-wipe-plate{plate_number}.gcode'
    filament=json.loads((V01/'filament-alzament-tpu95a-navrh.json').read_text())
    name='EXPERIMENT V02 bez wipe Alzament TPU95A 225C bed60C @Kobra X'
    filament.update({'name':name,'setting_id':name,'filament_settings_id':[name],
        'filament_wipe':['0'],'filament_retraction_length':['0.8'],
        'filament_retraction_speed':['20'],'filament_deretraction_speed':['20'],
        'filament_retract_when_changing_layer':['0']})
    filament['filament_notes']=[filament['filament_notes'][0]+' V02: wipe disabled; explicit retraction0.8mm and retraction/restoration20mm/s; layer-change retraction disabled. Candidate only; not a verified fix for printer error11833. Firmware startup G9111 not audited.']
    process_path=HERE/'proces-v02-kobra-x-tpu.json';filament_path=HERE/'filament-v02-alzament-tpu95a.json'
    m.write_json(process_path,process);m.write_json(filament_path,filament)
    configured=CACHE/'configured-v02.3mf';slice_dir=CACHE/'slice';slice_dir.mkdir(exist_ok=True)
    m.run_cli([m.CLI,'--datadir',str(CACHE/'export-profile'),'--load-settings',str(m.MACHINE)+';'+str(process_path),
        '--load-filaments',str(filament_path),'--arrange','0','--orient','0','--export-3mf',configured.name,'--outputdir',str(CACHE),str(geometry)],CACHE/'export.log')
    c=m.inspect_project(configured,layout,False)
    m.run_cli([m.CLI,'--datadir',str(CACHE/'slice-profile'),'--arrange','0','--orient','0','--slice','0',
        '--export-3mf',DELIVERED.name,'--outputdir',str(slice_dir),str(configured)],CACHE/'slice.log')
    shutil.copyfile(slice_dir/DELIVERED.name,DELIVERED)
    final=m.inspect_project(DELIVERED,layout,True)
    with ZipFile(SOURCE_PROJECT) as z:old=json.loads(z.read('Metadata/project_settings.config'))
    with ZipFile(DELIVERED) as z:
        new=json.loads(z.read('Metadata/project_settings.config'));gcode=z.read('Metadata/plate_1.gcode').decode()
    differences={k:{'v01':old.get(k),'v02':new.get(k)} for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)}
    allowed={'filament_settings_id','filament_notes','filament_wipe','filament_retraction_length',
        'filament_retraction_speed','filament_deretraction_speed','filament_retract_when_changing_layer','filename_format'}
    m.require(set(differences)<=allowed,f'Unexpected settings changes {set(differences)-allowed}')
    for k,v in {'filament_wipe':['0'],'filament_retraction_length':['0.8'],'filament_retraction_speed':['20'],
            'filament_deretraction_speed':['20'],'filament_retract_when_changing_layer':['0']}.items():m.require(new.get(k)==v,f'Override not preserved {k}')
    full_e=audit_all_e(gcode)
    for p in source_files:m.require(m.sha(p)==hashes[str(p.relative_to(V01))],f'V01 input changed while building {p}')
    report={'status':'V02 candidate for physical retest after feed-path and failed-phase assessment; not a verified repair of error11833',
        'date':'2026-10-24','v01_inputs_sha256':hashes,'v01_inputs_unchanged':True,'geometry':layout,
        'configured_project':c,'delivered_project':final,'effective_settings_differences':differences,
        'all_explicit_e_audit':full_e,'printer_contact':False}
    m.write_json(HERE/'kontrola-v02.json',report)
    print(json.dumps({'project':str(DELIVERED),'time':final['paths']['estimated_print_time'],'mass_g':final['paths']['estimated_filament_g'],
        'differences':list(differences),'all_e_audit':full_e},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
