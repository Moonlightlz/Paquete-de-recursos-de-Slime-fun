"""Comprueba la ruta exacta del Nucleo Aurico y el resto de modelos."""
from pathlib import Path
import json, zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "dist/RainxEnma-Slimefun-26.2.zip"
CARRIER = "assets/minecraft/items/amethyst_shard.json"
MODEL = "rainxauraboost:item/nucleo_aurico"
TEXTURE = "assets/rainxauraboost/textures/item/nucleo_aurico.png"

with zipfile.ZipFile(PACK) as pack, zipfile.ZipFile(ROOT / "vendor/SlimefunLegacyRP-4.0.2.zip") as base:
    assert "assets/rainxauraboost/models/item/nucleo_aurico.json" in pack.namelist()
    assert TEXTURE in pack.namelist()
    assert pack.read(TEXTURE)[:8] == b"\\x89PNG\\r\\n\\x1a\\n"
    data = json.loads(pack.read(CARRIER))
    model = data["model"]
    assert model["type"] == "minecraft:range_dispatch"
    assert model["property"] == "minecraft:custom_model_data"
    assert model["entries"][0]["threshold"] == 260310
    assert model["entries"][0]["model"]["model"] == MODEL
    assert model["entries"][1]["threshold"] == 260311
    assert model["entries"][1]["model"] == model["fallback"]
    # El modelo anterior debe quedar intacto en el fallback, incluso si venia del ZIP base.
    previous = json.loads(base.read(CARRIER))["model"] if CARRIER in base.namelist() else {
        "type": "minecraft:model", "model": "minecraft:item/amethyst_shard"
    }
    assert model["fallback"] == previous, "Se altero el modelo anterior de amatista"
print("PASS: Nucleo Aurico CMD 260310, textura y fallback original intactos")
