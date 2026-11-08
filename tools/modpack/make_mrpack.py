"""Builds dist/RainxEnma-Ligero-26.2.mrpack (Modrinth format) for low-end PCs.

Only Modrinth download links and hashes go into the pack; launchers (Modrinth App, Prism, ATLauncher...)
download the mods themselves. Overrides: servers.dat with RainxEnma (textures accepted) and light options.
"""
import hashlib, io, json, struct, sys, urllib.parse, urllib.request, zipfile
from pathlib import Path

MC = '26.2'
MODS = ['fabric-api', 'sodium', 'lithium', 'ferrite-core', 'entityculling', 'moreculling', 'immediatelyfast', 'dynamic-fps', 'sodium-extra']
SERVER = ('RainxEnma', 'rainxenma.holy.gg:26529')
UA = {'User-Agent': 'rainxenma-modpack/1.0'}
r = Path(__file__).resolve().parents[2] / 'dist'


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as response:
        return json.load(response)


def best_version(project):
    query = urllib.parse.urlencode({'game_versions': json.dumps([MC]), 'loaders': json.dumps(['fabric'])})
    versions = get(f'https://api.modrinth.com/v2/project/{project}/version?{query}')
    releases = [v for v in versions if v['version_type'] == 'release'] or versions
    if not releases:
        raise SystemExit(f'{project}: no Fabric build for {MC}')
    return releases[0]


loader = next(v['loader']['version'] for v in get(f'https://meta.fabricmc.net/v2/versions/loader/{MC}') if v['loader']['stable'])
chosen, queue = {}, list(MODS)
while queue:
    project = queue.pop(0)
    version = best_version(project)
    if version['project_id'] in chosen:
        continue
    chosen[version['project_id']] = version
    for dep in version['dependencies']:
        if dep['dependency_type'] == 'required' and dep.get('project_id') and dep['project_id'] not in chosen:
            queue.append(dep['project_id'])

problems = []
for version in chosen.values():
    for dep in version['dependencies']:
        if dep['dependency_type'] == 'incompatible' and dep.get('project_id') in chosen:
            problems.append((version['name'], dep['project_id']))
if problems:
    raise SystemExit(f'incompatible mods: {problems}')

files, listing = [], []
for version in chosen.values():
    file = next((f for f in version['files'] if f['primary']), version['files'][0])
    files.append({'path': f"mods/{file['filename']}", 'hashes': {'sha1': file['hashes']['sha1'], 'sha512': file['hashes']['sha512']},
                  'env': {'client': 'required', 'server': 'unsupported'}, 'downloads': [file['url']], 'fileSize': file['size']})
    listing.append(f"{version['name']} {version['version_number']}")
index = {'formatVersion': 1, 'game': 'minecraft', 'versionId': '1.0.0', 'name': 'RainxEnma Ligero',
         'summary': 'Mods de rendimiento para jugar RainxEnma en PC de bajos recursos (Minecraft 26.2, Fabric).',
         'files': sorted(files, key=lambda f: f['path']), 'dependencies': {'minecraft': MC, 'fabric-loader': loader}}


def nbt_string(value):
    raw = value.encode('utf-8')
    return struct.pack('>H', len(raw)) + raw


def servers_dat():
    entry = b'\x08' + nbt_string('name') + nbt_string(SERVER[0]) + b'\x08' + nbt_string('ip') + nbt_string(SERVER[1]) \
            + b'\x01' + nbt_string('acceptTextures') + b'\x01' + b'\x00'
    return b'\x0a' + nbt_string('') + b'\x09' + nbt_string('servers') + b'\x0a' + struct.pack('>i', 1) + entry + b'\x00'


# Conservative low-end defaults; unknown keys are ignored by the game and everything can be changed in-game.
options = '\n'.join([
    'renderDistance:6', 'simulationDistance:5', 'graphicsMode:0', 'ao:false', 'renderClouds:"false"', 'entityShadows:false',
    'particles:1', 'biomeBlendRadius:0', 'mipmapLevels:0', 'maxFps:60', 'enableVsync:false', 'entityDistanceScaling:0.75',
    'fullscreen:false', 'lang:es_es', 'resourcePacks:["vanilla"]',
]) + '\n'

out = r / 'RainxEnma-Ligero-26.2.mrpack'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('modrinth.index.json', json.dumps(index, indent=2, ensure_ascii=False))
    z.writestr('overrides/servers.dat', servers_dat())
    z.writestr('overrides/options.txt', options)
print('fabric-loader', loader)
print('\n'.join(sorted(listing)))
print(out.name, out.stat().st_size, hashlib.sha256(out.read_bytes()).hexdigest())
