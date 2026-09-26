"""Read the completed revision-03 CAD audit; no output files or CAD imports."""
import json
from pathlib import Path

MODEL_ROOT = Path(__file__).resolve().parent.parent
MODEL_AUDIT = MODEL_ROOT / 'kontrola-modelu.json'


def load_parts(sample=False):
    data = json.loads(MODEL_AUDIT.read_text())
    if data.get('validation_pass') is not True:
        raise ValueError('CAD audit is not complete: validation_pass must be true')
    user_length = data.get('user_parameters_mm', {}).get('length')
    if user_length is not None and abs(float(user_length)-575.0)>0.001:
        raise ValueError(f'Wrong model revision: requested575mm, audit reports{user_length}')
    nominal = data.get('nominal_after_restore', data.get('nominal', {}))
    source = data.get('test_sample_stl' if sample else 'stl')
    if not source or len(source) != (2 if sample else 3):
        raise ValueError('Expected exactly two test or three full-part STL entries')
    dimensions = data.get('sample_bounds_mm') if sample else nominal.get('part_bounds_mm')
    nominal_height = data.get('body_height_mm', nominal.get('tpu_body_height_mm'))
    records = []
    for i, entry in enumerate(source):
        relative = Path(entry['file'])
        resolved = (MODEL_ROOT/relative).resolve()
        if relative.is_absolute() or not resolved.is_relative_to(MODEL_ROOT.resolve()):
            raise ValueError('STL reference must remain within the current model revision')
        if entry.get('closed') is not True:
            raise ValueError(f'CAD did not confirm closed STL: {relative}')
        expected = entry.get('nominal_bounds_mm') or (dimensions[i] if dimensions else None)
        if expected is None:
            expected = list(entry['bounds_mm'])
            if nominal_height is not None:
                expected[2] = float(nominal_height)
        if len(expected)!=3 or any(float(value)<=0 for value in expected):
            raise ValueError(f'Invalid dimensions for {relative}')
        records.append({'file':relative.as_posix(), 'dimensions':tuple(map(float,expected)),
                        'cad_export_bounds_mm':entry['bounds_mm'],
                        'sha256':entry.get('sha256'),
                        'retention_regions':entry.get('retention_audit_regions',[])})
    if len({entry['file'] for entry in records}) != len(records):
        raise ValueError('Duplicate STL references')
    # Preserve each original XYZ orientation. Put parts on the centre of the
    #260mm plate with20mm between bounding boxes; no automatic rotations.
    gap=20.0
    if sample:
        position=(260.0-sum(record['dimensions'][0] for record in records)-gap*(len(records)-1))/2
        for record in records:
            dx,dy,dz=record['dimensions']
            record['translation']=(position,(260.0-dy)/2,0.0)
            position+=dx+gap
    else:
        position=(260.0-sum(record['dimensions'][1] for record in records)-gap*(len(records)-1))/2
        for record in records:
            dx,dy,dz=record['dimensions']
            record['translation']=((260.0-dx)/2,position,0.0)
            position+=dy+gap
    return data,records
