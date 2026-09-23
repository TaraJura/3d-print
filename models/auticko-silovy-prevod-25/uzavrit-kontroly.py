#!/usr/bin/env python3
"""Uzavře aktuální NOMINÁLNÍ tiskový prototyp; nepřijímá dřívější radiální worst-casePASS."""
from pathlib import Path
from collections import Counter
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent
def read(n):return json.loads((ROOT/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read('kontrola-modelu.json');v=read('kontrola-revize-fitu.json');p=read('kontrola-parametru.json');g=read('kontrola-gui.json')
assert r['validation_mode']=='user_authorized_nominal_print_prototype'
assert g['gui_validation']['saved_and_reopened']
assert all(a['source_hashes']==r['source_hashes'] for a in (v,p,g))
assert r['source_hashes']=={n:sha(ROOT/n) for n in r['source_hashes']}
assert v['nominal_cad_validation_pass'] and not v['full_nominal_radial_clearance_scenario_pass'] and p['passed']
assert v['input_fcstd_sha256']==p['input_fcstd_sha256']
transition=read('kontrola-prechodu-gui.json');assert transition['passed']
assert transition['input_fcstd_sha256']==v['input_fcstd_sha256']
assert transition['final_fcstd_sha256']==sha(ROOT/'auticko-silovy-prevod-25.FCStd')
assert not v['nominal_collisions']
archive=ROOT/v['reused_evidence']['archive']
with zipfile.ZipFile(archive) as z:
 for n,h in v['reused_evidence']['member_sha256'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 old=json.loads(z.read('kontrola-modelu.json'))
r['assembly_pairs']=v['nominal_pairs'];r['assembly_collisions']=v['nominal_collisions']
r['gui_validation']=g['gui_validation'];r['final_print_group']=g['final_print_group'];r['gui_geometry_provenance']=transition
r['gui_validation']['visual_review']={'method':'view_image','images':['rovne.png','doleva.png','doprava.png','mechanismus.png','rozlozena-sestava.png'],'all_viewed':True,'result':'Různé polohy řízení, sestava a všech66 rozložených instancí bez chybějících viditelných dílů.'}
r['nominal_cad_validation_pass']=True;r['full_nominal_radial_clearance_scenario_pass']=False
r['gear_nominal_validation_pass']=True;r['gear_validation_pass']=False
r['steering_validation_pass']=True;r['reused_evidence']=v['reused_evidence'];r['nominal_revision_checks']=v
r['drivetrain_parameter_checks']=p
r['gear_motion']={'nominal_65_phase_evidence':'archived kontrola-modelu.json, gear_motion.samples[*].pairs[*].nominal_overlap_mm3','geometry_identity':'kontrola-revize-fitu.json, gear_outline_identity; stejné6obrysy, rozteče a fáze','radial_minimum_maximum_evidence_reused':False}
r['axial_extremes']={'cases':v['axial_extremes'],'stage3_minimum_full_width_margin_mm':v['stage3_full_8mm_contact_minimum_margin_mm'],'stage1_minimum_contact_width_mm':4.9,'explanation':'Výstup±0,3 = osa±0,2 + součet vůlí dvou otvorů klínku±0,1; A/B±0,2; motor0..+0,4.'}
r['gear_profile']=old['gear_profile'];r['gear_profile']['maximum_centre_contact_ratio']=v['conservative_radial_contact_ratios'];r['gear_profile']['limit']='Obrysy jsou geometricky shodné s archivem, měření špiček přebráno s touto identitou. Nominální20°záběr je ověřen; celý konzervativní scénář nových CAD radiálních vůlí NENÍ pokryt a fyzická vůle není změřena.'
r['ground_clearance_mm']=old['ground_clearance_mm']
r['guide_bands']={'journal_diameter_mm':8,'running_bore_mm':r['parameters_mm']['RunningBore'],'two_contact_lengths_mm':[r['parameters_mm']['JournalLength']]*2,'relieved_middle_diameter_mm':r['parameters_mm']['MiddleBore'],'relieved_middle_length_mm':30-2*r['parameters_mm']['JournalLength'],'limit':'Menší kontaktní plocha nezaručuje nižší tření. Skutečná vůle, naklopení, ohyb a nosnost neověřeny.'}
r['validation_pass']=True
r['status']='Autorizovaný tiskový prototyp25:1+SG90: nominální CAD ověřen, celý konzervativní radiální scénář NEPOKRYT. Fyzická montáž/fit/nosnost/jízda neověřeny.'
r['validation_scope']={'mode':'nominal_print_prototype','nominal_static_assembly':True,'changed_parametric_recompute_restore':True,'changed_horn_lock_holes_at_steering_extremes':True,'axial_8mm_in_12mm_engagement':True,'unchanged_gears_nominal_motion_reused_with_shape_identity':True,'unchanged_steering_motion_reused_with_source_and_parameter_identity':True,'full_nominal_radial_clearance_scenario_pass':False,'physical_test':False}
counts=Counter(i['part'] for i in r['assembly_instances']);assert counts==Counter({k:v['copies'] for k,v in r['parts'].items()})
with zipfile.ZipFile(ROOT/'tiskovy-balicek.zip') as z:
 manifest=json.loads(z.read('KUSOVNIK.json'));assert manifest['part_counts']==dict(counts) and manifest['total']==len(r['assembly_instances'])
 assert manifest['source_hashes']==r['source_hashes']
 for e in manifest['instances']:assert hashlib.sha256(z.read(e['archive_entry'])).hexdigest()==r['parts'][e['part']]['sha256']
assert r['print_bundle']['sha256']==sha(ROOT/'tiskovy-balicek.zip')
r['validation_evidence']={n:sha(ROOT/n) for n in ['kontrola-revize-fitu.json','kontrola-parametru.json','kontrola-gui.json','overit-revizi-fitu.FCMacro','overit-parametry.FCMacro','nahled.FCMacro','uzavrit-kontroly.py','kontrola-prechodu-gui.json','overit-prechod-gui.py']}
(ROOT/'kontrola-modelu.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
files=['auticko-silovy-prevod-25.FCStd','tiskovy-balicek.zip','kontrola-modelu.json','rovne.png','doleva.png','doprava.png','mechanismus.png','rozlozena-sestava.png']+[v['stl'] for v in r['parts'].values()]
proof={'scope':r['validation_scope'],'source_hashes':r['source_hashes'],'artifact_sha256':{n:sha(ROOT/n) for n in files},'validation_evidence':r['validation_evidence'],'actual_print_instances':len(r['assembly_instances'])}
(ROOT/'overeni-finalnich-souboru.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'nominal_cad_validation_pass':True,'full_nominal_radial_clearance_scenario_pass':False,'types':len(counts),'copies':len(r['assembly_instances']),'zip_sha256':sha(ROOT/'tiskovy-balicek.zip'),'fcstd_sha256':sha(ROOT/'auticko-silovy-prevod-25.FCStd')},ensure_ascii=False))
