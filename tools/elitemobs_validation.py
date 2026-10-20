"""Validate EM routing separately, and expose the preserved original item graph."""
from pathlib import Path
import copy,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def strip(path,document):
    manifest=json.loads((ROOT/'server/elitemobs-integration.json').read_text(encoding='utf-8'))
    row=next((r for r in manifest['routes'] if r['item']==path),None)
    if row is None:return document
    node=document['model'];assert node['type']=='minecraft:range_dispatch' and node['property']=='minecraft:custom_model_data'
    fallback=node['fallback'];expected=[]
    models={int(n):v for n,v in row['models'].items()}
    for n,ref in sorted(models.items()):
        expected.append({'threshold':n,'model':{'type':'minecraft:model','model':ref}})
        if n+1 not in models:expected.append({'threshold':n+1,'model':copy.deepcopy(fallback)})
    assert node['entries']==expected,('Changed EM route',path)
    result=copy.deepcopy(document);result['model']=copy.deepcopy(fallback);return result
def validate(pack):
    manifest=json.loads((ROOT/'server/elitemobs-integration.json').read_text(encoding='utf-8'));checks=0
    with zipfile.ZipFile(pack) as z:
        names=set(z.namelist())
        for row in manifest['routes']:
            strip(row['item'],json.loads(z.read(row['item'])));checks+=1
            for ref in row['models'].values():
                ns,path=ref.split(':',1);assert f'assets/{ns}/models/{path}.json' in names,ref;checks+=1
        for name in names:
            if not name.startswith('assets/elitemobs/') or not name.endswith('.json'):continue
            obj=json.loads(z.read(name))
            def refs(node):
                if isinstance(node,dict):
                    if node.get('type')=='minecraft:model':
                        ns,path=node['model'].split(':',1);assert f'assets/{ns}/models/{path}.json' in names,node
                    for v in node.values():refs(v)
                elif isinstance(node,list):
                    for v in node:refs(v)
            if '/items/' in name:refs(obj)
            if '/models/' in name:
                for ref in obj.get('textures',{}).values():
                    if not ref.startswith('elitemobs:'):continue
                    assert 'assets/elitemobs/textures/'+ref.split(':',1)[1]+'.png' in names,ref
            checks+=1
        font=json.loads(z.read('assets/minecraft/font/default.json'))
        assert not any(p.get('type')=='bitmap' and p.get('height',0)<0 for p in font['providers'])
        assert next(p['advances'] for p in font['providers'] if p['type']=='space')=={'\uf801':-17,'\uf805':-183}
    print(f'EliteMobs integration passed: {checks} checks; original model graphs retained.')
