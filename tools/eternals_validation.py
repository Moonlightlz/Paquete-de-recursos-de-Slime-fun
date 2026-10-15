"""Validate the scoped Eternals migration against original carrier definitions."""
from pathlib import Path
import collections,copy,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]

def load():return json.loads((ROOT/'server/eternals-selection.json').read_text(encoding='utf-8'))

def before_carrier(path,document):
    manifest=load()
    if path not in manifest['changed_carriers']:return document
    with zipfile.ZipFile(ROOT/'vendor/eternals-baseline-carriers.zip') as z:return json.loads(z.read(path))

def validate(pack):
    m=load();checks=0
    for filename,key in [('eternals-baseline-carriers.zip','baseline_carriers_sha256'),('eternals-selected.zip','selected_source_zip_sha256')]:
        assert hashlib.sha256((ROOT/'vendor'/filename).read_bytes()).hexdigest()==m[key],filename
    assert len(m['selected_items'])==177
    assert set(x['group'] for x in m['selected_items'])==set(m['groups'])
    with zipfile.ZipFile(pack) as out,zipfile.ZipFile(ROOT/'vendor/eternals-baseline-carriers.zip') as old,zipfile.ZipFile(ROOT/'vendor/eternals-selected.zip') as source:
        names=set(out.namelist());patches=collections.defaultdict(dict)
        for row in m['patches']:
            key=json.dumps(row['before'],sort_keys=True)
            patches[row['path']][(row['custom_model_data'],key)]=row['after']
        for path in m['changed_carriers']:
            expected=json.loads(old.read(path))
            def apply(node):
                if isinstance(node,dict):
                    if str(node.get('type','')).endswith('range_dispatch') and str(node.get('property','')).endswith('custom_model_data'):
                        for entry in node.get('entries',[]):
                            key=(entry['threshold'],json.dumps(entry['model'],sort_keys=True))
                            if key in patches[path]:entry['model']=copy.deepcopy(patches[path][key])
                    for value in node.values():apply(value)
                elif isinstance(node,list):
                    for value in node:apply(value)
            apply(expected)
            assert expected==json.loads(out.read(path)),f'Unapproved carrier change: {path}'
            checks+=1
        for path,expected in m['source_files'].items():
            assert hashlib.sha256(source.read(path)).hexdigest()==expected,path
            checks+=1
        for original,target in m['imported_textures'].items():
            ons,op=original.split(':',1);tns,tp=target.split(':',1)
            a=f'assets/{ons}/textures/{op}.png';b=f'assets/{tns}/textures/{tp}.png'
            assert source.read(a)==out.read(b),f'Altered source image: {original}'
            if a+'.mcmeta' in source.namelist():assert source.read(a+'.mcmeta')==out.read(b+'.mcmeta')
            checks+=1
        def model_path(ref):
            ns,p=ref.split(':',1) if ':' in ref else ('minecraft',ref)
            return f'assets/{ns}/models/{p}.json'
        for ref in list(m['imported_models'].values())+list(m['derived_trim_models']):
            data=json.loads(out.read(model_path(ref)))
            parent=data.get('parent','')
            if parent:assert parent in ('item/generated','item/handheld','block/cube_all','minecraft:item/generated','minecraft:item/handheld','minecraft:block/cube_all') or model_path(parent) in names,parent
            for tex in data.get('textures',{}).values():
                if tex.startswith('#'):continue
                ns,p=tex.split(':',1) if ':' in tex else ('minecraft',tex)
                if ns=='rainxenma_eternals':assert f'assets/{ns}/textures/{p}.png' in names,tex
            checks+=1
        for new,original in m['derived_trim_models'].items():
            original_json=json.loads(out.read(model_path(original)))
            updated=json.loads(out.read(model_path(new)))
            assert original_json['textures']['layer1']==updated['textures']['layer1'],new
            assert updated['textures']['layer0'].startswith('rainxenma_eternals:'),new
            checks+=1
        atlas=json.loads(out.read('assets/minecraft/atlases/items.json'))
        assert any(s.get('source')=='item' and s.get('prefix')=='item/' for s in atlas['sources'])
        checks+=1
    print(f'Eternals validation passed: {checks} checks; 177 selected items, exact source PNG bytes and preserved carrier behavior.')
    return checks

if __name__=='__main__':validate(ROOT/'dist/RainxEnma-Slimefun-26.2.zip')
