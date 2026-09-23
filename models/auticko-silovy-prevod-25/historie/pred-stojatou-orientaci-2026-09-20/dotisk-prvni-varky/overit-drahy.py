#!/usr/bin/env python3
"""Audit already sliced local outputs, never invoke or send to a printer.

Usage: python overit-drahy.py /path/to/isolated/slicing/cache
Output: allowlisted evidence and actual extrusion-path projection PNGs here.
"""
import hashlib, importlib.util, json, re, sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve()
spec=importlib.util.spec_from_file_location('roundtrip',HERE.parent/'overit-import.py')
roundtrip=importlib.util.module_from_spec(spec);spec.loader.exec_module(roundtrip)
NUM=re.compile(r'([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)')
KEYS='printer_model printer_settings_id print_settings_id filament_settings_id filament_type nozzle_diameter layer_height initial_layer_print_height enable_support support_type support_style support_on_build_plate_only support_remove_small_overhang support_threshold_angle support_top_z_distance support_bottom_z_distance support_object_xy_distance support_interface_top_layers brim_type brim_width brim_object_gap initial_layer_speed inner_wall_speed outer_wall_speed small_perimeter_speed small_perimeter_threshold default_acceleration initial_layer_acceleration wall_loops sparse_infill_density sparse_infill_pattern top_surface_pattern print_sequence nozzle_temperature nozzle_temperature_initial_layer hot_plate_temp hot_plate_temp_initial_layer textured_plate_temp textured_plate_temp_initial_layer curr_bed_type temperature_vitrification'.split()

def paths(text):
    absolute=True;erel=False;pos=dict(X=0.,Y=0.,Z=0.,E=0.);role='Custom';segments=defaultdict(list)
    for line in text.splitlines():
        if line.startswith(';TYPE:'):role=line.removeprefix(';TYPE:').strip()
        code=line.split(';',1)[0].strip()
        if not code:continue
        cmd=code.split()[0];a={k:float(v) for k,v in NUM.findall(code)}
        if cmd=='G90':absolute=True
        elif cmd=='G91':absolute=False
        elif cmd=='M83':erel=True
        elif cmd=='M82':erel=False
        elif cmd=='G92':pos.update(a)
        elif cmd in ('G0','G1'):
            old=dict(pos)
            for k in ('X','Y','Z'):
                if k in a:pos[k]=a[k] if absolute else pos[k]+a[k]
            de=a.get('E',0) if erel else a.get('E',pos['E'])-pos['E']
            if 'E' in a:pos['E']=pos['E']+a['E'] if erel else a['E']
            if de>0 and (old['X']!=pos['X'] or old['Y']!=pos['Y']) and role!='Custom':
                segments[role].append([[old[k] for k in ('X','Y','Z')],[pos[k] for k in ('X','Y','Z')]])
        elif cmd in ('G2','G3') and role!='Custom':raise ValueError('Arc extrusion requires separate parser')
    return {k:np.array(v) for k,v in segments.items()}

