#!/usr/bin/env python3
"""Nezavisle overeni kalibracnich STL, ZIP a lokalnich odkazu. Bez externich knihoven."""
from pathlib import Path
from collections import defaultdict
import hashlib, json, struct, zipfile, re
ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / 'kontrola-kalibrace.json').read_text())
assert source['validation_pass'] and source['gui_validation']['saved_and_reopened']
sha = lambda b: hashlib.sha256(b).hexdigest()
assert source['generator_sha256'] == sha((ROOT / 'kalibrace-4-v2.FCMacro').read_bytes())
report = {'generator_sha256': source['generator_sha256'], 'files': {}, 'stl': {}}
for name in ['kalibrace-4-v2.FCStd', 'kalibrace-4-v2.zip', 'nahled.FCMacro', 'nahled.png', 'README.md', 'kontrola-kalibrace.json']:
    b = (ROOT / name).read_bytes(); report['files'][name] = {'sha256': sha(b), 'bytes': len(b)}
for key, info in source['parts'].items():
    b = (ROOT / info['stl']).read_bytes(); n = struct.unpack_from('<I', b, 80)[0]
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
with zipfile.ZipFile(ROOT / 'kalibrace-4-v2.zip') as z:
    expected = {key + '__01.stl': report['stl'][key]['sha256'] for key in source['parts']}
    assert {n for n in z.namelist() if n.endswith('.stl')} == set(expected)
    assert all(sha(z.read(n)) == h for n, h in expected.items())
    report['zip_stl_count'] = len(expected)
missing = []
for label, target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', (ROOT / 'README.md').read_text()):
    path = target.split('#')[0]
    if path and path != 'overeni-exportu.json' and not re.match(r'[a-z]+:', path) and not (ROOT / path).exists(): missing.append(path)
assert not missing, missing
report['markdown_links_pass'] = True; report['all_passed'] = True
(ROOT / 'overeni-exportu.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS: 2 STL, 2 ZIP copies, manifold/orientation/dimensions/Z0/links/source hash')
