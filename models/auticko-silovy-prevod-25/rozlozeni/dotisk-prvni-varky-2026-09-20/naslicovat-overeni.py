#!/usr/bin/env python3
"""Reproduce diagnostic slicing in ignored cache, with no printer connection.

Does not touch personal profiles or deliver a printer-ready G-code. Run with
project packing Python, then overit-drahy.py with the printed cache path.
"""
import hashlib,json,os,subprocess,importlib.util,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CACHE=REPO/'.cache/dotisk-2026-09-20'
PROFILES=Path('/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic')
MACHINE=PROFILES/'machine/Anycubic Kobra X 0.4 nozzle.json'
FILAMENT=PROFILES/'filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json'
PROCESS=PROFILES/'process/0.12mm High Quality @Anycubic Kobra X 0.4 nozzle.json'

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    settings=json.loads((HERE/'doporucene-nastaveni.json').read_text())
    base=json.loads(PROCESS.read_text())
    def run(i):
        if i==1:
            spec=importlib.util.spec_from_file_location('upright_projects',HERE.parent/'stojate-cepy-2026-09-20/projekty.py')
            upright=importlib.util.module_from_spec(spec);spec.loader.exec_module(upright)
            result=upright.run('dotisk-01')
            out=CACHE/'plate-1';out.mkdir(exist_ok=True)
            shutil.copy2(result['sliced'],out/'sliced.3mf')
            return {'plate':1,'upright_native_project':result,'exit_code':0}
        process=dict(base);process.update(settings['common_overrides'])
        process['enable_support']='1' if settings['supports_by_plate'][str(i)] else '0'
        process['name']=process['print_settings_id']=f'Dotisk V3 diagnostic plate {i} 0.12mm'
        cfg=CACHE/f'process-{i}.json';cfg.write_text(json.dumps(process,indent=2))
        out=CACHE/f'plate-{i}';out.mkdir(exist_ok=True)
        cmd=['/usr/bin/AnycubicSlicerNext','--datadir',str(out/'profile'),'--arrange','0','--orient','0','--debug','3',
             '--load-settings',str(MACHINE)+';'+str(cfg),'--load-filaments',str(FILAMENT),'--slice','0',
             '--export-3mf','sliced.3mf','--outputdir',str(out),str(HERE/f'dotisk-25-podlozka-{i:02d}.3mf')]
        with (out/'cli.log').open('w') as log:
            result=subprocess.run(cmd,env=dict(os.environ,DISPLAY=''),stdout=log,stderr=subprocess.STDOUT,timeout=420)
        assert result.returncode==0 and (out/'sliced.3mf').is_file(),(i,result.returncode)
        return {'plate':i,'command':cmd,'exit_code':result.returncode,'process_sha256':hashlib.sha256(cfg.read_bytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(run,(1,2,3)))
    evidence={'scope':'Offline diagnostic slicing only; no personal settings or printer access.',
              'profiles':[{ 'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (MACHINE,FILAMENT,PROCESS)],'runs':results}
    (HERE/'evidence/rezani-prikazy.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(CACHE)

if __name__=='__main__':main()
