#!/usr/bin/env python3
"""Nezavisle overeni celeho auta: instance, STL, ZIP a hashe. Bez externich knihoven."""
from pathlib import Path
from collections import defaultdict, Counter
import hashlib, json, struct, zipfile, re
ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / 'kontrola-modelu.json').read_text())
assert source['validation_pass'] and source['gui_validation']['saved_and_reopened']
assert source['nominal_cad_validation_pass'] is True
assert source['full_nominal_radial_clearance_scenario_pass'] is False
assert source['validation_mode'] == 'user_authorized_nominal_print_prototype'
sha = lambda b: hashlib.sha256(b).hexdigest()
assert source['source_sha256'] == sha((ROOT / 'auticko-silovy-prevod-25.FCMacro').read_bytes())
assert set(source['source_hashes']) == {'auticko-silovy-prevod-25.FCMacro', 'rizeni-geometrie.py', 'servo-uchyceni.py', 'rizeni-sestava.py'}
assert all(sha((ROOT / name).read_bytes()) == h for name, h in source['source_hashes'].items()), 'Stale generator module'
report = {'generator_sha256': source['source_sha256'], 'source_hashes': source['source_hashes'], 'files': {}, 'stl': {}, 'scope': 'Current nominal print prototype and actual exports; no full radial-clearance or physical-fit guarantee', 'nominal_cad_validation_pass': True, 'full_nominal_radial_clearance_scenario_pass': False, 'physical_test_claimed': False}
for name in ['auticko-silovy-prevod-25.FCStd', 'tiskovy-balicek.zip', 'nahled.FCMacro', 'rovne.png', 'doleva.png', 'doprava.png', 'mechanismus.png', 'rozlozena-sestava.png', 'README.md', 'architektura.md', 'montaz.md', 'kontrola-modelu.json']:
    b = (ROOT / name).read_bytes(); report['files'][name] = {'sha256': sha(b), 'bytes': len(b)}
assert source['print_bundle']['sha256'] == report['files']['tiskovy-balicek.zip']['sha256']
# Changed geometry is checked on the regenerated pre-GUI snapshot; a later GUI
# save has its own final hash. Historical unchanged-motion reports retain their
# original source/hash and are not relabelled as current reruns.
revision = json.loads((ROOT/'kontrola-revize-fitu.json').read_text())
parameters = json.loads((ROOT/'kontrola-parametru.json').read_text())
gui = json.loads((ROOT/'kontrola-gui.json').read_text())
independent = json.loads((ROOT/'nezavisla-kontrola-revize.json').read_text())
final_proof = json.loads((ROOT/'overeni-finalnich-souboru.json').read_text())
for proof in [revision, parameters, gui, independent, final_proof]:
    assert proof['source_hashes'] == source['source_hashes'], 'Stale current evidence source'
assert revision['nominal_cad_validation_pass'] and parameters['passed']
assert revision['full_nominal_radial_clearance_scenario_pass'] is False
assert revision['input_fcstd_sha256'] == parameters['input_fcstd_sha256']
bridge = json.loads((ROOT/'kontrola-prechodu-gui.json').read_text())
assert bridge['passed']
assert bridge['input_fcstd_sha256'] == revision['input_fcstd_sha256']
assert bridge['final_fcstd_sha256'] == report['files']['auticko-silovy-prevod-25.FCStd']['sha256']
assert bridge['maximum_numeric_token_difference'] <= bridge['numeric_serialization_tolerance'] <= 1e-6
assert bridge['maximum_placement_numeric_difference'] <= 1e-10
with zipfile.ZipFile(ROOT/'auticko-silovy-prevod-25.FCStd') as saved:
    assert len(bridge['checks']) == bridge['brep_members']
    assert {p['member'] for p in bridge['checks']} == {n for n in saved.namelist() if n.endswith('.brp')}
    assert all(sha(saved.read(p['member'])) == p['final_sha256'] for p in bridge['checks'])
