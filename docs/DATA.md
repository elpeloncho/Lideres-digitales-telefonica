# Fuentes de datos de Luma Málaga

**Estado:** borrador inicial, redactado a partir de una investigación
hecha el 2026-10-13.\
**Quién lo completa:** el agente de datos, al descargar y comprobar cada
fichero.

## Cómo leer este documento

Cada afirmación lleva una marca:

-   **[visto]**: se observó directamente en la web del portal o en el
    contenido del fichero.
-   **[por verificar]**: se deduce de un listado o de fuentes
    secundarias, o no se ha podido comprobar. No se debe dar por cierto
    hasta inspeccionarlo.

Reglas que no cambian (ver `DESIGN.md`, secciones 6 y 16):

-   Las incidencias resueltas no son averías activas.
-   Los datos sintéticos no son evidencia y siempre se etiquetan.
-   No se afirma que un campo existe sin haber abierto el fichero.
-   Los originales se guardan sin modificar en `data/raw/`, con URL,
    fecha de descarga, licencia y checksum.

------------------------------------------------------------------------

## 1. GECOR: incidencias resueltas en la vía pública

Fuente principal de datos reales del MVP.

| Metadato | Valor |
|---|---|
| Nombre | Incidencias resueltas en la vía pública para el año AAAA |
| Organismo | Ayuntamiento de Málaga, portal de datos abiertos **[visto]** |
| Qué recoge | Incidencias detectadas y resueltas, gestionadas por GECOR (técnicos municipales) y Málaga Funciona (ciudadanos) **[visto]** |
| Página 2025 | https://datosabiertos.malaga.eu/dataset/incidencias-resueltas-en-la-via-publica-para-el-ano-2025 **[visto]** |
| URL directa 2025 | https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/GECOR/2025.csv **[visto]** |
| Página 2026 | https://datosabiertos.malaga.eu/dataset/incidencias-resueltas-en-la-via-publica-para-el-ano-2026 **[por verificar]**: aparece en los listados del portal, pero no se pudo abrir su ficha ni su fichero |
| Última actualización 2025 | 25/03/2025 según el catálogo datos.gob.es **[visto]**; comprobar si el CSV se ha actualizado después |
| Formato | CSV **[visto]** |
| Licencia | **[por verificar]**. El filtro de licencia del listado GECOR en el portal es `by-sa-40` (CC BY-SA 4.0). Confirmarlo en la ficha de cada año |
| Fecha de consulta | 2026-10-13 |

### Campos observados en el CSV de 2025 **[visto]**

| Campo | Contenido observado |
|---|---|
| `CODIGO` | Identificador con prefijo variable (`WWW-`, `DIST-`, `MlgF-`, `010-`, `900-`, `POL-`...) y espacios finales en algunos |
| `FECHA_REGISTRO` | Fecha y hora, formato `AAAA-MM-DD HH:MM:SS.mmm` |
| `FECHA_RESOLUCION` | Mismo formato; a veces con hora `00:00:00` (solo fecha) |
| `PRIORIDAD` | `Urgente`, `Alta`, `Media`, `Baja` (con espacios finales en algunos) |
| `DIRECCION` | Texto libre de calle y número |
| `LONGITUD`, `LATITUD` | Valores como 373309.1 y 4068574.1: **metros proyectados, no grados** |
| `TIPO` | `Categoría - Subcategoría`, por ejemplo `Farolas / Alumbrado - Farola apagada` |
| `RESPONSABLE` | Distrito, área municipal o empresa (por ejemplo `ETRALUX`, `LIMASAM`, `ENDESA`) |
| (4 columnas vacías) | Sin nombre, siempre vacías |

### Tipos de alumbrado observados **[visto]**

| `TIPO` (prefijo `Farolas / Alumbrado - `) | Categoría de Luma propuesta |
|---|---|
| Farola apagada, Todo apagado | `streetlight_failure` |
| Farola se apaga y se enciende | `streetlight_flickering` |
| Base farola deteriorada con peligro caída | `damaged_pole` |
| Cables al descubierto, Puerta farola abierta | `electrical_hazard` |
| Otros | `other` |
| `Tapas de arquetas o registros - Alumbrado` | **[por verificar]** si pertenece al ámbito; decidir y documentar |

