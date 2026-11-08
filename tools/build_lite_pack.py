"""Build the light variant used by /optimizacion (RainxOptimizacion) from dist/RainxEnma-Slimefun-26.2.zip.

- Animated textures keep only their first frame (the animation section is removed from the .mcmeta).
- Textures larger than LIMIT px are downscaled by a power of two that divides both sides, so models, UVs
  and atlases stay valid; results are between LIMIT and 2*LIMIT-1 px.
- Never touched: font bitmaps, textures/gui (nine-slice sprites), textures whose .mcmeta has gui/mcmodels
  sections, every JSON, sound and overlay definition.
The output is deterministic (sorted entries, fixed timestamps) so CI only commits real changes.
Requires Pillow.
"""
from pathlib import Path
import hashlib, io, json, re, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'dist/RainxEnma-Slimefun-26.2.zip'
OUT = ROOT / 'dist/RainxEnma-Slimefun-26.2-lite.zip'
CHECKSUMS = ROOT / 'dist/checksums-lite.json'
LIMIT = 128
STAMP = (2026, 10, 14, 0, 0, 0)

src = zipfile.ZipFile(SOURCE)
names = set(src.namelist())

font_files = set()
for name in names:
    if re.search(r'(?:^|/)assets/[^/]+/font/[^/]+\.json$', name):
        for provider in json.loads(src.read(name).decode('utf-8-sig')).get('providers', []):
            if 'file' in provider:
                ns, path = provider['file'].split(':', 1) if ':' in provider['file'] else ('minecraft', provider['file'])
                font_files.add(f'assets/{ns}/textures/{path}')


def protected(name, meta):
    root = name[name.index('assets/'):] if 'assets/' in name else name
    return root in font_files or '/textures/gui/' in name or (meta is not None and ('gui' in meta or 'mcmodels' in meta))


def first_frame(image, anim):
    w, h = image.size
    if 'width' in anim:
        fw, fh = anim['width'], anim.get('height', h)
    elif 'height' in anim:
        fw, fh = w, anim['height']
    else:
        fw = fh = min(w, h)
    fw, fh = max(1, min(fw, w)), max(1, min(fh, h))
    frames = anim.get('frames')
    first = 0
    if frames:
        first = frames[0]['index'] if isinstance(frames[0], dict) else int(frames[0])
    per_row = max(1, w // fw)
    x, y = (first % per_row) * fw, (first // per_row) * fh
    if x + fw > w or y + fh > h:
        x, y = 0, 0
    return image.crop((x, y, x + fw, y + fh))


files = {}
stats = {'scaled': 0, 'frozen': 0, 'protected': 0, 'px_before': 0, 'px_after': 0}
for name in sorted(names):
    if name.endswith('/') or name.endswith('.png.mcmeta'):
        continue
    data = src.read(name)
    if name == 'pack.mcmeta':
        pack = json.loads(data.decode('utf-8-sig'))
        if isinstance(pack.get('pack', {}).get('description'), str):
            pack['pack']['description'] += ' §7(ligero)'
        data = json.dumps(pack, ensure_ascii=False, indent=2).encode('utf-8')
    elif name.endswith('.png'):
        meta_name = name + '.mcmeta'
        meta = json.loads(src.read(meta_name).decode('utf-8-sig')) if meta_name in names else None
        image = Image.open(io.BytesIO(data))
        original_size = image.size
        stats['px_before'] += original_size[0] * original_size[1]
        if protected(name, meta):
            stats['protected'] += 1
            stats['px_after'] += original_size[0] * original_size[1]
            if meta is not None:
                files[meta_name] = src.read(meta_name)
            files[name] = data
            continue
        changed = False
        animated = meta is not None and 'animation' in meta
        if animated:
            image = first_frame(image, meta['animation'])
            meta = {k: v for k, v in meta.items() if k != 'animation'}
            stats['frozen'] += 1
            changed = True
        w, h = image.size
        factor = 1
        while max(w, h) // (factor * 2) >= LIMIT and w % (factor * 2) == 0 and h % (factor * 2) == 0:
            factor *= 2
        if factor > 1:
            image = image.convert('RGBA').resize((w // factor, h // factor), Image.Resampling.LANCZOS)
            stats['scaled'] += 1
            changed = True
        if not changed and image.size != original_size:
            changed = True
        if changed:
            buffer = io.BytesIO()
            image.save(buffer, 'PNG', optimize=True)
            data = buffer.getvalue()
            check = Image.open(io.BytesIO(data))
            check.load()
            if not animated:
                assert original_size[0] * check.size[1] == original_size[1] * check.size[0], f'aspect changed: {name}'
        stats['px_after'] += image.size[0] * image.size[1]
        if meta:
            files[meta_name] = json.dumps(meta, separators=(',', ':')).encode('utf-8')
    files[name] = data

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, data in sorted(files.items()):
        info = zipfile.ZipInfo(name, STAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, data)

for name in names:
    if name.endswith('.json'):
        assert files.get(name) == src.read(name), f'json changed: {name}'
blob = OUT.read_bytes()
result = {'file': OUT.name, 'bytes': len(blob), 'sha1': hashlib.sha1(blob).hexdigest(), 'sha256': hashlib.sha256(blob).hexdigest(),
          'entries': len(files), 'source_sha1': hashlib.sha1(SOURCE.read_bytes()).hexdigest(),
          'texture_memory_mb': {'normal': round(stats['px_before'] * 4 / 1e6, 1), 'lite': round(stats['px_after'] * 4 / 1e6, 1)},
          'scaled': stats['scaled'], 'frozen_animations': stats['frozen'], 'protected': stats['protected']}
CHECKSUMS.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