assert not revision['nominal_collisions']
assert len(revision['gear_outline_identity']) == 6
assert all(p['symmetric_difference_mm3_at_1mm'] < 1e-6 for p in revision['gear_outline_identity'])
assert revision['stage3_full_8mm_contact_minimum_margin_mm'] >= 1.5 - 1e-8
assert gui['gui_validation']['saved_and_reopened'] and not gui['gui_validation']['invalid_objects']
assert independent['pass'] and all(independent['checks'].values())
assert independent['full_nominal_radial_clearance_scenario_pass'] is False
assert independent['current_fcstd_sha256'] == report['files']['auticko-silovy-prevod-25.FCStd']['sha256']
assert independent['supplied_current_geometry_evidence']['report_sha256'] == sha((ROOT/'kontrola-revize-fitu.json').read_bytes())
assert all(sha((ROOT/n).read_bytes()) == h for n,h in final_proof['artifact_sha256'].items())
assert all(sha((ROOT/n).read_bytes()) == h for n,h in source['validation_evidence'].items())
archive = ROOT/revision['reused_evidence']['archive']
assert sha(archive.read_bytes()) == independent['archive']['zip_sha256']
with zipfile.ZipFile(archive) as old:
    assert all(sha(old.read(n)) == h for n,h in revision['reused_evidence']['member_sha256'].items())
    for proof in [independent['historical_evidence']['steering'], independent['historical_evidence']['gears']]:
        assert proof['is_current_revision_rerun'] is False
        assert sha(old.read(proof['archive_report'])) == proof['report_sha256']
for name in ['kontrola-revize-fitu.json','kontrola-parametru.json','kontrola-gui.json',
             'nezavisla-kontrola-revize.json','overeni-finalnich-souboru.json','kontrola-prechodu-gui.json']:
    path=ROOT/name
    report['files'][name]={'sha256':sha(path.read_bytes()), 'bytes':path.stat().st_size}
