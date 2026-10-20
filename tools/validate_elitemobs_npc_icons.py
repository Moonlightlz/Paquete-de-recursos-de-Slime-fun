"""GUI textures must exist AND be registered in Minecraft's item atlas."""
from pathlib import Path
import json,zipfile,struct
ROOT=Path(__file__).resolve().parents[1]
def registrations(z):
    result=set()
    atlas=json.loads(z.read('assets/minecraft/atlases/items.json'))
    for source in atlas['sources']:
        kind=source.get('type','').removeprefix('minecraft:')
        if kind=='single':result.add(source.get('sprite',source['resource']))
        elif kind=='directory':
            directory=source['source'].rstrip('/')+'/'
            for path in z.namelist():
                parts=path.split('/')
                if len(parts)<5 or parts[0]!='assets' or parts[2]!='textures' or not path.endswith('.png'):continue
                resource='/'.join(parts[3:]).removesuffix('.png')
                if resource.startswith(directory):result.add(parts[1]+':'+source['prefix']+resource[len(directory):])
    return result
def validate(pack):
    report=json.loads((ROOT/'server/elitemobs-npc-menu-icons.json').read_text(encoding='utf-8'));checks=0
    with zipfile.ZipFile(pack) as z:
        registered=registrations(z)
        for model in report['unchanged_model_files']:
            for ref in json.loads(z.read(model)).get('textures',{}).values():
                if not ref.startswith('elitemobs:ui/'):continue
                assert ref in registered,f'GUI sprite not registered: {ref}'
                ns,path=ref.split(':',1);data=z.read(f'assets/{ns}/textures/{path}.png')
                assert data.startswith(b'\x89PNG\r\n\x1a\n'),ref
                width,height=struct.unpack('>II',data[16:24]);assert width>0 and height>0
                checks+=1
        for ref in report['added_sprites']:assert ref in registered
        assert len(report['added_sprites'])==15
    print(f'NPC menu icons: {checks} textures registered, valid PNGs and preserved model paths.')
    return checks
if __name__=='__main__':validate(ROOT/'dist/RainxEnma-Slimefun-26.2.zip')
