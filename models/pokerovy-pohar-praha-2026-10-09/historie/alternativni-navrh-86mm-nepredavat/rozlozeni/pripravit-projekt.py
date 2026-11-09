#!/usr/bin/env python3
"""Jedna tisková podložka pokerového poháru: 3MF, řez a skutečné dráhy.

Čte ../stl/pohar.stl. Přepíše pouze výstupy této složky a místní .cache/.
Používá místní Anycubic Slicer Next CLI; nekontaktuje ani neovládá tiskárnu.
"""
from collections import Counter
import hashlib, json, math, os, re, struct, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
STL=HERE.parent/'stl/pohar.stl'
CACHE=HERE/'.cache'
PROFILE=Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
MACHINE=PROFILE/'machine/Anycubic Kobra X 0.4 nozzle.json'
PROCESS=PROFILE/'process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json'
FILAMENT=PROFILE/'filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json'
CLI='/usr/bin/AnycubicSlicerNext'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PNS='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
XMLNS={'m':NS}
IDENTITY=[1,0,0,0,1,0,0,0,1]
ET.register_namespace('',NS)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GEOMETRY=HERE/'podlozka-01-geometrie.3mf'
PROJECT=HERE/'podlozka-01-kobra-x-zlaty-silk-projekt.3mf'


def require(ok,msg):
    if not ok: raise RuntimeError(msg)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def save_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def read_mesh():
    raw=STL.read_bytes()
    count=struct.unpack_from('<I',raw,80)[0] if len(raw)>=84 else 0
    if len(raw)==84+50*count:
        points=[]
        for i in range(count):
            vals=struct.unpack_from('<12fH',raw,84+50*i)
            points.extend(tuple(vals[j:j+3]) for j in (3,6,9))
    else:points=[tuple(map(float,p)) for p in re.findall(rb'\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',raw)]
    require(len(points)>=12 and len(points)%3==0,'Neplatné STL')
    vertices,lookup,faces=[],{},[]
    for i in range(0,len(points),3):
        face=[]
        for p in points[i:i+3]:
            key=tuple(round(v,6) for v in p)
            if key not in lookup:lookup[key]=len(vertices);vertices.append(p)
            face.append(lookup[key])
        require(len(set(face))==3,'Degenerovaný trojúhelník')
        faces.append(face)
    edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
    require(all(n==2 for n in edges.values()),'STL není uzavřené/manifold')
    lo=[min(p[i] for p in vertices) for i in range(3)]
    hi=[max(p[i] for p in vertices) for i in range(3)]
    size=[hi[i]-lo[i] for i in range(3)]
    require(all(0<v<240 for v in size),'Neplatné rozměry STL')
    return {'vertices':vertices,'faces':faces,'lo':lo,'hi':hi,'size_mm':size}