def main():
    evidence=HERE/'evidence';evidence.mkdir(exist_ok=True);reports=[]
    for plate in (1,2,3):
        src=ROOT/f'plate-{plate}/sliced.3mf'
        with ZipFile(src) as z:
            g=z.read('Metadata/plate_1.gcode');s=g.decode();cfg=json.loads(z.read('Metadata/project_settings.config'))
            meta=E.fromstring(z.read('Metadata/slice_info.config'))
            info={m.get('key'):m.get('value') for m in meta.iter('metadata') if m.get('key') in ('prediction','weight','outside','support_used','printer_model_id','nozzle_diameters')}
            warnings=[w.attrib for w in meta.iter('warning')]
            obj=json.loads(z.read('Metadata/plate_1.json'))['bbox_objects']
        seg=paths(s);allp=np.concatenate(list(seg.values())).reshape(-1,3)
        support=np.concatenate([v for k,v in seg.items() if k.startswith('Support')]) if plate<3 else np.empty((0,2,3))
        brim=seg.get('Brim');assert brim is not None and len(brim)>0
        original=roundtrip.meshes(HERE/f'dotisk-25-podlozka-{plate:02d}.3mf')
        imported=roundtrip.meshes(src)
        assert original.keys()==imported.keys()
        vertex_delta=0
        for name,(vertices,faces) in original.items():
            new_vertices,new_faces=imported[name]
            assert np.array_equal(faces,new_faces)
            delta=float(np.max(np.abs(vertices-new_vertices)));assert delta<.00002
            vertex_delta=max(delta,vertex_delta)
        assert (info['support_used']=='true')==(plate<3)
        assert ('Support' in seg)==(plate<3)
        assert cfg['printer_model']=='Anycubic Kobra X' and cfg['nozzle_diameter']==['0.4']
        assert len(obj)==(1 if plate<3 else 5)
        assert cfg['brim_type']=='outer_only' and float(cfg['brim_width'])==8
        assert info['outside']=='false' and np.min(allp[:,:2])>.5 and np.max(allp[:,:2])<259.5
        bounds=[allp.min(0).tolist(),allp.max(0).tolist()]
        # Render the actual extrusion centre lines; supports/interface are orange.
        fig,axes=plt.subplots(1,3,figsize=(16,6),facecolor='white')
        roles={}
        for k,v in seg.items():
            roles[k]={'segments':len(v),'bounds_mm':[v.reshape(-1,3).min(0).tolist(),v.reshape(-1,3).max(0).tolist()]}
        groups=[('Model','#477b9f',.28,[v for k,v in seg.items() if k!='Brim' and not k.startswith('Support')]),
                ('Brim','#299562',.9,[brim]),('Podpory + rozhraní','#e37b20',.9,[support] if len(support) else [])]
        for ax,dims,title in zip(axes,((0,1),(0,2),(1,2)),('Pohled shora XY','Pohled z boku XZ','Pohled z boku YZ')):
            for label,color,alpha,group in groups:
                if not group:continue
                a=np.concatenate(group)[:,:,list(dims)]
                ax.add_collection(LineCollection(a,colors=color,linewidths=.3,alpha=alpha,rasterized=True,label=label))
            ax.autoscale();ax.margins(.1);ax.set_aspect('equal');ax.grid(alpha=.15)
            ax.set_title(title);ax.set_xlabel('XYZ'[dims[0]]+' [mm]');ax.set_ylabel('XYZ'[dims[1]]+' [mm]')
        axes[0].legend(loc='best',fontsize=8)
        fig.suptitle(f'Dotisk {plate} · skutečné dráhy z místního řezání · Kobra X 0,4 / PLA / vrstva 0,12 mm',fontsize=15)
        fig.text(.04,.025,'Oranžová: podpory a jejich rozhraní. Zelená: brim. Kontrola drah není potvrzení fyzického tisku.',fontsize=11)
        fig.tight_layout(rect=(0,.065,1,.94));fig.savefig(evidence/f'drahy-{plate:02d}.png',dpi=140);plt.close(fig)
        reports.append({'plate':plate,'source_3mf':f'dotisk-25-podlozka-{plate:02d}.3mf','source_sha256':hashlib.sha256((HERE/f'dotisk-25-podlozka-{plate:02d}.3mf').read_bytes()).hexdigest(),
                        'sliced_archive_path':str(src),'sliced_archive_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'gcode_sha256':hashlib.sha256(g).hexdigest(),
                        'slicer':'Installed AnycubicSlicerNext; generated header reports 2.0.0.5','exit_code':0,'metadata':info,'warnings':warnings,
                        'object_names':[o['name'] for o in obj],'settings':{k:cfg[k] for k in KEYS if k in cfg},
                        'imported_triangle_indices_unchanged':True,'maximum_import_vertex_error_mm':vertex_delta,
                        'extruding_path_bounds_mm':bounds,'roles':roles,'extrusion_centre_lines_inside_bed':True})
    report={'status':'pass_with_recorded_profile_warnings','method':'Offline slicing, isolated profiles; actual G-code feature roles and all non-custom extrusion centre lines parsed. No printer connection.',
            'limits':'No physical print, strength, support removability or live personal profile verified. Full startup/custom moves and machine execution are outside this path audit. Diagnostic G-code is not a deliverable to send to the printer.',
            'plates':reports}
    (HERE/'overeni-rezani.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'plate':r['plate'],'metadata':r['metadata'],'bounds_mm':r['extruding_path_bounds_mm']} for r in reports],indent=2))

if __name__=='__main__':main()
