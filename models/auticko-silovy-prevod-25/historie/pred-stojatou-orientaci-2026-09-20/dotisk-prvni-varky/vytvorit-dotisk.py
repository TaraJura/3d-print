#!/usr/bin/env python3
"""Seven replacement copies, rigid orientation changes only; no printer access.

Run with the project packing Python (numpy, trimesh, shapely, matplotlib).
Overwrites only this repair directory's generated 3MF/PNG/JSON files.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as E
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import trimesh
from shapely.geometry import MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).resolve().parent
LAYOUT = HERE.parent
MODEL = LAYOUT.parent
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('', NS)
def tag(s): return '{'+NS+'}'+s
def sha(data): return hashlib.sha256(data).hexdigest()
def load_helper(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

helper = load_helper('core3mf', LAYOUT/'vytvorit-3mf.py')
# Order: original plate-1 number, repair plate, orientation, XY bbox centre.
RY_MINUS_90 = np.array([[0,0,-1],[0,1,0],[1,0,0]], dtype=float)
RX_180 = np.diag([1,-1,-1]).astype(float)
PLAN = [(8,1,RX_180,(130,130)), (11,2,RY_MINUS_90,(130,130)),
        (12,3,RY_MINUS_90,(85,110)), (13,3,RY_MINUS_90,(130,110)),
        (14,3,RY_MINUS_90,(175,110)), (17,3,RY_MINUS_90,(105,155)),
        (19,3,RY_MINUS_90,(155,155))]
TITLES = {1:'Zadní osa · naležato s podporami', 2:'Pravá těhlice · otočená s podporami',
          3:'Pět čepů · hlavami na podložku'}

def write3mf(path, parts):
    model = E.Element(tag('model'), {'unit':'millimeter'})
    E.SubElement(model,tag('metadata'),{'name':'Title'}).text = TITLES[parts[0]['plate']]
    E.SubElement(model,tag('metadata'),{'name':'Description'}).text = 'Dotisk V3 25:1. Pouze geometrie, meritko 1:1; bez podpor, brimu, presetu a G-code.'
    res = E.SubElement(model,tag('resources')); build=E.SubElement(model,tag('build'))
    for oid,p in enumerate(parts,1):
        o=E.SubElement(res,tag('object'),{'id':str(oid),'type':'model','name':Path(p['name']).stem})
        mesh=E.SubElement(o,tag('mesh')); vs=E.SubElement(mesh,tag('vertices'));fs=E.SubElement(mesh,tag('triangles'))
        for v in p['_vertices']:
            E.SubElement(vs,tag('vertex'),{k:f'{x:.9f}' for k,x in zip(('x','y','z'),v)})
        for f in p['_faces']:
            E.SubElement(fs,tag('triangle'),{f'v{k+1}':str(x) for k,x in enumerate(f)})
        E.SubElement(build,tag('item'),{'objectid':str(oid)})
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))

def preview(parts, plate):
    fig=plt.figure(figsize=(14,9),facecolor='white')
    ax=fig.add_axes([.06,.18,.5,.73]);ax.set_aspect('equal')
    ax.set(xlim=(0,260),ylim=(0,260),xlabel='X [mm]',ylabel='Y [mm]')
    ax.set_xticks(range(0,261,20));ax.set_yticks(range(0,261,20));ax.grid(alpha=.18)
    colors=plt.get_cmap('tab10')
    for j,p in enumerate(parts,1):
        v,f=p['_vertices'],p['_faces'];h=p['_hull']
        pad=np.array(h.buffer(8.1).exterior.coords)
        ax.fill(*pad.T,color=colors(j-1),alpha=.12)
        ax.plot(*pad.T,color=colors(j-1),ls=':',lw=1)
        ax.add_collection(PolyCollection(v[f][:,:,:2],facecolors=[colors(j-1)],edgecolors='none',zorder=3))
        c=h.centroid; ax.annotate(str(j),(c.x,c.y),xytext=(c.x,c.y-17),ha='center',fontweight='bold',arrowprops={'arrowstyle':'-'},bbox={'facecolor':'white','edgecolor':'none'})
        fig.text(.6,.87-(j-1)*.056,f"{j}. {p['name'].removesuffix('.stl')}\n    původní podložka 1 / č. {p['original_number']}",fontsize=10)
    side=fig.add_axes([.59,.19,.36,.36],projection='3d')
    allv=np.concatenate([p['_vertices'] for p in parts]);low=allv.min(0);high=allv.max(0)
    for j,p in enumerate(parts):
        coll=Poly3DCollection(p['_vertices'][p['_faces']],facecolors=[colors(j)],edgecolors=None,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=315,altdeg=45))
        side.add_collection3d(coll)
    size=np.maximum(high-low,5);center=(high+low)/2
    for dim,fun in enumerate((side.set_xlim,side.set_ylim,side.set_zlim)):
        fun(center[dim]-size[dim]*.56,center[dim]+size[dim]*.56)
    side.set_box_aspect(size);side.view_init(elev=24,azim=-65);side.set_axis_off()
    fig.text(.06,.955,f'Dotisk V3 25:1 · {TITLES[plate]}',fontsize=19,fontweight='bold')
    fig.text(.06,.09,f'Kobra X 260 × 260 mm · 100 % · {len(parts)} samostatných dílů · pořadí tisku po vrstvách',fontsize=12)
    fig.text(.06,.05,'Tečkovaná obálka = 8,1 mm rezerva. Zobrazená je skutečná geometrie; podpory a brim zde nejsou vložené.',fontsize=10)
    fig.savefig(HERE/f'podlozka-{plate:02d}.png',dpi=150);plt.close(fig)

def main():
    orig=json.loads((LAYOUT/'rozlozeni.json').read_text())
    first=[p for p in orig['items'] if p['plate']==1]
    assert len(first)==26
    items=[]; proofs=[]
    with ZipFile(MODEL/'tiskovy-balicek.zip') as z:
        for number,plate,R,centre in PLAN:
            old=first[number-1];data=z.read(old['name'])
            assert sha(data)==old['source_sha256']
            canonical=MODEL/'stl'/(old['name'].split('__')[0]+'.stl')
            assert canonical.read_bytes()==data
            v,f=helper.stl(data);v=np.array(v);f=np.array(f)
            transformed=v@R.T
            t=np.r_[np.array(centre)-(transformed[:,:2].min(0)+transformed[:,:2].max(0))/2,-transformed[:,2].min()]
            w=transformed+t
            src=trimesh.Trimesh(v,f,process=False);mesh=trimesh.Trimesh(w,f,process=False)
            assert src.is_watertight and mesh.is_watertight and np.linalg.det(R)==1
            assert abs(src.volume-mesh.volume)<1e-6
            low,high=w.min(0),w.max(0);h=MultiPoint(w[:,:2]).convex_hull
            assert min(low[0],low[1],260-high[0],260-high[1])>16.1
            normals=mesh.face_normals;centers=mesh.triangles_center
            contact=float(mesh.area_faces[(normals[:,2]<-.999999)&(centers[:,2]<1e-7)].sum())
            mask=(normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.201)
            unsupported=float((mesh.area_faces[mask]*(-normals[mask,2])).sum())
            item={'name':old['name'],'original_plate':1,'original_number':number,'plate':plate,
                  'source_sha256':sha(data),'rotation_matrix':R.tolist(),'translation_mm':t.tolist(),'scale':1.0,
                  'bounds_mm':[low.tolist(),high.tolist()],'height_mm':float(high[2]),
                  'volume_mm3':float(mesh.volume),'triangles':len(f),'watertight':bool(mesh.is_watertight),
                  'planar_contact_area_mm2':contact,'downward_overhang_xy_projection_mm2':unsupported,
                  '_vertices':w,'_faces':f,'_source_vertices':v,'_hull':h}
            items.append(item)
    for plate in (1,2,3):
        parts=[p for p in items if p['plate']==plate]
        clearance=min((a['_hull'].distance(b['_hull']) for i,a in enumerate(parts) for b in parts[i+1:]),default=None)
        if clearance is not None:assert clearance>32.2
        path=HERE/f'dotisk-25-podlozka-{plate:02d}.3mf';write3mf(path,parts)
        # Independently reopen the delivered XML, invert each rigid transform.
        with ZipFile(path) as z:
            assert sorted(z.namelist())==['3D/3dmodel.model','[Content_Types].xml','_rels/.rels']
            root=E.fromstring(z.read('3D/3dmodel.model'));assert root.get('unit')=='millimeter'
            objects=root.find(tag('resources')).findall(tag('object'));assert len(objects)==len(parts)
            maxdelta=0
            for o,p in zip(objects,parts):
                readv=np.array([[float(v.get(k)) for k in ('x','y','z')] for v in o.find(tag('mesh')).find(tag('vertices'))])
                readf=np.array([[int(f.get(k)) for k in ('v1','v2','v3')] for f in o.find(tag('mesh')).find(tag('triangles'))])
                assert o.get('name')==Path(p['name']).stem and np.array_equal(readf,p['_faces'])
                inverse=(readv-np.array(p['translation_mm']))@np.array(p['rotation_matrix'])
                delta=float(np.abs(inverse-p['_source_vertices']).max());assert delta<1e-8
                maxdelta=max(delta,maxdelta)
        proofs.append({'plate':plate,'file':path.name,'sha256':sha(path.read_bytes()),'objects':len(parts),
                       'minimum_part_clearance_mm':clearance,'minimum_edge_clearance_mm':min(min(p['bounds_mm'][0][0],p['bounds_mm'][0][1],260-p['bounds_mm'][1][0],260-p['bounds_mm'][1][1]) for p in parts),
                       'maximum_inverse_vertex_error_mm':maxdelta,'triangles_preserved':True,'only_rigid_transforms':True})
        preview(parts,plate)
    report={'status':'pass','units':'mm','counts':[1,1,5],'total_repair_copies':7,'source_zip_sha256':sha((MODEL/'tiskovy-balicek.zip').read_bytes()),
            'orientation_only':True,'original_cad_stl_plates_unchanged':True,'print_order':'by layer',
            'geometry_only':True,'embedded_supports':False,'embedded_brim':False,
            'clearance_reserve_mm':8.1,'overhang_metric':'Sum of XY-projected downward triangles steeper than 45 degrees above Z0.201; not generated supports.',
            'items':[{k:v for k,v in p.items() if not k.startswith('_')} for p in items], 'plates':proofs}
    (HERE/'overeni-dotisku.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(proofs,indent=2))

if __name__=='__main__': main()