### Problemas conocidos del fichero

1.  **Sistema de coordenadas.** Las columnas se llaman `LONGITUD` y
    `LATITUD`, pero contienen UTM. Otros años describen EPSG:4326 **[visto]**,
    así que la documentación no coincide con los datos. Probablemente
    sea EPSG:25830 (ETRS89 / UTM 30N) **[por verificar]**. Confirmar
    contrastando algunos puntos con una dirección conocida, y convertir
    con `pyproj`. Comprobar además que los puntos convertidos caen dentro
    del ámbito de Málaga.
2.  **Codificación.** El texto se vio con caracteres rotos (`SolerÃ­a`).
    Puede ser un efecto de la descarga **[por verificar]**. Detectar la
    codificación real del fichero antes de normalizar.
3.  **Comas sin escapar en `TIPO`.** Algunas filas parten el campo en dos
    y desplazan las columnas siguientes. El lector debe detectarlo y, si
    no puede repararlo, enviar la fila al registro de errores.
4.  **Espacios finales** en `CODIGO` y `PRIORIDAD`. Recortar.
5.  **Un mismo `CODIGO` con varias filas**, cada una con coordenadas
    distintas (incidencias de varios puntos). La clave de idempotencia
    no puede ser solo el código: usar `CODIGO` más las coordenadas
    redondeadas, o agrupar y documentar la decisión.
6.  **Solo incidencias resueltas.** Ninguna fila representa una avería
    abierta.
7.  **`PRIORIDAD` no es un criterio de seguridad.** En una fila observada,
    `Cables al descubierto` figuraba como `Baja` y tardó unos 36 días en
    resolverse. Es una observación puntual, pero impide tratar esa
    columna como verdad de referencia. Úsese solo como comparación.

### Reglas de importación propuestas

-   Guardar el CSV original en `data/raw/` con su SHA-256 y registrar
    URL, fecha, tamaño y licencia.
-   Filtrar por `TIPO` que empiece por `Farolas / Alumbrado` (y la
    decisión sobre arquetas de alumbrado).
-   Normalizar fechas, recortar espacios, convertir coordenadas a
    WGS84 y validar el ámbito.
-   Asignar `source_type = municipal_open_data` a los registros tal como
    vienen. Todo valor calculado (tiempo de resolución, agregados por
    distrito) es `derived` y lleva su fuente y transformación.
-   Estado de los registros importados: nunca `pending` ni `assigned`.
    Son históricos y se muestran como tales, con su fecha real.
-   Los registros con coordenadas o fechas inválidas van a una lista de
    errores y no generan marcador ni entran en los cálculos.
-   Importar dos veces el mismo fichero no debe duplicar registros.

### Usos previstos

-   Capa histórica real, claramente rotulada como histórica.
-   Distribución real de tiempos de resolución por tipo, prioridad
    municipal y distrito (`derived`). Puede servir de base empírica para
    revisar `age_reference_hours`, que hoy es un valor ilustrativo.
-   Modelo para generar datos sintéticos verosímiles (tipos, distritos y
    ubicaciones muestreados de los reales), siempre `synthetic`.

### Registro de descarga (rellenar)

| Año | Fecha de descarga | Bytes | SHA-256 | Registros originales | Válidos | Descartados | Ruta en `data/raw/` |
|---|---|---|---|---|---|---|---|
| 2025 |  |  |  |  |  |  |  |
| 2026 |  |  |  |  |  |  |  |

### Comprobaciones pendientes

-   [ ] Descargar 2025 y 2026; calcular checksums.
-   [ ] Abrir la ficha de 2026 y confirmar licencia, fecha de
        actualización y URL directa.
-   [ ] Confirmar codificación y CRS reales.
-   [ ] Contar filas de alumbrado y su distribución por tipo y distrito.
-   [ ] Comprobar si los años anteriores (2014 en adelante) usan las
        mismas columnas y el mismo CRS.
