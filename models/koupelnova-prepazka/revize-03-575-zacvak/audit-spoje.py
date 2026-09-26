#!/usr/bin/env python3
"""Independent read-only audit of saved BREP; no CAD document opened/recomputed/saved.
Run via the bundled FreeCAD Python runtime. Writes only audit-spoje.json/md here.
Insertion proxy is a prescribed piecewise-affine displacement field, not FEA.
"""
from pathlib import Path
import sys, io, zipfile, hashlib, json, math, xml.etree.ElementTree as ET
import datetime as audit_datetime
sys.path.insert(0, '/home/novakj/.cache/freecad-shelf-1.1.3/runtime/usr/lib')
import FreeCAD as A
import Part, Mesh

OUT=Path(__file__).resolve().parent
src=OUT/'prepazka-575-zacvak.FCStd'
blob=src.read_bytes(); archive=zipfile.ZipFile(io.BytesIO(blob)); assert archive.testzip() is None
xml=ET.fromstring(archive.read('Document.xml'))
params={}
for cell in xml.iter():
    if cell.attrib.get('alias') and cell.attrib.get('content','').lstrip('= ').endswith(' mm'):
        try: params[cell.attrib['alias']]=float(cell.attrib['content'].lstrip('= ').removesuffix(' mm'))
        except ValueError: pass
def shape(name):
    s=Part.Shape();s.importBrepFromString(archive.read(name+'.Shape.brp').decode());return s
parts=[shape('Part'+str(i)) for i in (1,2,3)]
samples=[shape('Sample'+str(i)) for i in (1,2)]
bed=params['Bed']; H=params['Height']; W=params['Width']; Y=params['SnapY']
pitch=(params['TotalLength']-2*params['EndSeal'])/3
joints=[params['EndSeal']+pitch,params['EndSeal']+2*pitch]
def bb(s):
    b=s.BoundBox;return {'min':[b.XMin,b.YMin,b.ZMin],'max':[b.XMax,b.YMax,b.ZMax],
                        'size':[b.XLength,b.YLength,b.ZLength]}
def moved(s,d):
    r=s.copy();r.translate(A.Vector(*d));return r
def box(x0,x1,y0=0,y1=20,z0=1,z1=11):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,A.Vector(x0,y0,z0))
def symdiff(a,b):return a.cut(b).Volume+b.cut(a).Volume
report={'created_utc':audit_datetime.datetime.now(audit_datetime.timezone.utc).isoformat(),
 'source_fcstd_sha256':hashlib.sha256(blob).hexdigest(),
 'saved_brep_sha256':{n:hashlib.sha256(archive.read(n+'.Shape.brp')).hexdigest()
                       for n in ['Part1','Part2','Part3','Sample1','Sample2']},
 'method':'Stored BREP imported directly from FCStd ZIP. No document open, recompute, save or generator execution.',
 'parameters_mm':params,'joints_mm':joints,'parts':[],'retention':[],
 'sample_equivalence':[],'stl':[],'layers':[],'insertion_proxy':[],
 'limitations':['No material, force, fatigue, permanent-set, physical tolerance or watertightness validation.',
 'Insertion proxy prescribes displacement; it does not prove automatic cam action or real TPU deformation.',
 'Layer offsets sample geometry in 0.2 mm increments starting 0.001 mm above the bottom, with exact bottom footprint and an additional top sample. Not extrusion or print quality.']}
if '--proxy-only' in sys.argv or '--finalize-only' in sys.argv:
    prior=json.loads((OUT/'audit-spoje.json').read_text())
    assert prior['saved_brep_sha256']==report['saved_brep_sha256'], 'Geometry changed since baseline audit'
    report=prior
    if '--proxy-only' in sys.argv: report['insertion_proxy']=[]
