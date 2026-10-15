"""Check exact model routing and preservation of all unchanged upstream files."""
from pathlib import Path
import json,zipfile
R=Path(__file__).resolve().parents[1]
with zipfile.ZipFile(R/'vendor/SlimefunLegacyRP-4.0.2.zip') as base,zipfile.ZipFile(R/'dist/RainxEnma-Slimefun-26.2.zip') as out:
    base_names=set(base.namelist());out_names=set(out.namelist())
    allowed={p.relative_to(R/'overrides').as_posix() for p in (R/'overrides').rglob('*') if p.is_file()}
    checks=0
    for p in base.namelist():
        if p.endswith('/'):continue
        assert p in out_names,p
        if p not in allowed:assert base.read(p)==out.read(p),p
        checks+=1
    def numbers(x):
        result={}
        if isinstance(x,dict):
            if str(x.get('type','')).endswith('range_dispatch') and str(x.get('property','')).endswith('custom_model_data'):
                result.update({e['threshold']:e['model'] for e in x.get('entries',[])})
            for v in x.values():result.update(numbers(v))
        elif isinstance(x,list):
            for v in x:result.update(numbers(v))
        return result
    for item in json.loads((R/'server/added-models.json').read_text(encoding='utf-8')):
        carrier=item['material'].lower();p=f'assets/minecraft/items/{carrier}.json'
        overlay='sfl_26_1_plus/'+p
        for path in [overlay if overlay in out_names else p]:
            model=json.loads(out.read(path))['model'];n=item['custom_model_data']
            assert numbers(model).get(n)==item['model'],item['id']
            checks+=1
    for p in allowed:
        if p=='pack.mcmeta':continue
        model=json.loads(out.read(p))['model']
        previous_path=p if p in base_names else p.removeprefix('sfl_26_1_plus/')
        previous=json.loads(base.read(previous_path))['model'] if previous_path in base_names else {'type':'minecraft:model','model':'minecraft:item/'+Path(previous_path).stem}
        assert model['fallback']==previous,p
        for entry in model['entries']:
            if entry['model']!=previous:
                assert any(e['threshold']==entry['threshold']+1 for e in model['entries']),p
        checks+=1
print(f'PASS: {checks} checks; upstream preserved and all added model routes exist.')
