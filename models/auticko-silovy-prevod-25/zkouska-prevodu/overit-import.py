#!/usr/bin/env python3
"""Roundtrip each final 3MF through isolated Next CLI; no slicing or printer IO."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from xml.etree import ElementTree as E
from zipfile import ZipFile

import numpy as np

NS = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
P = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'


def transform(text):
    matrix = np.eye(4)
    if text:
        matrix[:3, :] = np.array(list(map(float, text.split()))).reshape(4, 3).T
    return matrix


def meshes(path):
    with ZipFile(path) as archive:
        roots = {n: E.fromstring(archive.read(n)) for n in archive.namelist() if n.endswith('.model')}
        assert all(root.get('unit', 'millimeter') == 'millimeter' for root in roots.values())
        objects = {(n, o.get('id')): o for n, root in roots.items() for o in root.findall('m:resources/m:object', NS)}
        names = {}
        if 'Metadata/model_settings.config' in archive.namelist():
            for obj in E.fromstring(archive.read('Metadata/model_settings.config')).findall('object'):
                name = obj.find('metadata[@key="name"]')
                if name is not None:
                    names[obj.get('id')] = name.get('value')

        def geometry(key, matrix):
            obj = objects[key]
            mesh = obj.find('m:mesh', NS)
            if mesh is not None:
                vs = np.array([[float(v.get(k)) for k in ('x', 'y', 'z')] + [1] for v in mesh.findall('m:vertices/m:vertex', NS)])
                faces = np.array([[int(f.get(k)) for k in ('v1', 'v2', 'v3')] for f in mesh.findall('m:triangles/m:triangle', NS)])
                return (vs @ matrix.T)[:, :3], faces
            vertices, triangles, count = [], [], 0
            for component in obj.findall('m:components/m:component', NS):
                file = component.get(P + 'path', key[0]).lstrip('/')
                vs, fs = geometry((file, component.get('objectid')), matrix @ transform(component.get('transform')))
                vertices.append(vs)
                triangles.append(fs + count)
                count += len(vs)
            return np.concatenate(vertices), np.concatenate(triangles)

        result = {}
        for item in roots['3D/3dmodel.model'].findall('m:build/m:item', NS):
            key = ('3D/3dmodel.model', item.get('objectid'))
            name = objects[key].get('name', names.get(key[1], key[1]))
            assert name not in result, ('Duplicate build object', name)
            result[name] = geometry(key, transform(item.get('transform')))
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=Path)
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--prefix', default='zkouska-prevodu')
    args = ap.parse_args()
    assert not args.cache.resolve().is_relative_to(args.directory.resolve().parent), 'Runtime must stay outside project'
    args.cache.mkdir(parents=True, exist_ok=True)
    results = []
    for source in sorted(args.directory.glob(f'{args.prefix}-podlozka-*.3mf')):
        run = args.cache / source.stem
        run.mkdir(parents=True, exist_ok=True)
        output = run / 'roundtrip.3mf'
        cmd = ['/usr/bin/AnycubicSlicerNext', '--datadir', str(args.cache / 'isolated-profile'), '--arrange', '0', '--orient', '0', '--debug', '3', '--export-3mf', 'roundtrip.3mf', '--outputdir', str(run), str(source.resolve())]
        with (run / 'cli.log').open('w') as log:
            proc = subprocess.run(cmd, env=dict(os.environ, DISPLAY=''), stdout=log, stderr=subprocess.STDOUT, timeout=120)
        assert proc.returncode == 0 and output.exists(), (source, proc.returncode)
        before, after = meshes(source), meshes(output)
        assert before.keys() == after.keys(), (source, list(before), list(after))
        records = []
        for name, (vertices, faces) in before.items():
            new_vertices, new_faces = after[name]
            assert vertices.shape == new_vertices.shape
            assert np.array_equal(faces, new_faces), ('Changed triangle indices', name)
            delta = float(np.max(np.abs(vertices - new_vertices)))
            assert delta <= .00002, (name, delta)
            assert abs(vertices[:, 2].min()) < 1e-5 and abs(new_vertices[:, 2].min()) < 1e-5
            records.append({'name': name, 'vertices': len(vertices), 'triangles': len(faces), 'max_world_vertex_delta_mm': delta, 'ordered_triangle_indices_preserved': True})
        results.append({'file': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'status': 'pass', 'command': cmd, 'objects': len(records), 'triangles': sum(r['triangles'] for r in records), 'max_world_vertex_delta_mm': max(r['max_world_vertex_delta_mm'] for r in records), 'object_records': records})
        print(source.name, 'PASS', len(records), 'objects', flush=True)
    assert results
    report = {'status': 'pass', 'method': 'Installed Anycubic Slicer Next CLI import/export, isolated cache, arrange=0 orient=0. No slicing, G-code or printer communication. Roundtrip outputs are not delivery files.', 'plate_count': len(results), 'objects': sum(r['objects'] for r in results), 'plates': results}
    (args.directory / 'overeni-importu.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
