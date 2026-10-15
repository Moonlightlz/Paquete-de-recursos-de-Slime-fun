"""Rebuild the combined pack without network access or external dependencies."""
from pathlib import Path
import hashlib, json, zipfile

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'vendor/SlimefunLegacyRP-4.0.2.zip'
manifest=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['upstream']['sha256'], 'Upstream checksum mismatch'
with zipfile.ZipFile(source) as archive:
    files={p:archive.read(p) for p in archive.namelist() if not p.endswith('/')}
for path in (ROOT/'overrides').rglob('*'):
    if path.is_file(): files[path.relative_to(ROOT/'overrides').as_posix()]=path.read_bytes()
files['LICENSE']=(ROOT/'LICENSE').read_bytes()
files['CREDITS.md']=(ROOT/'CREDITS.md').read_bytes()
for path,content in files.items():
    if path.endswith(('.json','.mcmeta')):json.loads(content)
out=ROOT/'dist/RainxEnma-Slimefun-26.2.zip'
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for name,data in sorted(files.items()):
        info=zipfile.ZipInfo(name,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644<<16;archive.writestr(info,data)
result={'file':out.name,'bytes':out.stat().st_size,'sha1':hashlib.sha1(out.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(files)}
(ROOT/'dist/checksums.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
