#!/usr/bin/env python3
"""Independent source/provenance audit of the authorized nominal fit prototype.

Does not run CAD geometry checks or rewrite their results. Re-run after the last
GUI save with --final-fcstd-sha256 SHA. Writes only its own JSON report.
"""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'historie/pred-kalibraci-8_6-12_6-2026-09-20'
MAIN = 'auticko-silovy-prevod-25'
REVIEWED = {
    MAIN + '.FCMacro': 'f970d5b78660a9bcd2cdd57ad66e9e7e9df38eb19f755fcae27e62a91e319df2',
    'rizeni-geometrie.py': '00de3cdfd40525ca7ef1b0d50cd2ba6953114b9f29b53cb15b997eb785255dcd',
    'servo-uchyceni.py': 'b9607955472bd3815e171139796e4d373b1fc03a4d0a64e88e9a8e3099397646',
    'rizeni-sestava.py': 'ad23bb77641200fc0f4ada5e97a5363b22f0fa44e3c76a01d51516032da44d0b',
}
sha = lambda data: hashlib.sha256(data).hexdigest()


def doc_objects(z):
    return {n.attrib['name']: n for n in ET.fromstring(z.read('Document.xml')).findall('./ObjectData/Object')}


def cells(obj):
    return {n.attrib['alias']: n.attrib['content']
            for n in obj.findall('./Properties/Property[@name="cells"]/Cells/Cell')
            if n.attrib.get('alias')}


def placement(obj, prop):
    n = obj.find('./Properties/Property[@name="%s"]/PropertyPlacement' % prop)
    return None if n is None else {k: float(v) for k, v in n.attrib.items()}


