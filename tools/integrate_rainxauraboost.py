"""Añade el Nucleo Aurico a la amatista, conservando todas las rutas anteriores."""
import json

CARRIER = "assets/minecraft/items/amethyst_shard.json"
CMD = 260310
MODEL = "rainxauraboost:item/nucleo_aurico"


def integrate(files):
    existing = json.loads(files[CARRIER]) if CARRIER in files else {
        "model": {"type": "minecraft:model", "model": "minecraft:item/amethyst_shard"}
    }
    old_model = existing["model"]
    # Se envuelve el modelo anterior, sin reemplazar ninguna ruta preexistente.
    existing["model"] = {
        "type": "minecraft:range_dispatch",
        "property": "minecraft:custom_model_data",
        "index": 0,
        "fallback": old_model,
        "entries": [
            {"threshold": CMD, "model": {"type": "minecraft:model", "model": MODEL}},
            {"threshold": CMD + 1, "model": old_model},
        ],
    }
    files[CARRIER] = (json.dumps(existing, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
