from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import PurePosixPath

REQUIRED_NAMESPACES = {
    "minecraft",
    "slimefun",
    "pylon",
    "rebar",
    "rebarmobs",
    "magic",
    "mmoitems_pack",
    "iaweapons",
    "mcicons",
}

FORBIDDEN_VANILLA_OVERRIDES = {
    "assets/minecraft/models/item/golden_sword.json",
    "assets/minecraft/textures/item/golden_sword.png",
    "assets/minecraft/textures/item/chainmail_helmet.png",
    "assets/minecraft/textures/item/chainmail_chestplate.png",
    "assets/minecraft/textures/item/chainmail_leggings.png",
    "assets/minecraft/textures/item/chainmail_boots.png",
}

WORKING_CARRIER_CANONICAL_HASHES = {
    "wooden_hoe": "bfcc45f5695719851f8e1fecde1de34ae224ddf23c3faefdeda25eb880fe7405",
    "leather_helmet": "034059c6b4774bfad32ba97770b55ec2791c34f6267076282c302d6ee4b6aa3c",
    "leather_chestplate": "36dd7f46f3c4c5d96226fc6617a5e02dbedcf88cb9e1904b3c0152b6ad7a7f97",
    "leather_leggings": "d6c7e7809544ae0e38d2ac246f7e32d1d0b357244548144517e702e3337c0b85",
    "leather_boots": "60154970567cc840f751b37e20a7ca9326d2a17a2fe967555ac1fe488bc038db",
    "chainmail_helmet": "11f438f2c5580e84a44a9708fb48cdab4d08d7de6aaac0448a26c05c82560dbd",
    "chainmail_chestplate": "35481d4896f4ffb0679b99b71f72877ff26591651d69ac2db2118dca5afc9f16",
    "chainmail_leggings": "ecbb1ec93999c908897819fd5964456d8cf893de6471b822aa841e26102060aa",
    "chainmail_boots": "7506442a7a516ee83b95ec7057ff032c09d23b0d41fb2dca406985889561622a",
    "iron_helmet": "12091578f3ce329e3f96ae16cf9789d2bd4881756d03f4a48245df84f13e159f",
    "iron_chestplate": "41b84abd369f95f5130219c9f70bc9ff264ccd95976a26d42670d00f47b3682d",
    "iron_leggings": "fa7ffa8397bb0a97fcfc31905e4c91144b364941f0d1005de5fdeb0e5c670dcb",
    "iron_boots": "cf4ed8ffc4813c035ee989d36a23c43ca542732fdda3784b378b251c94e568eb",
    "golden_helmet": "b9fed125d755dda3af231c04f54d96e24df04be75dbe2a2c9b1cbdc6b2268feb",
    "golden_chestplate": "3e93da542da00eb467ec39e5d0c3b4ab6581d97e2b94b893da7c97e8c92bd6c2",
    "golden_leggings": "416a8ff1e4d6db578c30fd717ccf862c1edaea967333940f83c1c7e006d2d678",
    "golden_boots": "a6045ef80e5543ab5d1f3fce67fccebc17dfdd4cfaa468ab473904769119070b",
    "diamond_helmet": "cc00d7fa13bd0152300df88934ec6744291d2828d3999618bac112f584664cf1",
    "diamond_chestplate": "146c09ecb8b5b10dc9a76297feb7911250ef1b33dc8404a58315901704bf33d5",
    "diamond_leggings": "4fc479ea6851283c295b239898677560dba80f3466f5774aea6550ea273ea60a",
    "diamond_boots": "06a2ba5e6963820dbf730a6ff5e7261fbb6bed9661b76c8590de6dd0766d87bf",
    "netherite_helmet": "bb3f588be3a9e61723976ae1ae2d46af24f4bd1857a3233deab7bd8248fe5f53",
    "netherite_chestplate": "12f8b3e162e2002b4e72daf26ff53c462ae3ef01dc1d8e6502be13749fc36cbf",
    "netherite_leggings": "0867d8fa357cf4df08acab694f6f9616ef7472c689bbf08a7b5b28f1ae67f359",
    "netherite_boots": "7e38e806a0c73d990559f216d98f1851c395dc67c0d37cb81638258e9b039908",
    "chest": "6ff2b5e74b8f48e3cb4004ad21efe81e0702ea3f428952a5122b1904991ce09a",
    "compass": "046d13cf9974feace0a653e1e4b2c88c116d09a5314205c62c008e2d223b075d",
    "clock": "2d0730b07250fc378d5c73962ffbb47b42fcb84daeb646d5c675681a05655c8f",
    "trident": "6e5d10ede46cc679a8f06f2cc5d1e02234ca252e3a5c90f02923ae8b07aabef2",
    "crossbow": "0ef4c367408e9f43640d9ddf579b4d942734edf61bfc5b3f590ca65b6de17a44",
    "oak_planks": "7873bd6583edb6a17615f5492b8f01b836cdff7b8978ae1198f248fc107f4eaf",
}

