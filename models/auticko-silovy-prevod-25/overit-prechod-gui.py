#!/usr/bin/env python3
"""Čtecí vazba geometrického snapshotu na GUI uložený dokument; nespouští CAD."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,re,sys
ROOT=Path(__file__).resolve().parent
A=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/home/novakj/.cache/auticko-fit-20260920/nominal-prototype-input.FCStd')
B=ROOT/'auticko-silovy-prevod-25.FCStd'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];maximum=0;flags={};placements=0;place_max=0;sheet_cells=0;expression_properties=0
with zipfile.ZipFile(A) as a,zipfile.ZipFile(B) as b:
 names=[n for n in a.namelist() if n.endswith('.brp')];assert set(names)=={n for n in b.namelist() if n.endswith('.brp')}
 for n in names:
  left=a.read(n);right=b.read(n);x=left.decode().splitlines();y=right.decode().splitlines();assert len(x)==len(y),(n,'line count');local=0
  for xx,yy in zip(x,y):
   if xx==yy:continue
   if re.fullmatch('[01]{7}',xx) and re.fullmatch('[01]{7}',yy):
    # OpenCascade TShape flags: Free/Checked can change during opening, meshing and validation.
    assert xx[1]+xx[3:]==yy[1]+yy[3:],(n,'geometric/topological flag',xx,yy)
    key=xx+' -> '+yy;flags[key]=flags.get(key,0)+1;continue
   tx=xx.split();ty=yy.split();assert len(tx)==len(ty),(n,'token count')
   for u,v in zip(tx,ty):
    if u==v:continue
    delta=abs(float(u)-float(v));local=max(local,delta);assert delta<=1e-6,(n,u,v,delta)
  maximum=max(maximum,local);checks.append({'member':n,'input_sha256':hashlib.sha256(left).hexdigest(),'final_sha256':hashlib.sha256(right).hexdigest(),'maximum_numeric_token_difference':local})
 def objects(z):return {o.get('name'):o for o in ET.fromstring(z.read('Document.xml')).findall('./ObjectData/Object')}
 x=objects(a);y=objects(b);assert set(x)==set(y)
 for name in x:
  for prop in ('Placement','LinkPlacement'):
   l=x[name].find("./Properties/Property[@name='"+prop+"']/PropertyPlacement");r=y[name].find("./Properties/Property[@name='"+prop+"']/PropertyPlacement")
   assert (l is None)==(r is None),(name,prop)
   if l is None:continue
   assert set(l.attrib)==set(r.attrib);d=max(abs(float(v)-float(r.get(k))) for k,v in l.attrib.items());assert d<=1e-10,(name,prop,d);place_max=max(place_max,d);placements+=1
 def canonical(element):
  if element is None:return None
  return (element.tag,tuple(sorted(element.attrib.items())),tuple(canonical(c) for c in element))
 for name in x:
  l=x[name].find("./Properties/Property[@name='ExpressionEngine']/ExpressionEngine");r=y[name].find("./Properties/Property[@name='ExpressionEngine']/ExpressionEngine")
  assert canonical(l)==canonical(r),(name,'ExpressionEngine')
  if l is not None:expression_properties+=1
 for name in ('Parameters','Steering'):
  def cells(o):return {c.get('address'):(c.get('content'),c.get('alias')) for c in o.findall("./Properties/Property[@name='cells']/Cells/Cell")}
  l=cells(x[name]);r=cells(y[name]);assert l==r,(name,'spreadsheet values/aliases');sheet_cells+=len(l)
report={'passed':True,'input_fcstd_sha256':sha(A),'final_fcstd_sha256':sha(B),'brep_members':len(checks),'checks':checks,'numeric_serialization_tolerance':1e-6,'maximum_numeric_token_difference':maximum,'ignored_non_geometric_tshape_flag_changes':flags,'placement_properties_checked':placements,'maximum_placement_numeric_difference':place_max,'spreadsheet_cells_content_and_alias_unchanged':sheet_cells,'expression_engine_properties_unchanged':expression_properties,'limit':'BREP topology token sequence unchanged. Floating-point serialization within1e-6 for each numeric token; only Free/Checked bookkeeping flags ignored. Parameters, expressions and all placements unchanged. This binds previous geometry checks to GUI save without claiming byte-identical BREP.'}
(ROOT/'kontrola-prechodu-gui.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
