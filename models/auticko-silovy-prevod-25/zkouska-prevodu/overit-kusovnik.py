#!/usr/bin/env python3
"""Compare actual assembly instances -> BOM -> ZIP copies -> final 3MF objects."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source_report', type=Path)
    ap.add_argument('zip', type=Path)
    ap.add_argument('verification_3mf', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--calibration', action='store_true')
    args = ap.parse_args()
    source = json.loads(args.source_report.read_text())
    parts = source['parts']
    aliases = {p['object']: name for name, p in parts.items()}
    aliases.update({name: name for name in parts})
    bom = Counter({name: p['copies'] for name, p in parts.items()})
    assert all(isinstance(n, int) and n > 0 for n in bom.values())
    if args.calibration:
        # Coupons are an unassembled collection. Count actual display objects,
        # explicitly without representing them as installed assembly instances.
        instances = source['display_objects']
        assert len(instances) == len(set(instances))
        actual = Counter(aliases[n.removeprefix('View')] for n in instances)
        method = 'Calibration: actual CAD display objects -> BOM -> ZIP -> 3MF; no assembly instance claim'
    else:
        instances = source['assembly_instances']
        assert source['counts_derived_from_assembly'] is True
        assert source['validation_pass'] is True
        assert len(instances) == len({i['name'] for i in instances})
        assert len(instances) == source['total_print_count']
        assert sorted([i['name'] for i in instances] + source['references']) == sorted(source['assembly_object_names'])
        actual = Counter(aliases[i['part']] for i in instances)
        for item in instances:
            canonical = aliases[item['part']]
            assert Path(item['stl']).stem == canonical, (item, canonical)
        method = 'Actual recorded CAD assembly instances -> BOM -> byte-exact ZIP copies -> final 3MF objects'
    assert actual == bom, ('Assembly versus BOM', actual, bom)

    final = json.loads(args.verification_3mf.read_text())
    assert final['status'] == 'pass' and final['source_zip_sha256'] == sha(args.zip)
    locations = {}
    for plate in final['plates']:
        for position, obj in enumerate(plate['objects'], 1):
            assert obj['name'] not in locations
            locations[obj['name']] = {'file': plate['file'], 'number_in_preview': position}
    records, zip_counts, zip_names = [], Counter(), []
    with zipfile.ZipFile(args.zip) as archive:
        entries = [n for n in archive.namelist() if n.lower().endswith('.stl')]
        assert len(entries) == len(set(entries))
        for name in entries:
            stem = Path(name).stem
            canonical = re.sub(r'__\d+$', '', stem)
            assert canonical in parts, ('Unknown ZIP type', name)
            original = args.source_report.parent / parts[canonical]['stl']
            assert archive.read(name) == original.read_bytes(), ('Changed STL copy', name)
            assert stem in locations, ('Missing final object', stem)
            zip_names.append(stem)
            zip_counts[canonical] += 1
        assert sorted(zip_names) == sorted(locations), ('ZIP versus 3MF names', zip_names, locations)
        assert zip_counts == bom, ('ZIP versus BOM counts', zip_counts, bom)
        for name in sorted(parts):
            copies = sorted(n for n in zip_names if re.sub(r'__\d+$', '', n) == name)
            records.append({'part': name, 'assembly_or_display_count': actual[name], 'bom_count': bom[name], 'zip_count': zip_counts[name], '3mf_count': len(copies), 'copies': [{'name': n, **locations[n]} for n in copies]})
    report = {'status': 'pass', 'method': method, 'source_report': str(args.source_report.resolve()), 'source_report_sha256': sha(args.source_report), 'source_zip_sha256': sha(args.zip), 'verification_3mf_sha256': sha(args.verification_3mf), 'physical_copies': sum(bom.values()), 'part_types': len(parts), 'all_counts_equal': True, 'all_zip_copies_identical_to_canonical_stl': True, 'parts': records}
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'parts'}, indent=2))


if __name__ == '__main__':
    main()
