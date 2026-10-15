"""Run upstream guards with the explicitly validated Eternals model substitutions."""
from pathlib import Path
import json,zipfile
import validate_upstream as upstream
from eternals_validation import validate,load

ROOT=Path(__file__).resolve().parents[1]
pack=ROOT/'dist/RainxEnma-Slimefun-26.2.zip'
validate(pack)
m=load()
with zipfile.ZipFile(ROOT/'vendor/eternals-baseline-carriers.zip') as before,zipfile.ZipFile(pack) as after:
    for carrier,expected in list(upstream.WORKING_CARRIER_CANONICAL_HASHES.items()):
        path=f'assets/minecraft/items/{carrier}.json'
        if path not in m['changed_carriers']:continue
        # First prove that the unchanged part came from the guarded upstream carrier.
        assert upstream._canonical_hash(upstream._working_document(json.loads(before.read(path))))==expected,path
        # validate() above proved that only listed item-model branches were replaced.
        upstream.WORKING_CARRIER_CANONICAL_HASHES[carrier]=upstream._canonical_hash(upstream._working_document(json.loads(after.read(path))))
errors=upstream.validate(str(pack))
assert not errors,'\n'.join(errors)
print('Resource-pack validation passed with scoped Eternals substitutions.')