def make_geometry(mesh):
    model=ET.Element(f'{{{NS}}}model',unit='millimeter')
    ET.SubElement(model,'metadata',name='Title').text='Pokerový pohár Praha 9. 10. 2026 – pouze geometrie'
    ET.SubElement(model,'metadata',name='Description').text='1 kus 1:1; alternativa bez procesu, filamentu a G-code.'
    resources=ET.SubElement(model,'resources')
    obj=ET.SubElement(resources,'object',id='1',type='model',name='01 Pokerovy pohar – 1 kus')
    node=ET.SubElement(obj,'mesh');verts=ET.SubElement(node,'vertices');tris=ET.SubElement(node,'triangles')
    for p in mesh['vertices']:ET.SubElement(verts,'vertex',**{a:format(v,'.12g') for a,v in zip('xyz',p)})
    for f in mesh['faces']:ET.SubElement(tris,'triangle',**{f'v{i+1}':str(v) for i,v in enumerate(f)})
    t=[130-(mesh['lo'][0]+mesh['hi'][0])/2,130-(mesh['lo'][1]+mesh['hi'][1])/2,-mesh['lo'][2]]
    build=ET.SubElement(model,'build');ET.SubElement(build,'item',objectid='1',transform=' '.join(map(str,IDENTITY+t)))
    types=ET.Element('Types',xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
    ET.SubElement(types,'Default',Extension='rels',ContentType='application/vnd.openxmlformats-package.relationships+xml')
    ET.SubElement(types,'Default',Extension='model',ContentType='application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
    rels=ET.Element('Relationships',xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
    ET.SubElement(rels,'Relationship',Target='/3D/3dmodel.model',Id='rel0',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    with ZipFile(GEOMETRY,'w',ZIP_DEFLATED) as z:
        for name,value in [('[Content_Types].xml',types),('_rels/.rels',rels),('3D/3dmodel.model',model)]:z.writestr(name,ET.tostring(value,encoding='utf-8',xml_declaration=True))
    return t


def create_profiles():
    process=json.loads(PROCESS.read_text())
    process.update({'name':'Pokerovy pohar 0.20mm Gold Silk Kobra X',
        'print_settings_id':'Pokerovy pohar 0.20mm Gold Silk Kobra X',
        'layer_height':'0.2','wall_loops':'2','sparse_infill_density':'8%',
        'sparse_infill_pattern':'gyroid','top_shell_layers':'4','bottom_shell_layers':'4',
        'brim_type':'outer_only','brim_width':'3','brim_object_gap':'0.1',
        'enable_support':'0','enable_prime_tower':'0','print_sequence':'by layer',
        'initial_layer_speed':'25','initial_layer_infill_speed':'40',
        'outer_wall_speed':'45','inner_wall_speed':'80','top_surface_speed':'45',
        'sparse_infill_speed':'80','internal_solid_infill_speed':'70','gap_infill_speed':'45',
        'small_perimeter_speed':'50%','bridge_speed':'25','wall_generator':'arachne',
        'default_acceleration':'2000','outer_wall_acceleration':'1000',
        'inner_wall_acceleration':'1500','top_surface_acceleration':'1000',
        'timelapse_type':'0'})
    filament=json.loads(FILAMENT.read_text());name='NAVRH Alzament PLA Silk Gold ALZMNTS07 @Kobra X 0.4'
    filament.update({'name':name,'setting_id':name,'filament_settings_id':[name],
        'filament_vendor':['Alzament'],'filament_colour':['#D4AF37'],
        'default_filament_colour':['#D4AF37'],
        'filament_notes':['Alzament PLA Silk Gold ALZMNTS07 1.75mm; navrhovy, fyzicky nekalibrovany profil. Skutecna civka a vstup neovereny. Alza 210-230C, bed45-60C; overeno 9.10.2026.'],
        'filament_max_volumetric_speed':['6']})
    for key,value in {'nozzle_temperature':'220','nozzle_temperature_initial_layer':'225',
        'nozzle_temperature_BRASS':'220','nozzle_temperature_HS':'220',
        'nozzle_temperature_initial_layer_BRASS':'225','nozzle_temperature_initial_layer_HS':'225',
        'hot_plate_temp':'50','hot_plate_temp_initial_layer':'50',
        'textured_plate_temp':'50','textured_plate_temp_initial_layer':'50'}.items():filament[key]=[value]
    pp=HERE/'proces-kobra-x-silk-navrh.json';fp=HERE/'filament-zlaty-silk-navrh.json'
    save_json(pp,process);save_json(fp,filament)
    return pp,fp


def run_cli(args,log):
    with log.open('w') as out:r=subprocess.run([CLI,*args],stdout=out,stderr=subprocess.STDOUT,env={**os.environ,'DISPLAY':''},timeout=1800)
    require(r.returncode==0,f'Slicer exit {r.returncode}, viz {log}')


def check_project(path,mesh,t,sliced):
    def translation(value):
        m=list(map(float,value.split())) if value else IDENTITY+[0,0,0]
        require(m[:9]==IDENTITY,'Změněná orientace/měřítko');return m[9:]
    with ZipFile(path) as z:
        require(z.testzip() is None,'Poškozený ZIP')
        root=ET.fromstring(z.read('3D/3dmodel.model'));require(root.get('unit')=='millimeter','Nesprávné jednotky')
        items=root.findall('m:build/m:item',XMLNS);require(len(items)==1,'Nesprávný počet fyzických kopií')
        modelcfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        cfg=json.loads(z.read('Metadata/project_settings.config'))
        expected={'printer_model':'Anycubic Kobra X','nozzle_diameter':['0.4'],
            'layer_height':'0.2','wall_loops':'2','sparse_infill_density':'8%',
            'enable_support':'0','enable_prime_tower':'0','filament_colour':['#D4AF37'],
            'nozzle_temperature':['220'],'nozzle_temperature_initial_layer':['225'],
            'textured_plate_temp':['50'],'filament_max_volumetric_speed':['6']}
        for k,v in expected.items():require(cfg.get(k)==v,f'Změněné nastavení {k}: {cfg.get(k)}')
        require(len(cfg['filament_settings_id'])==1,'Více než jeden logický filament')
        repairs=[p.attrib for p in modelcfg.findall('.//mesh_stat')]
        require(all(all(int(v)==0 for v in p.values()) for p in repairs),f'Opravy sítě: {repairs}')
        item=items[0];obj=root.find(f'm:resources/m:object[@id="{item.get("objectid")}"]',XMLNS)
        components=obj.findall('m:components/m:component',XMLNS);require(len(components)==1,'Nesprávný počet dílů')
        comp=components[0];nested=ET.fromstring(z.read(comp.get(f'{{{PNS}}}path').lstrip('/')))
        node=nested.find(f'm:resources/m:object[@id="{comp.get("objectid")}"]/m:mesh',XMLNS)
        offset=[a+b for a,b in zip(translation(item.get('transform')),translation(comp.get('transform')))]
        vv=[[float(p.get(a))+offset[i] for i,a in enumerate('xyz')] for p in node.findall('m:vertices/m:vertex',XMLNS)]
        ff=node.findall('m:triangles/m:triangle',XMLNS)
        require(len(vv)==len(mesh['vertices']) and len(ff)==len(mesh['faces']),'Změněná síť')
        delta=max(abs(mesh['vertices'][i][a]+t[a]-vv[i][a]) for i in range(len(vv)) for a in range(3))
        require(delta<0.001,'Slicer změnil geometrii/umístění')
        require(('Metadata/plate_1.gcode' in z.namelist())==sliced,'Chybí/nečekaný G-code')
        info={'sha256':sha(path),'physical_pieces':1,'maximum_vertex_delta_mm':delta,
            'mesh_repairs':repairs,'has_gcode':sliced,'settings':{k:cfg.get(k) for k in set(expected)|{'print_settings_id','filament_settings_id','outer_wall_speed','inner_wall_speed','brim_width','sparse_infill_pattern','filament_density'}}}
        if sliced:
            gcode=z.read('Metadata/plate_1.gcode');info['gcode_sha256']=hashlib.sha256(gcode).hexdigest()
            info['gcode_bytes']=len(gcode)
            si=ET.fromstring(z.read('Metadata/slice_info.config'))
            info['slice_metadata']={n.get('key'):n.get('value') for n in si.iter('metadata') if n.get('key') in ('prediction','weight','outside','support_used')}
            info['warnings']=[n.attrib for n in si.iter('warning')]
            require(info['slice_metadata'].get('outside')=='false','Přesah podložky')
            require(info['slice_metadata'].get('support_used')=='false','Neočekávané podpory')
            require(not [n for n in info['warnings'] if n.get('msg') not in ('not_support_traditional_timelapse',)],f'Varování sliceru: {info["warnings"]}')
            require(int(info['slice_metadata']['prediction'])<=7200,'Odhad překračuje 2 hodiny')
        return info


def parse_paths(gcode):
    layers=[];x=y=z=e=0.0;relative_xyz=relative_e=False;role='';f=0
    for line in gcode.splitlines():
        if line.startswith(';LAYER_CHANGE'):layers.append([])
        elif line.startswith(';TYPE:'):role=line[6:].strip()
        code=line.split(';',1)[0].strip()
        if code=='G90':relative_xyz=False
        elif code=='G91':relative_xyz=True
        elif code=='M82':relative_e=False
        elif code=='M83':relative_e=True
        if code.startswith('G92'):
            for key,value in re.findall(r'\b([XYZE])([+-]?\d*\.?\d+)',code):
                if key=='X':x=float(value)
                elif key=='Y':y=float(value)
                elif key=='Z':z=float(value)
                elif key=='E':e=float(value)
        if not code.startswith(('G0 ','G1 ')):continue
        args={k:float(v) for k,v in re.findall(r'\b([XYZEF])([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)',code)}
        nx=x+args.get('X',0) if relative_xyz else args.get('X',x)
        ny=y+args.get('Y',0) if relative_xyz else args.get('Y',y)
        nz=z+args.get('Z',0) if relative_xyz else args.get('Z',z)
        ne=args.get('E',e);f=args.get('F',f)
        extruded='E' in args and (ne>0 if relative_e else ne>e)
        if layers and extruded and (nx!=x or ny!=y) and role!='Custom':layers[-1].append((x,y,nx,ny,nz,role,f/60))
        x,y,z=nx,ny,nz
        if 'E' in args:e=e+ne if relative_e else ne
    return layers


def check_paths(gcode,mesh,t):
    layers=parse_paths(gcode);require(all(layers),'Vrstva bez extruze')
    segments=[s for lay in layers for s in lay]
    roles=Counter(s[5] for s in segments)
    require(not any('support' in r.lower() for r in roles),'Neočekávané podpory v drahách')
    require(not any('tower' in r.lower() for r in roles),'Neočekávaná purge tower')
    require(roles['Brim']>0,'Chybí brim')
    lo=[min(min(s[i],s[i+2]) for s in segments) for i in range(2)]
    hi=[max(max(s[i],s[i+2]) for s in segments) for i in range(2)]
    require(all(0<=lo[i]<hi[i]<=260 for i in range(2)),'Dráhy mimo Kobra X')
    maxz=max(s[4] for s in segments);require(abs(maxz-mesh['size_mm'][2])<0.21,'Nesprávná výška drah')
    require('G9111 bedTemp=50 extruderTemp=225' in gcode,'Nesprávné startovací teploty')
    tool_commands=re.findall(r'^T(\d+)',gcode,re.M);require(set(tool_commands)<=set('0'),'Více barev v G-code')
    return {'layer_count':len(layers),'all_layers_have_extrusion':True,'maximum_extrusion_z_mm':maxz,
        'roles_segments':dict(roles),'extrusion_xy_min_mm':lo,'extrusion_xy_max_mm':hi,
        'minimum_edge_margin_mm':min(lo+[260-v for v in hi]),'tool_commands':tool_commands,
        'start_temperature_c':{'nozzle':225,'bed':50},'supports_generated':False,
        'purge_tower_generated':False,'layer_previews':render_layers(layers,mesh,t)},layers


def render_layers(layers,mesh,t):
    selected=[1,20,50,100,150,200,250,300,350,len(layers)]
    selected=sorted(set(i for i in selected if 0<i<=len(layers)))
    pw,ph=480,400;columns=5;rows=math.ceil(len(selected)/columns)
    im=Image.new('RGB',(pw*columns,ph*rows+100),'#f5f2e9');d=ImageDraw.Draw(im)
    title=ImageFont.truetype(FONT,25);small=ImageFont.truetype(FONT,17)
    d.text((25,15),'Podložka 01 · skutečné extruzní dráhy předávaného projektu',font=title,fill='#453619')
    x0=mesh['lo'][0]+t[0]-5;x1=mesh['hi'][0]+t[0]+5;y0=mesh['lo'][1]+t[1]-5;y1=mesh['hi'][1]+t[1]+5
    scale=min((pw-50)/(x1-x0),(ph-100)/(y1-y0))
    for idx,n in enumerate(selected):
        ox=(idx%columns)*pw;oy=65+(idx//columns)*ph
        d.text((ox+20,oy),f'Vrstva {n:03d} · Z {layers[n-1][0][4]:g} mm',font=small,fill='#453619')
        xy=lambda x,y:(ox+25+(x-x0)*scale,oy+50+(y1-y)*scale)
        for x,y,nx,ny,z,role,f in layers[n-1]:d.line((*xy(x,y),*xy(nx,ny)),fill='#bf5a31' if 'bridge' in role.lower() or 'overhang' in role.lower() else '#497f69' if role=='Brim' else '#574321',width=2)
    d.text((25,im.height-30),'Zeleně brim · oranžově most/převis · hnědě model. Jeden kus, jedna barva.',font=small,fill='#453619')
    im.save(HERE/'podlozka-01-vrstvy.png')
    return {'file':'podlozka-01-vrstvy.png','selected_layers':selected}


def render_plate(mesh,t):
    im=Image.new('RGB',(1000,1080),'#f5f2e9');d=ImageDraw.Draw(im)
    title=ImageFont.truetype(FONT,28);small=ImageFont.truetype(FONT,21)
    d.text((45,20),'Podložka 01 · Kobra X · 260 × 260 mm',font=title,fill='#453619')
    xy=lambda x,y:(45+3.5*x,80+3.5*(260-y))
    d.rectangle((xy(0,260),xy(260,0)),fill='#eae6db',outline='#a39777',width=3)
    for face in sorted(mesh['faces'],key=lambda f:sum(mesh['vertices'][i][2] for i in f)):
        pp=[mesh['vertices'][i] for i in face];h=sum(p[2] for p in pp)/3
        q=min(1,max(0,(h-mesh['lo'][2])/mesh['size_mm'][2]));tone=(int(145+65*q),int(111+64*q),int(35+30*q))
        d.polygon([xy(p[0]+t[0],p[1]+t[1]) for p in pp],fill=tone)
    x,y=xy(130,130);d.rounded_rectangle((x-20,y-18,x+20,y+18),radius=5,fill='white');d.text((x-14,y-15),'01',font=small,fill='#453619')
    d.text((45,1010),'01 = 1× celý pokerový pohár · skutečná STL · nastojato',font=small,fill='#453619')
    d.text((45,1040),'Kopie je již vložená. Nenásobit ani automaticky nepřerovnávat.',font=small,fill='#72664e')
    im.save(HERE/'podlozka-01.png')


def main():
    HERE.mkdir(exist_ok=True);CACHE.mkdir(exist_ok=True)
    require(all(p.exists() for p in (STL,MACHINE,PROCESS,FILAMENT)),'Chybí STL/profily')
    mesh=read_mesh();t=make_geometry(mesh);render_plate(mesh,t);pp,fp=create_profiles()
    configured=CACHE/'configured.3mf'
    run_cli(['--datadir',str(CACHE/'datadir-export'),'--load-settings',f'{MACHINE};{pp}','--load-filaments',str(fp),'--arrange','0','--orient','0','--export-3mf',configured.name,'--outputdir',str(CACHE),str(GEOMETRY)],CACHE/'export.log')
    cfginfo=check_project(configured,mesh,t,False)
    run_cli(['--datadir',str(CACHE/'datadir-slice'),'--arrange','0','--orient','0','--slice','0','--export-3mf','sliced.3mf','--outputdir',str(CACHE),str(configured)],CACHE/'slice.log')
    sliced=CACHE/'sliced.3mf';info=check_project(sliced,mesh,t,True)
    with ZipFile(sliced) as src,ZipFile(PROJECT,'w',ZIP_DEFLATED) as out:
        for name in src.namelist():
            b=src.read(name)
            if name=='3D/3dmodel.model':b=b.replace('pouze geometrie'.encode(),'nastavený a nařezaný projekt'.encode()).replace('1 kus 1:1; alternativa bez procesu, filamentu a G-code.'.encode(),'1 kus; Kobra X 0.4; Alzament PLA Silk Gold; návrhový profil, fyzicky neověřený.'.encode())
            out.writestr(name,b)
    final=check_project(PROJECT,mesh,t,True);require(final['gcode_sha256']==info['gcode_sha256'],'Změněný G-code při předání')
    with ZipFile(PROJECT) as z:gcode=z.read('Metadata/plate_1.gcode').decode(errors='replace')
    audit,layers=check_paths(gcode,mesh,t)
    errors=sorted(set(re.findall(r'error[^\n]*',(CACHE/'slice.log').read_text(errors='replace'),re.I)))
    report={'status':'Lokálně nařezáno; fyzický tisk neověřen','source_stl_sha256':sha(STL),
        'geometry_3mf_sha256':sha(GEOMETRY),'source_size_mm':mesh['size_mm'],'source_triangles':len(mesh['faces']),
        'translation_mm':t,'machine_profile_sha256':sha(MACHINE),'process_profile_sha256':sha(pp),
        'filament_profile_sha256':sha(fp),'configured':cfginfo,'delivered':final,'toolpath_audit':audit,
        'cli_error_messages':errors,'printer_contact':False,'physical_print_verified':False,
        'material_source':{'url':'https://www.alza.cz/alzament-pla-silk-1-kg-gold-d12869930.htm',
        'checked_date':'2026-10-09','product':'Alzament PLA Silk 1 kg Gold ALZMNTS07',
        'supplier_nozzle_c':[210,230],'supplier_bed_c':[45,60],'supplier_speed_mm_s':[40,250],
        'profile_status':'Návrhový profil, bez fyzické kalibrace; skutečný slot/cívka neověřeny'}}
    save_json(HERE/'kontrola-rezani.json',report)
    print(json.dumps({'project':str(PROJECT),'size_mm':mesh['size_mm'],'layers':len(layers),'slice':final['slice_metadata'],'warnings':final['warnings'],'cli_errors':errors},ensure_ascii=False))

if __name__=='__main__':main()
