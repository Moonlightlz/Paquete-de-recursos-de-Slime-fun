# Recursos de Slimefun para RainxEnma

Paquete combinado para **Minecraft Java 26.2**, basado en
[Slimefun Legacy RP 4.0.2](https://github.com/wickidcow/SFL_RP_Official/releases/tag/v4.0.2).

Descarga directa del ZIP listo para Minecraft:
[RainxEnma-Slimefun-26.2.zip](https://raw.githubusercontent.com/Moonlightlz/Paquete-de-recursos-de-Slime-fun/main/dist/RainxEnma-Slimefun-26.2.zip).
El botón de GitHub «Download ZIP» descarga el repositorio completo y no sirve como paquete del servidor.

## Cobertura

Se conservan los modelos ya asignados a Slimefun y se añaden **647 asignaciones**
validadas contra el material y los modelos disponibles:

| Addon instalado | Asignaciones añadidas |
|---|---:|
| InfinityExpansion2 | 48 |
| FluffyMachines | 28 |
| LiteXpansion | 19 |
| Supreme | 34 |
| SlimeTinker | 491 |
| ElectricSpawners | 27 |

La cobertura es **parcial**: no todos los objetos de esos addons tienen texturas
publicadas. No se encontraron paquetes compatibles y redistribuibles para
DynaTech, FNAmplifications y Networks. JustEnoughGuide utiliza también iconos
nativos y cabezas. No se incluye ExoticGarden como addon del servidor.
La base combinada conserva otros espacios de nombres para mantener sus referencias.

El visualizador de Networks localizado durante la búsqueda cambia todo el cristal
y la terracota vidriada de Minecraft y depende de mods de cliente; por ese motivo
no forma parte de este paquete automático.

## Configuración del servidor

1. Respaldar `server.properties` y `plugins/Slimefun/item-models.yml`.
2. Integrar `server/item-models.yml`, preservando cualquier asignación personalizada
   posterior. Esta copia corresponde a los addons de RainxEnma del 14/10/2026.
3. Usar estas propiedades; el SHA-1 exacto está en `dist/checksums.json`:

```properties
resource-pack=https://raw.githubusercontent.com/Moonlightlz/Paquete-de-recursos-de-Slime-fun/main/dist/RainxEnma-Slimefun-26.2.zip
resource-pack-sha1=PEGAR_SHA1_DE_DIST_CHECKSUMS_JSON
require-resource-pack=true
resource-pack-prompt=Recursos de Slimefun y addons de RainxEnma
```

En producción es preferible sustituir `main` en la URL por el SHA completo del
commit publicado: así URL y checksum siempre identifican la misma versión.
La integración de RainxEnma se entrega configurada de esa manera.

4. Mantener la entrega del paquete de Slimefun Legacy en modo `external`, con
   `resource-pack.enabled=false` en `configSFLAddons.yml`: lo entrega Minecraft
   desde `server.properties`, evitando dos solicitudes.
5. Reiniciar manualmente cuando el administrador lo decida. Los jugadores deben
   aceptar la descarga; pueden activar «Paquetes de recursos del servidor» en la
   entrada del servidor del multijugador. No se necesitan OptiFine ni mods para
   los modelos incluidos.

La calavera de esqueleto del Wither incluye la transformación vanilla para
Minecraft 26.1 y posteriores. Esto corrige el icono reducido a un punto en el
inventario, conservando las rutas de modelos personalizados y la definición
original para versiones anteriores.

## Objetos que ya existían

`item-models.yml` se aplica a las plantillas y los objetos nuevos que crea Slimefun.
Los objetos antiguos sin CustomModelData no se reescriben automáticamente. Para
examinar la adopción que ofrece el núcleo instalado, el administrador puede usar:

```text
/sf doctor item-models enable-pack scan
```

Revisar ese informe y seguir la confirmación que muestre el propio comando.
Su referencia integrada cubre los IDs conocidos por ese núcleo y **puede omitir
los IDs IE_ de InfinityExpansion2**. Este repositorio no modifica IDs, recetas,
inventarios almacenados, encantamientos, traducciones ni datos persistentes de los
objetos. No se debe sustituir un objeto antiguo por un objeto vanilla renombrado.

## Reconstrucción y auditoría

```text
python tools/build_pack.py
python tools/validate_upstream.py dist/RainxEnma-Slimefun-26.2.zip
python tools/validate_integration.py
```

La construcción es determinista, no usa red y comprueba el SHA-256 de la base.
`vendor/` contiene la publicación original, `overrides/` los cambios mínimos,
`server/added-models.json` cada asignación añadida y `sources.json` la procedencia.
No se publican credenciales ni archivos privados del servidor.

Ver [CREDITS.md](CREDITS.md) y [LICENSE](LICENSE).