report['evidence_scope'] = source['validation_scope']
report['pre_gui_geometry_snapshot_sha256'] = revision['input_fcstd_sha256']
report['final_gui_fcstd_sha256'] = independent['current_fcstd_sha256']
report['historical_checks_reused_with_explicit_provenance'] = True
instances = source['assembly_instances']
counts = Counter(i['part'] for i in instances)
assert len({i['name'] for i in instances}) == len(instances), 'Duplicate physical instance name'
assert source['counts_derived_from_assembly']
assert len(instances) == source['total_print_count']
assert counts == Counter({k: p['copies'] for k, p in source['parts'].items()})
assert all(i['stl'] == source['parts'][i['part']]['stl'] for i in instances)
assert {p.name for p in (ROOT/'stl').glob('*.stl')} == {Path(p['stl']).name for p in source['parts'].values()}, 'Stale or missing STL'
wheel_counts = {k: n for k,n in counts.items() if k.startswith('kolo-')}
assert sum(wheel_counts.values()) == 4 and sum(n for k,n in wheel_counts.items() if 'predni' in k)==2 and sum(n for k,n in wheel_counts.items() if 'zadni' in k)==2
report['physical_instances'] = instances
report['instance_counts'] = dict(counts)
report['wheel_counts'] = wheel_counts
report['physical_parts'] = len(instances)
assert Counter(independent['counts']) == counts
bom = (ROOT/'README.md').read_text().split('<!-- BOM-BEGIN -->')[1].split('<!-- BOM-END -->')[0]
bom_rows = re.findall(r'^\| \[([^]]+)\]\(stl/[^)]+\) \|\s*(\d+)\s*\|', bom, re.M)
assert len(bom_rows) == len(counts) and Counter({k:int(n) for k,n in bom_rows}) == counts, 'README BOM mismatch'
report['readme_bom_pass'] = True
for key, info in source['parts'].items():
    b = (ROOT / info['stl']).read_bytes(); assert sha(b) == info['sha256'], key; n = struct.unpack_from('<I', b, 80)[0]
    assert len(b) == 84 + n * 50
    vertices = {}; coords = []; edges = defaultdict(list); volume = 0; degenerate = 0
    for i in range(n):
        q = struct.unpack_from('<12fH', b, 84 + 50*i)
        vv = [q[3:6], q[6:9], q[9:12]]; ids = []
        for v in vv:
            p = tuple(round(x, 5) for x in v)
            if p not in vertices: vertices[p] = len(vertices); coords.append(p)
            ids.append(vertices[p])
        a, c, d = vv
        volume += (a[0]*(c[1]*d[2]-c[2]*d[1]) + a[1]*(c[2]*d[0]-c[0]*d[2]) + a[2]*(c[0]*d[1]-c[1]*d[0]))/6
        if len(set(ids)) != 3: degenerate += 1
        for j, k in [(0, 1), (1, 2), (2, 0)]:
            edges[tuple(sorted((ids[j], ids[k])))].append((i, 1 if ids[j] < ids[k] else -1))
    parent = list(range(n))
    def root(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    bad = 0; winding = 0
    for ee in edges.values():
        if len(ee) != 2: bad += 1
        else:
            if sum(e[1] for e in ee) != 0: winding += 1
            u, v = [root(e[0]) for e in ee]; parent[u] = v
    components = len({root(i) for i in range(n)})
    bbox = [max(c[j] for c in coords) - min(c[j] for c in coords) for j in range(3)]
    error = abs(volume - info['volume_mm3']) / info['volume_mm3']
    assert bad == winding == degenerate == 0 and components == 1 and volume > 0 and error < 0.005, key
    assert abs(min(c[2] for c in coords)) < 1e-5
    assert max(abs(a-b) for a,b in zip(bbox, info['bbox_mm'])) < 0.04, (key, bbox)
    report['stl'][key] = {'sha256': sha(b), 'triangles': n, 'components': components,
        'bad_edges': bad, 'bad_winding': winding, 'degenerate_triangles': degenerate,
        'volume_error_fraction': error, 'bbox_mm': bbox, 'minimum_z_mm': min(c[2] for c in coords)}
with zipfile.ZipFile(ROOT / 'tiskovy-balicek.zip') as z:
    expected = {key + f'__{i:02d}.stl': report['stl'][key]['sha256'] for key in source['parts'] for i in range(1, counts[key]+1)}
    assert len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP entry'
    assert {n for n in z.namelist() if n.endswith('.stl')} == set(expected)
    assert all(sha(z.read(n)) == h for n, h in expected.items())
    report['zip_stl_count'] = len(expected)
packing = json.loads((ROOT/'rozlozeni/overeni-kusovniku.json').read_text())
meshes = json.loads((ROOT/'rozlozeni/overeni-3mf.json').read_text())
imports = json.loads((ROOT/'rozlozeni/overeni-importu.json').read_text())
assert packing['status'] == meshes['status'] == imports['status'] == 'pass'
assert packing['source_report_sha256'] == report['files']['kontrola-modelu.json']['sha256']
assert packing['source_zip_sha256'] == meshes['source_zip_sha256'] == report['files']['tiskovy-balicek.zip']['sha256']
assert packing['verification_3mf_sha256'] == sha((ROOT/'rozlozeni/overeni-3mf.json').read_bytes())
assert packing['physical_copies'] == meshes['objects'] == imports['objects'] == len(instances)
for column in ['assembly_or_display_count', 'bom_count', 'zip_count', '3mf_count']:
    assert Counter({p['part']:p[column] for p in packing['parts']}) == counts, column
assert len(meshes['plates']) == imports['plate_count'] == 3
for plate in meshes['plates']:
    path = ROOT/'rozlozeni'/plate['file']; h = sha(path.read_bytes())
    assert h == plate['sha256']
    imported = next(i for i in imports['plates'] if i['file'] == plate['file'])
    assert imported['status'] == 'pass' and imported['source_sha256'] == h and imported['objects'] == plate['count']
    report['files']['rozlozeni/'+plate['file']] = {'sha256':h, 'bytes':path.stat().st_size}
report['packing_pass'] = True
report['plate_counts'] = [p['count'] for p in meshes['plates']]
preserved = json.loads((ROOT/'overeni-zachovani.json').read_text())
for group in ['originals', 'frozen_calibration']:
    assert all(sha((ROOT.parent.parent/item['path']).read_bytes()) == item['sha256'] for item in preserved[group]['files']), group
report['originals_and_frozen_calibration_unchanged'] = True
missing = []
for label, target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', (ROOT / 'README.md').read_text()):
    path = target.split('#')[0]
    if path and path != 'overeni-exportu.json' and not re.match(r'[a-z]+:', path) and not (ROOT / path).exists(): missing.append(path)
assert not missing, missing
report['markdown_links_pass'] = True; report['all_passed'] = True
(ROOT / 'overeni-exportu.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS:',len(source['parts']),'STL types,',len(instances),'physical instances / ZIP copies, four wheels, manifold/orientation/dimensions/Z0/links/source hash')