def literal_assignment(src, name):
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return ast.literal_eval(n.value)
    raise ValueError(name)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--final-fcstd-sha256', required=True)
    args = ap.parse_args()
    checks = {}
    with zipfile.ZipFile(BASE / 'puvodni-revize.zip') as old:
        manifest = json.loads((BASE / 'sha256.json').read_text())
        manifest_bad = [n for n, h in manifest.items() if n not in old.namelist() or sha(old.read(n)) != h]
        checks['archived_86_files_match_manifest'] = len(manifest) == 86 and not manifest_bad
        old_report = json.loads(old.read('kontrola-modelu.json'))
        old_audit = json.loads(old.read('nezavisla-kontrola.json'))
        current = json.loads((ROOT / 'kontrola-modelu.json').read_text())
        source_hashes = {n: sha((ROOT / n).read_bytes()) for n in REVIEWED}
        checks['source_matches_independently_reviewed_diff'] = source_hashes == REVIEWED
        checks['model_report_binds_current_source'] = current['source_hashes'] == source_hashes
        identical_source = {n: old.read(n) == (ROOT / n).read_bytes()
                            for n in ['rizeni-geometrie.py', 'rizeni-sestava.py', 'kinematika.py']}
        checks['steering_and_kinematics_source_unchanged'] = all(identical_source.values())

        before = dict(literal_assignment(old.read(MAIN + '.FCMacro').decode(), 'values'))
        now = dict(literal_assignment((ROOT / (MAIN + '.FCMacro')).read_text(), 'values'))
        changes = {k: [before.get(k), now.get(k)] for k in sorted(before.keys() | now.keys()) if before.get(k) != now.get(k)}
        expected = {'RearBearingBore': [12.2, 12.6], 'OutputBore': [None, 12.1],
                    'DriveBore': [12.3, 12.1], 'DriveFlat': [4.2, 4.05],
                    'RunningBore': [8.2, 8.6], 'CrossPinBore': [4.2, None],
                    'StaticLockBore': [None, 4.1], 'DeckSocketBore': [None, 8.1]}
        checks['only_reviewed_fit_dimensions_changed'] = changes == expected
        gear_values = literal_assignment((ROOT / (MAIN + '.FCMacro')).read_text(), 'gear_values')
        checks['original_tooth_profile_parameters'] = gear_values == [
            ('PressureAngle', 20, 'deg'), ('SmallAddendum', 1.1, ''),
            ('LargeAddendum', 1.2, ''), ('Dedendum', 1.25, ''), ('ProfileShift', 0, '')]
        checks['teeth_ratio_phases_and_centres_unchanged'] = all(current[k] == old_report[k] for k in [
            'teeth', 'ratio', 'gear_phases_deg', 'gear_centres_mm',
            'gear_addendum_coefficients', 'gear_dedendum_coefficient'])

        old_doc_bytes = old.read(MAIN + '.FCStd')
        current_doc_bytes = (ROOT / (MAIN + '.FCStd')).read_bytes()
        fcstd_sha = sha(current_doc_bytes)
        checks['fcstd_matches_final_gui_saved_hash'] = fcstd_sha == args.final_fcstd_sha256
        with zipfile.ZipFile(io.BytesIO(old_doc_bytes)) as az, zipfile.ZipFile(io.BytesIO(current_doc_bytes)) as bz:
            a, b = doc_objects(az), doc_objects(bz)
            checks['steering_spreadsheet_unchanged'] = cells(a['Steering']) == cells(b['Steering'])
            placements = []
            for name in sorted(a.keys() & b.keys()):
                for prop in ['Placement', 'LinkPlacement']:
                    pa, pb = placement(a[name], prop), placement(b[name], prop)
                    if pa is None and pb is None:
                        continue
                    err = max(abs(pa[k] - pb[k]) for k in pa) if pa is not None and pb is not None and pa.keys() == pb.keys() else None
                    placements.append({'object': name, 'property': prop, 'maximum_numeric_difference': err})
            checks['all_existing_placements_unchanged_within_1e-10'] = all(p['maximum_numeric_difference'] is not None and p['maximum_numeric_difference'] < 1e-10 for p in placements)
            shape_hashes = {n: sha(bz.read(n)) for n in sorted(bz.namelist()) if n.endswith('.Shape.brp')}
            shape_fingerprint = sha(json.dumps(shape_hashes, sort_keys=True).encode())
            # Serialization equality is not a geometric test: regenerated floats
            # and topology IDs can change even for the same nominal outline.
            outlines = {n: {'baseline_sha256': sha(az.read(n)), 'current_sha256': sha(bz.read(n)),
                            'serialized_bytes_identical': az.read(n) == bz.read(n)}
                        for n in ['A54Outline.Shape.brp', 'A18Outline.Shape.brp', 'B60Outline.Shape.brp',
                                  'B22Outline.Shape.brp', 'Output55Outline.Shape.brp', 'Input18Outline.Shape.brp']}
            current_instances = [n.attrib.get('name') for n in ET.fromstring(bz.read('Document.xml')).findall('./Objects/Object')]
            checks['all_reported_assembly_objects_exist_in_fcstd'] = all(n['name'] in current_instances for n in current['assembly_instances'])

        counts = Counter(i['part'] for i in current['assembly_instances'])
        stl_hashes = {p['stl']: sha((ROOT / p['stl']).read_bytes()) for p in current['parts'].values()}
        checks['stl_hashes_match_model_report'] = all(stl_hashes[p['stl']] == p['sha256'] for p in current['parts'].values())
        checks['34_types_66_instances_unchanged'] = len(counts) == 34 and sum(counts.values()) == 66 and current['assembly_instances'] == old_report['assembly_instances']
        checks['counts_derived_from_assembly_match_parts'] = all(counts[k] == p['copies'] for k, p in current['parts'].items())
        checks['four_wheels'] = counts['kolo-76x12-predni'] == 2 and counts['kolo-76x12-zadni-d'] == 2
        checks['all_34_exports_valid_single_closed_solids'] = all(p['valid'] and p['solid_count'] == 1 and p['closed_mesh'] for p in current['parts'].values())
        checks['conservative_full_play_scenario_not_claimed_pass'] = current.get('full_nominal_radial_clearance_scenario_pass') is False
        supplied_geometry_bytes = (ROOT / 'kontrola-revize-fitu.json').read_bytes()
        supplied_geometry = json.loads(supplied_geometry_bytes)
        checks['supplied_geometry_report_binds_reviewed_source'] = supplied_geometry['source_hashes'] == source_hashes
        checks['supplied_nominal_geometry_pass'] = supplied_geometry['nominal_cad_validation_pass'] is True and supplied_geometry['full_nominal_radial_clearance_scenario_pass'] is False
        checks['supplied_nominal_pairs_have_no_interference'] = not supplied_geometry['nominal_collisions'] and all(p['overlap_mm3'] < 1e-6 for p in supplied_geometry['nominal_pairs'])
        checks['supplied_six_outlines_identical_to_archived_geometry'] = len(supplied_geometry['gear_outline_identity']) == 6 and all(
            p['symmetric_difference_mm3_at_1mm'] < 1e-6 and p['archive_fcstd_sha256'] == sha(old_doc_bytes)
            for p in supplied_geometry['gear_outline_identity'])
        checks['supplied_historical_member_hashes_match_archive'] = all(
            sha(old.read(n)) == h for n, h in supplied_geometry['reused_evidence']['member_sha256'].items())
        checks['supplied_changed_horn_void_extremes_clear'] = all(p['overlap_mm3'] < 1e-6 for p in supplied_geometry['changed_horn_voids_extreme_checks'])
        checks['supplied_stage3_retains_full_8mm_contact_width'] = supplied_geometry['stage3_full_8mm_contact_minimum_margin_mm'] > 0
        reviewed_diffs = {}
        for n in [MAIN + '.FCMacro', 'servo-uchyceni.py']:
            diff = '\n'.join(difflib.unified_diff(old.read(n).decode().splitlines(), (ROOT / n).read_text().splitlines(), fromfile='archive/' + n, tofile=n))
            reviewed_diffs[n] = {'baseline_sha256': sha(old.read(n)), 'current_sha256': source_hashes[n], 'unified_diff_sha256': sha(diff.encode())}
        report = {
            'audit': 'Independent source and provenance review of the user-authorized nominal print prototype',
            'updated_utc': datetime.now(timezone.utc).isoformat(),
            'pass': all(checks.values()),
            'scope': 'source_diff_and_nominal_geometry_provenance_only',
            'nominal_provenance_pass': all(checks.values()),
            'full_nominal_radial_clearance_scenario_pass': False,
            'full_play_scenario_is_release_gate': False,
            'physical_assembly_or_load_test_claimed': False,
            'source_sha256': source_hashes[MAIN + '.FCMacro'], 'source_hashes': source_hashes,
            'snapshot_fcstd_sha256': fcstd_sha, 'current_fcstd_sha256': fcstd_sha,
            'final_gui_saved_fcstd_binding': checks['fcstd_matches_final_gui_saved_hash'],
            'current_brep_data_fingerprint_sha256': shape_fingerprint,
            'executed_audit_script_sha256': sha(Path(__file__).read_bytes()),
            'checks': checks, 'counts': dict(sorted(counts.items())), 'instance_count': sum(counts.values()), 'wheel_count': 4,
            'fit_parameter_changes_mm': changes, 'reviewed_source_diffs': reviewed_diffs,
            'unchanged_sources': identical_source,
            'placement_check': {'count': len(placements), 'numeric_tolerance': 1e-10,
                                'maximum_difference': max(p['maximum_numeric_difference'] or 0 for p in placements)},
            'gear_outline_serialization': outlines,
            'current_stl_sha256': stl_hashes,
            'supplied_current_geometry_evidence': {
                'report': 'kontrola-revize-fitu.json', 'report_sha256': sha(supplied_geometry_bytes),
                'executed_by_this_independent_audit': False,
                'input_fcstd_sha256_before_final_gui_save': supplied_geometry['input_fcstd_sha256'],
                'nominal_pair_count': len(supplied_geometry['nominal_pairs']),
                'nominal_collision_count': len(supplied_geometry['nominal_collisions']),
                'gear_outline_identity': supplied_geometry['gear_outline_identity'],
                'changed_horn_void_extreme_pairs': len(supplied_geometry['changed_horn_voids_extreme_checks']),
                'stage3_full_8mm_contact_minimum_margin_mm': supplied_geometry['stage3_full_8mm_contact_minimum_margin_mm']},
            'archive': {'path': str((BASE / 'puvodni-revize.zip').relative_to(ROOT)),
                        'zip_sha256': sha((BASE / 'puvodni-revize.zip').read_bytes()),
                        'manifest_sha256': sha((BASE / 'sha256.json').read_bytes()),
                        'verified_files': len(manifest), 'manifest_mismatches': manifest_bad,
                        'archived_final_fcstd_sha256': sha(old_doc_bytes)},
            'historical_evidence': {
                'current_cad_checks_rerun_by_this_audit': False,
                'reuse_scope': 'Only unchanged tooth profiles, axes, outer material geometry and kinematics; changed fit voids require current nominal geometry checks in kontrola-modelu.json. No inherited clearance guarantee.',
                'steering': {'archive_report': 'nezavisla-kontrola.json', 'report_sha256': sha(old.read('nezavisla-kontrola.json')),
                             'snapshot_fcstd_sha256': old_audit['snapshot_fcstd_sha256'],
                             'source_sha256': old_audit['source_sha256'],
                             'samples': len(old_audit['steering']),
                             'pair_checks': sum(s['tests'] for s in old_audit['steering']),
                             'collisions': sum(len(s['collisions']) for s in old_audit['steering']),
                             'is_current_revision_rerun': False},
                'gears': {'archive_report': 'kontrola-modelu.json', 'report_sha256': sha(old.read('kontrola-modelu.json')),
                          'source_sha256': old_report['source_sha256'],
                          'phase_samples': len(old_report['gear_motion']['samples']),
                          'is_current_revision_rerun': False},
                'snapshot_note': 'Historical independent audit snapshot hash differs from later archived GUI-saved FCStd. Both are named explicitly; source and current XML placement checks establish source-level continuity, not byte identity or a new motion rerun.'},
            'limitations': [
                'PASS refers to the listed source/provenance checks, not every tolerance combination or measured load capacity.',
                'Nominal CAD diametric differences are not measured running clearances. Actual printed radial play is unknown.',
                'The original20degree/m1 gear geometry is retained; no successful full enlarged radial-play envelope is claimed.',
                '8.1/12.1 fixed fits,4.1static locks and Dflat4.05 are requested nominal fit drafts; complete revised car has not been physically assembled.',
                'Byte differences in regenerated BREP serialization are not by themselves geometry differences; current geometry comparison is a separate writer-produced check.']}
    (ROOT / 'nezavisla-kontrola-revize.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'failed_checks': [k for k, v in checks.items() if not v],
                      'fcstd_sha256': fcstd_sha, 'parts': len(counts), 'instances': sum(counts.values())}, ensure_ascii=False))
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
