# Recursos de Slimefun para RainxEnma

Paquete combinado para **Minecraft Java 26.2**, basado en
[Slimefun Legacy RP 4.0.2](https://github.com/wickidcow/SFL_RP_Official/releases/tag/v4.0.2).

Descarga directa del ZIP listo para Minecraft:
[RainxEnma-Slimefun-26.2.zip](https://raw.githubusercontent.com/Moonlightlz/Paquete-de-recursos-de-Slime-fun/main/dist/RainxEnma-Slimefun-26.2.zip).
El botón de GitHub «Download ZIP» descarga el repositorio completo y no sirve como paquete del servidor.

## Cobertura

### Aspecto seleccionado de Eternals

Se importaron únicamente las secciones solicitadas del `eternals.zip` proporcionado
por el administrador, adaptadas a Minecraft 26.2:

| Sección del servidor | Objetos con diseño de Eternals |
|---|---:|
| Resources | 66 |
| Useful Items | 16 |
| Technical Components | 20 |
| Miscellaneous Items | 42 |
| Magical Gadgets | 27 |
| InfinityExpansion2: Gear | 6 |

El libro que entrega `/sf guide` también utiliza la textura de Eternals,
conservando su asignación de modelo `2200001`.

Son **177 objetos**. Se conservan los estados del arco, las variantes de élitros y
las decoraciones de armadura. Los modelos de las cabezas se sustituyen por los
iconos que especifica el paquete proporcionado. No se importan sus shaders,
muebles, interfaz general ni cambios globales de Minecraft.

El ZIP no contiene un diseño dedicado para `IE_INFINITY_SHIELD` ni
`IE_INFINITY_CROSSBOW`: conservan su aspecto anterior. Tampoco trae un diseño
separado para el frasco lleno de conocimiento ni para los alias vanilla de
élitros, tridente y tótem incluidos en Magical Gadgets; esos cuatro se conservan.

Los iconos y modelos de inventario/mano funcionan sin mods. Las capas de armadura
equipada del ZIP original dependen de su antigua configuración OptiFine/CIT y no
se aplican globalmente a la armadura vanilla.

Para las seis piezas de Infinity se habilitan sus números de modelo históricos
en `item-models.yml`. Esto afecta a los objetos nuevos; los objetos antiguos sin
CustomModelData no se reescriben automáticamente.

### Asignaciones de la base combinada

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
python tools/validate_pack.py
python tools/validate_integration.py
```

La construcción es determinista, no usa red y comprueba el SHA-256 de la base.
`vendor/` contiene la publicación original, `overrides/` los cambios mínimos,
`server/added-models.json` cada asignación añadida y `sources.json` la procedencia.
No se publican credenciales ni archivos privados del servidor.

`vendor/eternals-selected.zip` contiene solo los recursos originales seleccionados;
`server/eternals-selection.json` enumera sus hashes, objetos y cambios de modelos.
`tools/validate_pack.py` ejecuta las guardas originales y comprueba que las
adaptaciones de Eternals solo afectan a los objetos listados, conservando las
imágenes originales y el resto de las rutas de cada material.

Ver [CREDITS.md](CREDITS.md) y [LICENSE](LICENSE).