WORKING_OVERLAYS = [
    {"directory": "sfl_26_1_plus", "min_format": 84, "max_format": 9999},
]

WORKING_TALISMAN_MODELS = {
    "assets/slimefun/models/item/slimefun/talisman1/caveman.json": "slimefun:item/slimefun/talisman1/caveman",
    "assets/slimefun/models/item/slimefun/talisman2/caveman.json": "slimefun:item/slimefun/talisman2/caveman",
    "assets/slimefun/models/item/slimefun/talisman1/wise.json": "slimefun:item/slimefun/talisman1/wise",
    "assets/slimefun/models/item/slimefun/talisman2/wise.json": "slimefun:item/slimefun/talisman2/wise",
    "assets/slimefun/models/item/slimefun/talisman1/farmer.json": "slimefun:item/slimefun/talisman1/farmer",
    "assets/slimefun/models/item/slimefun/talisman2/farmer.json": "slimefun:item/slimefun/talisman2/farmer",
}

REQUIRED_FILES = {
    "pack.mcmeta",
    "pack.png",
    "assets/minecraft/atlases/items.json",
    "assets/minecraft/atlases/blocks.json",
    "assets/minecraft/items/player_head.json",
    "assets/minecraft/items/golden_sword.json",
    "assets/minecraft/items/chainmail_helmet.json",
    "assets/minecraft/items/chainmail_chestplate.json",
    "assets/minecraft/items/chainmail_leggings.json",
    "assets/minecraft/items/chainmail_boots.json",
    "sfl_26_1_plus/assets/minecraft/items/golden_sword.json",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_json(zf: zipfile.ZipFile, name: str, errors: list[str]):
    try:
        return json.loads(zf.read(name))
    except KeyError:
        fail(errors, f"missing JSON file: {name}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid JSON {name}: {exc}")
    return None


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def model_refs(obj) -> set[str]:
    refs: set[str] = set()
    for node in walk(obj):
        if node.get("type") in {"model", "minecraft:model"}:
            model = node.get("model")
            if isinstance(model, str):
                refs.add(model)
    return refs


TALISMAN_ALIAS_MODELS = {
    "assets/slimefun/models/slimefun/talisman1/caveman.json":
        "_slimefun:slimefun/talisman1/caveman",
    "assets/slimefun/models/slimefun/talisman2/caveman.json":
        "_slimefun:slimefun/talisman2/caveman",
    "assets/slimefun/models/slimefun/talisman1/wise.json":
        "_slimefun:slimefun/talisman1/wise",
    "assets/slimefun/models/slimefun/talisman2/wise.json":
        "_slimefun:slimefun/talisman2/wise",
    "assets/slimefun/models/slimefun/talisman1/farmer.json":
        "_slimefun:slimefun/talisman1/farmer",
    "assets/slimefun/models/slimefun/talisman2/farmer.json":
        "_slimefun:slimefun/talisman2/farmer",
}


def texture_refs(obj) -> set[str]:
    refs: set[str] = set()
    for node in walk(obj):
        textures = node.get("textures")
        if not isinstance(textures, dict):
            continue
        for value in textures.values():
            if isinstance(value, str) and not value.startswith("#"):
                refs.add(value)
    return refs


def slimefun_sprite_aliases(zf: zipfile.ZipFile, names: set[str], errors: list[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}

    for name in sorted(n for n in names if n.endswith("assets/minecraft/atlases/items.json")):
        atlas = parse_json(zf, name, errors)
        if not isinstance(atlas, dict):
            continue

        for source in atlas.get("sources", []):
            if not isinstance(source, dict):
                continue
            if source.get("type") not in {"single", "minecraft:single"}:
                continue

            resource = source.get("resource")
            sprite = source.get("sprite")
            if not (
                isinstance(resource, str)
                and isinstance(sprite, str)
                and resource.startswith("slimefun:")
                and sprite.startswith("_slimefun:")
            ):
                continue

            previous = aliases.get(resource)
            if previous is not None and previous != sprite:
                fail(
                    errors,
                    f"conflicting Slimefun item-atlas aliases for {resource}: {previous} vs {sprite}",
                )
            else:
                aliases[resource] = sprite

    return aliases


def check_slimefun_model_aliases(zf: zipfile.ZipFile, names: set[str], errors: list[str]) -> None:
    aliases = slimefun_sprite_aliases(zf, names, errors)
    if not aliases:
        # The modern v4 layout stores Slimefun sprites under item/ and does not need
        # the historical _slimefun alias layer. There is nothing to validate here.
        return

    mismatches: list[tuple[str, str, str]] = []
    for name in sorted(
        n for n in names if n.startswith("assets/slimefun/models/") and n.endswith(".json")
    ):
        model = parse_json(zf, name, errors)
        if not isinstance(model, dict):
            continue

        for ref in sorted(texture_refs(model)):
            expected = aliases.get(ref)
            if expected is not None:
                mismatches.append((name, ref, expected))

    if mismatches:
        examples = "; ".join(
            f"{name}: {actual} -> {expected}"
            for name, actual, expected in mismatches[:8]
        )
        extra = "" if len(mismatches) <= 8 else f"; ... {len(mismatches) - 8} more"
        fail(
            errors,
            "Slimefun models reference atlas resources instead of their registered "
            f"_slimefun sprite aliases ({len(mismatches)} reference(s)): {examples}{extra}",
        )

    # Regression guard for the six exact models reported broken on standalone 26.3.
    for name, expected in TALISMAN_ALIAS_MODELS.items():
        if name not in names:
            continue
        model = parse_json(zf, name, errors)
        if not isinstance(model, dict):
            continue
        refs = texture_refs(model)
        if expected not in refs:
            fail(errors, f"{name} does not reference required sprite alias {expected}")


def validate_aliases_only(path: str, expected_sha256: str | None = None) -> list[str]:
    errors: list[str] = []
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()

    if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
        fail(errors, f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}")

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        return [f"invalid ZIP: {exc}"]

    with zf:
        bad = zf.testzip()
        if bad:
            fail(errors, f"ZIP CRC failure: {bad}")
        names = {n for n in zf.namelist() if not n.endswith("/")}
        check_slimefun_model_aliases(zf, names, errors)

    print(f"SHA-256 {actual_sha256}  {path}")
    return errors


def has_player_head_fallback(obj) -> bool:
    for node in walk(obj):
        if node.get("type") == "minecraft:special":
            model = node.get("model")
            if isinstance(model, dict) and model.get("type") == "minecraft:player_head":
                return True
    return False


def check_pack_icon(zf: zipfile.ZipFile, errors: list[str]) -> None:
    try:
        data = zf.read("pack.png")
    except KeyError:
        fail(errors, "missing pack.png")
        return

    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(errors, "pack.png is not a valid PNG header")
        return

    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (256, 256):
        fail(errors, f"pack.png must remain 256x256, got {width}x{height}")


def check_pack_meta(meta, errors: list[str]) -> None:
    if not isinstance(meta, dict) or not isinstance(meta.get("pack"), dict):
        fail(errors, "pack.mcmeta does not contain a pack object")
        return

    pack = meta["pack"]
    pack_format = pack.get("pack_format")
    if not isinstance(pack_format, int) or pack_format < 75:
        fail(errors, f"pack_format must be >= 75, got {pack_format!r}")

    min_format = pack.get("min_format")
    if min_format not in (75, [75, 0]):
        fail(errors, f"min_format must remain 75/[75,0], got {min_format!r}")

    for node in walk(meta):
        if "formats" in node:
            fail(errors, "deprecated 'formats' key found in pack.mcmeta")
            break


def check_item_atlas(atlas, errors: list[str]) -> None:
    if not isinstance(atlas, dict):
        return
    for i, source in enumerate(atlas.get("sources", [])):
        if not isinstance(source, dict):
            continue
        source_dir = source.get("source")
        resource = source.get("resource")
        sprite = source.get("sprite")

        # Regression guard: this broke every placed block during 26.x testing.
        if source.get("type") in {"directory", "minecraft:directory"} and source_dir == "block":
            fail(errors, f"item atlas source #{i} imports the block directory")
        for value in (resource, sprite):
            if isinstance(value, str) and (":block/" in value or value.startswith("minecraft:block/")):
                fail(errors, f"item atlas source #{i} registers a block sprite: {value}")


def check_block_atlas(atlas, errors: list[str]) -> None:
    if not isinstance(atlas, dict):
        return
    sources = atlas.get("sources", [])
    if not sources:
        fail(errors, "block atlas has no custom sources")
        return
    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            continue
        source_dir = source.get("source")
        resource = source.get("resource")
        sprite = source.get("sprite")
        if source.get("type") in {"directory", "minecraft:directory"} and source_dir == "item":
            fail(errors, f"block atlas source #{i} imports the item directory")
        for value in (resource, sprite):
            if isinstance(value, str) and ":item/" in value:
                fail(errors, f"block atlas source #{i} registers an item sprite: {value}")


def _is_identity_wrapper(model) -> bool:
    if not isinstance(model, dict):
        return False
    kind = str(model.get("type", "")).removeprefix("minecraft:")
    prop = str(model.get("property", "")).removeprefix("minecraft:")
    component = str(model.get("component", "")).removeprefix("minecraft:")
    if kind != "condition" or prop != "has_component" or component != "custom_model_data":
        return False
    if not isinstance(model.get("on_true"), dict) or not isinstance(model.get("on_false"), dict):
        return False
    node = model["on_false"]
    while isinstance(node, dict):
        node_kind = str(node.get("type", "")).removeprefix("minecraft:")
        node_prop = str(node.get("property", "")).removeprefix("minecraft:")
        if node_kind != "condition":
            return False
        if node_prop == "component" and node.get("predicate") == "minecraft:custom_data":
            value = node.get("value")
            if isinstance(value, dict) and isinstance(value.get("PublicBukkitValues"), dict):
                return True
        node = node.get("on_false")
    return False


def _working_document(document):
    if not isinstance(document, dict):
        return document
    model = document.get("model")
    if _is_identity_wrapper(model):
        document = dict(document)
        document["model"] = model["on_true"]
    return document


def _canonical_hash(document) -> str:
    payload = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def check_working_generation(zf: zipfile.ZipFile, meta, errors: list[str]) -> None:
    overlays = meta.get("overlays", {}).get("entries", []) if isinstance(meta, dict) else []
    if overlays != WORKING_OVERLAYS:
        fail(errors, f"working overlay layout changed: {overlays!r}")

    names = set(zf.namelist())
    for item, expected in WORKING_CARRIER_CANONICAL_HASHES.items():
        name = f"assets/minecraft/items/{item}.json"
        data = parse_json(zf, name, errors)
        if not isinstance(data, dict):
            continue
        actual = _canonical_hash(_working_document(data))
        if actual != expected:
            fail(errors, f"{name} no longer matches owner-confirmed working carrier structure")

    for model_path, texture in WORKING_TALISMAN_MODELS.items():
        data = parse_json(zf, model_path, errors)
        if not isinstance(data, dict):
            continue
        actual = data.get("textures", {}).get("layer0")
        if actual != texture:
            fail(errors, f"{model_path} texture changed: {actual!r} != {texture!r}")
            continue
        namespace, rel = texture.split(":", 1)
        png = f"assets/{namespace}/textures/{rel}.png"
        if png not in names:
            fail(errors, f"{model_path} points to missing texture {png}")

    oak = parse_json(zf, "assets/minecraft/items/oak_planks.json", errors)
    if isinstance(oak, dict):
        model = _working_document(oak).get("model", {})
        fallback = model.get("fallback", {}) if isinstance(model, dict) else {}
        if fallback.get("model") != "minecraft:block/oak_planks":
            fail(errors, "oak_planks lost its 3D minecraft:block/oak_planks fallback")


def check_chainmail(zf: zipfile.ZipFile, errors: list[str]) -> None:
    for piece in ("helmet", "chestplate", "leggings", "boots"):
        name = f"assets/minecraft/items/chainmail_{piece}.json"
        data = parse_json(zf, name, errors)
        if data is None:
            continue
        expected = f"minecraft:item/chainmail_{piece}"
        if expected not in model_refs(data):
            fail(errors, f"{name} no longer contains the vanilla fallback {expected}")


def check_golden_sword(zf: zipfile.ZipFile, errors: list[str]) -> None:
    required_models = {
        "pylon:item/combat/bronze_sword",
        "iaweapons:ak47",
        "iaweapons:hand_gun",
        "iaweapons:revolver",
        "slimefun:slimefun/weapons/blade_of_vampires",
        "extra_gear:swords/gilded_iron_sword",
        "minecraft:item/golden_sword",
    }
    for name in (
        "assets/minecraft/items/golden_sword.json",
        "sfl_26_1_plus/assets/minecraft/items/golden_sword.json",
    ):
        data = parse_json(zf, name, errors)
        if data is None:
            continue
        refs = model_refs(data)
        missing = sorted(required_models - refs)
        if missing:
            fail(errors, f"{name} lost required Golden Sword mappings: {', '.join(missing)}")


def validate(path: str, expected_sha256: str | None = None) -> list[str]:
    errors: list[str] = []
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()

    if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
        fail(errors, f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}")

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        return [f"invalid ZIP: {exc}"]

    with zf:
        bad = zf.testzip()
        if bad:
            fail(errors, f"ZIP CRC failure: {bad}")

        names = {n for n in zf.namelist() if not n.endswith("/")}
        for name in sorted(REQUIRED_FILES - names):
            fail(errors, f"missing required file: {name}")
        for name in sorted(FORBIDDEN_VANILLA_OVERRIDES & names):
            fail(errors, f"forbidden vanilla override reintroduced: {name}")

        namespaces = {
            PurePosixPath(n).parts[1]
            for n in names
            if n.startswith("assets/") and len(PurePosixPath(n).parts) >= 3
        }
        for namespace in sorted(REQUIRED_NAMESPACES - namespaces):
            fail(errors, f"required namespace missing: assets/{namespace}/")

        check_pack_icon(zf, errors)
        meta = parse_json(zf, "pack.mcmeta", errors)
        if meta is not None:
            check_pack_meta(meta, errors)
            check_working_generation(zf, meta, errors)

        item_atlas = parse_json(zf, "assets/minecraft/atlases/items.json", errors)
        if item_atlas is not None:
            check_item_atlas(item_atlas, errors)

        block_atlas = parse_json(zf, "assets/minecraft/atlases/blocks.json", errors)
        if block_atlas is not None:
            check_block_atlas(block_atlas, errors)

        head = parse_json(zf, "assets/minecraft/items/player_head.json", errors)
        if head is not None and not has_player_head_fallback(head):
            fail(errors, "player_head.json lost the native minecraft:player_head fallback")

        check_golden_sword(zf, errors)
        check_chainmail(zf, errors)
        check_slimefun_model_aliases(zf, names, errors)

    print(f"SHA-256 {actual_sha256}  {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Slimefun Legacy resource-pack invariants."
    )
    parser.add_argument("pack", help="Path to SlimefunLegacyRP.zip")
    parser.add_argument("--sha256", help="Optional exact SHA-256 expected for this candidate")
    parser.add_argument(
        "--aliases-only",
        action="store_true",
        help="Validate only ZIP integrity and Slimefun item-atlas sprite aliases",
    )
    args = parser.parse_args()

    errors = (
        validate_aliases_only(args.pack, args.sha256)
        if args.aliases_only
        else validate(args.pack, args.sha256)
    )
    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("Resource-pack validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
