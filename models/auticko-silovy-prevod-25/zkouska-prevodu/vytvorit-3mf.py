#!/usr/bin/env python3
"""Create generic Core 3MF plates; never writes machine/material/process presets."""
import argparse, hashlib, json, math, struct, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def stl(data):
    count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+count*50,'Expected binary STL'
    points=[]; faces=[]; ids={}
    for i in range(count):
        q=struct.unpack_from('<12fH',data,84+50*i)
        face=[]
        for j in (3,6,9):
            p=q[j:j+3]
            if p not in ids:ids[p]=len(points);points.append(p)
            face.append(ids[p])
        faces.append(face)
    return points,faces
def write_plate(out,items,source):
    model=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'cs-CZ'})
    ET.SubElement(model,tag('metadata'),{'name':'Title'}).text=out.stem
    ET.SubElement(model,tag('metadata'),{'name':'Description'}).text='Rucni zkouska 18->60, 7 dilu, Kobra X 260x260: pouze geometrie a rozlozeni, bez tiskovych nastaveni.'
    resources=ET.SubElement(model,tag('resources'));build=ET.SubElement(model,tag('build'))
    for i,p in enumerate(items,1):
        name=p['name'];data=source.read(name);vertices,faces=stl(data)
        obj=ET.SubElement(resources,tag('object'),{'id':str(i),'type':'model','name':Path(name).stem})
        mesh=ET.SubElement(obj,tag('mesh'));vs=ET.SubElement(mesh,tag('vertices'));fs=ET.SubElement(mesh,tag('triangles'))
        a=math.radians(p['angle_deg']);c=math.cos(a);s=math.sin(a)
        for x,y,z in vertices:
            ET.SubElement(vs,tag('vertex'),dict(zip(['x','y','z'],[f'{x*c-y*s+p["dx_mm"]:.9f}',f'{x*s+y*c+p["dy_mm"]:.9f}',f'{z:.9f}'])))
        for f in faces:ET.SubElement(fs,tag('triangle'),{f'v{j+1}':str(v) for j,v in enumerate(f)})
        ET.SubElement(build,tag('item'),{'objectid':str(i)})
    contents=b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rel=b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('[Content_Types].xml',contents);z.writestr('_rels/.rels',rel)
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
    return {'file':out.name,'objects':len(items),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('zip',type=Path);ap.add_argument('layout',type=Path);ap.add_argument('output',type=Path)
    ap.add_argument('--prefix',default='zkouska-prevodu');args=ap.parse_args();d=json.loads(args.layout.read_text());items=d['items']
    args.output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.zip) as z:
        assert sorted(p['name'] for p in items)==sorted(n for n in z.namelist() if n.lower().endswith('.stl'))
        files=[write_plate(args.output/f'{args.prefix}-podlozka-{b:02d}.3mf',[p for p in items if p['plate']==b],z) for b in sorted({p['plate'] for p in items})]
    print(json.dumps(files,indent=2))
if __name__=='__main__':main()