-   [ ] Decidir el tratamiento de `Tapas de arquetas - Alumbrado`.

------------------------------------------------------------------------

## 2. Capas para derivar factores de contexto

No existe una fuente directa de uso peatonal ni de sensibilidad del
entorno. Se pueden **derivar** proxies, siempre marcados como
`derived`, con su fuente y su fórmula, y nunca presentados como aforos
reales.

| Capa | Estado | Notas |
|---|---|---|
| EMT: líneas y paradas | Aparece en el portal **[visto]**; hay también una versión KML por línea y sentido **[visto]** | Licencia y formato de coordenadas **[por verificar]**. Otras capas de EMT del portal ofrecen CSV en EPSG:4326 y EPSG:25830, bajo CC BY 4.0 **[visto]** |
| Centros de salud (Agenda 21) | Shapefile de 2012, actualizado por última vez en 2017 **[visto]** | Antiguo: validar que los centros siguen existiendo |
| Capas del geoportal `callejero.malaga.eu` | Varias capas se mencionan en el portal **[visto]** | Comprobar cuáles tienen descarga y con qué licencia |
| Centros educativos, residencias, parques | **[por verificar]** | No se localizó un conjunto concreto |
| OpenStreetMap (vías peatonales, equipamientos, `highway=street_lamp`) | **[por verificar]** | Cobertura en Málaga no comprobada. Revisar la licencia ODbL y su obligación de atribución y compartir igual |
| Intensidades de tráfico | https://movilidad.malaga.eu/es/servicios/intensidades/ **[por verificar]** | Es tráfico rodado, no peatonal; fuente contextual opcional |

Para la formulación de los factores a partir de estas capas (por
ejemplo, distancia a paradas o centros de salud), documentar cada
decisión en `docs/RULES.md`. Sigue siendo experimental hasta su
validación profesional.

------------------------------------------------------------------------

## 3. Estado del alumbrado

**No se ha encontrado** inventario de luminarias ni estado de
funcionamiento publicados por el Ayuntamiento de Málaga. Esto no
demuestra que no existan.

Acciones propuestas:

-   [ ] Buscar en la API de CKAN del portal (`package_search`) con los
        términos `alumbrado`, `luminarias`, `farolas`, `puntos de luz`.
        El portal usa CKAN con datastore **[visto]**.
-   [ ] Si no hay nada, pedirlo por el canal de solicitud del portal
        (`datosabiertos@malaga.eu`) **[visto]**.
-   [ ] Mientras tanto, `NullProvider` y `SimulatedProvider` son las
        únicas implementaciones de `LightingStatusProvider`.

------------------------------------------------------------------------

## 4. Canal oficial de avisos (para la página de residentes)

GECOR es el canal real para que un ciudadano avise al Ayuntamiento, por
web o por el teléfono 010 **[visto]**. Los reportes de Luma no llegan al
Ayuntamiento. La página pública de reporte debe decirlo y remitir a
GECOR o al 010 para avisos reales, además de indicar que ante un
peligro inmediato se llame a los servicios de emergencia.

------------------------------------------------------------------------

## 5. Resumen de licencias

| Fuente | Licencia | Estado |
|---|---|---|
| GECOR incidencias resueltas | CC BY-SA 4.0 probable | **[por verificar]** |
| EMT, puntos de venta (como ejemplo de capa EMT) | CC BY 4.0 | **[visto]** |
| Resto de capas | Desconocida | **[por verificar]** |
| OpenStreetMap | ODbL | **[por verificar]** |

Si una licencia exige compartir igual (SA), cualquier dato derivado que
se publique debe ofrecerse bajo la misma licencia. Decidirlo antes de
publicar nada.

------------------------------------------------------------------------

## 6. Datos sintéticos

-   Viven en `data/synthetic/`, con `source_type = synthetic` y
    `source_name` explícito.
-   Pueden generarse a partir de las distribuciones observadas en los
    datos reales, pero siguen siendo ficticios: no se presentan como
    registros del Ayuntamiento ni se usan para calibrar pesos o sacar
    conclusiones.
-   Cualquier cifra calculada sobre ellos se rotula como "simulado".