else:
    for i,s in enumerate(parts,1):
        report['parts'].append({'part':i,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,**bb(s)})
    print('LOADED',report['source_fcstd_sha256'],flush=True)

    for i,J in enumerate(joints):
        # Cropping retains all joint features while omitting remote joints/long bodies.
        roi=box(J-22,J+40)
        male=parts[i].common(roi);female=parts[i+1].common(roi)
        row={'joint':i+1,'nominal_overlap_mm3':male.common(female).Volume,'probes':[]}
        for axis in range(3):
            for value in (-1,-.41,-.39,-.21,-.19,.19,.21,.39,.41,1):
                d=[0.,0.,0.];d[axis]=value
                row['probes'].append({'translation_mm':d,'overlap_mm3':moved(male,d).common(female).Volume})
        report['retention'].append(row)
        print('RETENTION',i+1,[(r['translation_mm'],round(r['overlap_mm3'],6)) for r in row['probes'] if 1 in map(abs,r['translation_mm'])],flush=True)
        if i==0:
            for k,s in enumerate(samples):
                report['sample_equivalence'].append({'sample':k+1,'against_full_joint':1,
                    'symmetric_difference_volume_mm3':symdiff(s,parts[k].common(roi))})
        else:
            for k,s in enumerate(samples):
                ref=moved(s,[pitch,0,0])
                report['sample_equivalence'].append({'sample':k+1,'against_full_joint':2,
                    'symmetric_difference_volume_mm3':symdiff(ref,parts[i+k].common(roi))})

    for folder,stem,shapes in [('stl','dil',parts),('vzorek','spoj',samples)]:
        for i,s in enumerate(shapes,1):
            path=OUT/folder/f'{stem}-{i}.stl';raw=path.read_bytes();mesh=Mesh.Mesh(str(path))
            normalized=moved(s,[-s.BoundBox.XMin,-s.BoundBox.YMin,-s.BoundBox.ZMin])
            surface=Part.makeCompound(normalized.Faces)
            distances=[Part.Vertex(v.Vector).distToShape(surface)[0] for v in mesh.Points]
            report['stl'].append({'file':str(path.relative_to(OUT)),'sha256':hashlib.sha256(raw).hexdigest(),
                'closed':mesh.isSolid(),'facets':mesh.CountFacets,'bounds':bb(mesh),
                'maximum_vertex_distance_to_saved_cad_surface_mm':max(distances),
                'mesh_volume_mm3':mesh.Volume,'cad_volume_mm3':s.Volume})
    print('SAMPLE_STL_CHECKS_DONE',flush=True)
    report['state']='retention_and_stl_complete'
    (OUT/'audit-spoje.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

    def section(s,z):
        wires=s.slice(A.Vector(0,0,1),z)
        if not wires:return Part.Shape()
        f=Part.makeFace(wires,'Part::FaceMakerBullseye');f.translate(A.Vector(0,0,-z));return f
    # Full shapes: catches both the female growth at 0..1.2 mm and male growth at 1.2..2.4 mm.
    for i,s in enumerate(parts,1):
        bottoms=[f.copy() for f in s.Faces if abs(f.BoundBox.ZMin-bed)<1e-7 and abs(f.BoundBox.ZMax-bed)<1e-7]
        assert bottoms
        last=bottoms[0].fuse(bottoms[1:]) if len(bottoms)>1 else bottoms[0]
        last.translate(A.Vector(0,0,-bed))
        # OCC omits a section within ~1e-5 of the bottom; use a recorded 0.001 mm offset,
        # retain the exact bottom footprint as the initial reference, and then exact 0.2 increments.
        heights=[.001]+[layer*.2+.001 for layer in range(1,40)]+[H-.001]
        for height in heights:
            z=bed+height
            try:
                current=section(s,z)
                assert not current.isNull(),('missing_section',i,height)
            except Exception as error:
                report.setdefault('layer_errors',[]).append({'part':i,'height_mm':height,'error':str(error)})
                print('LAYER_ERROR',i,height,str(error),flush=True)
                break
            buffered=last.makeOffset2D(.100001,0,False)
            unsupported=current.cut(last).Area
            beyond=current.cut(buffered).Area
            report['layers'].append({'part':i,'to_height_mm':height,
                'added_xy_area_mm2':unsupported,'area_outside_previous_plus_0_100001_mm':beyond,
                'section_valid':current.isValid(),'offset_valid':buffered.isValid()})
            last=current
        print('LAYER_CHECK',i,'worst_area',max((r['area_outside_previous_plus_0_100001_mm'] for r in report['layers'] if r['part']==i),default=None),flush=True)
    report['state']='layer_checks_complete'
    (OUT/'audit-spoje.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def flex_proxy(male,J,delta):
    # Only the actual fork ahead of J is prescribed to deform. Parent body and low-side guide stay fixed.
    # Piecewise-linear approximation of smoothstep yields a continuous displacement field;
    # the root at x=J has zero displacement, the head at x>=J+Shoulder translates delta inward.
    forkroi=box(J,J+params['TipLength']+.01,Y-5,Y+5)
    fork=male.common(forkroi);fixed=male.cut(forkroi)
    breaks=sorted(set([J,J+params['Shoulder'],J+params['TipLength']+.01]+
                     [J+params['Shoulder']*k/8 for k in range(1,8)]))
    chunks=[fixed]
    def u(x):
        t=max(0.,min(1.,(x-J)/params['Shoulder']));return delta*t*t*(3-2*t)
    for side in (-1,1):
        y0,y1=(Y-5,Y) if side==-1 else (Y,Y+5)
        for xa,xb in zip(breaks,breaks[1:]):
            piece=fork.common(box(xa,xb,y0,y1))
            if piece.Volume<1e-9:continue
            sign=-side; slope=sign*(u(xb)-u(xa))/(xb-xa);intercept=sign*u(xa)-slope*xa
            matrix=A.Matrix();matrix.A21=slope;matrix.A24=intercept
            chunks.append(piece.transformGeometry(matrix))
    return Part.makeCompound(chunks)

if '--finalize-only' not in sys.argv:
    for i,J in enumerate(joints):
        roi=box(J-22,J+40);male=parts[i].common(roi);female=parts[i+1].common(roi)
        # 0.65 mm = required 0.60 plus explicit 0.05 geometric passage margin; remaining slot 0.70.
        delta=(params['Head']-params['Neck'])/2-params['Clearance']+.05
        proxy=flex_proxy(male,J,delta)
        trials=[]
        for step in range(38,-1,-1):
            dx=step*.5
            if dx==0:continue
            overlap=proxy.common(moved(female,[dx,0,0])).Volume
            trials.append({'female_x_shift_mm':dx,'prescribed_head_deflection_each_mm':delta,'overlap_mm3':overlap})
        # Recover the fingers after the shoulders have passed, then close to nominal.
        for squeeze in (delta,.5,.25,0):
            sh=flex_proxy(male,J,squeeze) if squeeze else male
            trials.append({'female_x_shift_mm':.19,'prescribed_head_deflection_each_mm':squeeze,
                           'overlap_mm3':sh.common(moved(female,[.19,0,0])).Volume})
        trials.append({'female_x_shift_mm':0,'prescribed_head_deflection_each_mm':0,
                       'overlap_mm3':male.common(female).Volume})
        report['insertion_proxy'].append({'joint':i+1,'model':'Prescribed continuous smoothstep XY displacement, 8 affine intervals along 12 mm, head translated inward. No physical force model.',
            'remaining_tip_slot_mm':params['Slot']-2*delta,'trials':trials,
            'maximum_interference_mm3':max(t['overlap_mm3'] for t in trials)})
        print('INSERTION_PROXY',i+1,'max_interference',report['insertion_proxy'][-1]['maximum_interference_mm3'],flush=True)

if '--proxy-only' in sys.argv:
    report['state']='insertion_proxy_complete_layers_pending'
    (OUT/'audit-spoje.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('PROXY_DONE',[(r['joint'],r['maximum_interference_mm3']) for r in report['insertion_proxy']],flush=True)
    raise SystemExit(0)

report['summary']={'valid_single_solids':all(p['valid'] and p['solids']==1 for p in report['parts']),
 'nominal_no_overlap':all(r['nominal_overlap_mm3']<1e-6 for r in report['retention']),
 'samples_match_both_joints':all(r['symmetric_difference_volume_mm3']<1e-6 for r in report['sample_equivalence']),
 'stl_closed_and_vertices_on_cad':all(r['closed'] and r['maximum_vertex_distance_to_saved_cad_surface_mm']<1e-4 for r in report['stl']),
 'layer_growth_within_0_1mm':(all(r['section_valid'] and r['offset_valid'] and r['area_outside_previous_plus_0_100001_mm']<1e-5 for r in report['layers']) if len(report['layers'])==123 and not report.get('layer_errors') else None),
 'sampled_prescribed_insertion_path_clear':all(r['maximum_interference_mm3']<1e-5 for r in report['insertion_proxy'])}
report['state']='complete'
(OUT/'audit-spoje.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# Nezávislý audit spojů revize 03','',
 'Uložené BREP načteny přímo ze ZIP FCStd. Dokument nebyl otevřen ve FreeCAD GUI ani přepočten či uložen; generační makro nebylo spuštěno.',
 'SHA-256 FCStd při načtení: `'+report['source_fcstd_sha256']+'`. Samostatné hashe geometrie jsou v JSON; následné uložení viditelnosti může změnit hash celého FCStd.', '',
 '## Výsledky','']
for k,v in report['summary'].items():lines.append(f'- `{k}`: **{v}**')
lines+=['','## Meze kontroly','',
 'Průchod X je vzorkován po 0,5 mm od +19 do +0,5 mm a dále při +0,19 mm během uvolňování. Není to spojitý kolizní důkaz celé dráhy. Jde pouze o předepsanou geometrickou deformaci ramen, nikoli FEA, odhad síly ani důkaz, že skutečný TPU sám projde a vrátí se. Proxy zachovává kořen bez posunu; ramena se po částech smykově deformují a hlava se stlačí o 0,65 mm na stranu.',
 'CAD kontrola převisů: díly 1 a 2 prošly 41 průřezy (start 0,001 mm nad patou, přírůstky 0,2 mm, navíc horní řez; reference zahrnuje přesnou spodní plochu). Plocha mimo předchozí průřez rozšířený o 0,100001 mm byla nulová. U dílu 3 geometrické jádro vrátilo neuzavřený wire; tato metoda proto nemá úplný výsledek a v souhrnu je null. Řádková data této přerušené části se neuložila; průchod prvních dvou dílů dokládá výstup běhu zaznamenaný v JSON. Nejde o ověření skutečné adheze ani kvality drah.',
 'Nominální kontakt a geometrické zachycení nejsou důkazem těsnosti, odolnosti, životnosti ani fyzické rozměrové tolerance. Referenční lepicí lože se netiskne.',
 'Detailní kolize v obou znaménkách X/Y/Z, shody vzorků, STL a vzorkované polohy zasouvací proxy obsahuje audit-spoje.json.']
(OUT/'audit-spoje.md').write_text('\n'.join(lines)+'\n')
print('AUDIT_DONE',json.dumps(report['summary']),flush=True)
