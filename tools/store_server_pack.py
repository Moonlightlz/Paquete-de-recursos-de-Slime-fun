"""Store and verify the server's combined Slimefun, ItemsAdder and EcoItems pack."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile,urllib.request

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,help='Already downloaded ItemsAdder generated.zip')
parser.add_argument('--url',default='http://ny05.holy.gg:26529/resourcepack')
args=parser.parse_args()
if args.source:
    data=args.source.read_bytes()
else:
    with urllib.request.urlopen(args.url,timeout=45) as response:data=response.read()
with zipfile.ZipFile(io.BytesIO(data)) as pack,zipfile.ZipFile(ROOT/'dist/RainxEnma-Slimefun-26.2.zip') as base:
    assert pack.testzip() is None,'Damaged ZIP'
    names=set(pack.namelist());base_names=set(base.namelist())
    assert base_names<=names,'Slimefun files missing'
    shared={'pack.mcmeta','pack.png','assets/minecraft/atlases/blocks.json','assets/minecraft/sounds.json'}
    for name in base_names-shared:assert base.read(name)==pack.read(name),'Slimefun asset changed: '+name
    for namespace in ['_iainternal','ecoitems']:
        assert any(name.startswith('assets/'+namespace+'/textures/') for name in names),'Missing namespace: '+namespace
    for name in names:
        if name.endswith(('.json','.mcmeta')):json.loads(pack.read(name))
    fonts=json.loads(pack.read('assets/minecraft/font/default.json'))['providers'];glyphs={}
    for provider in fonts:
        if provider.get('type')!='bitmap':continue
        namespace,path=provider['file'].split(':',1) if ':' in provider['file'] else ('minecraft',provider['file'])
        assert 'assets/'+namespace+'/textures/'+path in names,'Missing font bitmap: '+provider['file']
        for row in provider['chars']:
            for char in row:
                if char=='\x00':continue
                assert char not in glyphs or glyphs[char]==provider['file'],'Conflicting glyph '+hex(ord(char))
                glyphs[char]=provider['file']
    result={'file':'RainxEnma-Completo-26.2.zip','minecraft':'26.2','source_url':args.url,'bytes':len(data),'sha1':hashlib.sha1(data).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'entries':len(names),'preserved_slimefun_entries':len(base_names),'ecoitems_entries':sum(n.startswith('assets/ecoitems/') for n in names),'font_bitmaps_verified':sum(p.get('type')=='bitmap' for p in fonts)}
(ROOT/'dist'/result['file']).write_bytes(data)
(ROOT/'dist/combined-checksums.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
