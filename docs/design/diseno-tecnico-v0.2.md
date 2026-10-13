# Luma Málaga - Documento de diseño técnico (v0.2)

**Versión:** 0.2\
**Estado:** Propuesta para MVP, revisada: motor determinista de decisiones
como núcleo del sistema\
**Objetivo:** construir un prototipo web demostrable con arquitectura
modular, datos trazables, decisiones explicables y un humano que
siempre decide.

------------------------------------------------------------------------

## 1. Resumen ejecutivo

Luma Málaga es un prototipo de apoyo a la toma de decisiones para
personal técnico que gestiona incidencias de alumbrado público en
Málaga. Presenta incidencias geolocalizadas, calcula una recomendación
de actuación explicable y permite al técnico **aceptarla, modificarla o
rechazarla**, dejando constancia de la decisión.

El núcleo del sistema es un **motor determinista de decisiones**,
independiente de la API y de la interfaz. A partir de una incidencia y
de su contexto, el motor aplica en orden cuatro etapas separadas:

1.  **Reglas de seguridad:** condiciones que fijan mínimos de prioridad
    o exigen revisión humana, y que ninguna puntuación puede compensar.
2.  **Cálculo de prioridad:** índice heurístico ponderado entre 0 y 100.
3.  **Recomendación de reparación:** acción sugerida y posición en la
    cola, con su justificación.
4.  **Planificación de recursos:** asignación de técnicos y agrupación de
    trabajos. Es una etapa posterior; el MVP solo ordena la cola.

El MVP no debe afirmar que conoce el estado operativo actual de las
luminarias de Málaga. El portal municipal publica datos de incidencias
históricas/resueltas, pero eso no equivale a un inventario de
luminarias ni a un flujo de averías abiertas en tiempo real. Hasta
verificar una fuente adecuada, las incidencias activas del prototipo
serán sintéticas o reportes de residentes, y estarán etiquetadas de
forma visible. **Los datos simulados no son evidencia real**: sirven
para probar el software, no para sacar conclusiones sobre la ciudad.

Además del flujo técnico, el sistema incluye una **ventana pública para
residentes** que permite reportar situaciones. Esos reportes no entran
en la cola de trabajo hasta que un técnico o administrativo los revisa
(triaje) y confirma su prioridad.

### Propuesta de valor

Convertir una lista de incidencias en una cola de trabajo priorizada,
geográfica y explicable, en la que cada recomendación puede auditarse y
discutirse.

### Usuarios

-   **Principal:** técnico municipal o responsable operativo de
    mantenimiento del alumbrado público.
-   **Secundario:** responsable de operaciones, que revisa prioridades,
    asignaciones, decisiones humanas y actividad.
-   **Terciario:** residente, que solo accede al formulario de reporte y
    no ve la cola ni datos operativos.

### Contexto urbano del MVP

Centro urbano de Málaga como área de demostración. La selección del
centro es una decisión de alcance del prototipo, no una afirmación de
que tenga más averías que otras zonas.

### Principios del producto

1.  **El humano decide:** el sistema recomienda; el técnico acepta,
    modifica o rechaza, y su decisión queda registrada con motivo.
2.  **Seguridad primero:** las reglas de seguridad se evalúan antes que
    la puntuación y no pueden compensarse con ella.
3.  **Determinismo:** la misma entrada y la misma configuración producen
    siempre la misma salida.
4.  **Trazabilidad:** cada registro indica si procede de una fuente
    real, si se ha transformado o si es sintético; cada decisión indica
    qué versión del motor y qué reglas la produjeron.
5.  **No fingir tiempo real:** los datos históricos no se presentarán
    como estado actual.
6.  **Datos simulados no son evidencia:** nada calculado sobre datos
    sintéticos se presenta como resultado real ni se usa para calibrar
    pesos.
7.  **Explicabilidad:** se muestran los factores, las reglas activadas y
    los datos ausentes que producen cada recomendación.
8.  **Datos ausentes visibles:** un dato que falta nunca se convierte en
    cero de forma silenciosa.
9.  **Separación de responsabilidades:** interfaz, API, persistencia y
    motor de decisiones separados; el motor no depende de ninguno de
    ellos.
10. **Degradación elegante:** la aplicación puede ejecutarse con datos
    sintéticos si una fuente municipal no está disponible.
11. **Privacidad y seguridad:** no incluir credenciales, tokens, datos
    personales ni secretos en el repositorio; el formulario de
    residentes no recoge datos personales.
12. **Desarrollo remoto seguro:** instalar dependencias dentro del
    proyecto y evitar cambios innecesarios en el sistema de la torre.

------------------------------------------------------------------------

## 2. Alcance del MVP

### 2.1 Incluido

-   Motor determinista de decisiones como paquete independiente, con
    reglas de seguridad, cálculo de prioridad y recomendación de
    reparación configurables y versionadas.
-   Aplicación web navegable y adaptable a escritorio y móvil.
-   Mapa interactivo centrado en Málaga con marcadores por prioridad.
-   Cola de recomendaciones ordenada, con explicación de por qué una
    incidencia va antes que otra.
-   Vista de detalle con factores, reglas activadas, datos ausentes y
    recomendación.
-   Aceptar, modificar o rechazar la recomendación, con motivo
    obligatorio cuando se modifica o rechaza.
-   Asignación a un técnico ficticio y cambio de estado.
-   Historial de acciones y registro de decisiones humanas.
-   Ventana pública de reporte para residentes y bandeja de triaje para
    el personal.
-   Persistencia en ficheros JSON con escrituras seguras.
-   Datos sintéticos claramente identificados.
-   Adaptador de importación de datos municipales si el formato y la
    licencia lo permiten.
-   Interfaz `LightingStatusProvider` para un futuro estado del
    alumbrado, con implementación nula y simulada.
-   API REST documentada.
-   Pruebas del motor (determinismo, reglas de seguridad, datos
    incompletos, conflictos, trazabilidad), de la persistencia y de los
    endpoints.
-   Indicadores y mensajes visibles sobre las limitaciones de los datos
    y el carácter experimental de las puntuaciones.

### 2.2 Fuera del alcance inicial

-   Planificación avanzada de recursos y rutas (se evalúa al final del
    plan).
-   Aprendizaje automático clásico (se evalúa al final del plan).
-   LLM: fase opcional posterior, nunca requisito del MVP.
-   Control real de luminarias, o lectura real de su estado, mientras no
    exista una fuente verificada.
-   Integración con sistemas internos del Ayuntamiento o contratistas.
-   Autenticación corporativa.
-   Aplicación móvil nativa.
-   Afirmaciones de impacto causal sobre seguridad ciudadana.
-   Inventario completo de farolas sin fuente verificada.
-   Subida de fotos o datos personales en los reportes de residentes.
-   Despliegue público en Internet.

### 2.3 Criterios de éxito del MVP

1.  La aplicación arranca siguiendo el README en un entorno limpio.
2.  El motor de decisiones se ejecuta y se prueba sin API ni interfaz.
3.  La misma incidencia y la misma configuración producen siempre la
    misma recomendación.
4.  Una regla de seguridad activada no puede ser compensada por una
    puntuación baja.
5.  La interfaz muestra por qué una incidencia se recomienda antes que
    otra.
6.  Aceptar, modificar o rechazar actualiza el estado en la API y en la
    interfaz, y queda registrado con el estado del motor en ese
    momento.
7.  Reiniciar la aplicación conserva incidencias, historial y decisiones.
8.  Un reporte de residente no entra en la cola sin revisión humana.
9.  Las incidencias sintéticas se distinguen claramente de los datos
    municipales y no se presentan como evidencia.
10. La API no necesita un proveedor de IA externo para funcionar.
11. Las pruebas principales pasan y los errores de datos se registran de
    forma comprensible.

------------------------------------------------------------------------

## 3. Usuarios, tareas y casos de uso

### UC-01 --- Identificar la siguiente reparación

**Actor:** técnico municipal.\
**Precondición:** existen incidencias cargadas.\
**Flujo:** 1. El técnico abre Inicio. 2. Consulta el resumen y el mapa.
3. Revisa la cola de recomendaciones. 4. Abre una incidencia. 5.
Consulta ubicación, antigüedad, factores, reglas activadas, datos
ausentes y la explicación de la recomendación. 6. Acepta, modifica o
rechaza la recomendación. 7. La aplicación registra la decisión.

**Resultado esperado:** el usuario entiende por qué una incidencia
aparece antes que otra y su decisión queda auditada.

### UC-02 --- Filtrar incidencias por zona y prioridad

**Actor:** técnico municipal.\
**Flujo:** abre Mapa, filtra por prioridad, estado, procedencia o
revisión urgente, selecciona un marcador y navega al detalle.

### UC-03 --- Gestionar una alerta

**Actor:** técnico o responsable de operaciones.\
**Flujo:** abre Alertas, consulta el motivo (regla activada o prioridad
alta), entra en el detalle y toma una decisión.

### UC-04 --- Revisar actividad y decisiones

**Actor:** responsable de operaciones.\
**Flujo:** abre Historial y revisa creación, triaje, asignación, cambios
de estado, decisiones humanas y excepciones a reglas de seguridad.

### UC-05 --- Ajustar el umbral de prioridad

**Actor:** responsable de operaciones.\
**Flujo:** cambia el umbral o el modo de ordenación. La interfaz pide a
la API recalcular; no calcula nada por su cuenta.

### UC-06 --- Reportar una situación

**Actor:** residente.\
**Flujo:** abre la página pública de reporte, indica categoría,
ubicación en el mapa y una descripción breve, y envía. Recibe una
confirmación genérica con una referencia opaca. No ve la cola ni otros
reportes.

### UC-07 --- Triar un reporte de residente

**Actor:** técnico o administrativo.\
**Flujo:** abre la bandeja de triaje, revisa el reporte con la
propuesta provisional del motor, y lo acepta (con prioridad
confirmada), lo marca como duplicado o lo rechaza con motivo. Solo los
aceptados pasan a la cola.

### UC-08 --- Discrepar de una recomendación

**Actor:** técnico.\
**Flujo:** en el detalle elige "Modificar" o "Rechazar", indica la
acción o prioridad que considera correcta y el motivo. Si la decisión
queda por debajo de un mínimo de seguridad, se marca como excepción a
regla de seguridad y requiere motivo explícito.

------------------------------------------------------------------------

## 4. Arquitectura propuesta

### 4.1 Arquitectura lógica

El motor de decisiones es el componente central. Todo depende de él;
él no depende de nada.

``` text
┌───────────────────────────────────────────────────────────┐
│ Frontend: React + TypeScript + Vite                       │
│  Zona técnica: Inicio · Mapa · Cola · Detalle · Alertas   │
│                Historial · Triaje · Perfil/Metodología    │
│  Zona pública: Reportar (sin acceso a datos operativos)   │
└───────────────────────────┬───────────────────────────────┘
                            │ HTTP / JSON
                            ▼
┌───────────────────────────────────────────────────────────┐
│ API: FastAPI                                              │
│  Endpoints · Validación Pydantic · Errores coherentes     │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Servicios: incidencias · triaje · decisiones humanas ·    │
│ auditoría                                                 │
└───────┬─────────────────────────────────────┬─────────────┘
        │ llama (funciones puras)             │ lee/escribe
        ▼                                     ▼
┌─────────────────────────────────┐   ┌─────────────────────┐
│ MOTOR DE DECISIONES (núcleo)    │   │ Persistencia JSON   │
│ 1 Reglas de seguridad           │   │ incidents.json      │
│ 2 Cálculo de prioridad          │   │ history.jsonl       │
│ 3 Recomendación de reparación   │   │ decisions.jsonl     │
│ 4 Planificación de recursos     │   │ escritura atómica   │
│   (fase posterior)              │   └─────────┬───────────┘
│ Sin red, sin disco, sin reloj   │             │
└─────────────────────────────────┘             ▼
                                      ┌─────────────────────┐
┌─────────────────────────────────┐   │ Fuentes externas    │
│ Proveedores de contexto         │   │ Datos abiertos      │
│ LightingStatusProvider          │   │ Málaga · OSM        │
│ (nulo / simulado)               │   │ Datos sintéticos    │
└─────────────────────────────────┘   └─────────────────────┘

Opcional, fase posterior, no bloqueante:
Servicios → IncidentAssistant → proveedor LLM local o remoto
(solo lectura; nunca modifica reglas, prioridades ni decisiones)
```

**Reglas de dependencia:**

-   `engine/` no importa FastAPI, el repositorio, el sistema de ficheros,
    la red ni el reloj. Puede usar Pydantic para sus tipos.
-   La hora de evaluación (`evaluated_at`) se pasa como parámetro; el
    motor nunca llama a `datetime.now()`.
-   Los servicios obtienen datos del repositorio y de los proveedores,
    llaman al motor y persisten el resultado. La API solo traduce HTTP.
-   El frontend nunca recalcula la prioridad ni las reglas: muestra lo
    que devuelve la API.

### 4.2 Estructura del repositorio

``` text
Lideres-digitales-telefonica/        # carpeta del proyecto
├── README.md
├── DESIGN.md
├── .gitignore
├── .env.example
├── data/
│   ├── raw/                 # descargas originales; no editar manualmente
│   ├── processed/           # datos normalizados
│   ├── synthetic/           # incidencias ficticias, siempre etiquetadas
│   └── store/               # estado de ejecución (JSON); fuera de git
├── docs/
│   ├── DATA_SOURCES.md
│   ├── API.md
│   ├── DECISIONS.md
│   └── RULES.md             # catálogo de reglas, pesos y su estado de validación
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── engine/                  # NÚCLEO, sin dependencias de API/IO
│   │   │   ├── models.py            # entradas y salidas del motor
│   │   │   ├── config.py            # pesos, umbrales, reglas; versionado
│   │   │   ├── safety_rules.py      # etapa 1
│   │   │   ├── priority.py          # etapa 2
│   │   │   ├── recommendation.py    # etapa 3 + orden de cola + comparación
│   │   │   ├── resource_planning.py # etapa 4 (fase posterior)
│   │   │   └── decide.py            # orquesta las etapas
│   │   ├── providers/
│   │   │   └── lighting_status.py   # nulo y simulado
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── incidents.py
│   │   │   ├── queue.py
│   │   │   ├── decisions.py
│   │   │   ├── triage.py
│   │   │   ├── public_reports.py
│   │   │   ├── alerts.py
│   │   │   └── meta.py
│   │   ├── schemas/
│   │   │   ├── incident.py
│   │   │   └── decision.py
│   │   ├── services/
│   │   │   ├── incident_service.py
│   │   │   ├── decision_service.py
│   │   │   ├── triage_service.py
│   │   │   └── audit_service.py
│   │   ├── repositories/
│   │   │   └── json_store.py        # única vía de escritura a disco
│   │   ├── ingestion/
│   │   │   ├── municipal_csv.py
│   │   │   └── normalize.py
│   │   └── data/
│   │       └── seed.py
│   └── tests/
│       ├── engine/
│       │   ├── test_determinism.py
│       │   ├── test_safety_rules.py
│       │   ├── test_priority.py
│       │   ├── test_incomplete_data.py
│       │   ├── test_rule_conflicts.py
│       │   └── test_traceability.py
│       ├── test_json_store.py
│       ├── test_health.py
│       └── test_api_*.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── api/client.ts
    │   ├── types/
    │   ├── components/      # AppShell, MapView, QueueList, PriorityBadge,
    │   │                    # DecisionPanel, WhyBefore, RuleBadge, SimulatedTag
    │   ├── pages/           # técnicas + public/ReportPage
    │   └── styles/
    └── tests/
```

**Migración desde la versión 0.1:** `backend/app/services/prioritization.py`
pasa a `backend/app/engine/priority.py` y sus pruebas a
`backend/tests/engine/`. La estructura es una guía modular. Para una
demo puede simplificarse, pero no se deben mezclar las reglas de
seguridad, la fórmula de puntuación, la importación de datos y los
componentes visuales en un único archivo.

------------------------------------------------------------------------

## 5. Dependencias y versiones

Las versiones exactas se fijan en los archivos de bloqueo una vez
comprobadas en la torre. No instalar versiones arbitrarias sin verificar
compatibilidad.

### 5.1 Herramientas del sistema

-   Git.
-   Python 3.12 (gestionado con `uv` dentro del proyecto).
-   Node.js compatible con la versión elegida de Vite, y npm.
-   Un navegador moderno.

No se requiere CUDA, PyTorch, TensorFlow, Docker, PostGIS ni una GPU
para el MVP.

### 5.2 Backend Python

Dependencias directas iniciales:

-   `fastapi`: API REST.
-   `uvicorn[standard]`: servidor ASGI de desarrollo.
-   `pydantic-settings`: configuración y variables de entorno.
-   `pytest`: pruebas.
-   `httpx`: cliente de pruebas para FastAPI.
-   `ruff`: linting y formato.

Opcionales, no instalar hasta necesitarlos:

-   `pandas`: lectura y transformación de CSV complejos.
-   `geopandas` y `shapely`: operaciones geoespaciales reales.
-   `filelock`: bloqueo entre procesos para el almacén JSON, solo si se
    usa más de un proceso.
-   Fase de evaluación: `ortools` u otra biblioteca de optimización, y
    `scikit-learn`, únicamente si se decide evaluar planificación
    avanzada o aprendizaje automático clásico.

Para un CSV sencillo, usar la biblioteca estándar es suficiente. No
introducir GeoPandas solo para representar puntos en un mapa. El motor
de decisiones usa solo la biblioteca estándar y Pydantic.

### 5.3 Frontend

Dependencias directas iniciales:

-   `react` y `react-dom`.
-   `vite`.
-   `typescript`.
-   `leaflet` y `react-leaflet`.
-   `react-router-dom`.
-   `lucide-react` para iconos.
-   `zod` opcional para validar respuestas en el cliente.

Dependencias de desarrollo:

-   `@vitejs/plugin-react`.
-   `vitest`.
-   `jsdom`.
-   `@testing-library/react`.
-   `@testing-library/jest-dom`.
-   `eslint` y configuración compatible con TypeScript.

El mapa necesita CSS de Leaflet y una altura explícita en el contenedor.
Las teselas de OpenStreetMap requieren conexión de red y atribución
visible.

### 5.4 Persistencia

Decisión cerrada: **ficheros JSON controlados por el backend** (ver
sección 8). No usar almacenamiento del navegador como fuente de verdad.
Si el volumen o la concurrencia lo exigieran más adelante, la capa de
repositorio permite sustituir el almacén por SQLite sin tocar el motor.

------------------------------------------------------------------------

## 6. Datos: fuentes, procedencia y pipeline

### 6.0 Tipos de dato y qué se puede afirmar de cada uno

El sistema maneja cuatro tipos de dato. Cada registro lleva su tipo y la
interfaz lo muestra.

  ------------------------------------------------------------------------------
  `source_type`           Qué es                      Qué NO se puede afirmar
  ----------------------- --------------------------- --------------------------
  `municipal_open_data`   Registro histórico          Que sea una avería abierta
                          publicado por el            ni el estado actual de una
                          Ayuntamiento, con su        luminaria.
                          fecha y periodo reales.     

  `derived`               Valor calculado a partir de Que sea un dato
                          una fuente identificada     observado por el
                          (agregados, conteos,        Ayuntamiento. Debe indicar
                          normalizaciones).           fuente y transformación.

  `synthetic`             Valor ficticio creado para  Que sea evidencia real.
                          probar el software.         No sirve para estadísticas,
                                                      calibrar pesos ni
                                                      conclusiones sobre la
                                                      ciudad.

  `resident_report`       Aviso de un residente, sin  Que esté verificado. Hasta
                          verificar.                  el triaje es una señal no
                                                      confirmada.
  ------------------------------------------------------------------------------

### 6.1 Fuentes municipales a investigar

1.  **Incidencias resueltas en la vía pública --- año 2026**\
    Portal de datos abiertos de Málaga:\
    https://datosabiertos.malaga.eu/dataset/incidencias-resueltas-en-la-via-publica-para-el-ano-2026

2.  **Portal de datos abiertos del Ayuntamiento de Málaga**\
    https://datosabiertos.malaga.eu/

3.  **Intensidades de tráfico de Málaga** --- fuente contextual
    opcional, no necesaria para el MVP de alumbrado:\
    https://movilidad.malaga.eu/es/servicios/intensidades/

Antes de consumir una fuente hay que verificar: URL directa del recurso
descargable, formato, fecha de actualización, sistema de coordenadas,
licencia, diccionario de campos y si las coordenadas corresponden a la
incidencia o a otra entidad.

**Limitación fundamental:** incidencias resueltas no equivalen a averías
de alumbrado pendientes. No se deben convertir automáticamente en
incidencias activas.

### 6.2 Pipeline de datos

``` text
Descarga de fuente municipal
        │
        ▼
Guardar original sin modificaciones en data/raw/
        │
        ▼
Registrar URL, fecha de descarga, licencia y checksum
        │
        ▼
Inspeccionar columnas, formato y CRS
        │
        ▼
Normalizar nombres, fechas, coordenadas y categorías
        │
        ▼
Validar registros y separar errores
        │
        ▼
Asignar procedencia y tipo de dato
        │
        ├── histórico municipal verificado
        ├── dato transformado derivado de fuente real
        └── dato sintético para demostración
        │
        ▼
Guardar resultado en data/processed/
        │
        ▼
API → servicios → motor de decisiones → frontend/mapa
```

### 6.3 Metadatos mínimos por conjunto de datos

Guardar en `docs/DATA_SOURCES.md`:

-   Nombre de la fuente.
-   URL de la página y URL directa de descarga.
-   Organismo responsable.
-   Fecha de consulta/descarga.
-   Fecha o periodo al que se refieren los datos.
-   Licencia y condiciones de reutilización.
-   Formato y sistema de coordenadas.
-   Campos utilizados y transformación aplicada.
-   Limitaciones conocidas.
-   Número de registros originales, válidos y descartados.

### 6.4 Contrato de normalización

Todos los registros que lleguen al backend deben normalizarse a un
esquema común. Ejemplo:

``` json
{
  "id": "INC-001",
  "title": "Luminaria apagada",
  "category": "streetlight_failure",
  "description": "Incidencia de demostración",
  "latitude": 36.7213,
  "longitude": -4.4214,
  "status": "pending",
  "source_type": "synthetic",
  "source_name": "demo_seed",
  "verification": "not_applicable",
  "observed_at": null,
  "created_at": "2026-10-13T08:00:00Z",
  "age_hours": 26,
  "context": {
    "pedestrian_use": 95,
    "sensitive_location": 92
  },
  "context_provenance": {
    "pedestrian_use": "synthetic",
    "sensitive_location": "synthetic"
  }
}
```

Los valores de ejemplo son ficticios y sirven únicamente para definir el
contrato. `age_hours`, los factores contextuales y las fechas de ejemplo
no deben presentarse como datos observados del Ayuntamiento.

Reglas del contrato:

-   `context.*` admite `null`: un factor ausente es `null`, nunca `0`.
-   `context_provenance` indica el origen de cada factor: `synthetic`,
    `derived`, `municipal`, `technician` (introducido o confirmado por un
    técnico en el triaje) o `unknown`.
-   `category` admite `streetlight_failure`, `streetlight_flickering`,
    `damaged_pole`, `electrical_hazard` y `other`.
-   `verification` toma `unverified`, `verified`, `rejected` o
    `not_applicable`. Los `resident_report` empiezan en `unverified`.
-   Los estados operativos son `reported` (reporte pendiente de triaje),
    `pending`, `assigned`, `resolved` y `rejected`. El estado de una
    incidencia sintética no representa el estado real de una luminaria.

### 6.5 Validaciones

-   Latitud y longitud deben ser numéricas y estar dentro de rangos
    geográficos válidos.
-   Los puntos deben quedar dentro del ámbito de Málaga definido para la
    aplicación, salvo que una fuente documentada justifique otra cosa.
-   Las fechas inválidas deben registrarse y excluirse de cálculos
    dependientes de tiempo.
-   Los registros sin coordenadas no aparecen en el mapa, pero pueden
    quedar en una lista de errores.
-   Los identificadores deben ser únicos.
-   La importación debe ser idempotente: importar dos veces el mismo
    fichero no debe duplicar todos sus registros.
-   Nunca asignar `municipal_open_data` a datos sintéticos.
-   Los datos históricos deben conservar su fecha real de observación o
    periodo de referencia.

### 6.6 Datos simulados y evidencia

-   Ningún KPI, gráfico o resumen calculado sobre datos sintéticos se
    presenta sin la etiqueta "simulado". Los totales se desglosan por
    `source_type`.
-   Los pesos, umbrales y reglas no se calibran con datos sintéticos.
-   El motor expone `is_simulated` en su salida; la interfaz lo muestra
    junto a la recomendación.
-   Las alertas generadas a partir de datos sintéticos se rotulan como
    ejercicio de demostración.
-   Un dato derivado conserva la referencia a su fuente y a la
    transformación aplicada.

### 6.7 Reportes de residentes

-   El formulario recoge categoría, coordenadas (seleccionadas en el
    mapa, dentro del ámbito de la demo) y una descripción de 10 a 500
    caracteres. No recoge nombre, teléfono, correo ni fotos.
-   El texto se trata como dato no confiable: se recorta, se limita su
    longitud y se escapa al mostrarlo. Nunca se interpreta como
    instrucción.
-   El endpoint público solo permite crear reportes. No devuelve datos de
    otros reportes ni de la cola; responde con una referencia opaca.
-   Se aplica un límite de frecuencia sencillo por origen para evitar
    abuso.
-   Un reporte nace como `reported` / `unverified`. Sus factores de
    contexto empiezan en `null` hasta que el triaje los confirme.
-   Si hubiera un `LightingStatusProvider` con datos reales, su
    respuesta es una señal adicional de verificación, nunca una
    resolución automática (ver 7.3).

------------------------------------------------------------------------

## 7. Motor de decisiones

### 7.1 Objetivo y propiedades

Ayudar a decidir qué revisar o reparar primero, no sustituir el criterio
del técnico ni emitir una evaluación oficial de riesgo.

Propiedades obligatorias del motor:

-   **Determinista:** misma entrada + misma configuración + mismo
    `evaluated_at` = misma salida, byte a byte al serializarla. Sin
    aleatoriedad, sin reloj interno, sin dependencia del orden de
    evaluación de las reglas ni del orden de las claves.
-   **Puro:** no lee ni escribe ficheros, no hace red, no importa la
    API.
-   **Versionado:** cada salida incluye `engine_version` y
    `config_version`.
-   **Explicable:** cada salida enumera factores, reglas activadas,
    datos ausentes y advertencias.
-   **Seguro por construcción:** las reglas de seguridad solo pueden
    subir la prioridad o exigir revisión; nunca bajarla.

### 7.2 Etapas

``` text
Entrada (incidencia + contexto + estado del alumbrado opcional + evaluated_at)
   │
   ▼
1. Reglas de seguridad ──► suelo de prioridad, revisión urgente, ruta
   │
   ▼
2. Cálculo de prioridad ──► puntuación 0-100, desglose, datos ausentes
   │
   ▼
   prioridad final = máx(prioridad por puntuación, suelo de seguridad)
   │
   ▼
3. Recomendación de reparación ──► acción, justificación, clave de cola
   │
   ▼
4. Planificación de recursos (fase posterior) ──► sugerencia de asignación
   │
   ▼
Salida: Decision  →  el técnico acepta / modifica / rechaza
```

La etapa 4 solo consume la salida de las tres primeras. No puede
cambiar reglas de seguridad ni prioridades.

### 7.3 Etapa 1: reglas de seguridad

Cada regla es una función determinista con identificador estable,
condición y efecto. Efectos posibles:

-   `priority_floor`: prioridad mínima (`low`, `medium` o `high`).
-   `urgent_review`: marca la incidencia para revisión humana
    inmediata.
-   `route`: `queue` (por defecto) o `triage` (exige validación humana
    antes de entrar en la cola).
-   `proposed_action`: acción que la regla propone (ver 7.5).

Catálogo inicial (ilustrativo y **experimental**, pendiente de
validación; ver sección 16):

  --------------------------------------------------------------------------
  ID       Condición                          Efecto
  -------- ---------------------------------- ------------------------------
  SR-01    Categoría `electrical_hazard` o    Suelo `high`, revisión urgente,
           `damaged_pole`                     acción `inspect_urgently`.

  SR-02    `sensitive_location` ≥ 90 y        Suelo `high`.
           categoría `streetlight_failure`    

  SR-03    Sin coordenadas válidas, o sin     Ruta `triage`, acción
           ningún factor de prioridad         `needs_triage`. No genera
           disponible                         puntuación.

  SR-04    Fuente `resident_report` sin       Ruta `triage`. No se resuelve,
           verificar                          descarta ni prioriza como
                                              baja de forma automática.

  SR-05    El estado del alumbrado            Ruta `triage`, marca
           contradice el reporte (p. ej.      `data_conflict`. No se
           luminaria "encendida" frente a     descarta el reporte.
           reporte de "apagada")              
  --------------------------------------------------------------------------

Los umbrales de las reglas (por ejemplo el 90 de SR-02) están en la
configuración versionada, no en el código de la regla.

**Invariantes del motor** (comprobados por pruebas):

-   I-01: ninguna regla ni configuración puede dejar una prioridad final
    por debajo del suelo de seguridad activo.
-   I-02: un dato ausente nunca se trata como cero.
-   I-03: un dato simulado nunca se presenta como real.
-   I-04: un `resident_report` sin verificar nunca llega a `resolved` ni
    a `rejected` sin una decisión humana.

**Estado del alumbrado.** El motor acepta como entrada opcional un
`lighting_status` (`on`, `off`, `unknown`) con su procedencia. Mientras
no exista una fuente verificada, `NullProvider` devuelve `unknown` y
`SimulatedProvider` devuelve valores sintéticos etiquetados. Con datos
reales, este dato serviría para verificar reportes y, si se valida, para
automatizar parte del triaje; no se asume que exista.

### 7.4 Etapa 2: cálculo de prioridad

Índice heurístico entre 0 y 100:

``` text
score = 0.40 × pedestrian_use
      + 0.20 × age_score
      + 0.40 × sensitive_location

age_score = min(age_hours / age_reference_hours, 1) × 100
```

Valor inicial de `age_reference_hours`: 30 horas. Pesos, referencia y
umbrales son parámetros ilustrativos, no criterios oficiales.

Clasificación por puntuación (configurable):

-   Alta: igual o superior a 75.
-   Media: entre 55 y 74.99.
-   Baja: inferior a 55.

**Datos incompletos.** Si falta un factor, no se sustituye por cero. El
motor calcula con los factores disponibles, reparte sus pesos
proporcionalmente, marca `complete: false`, lista el factor en
`missing_factors` y añade una advertencia. Si no hay ningún factor,
`score` es `null` y no hay prioridad por puntuación. Los valores fuera
de rango se rechazan con error; no se recortan.

**Prioridad final:** `final_priority = máx(score_priority,
priority_floor)`. Ambas se devuelven por separado para que la
explicación diga qué parte viene de la puntuación y cuál de una regla.

No es una probabilidad de accidente ni predice delitos, lesiones o
fallos futuros.

### 7.5 Etapa 3: recomendación de reparación

Acciones posibles, por orden de precedencia (de mayor a menor):

  -----------------------------------------------------------------------
  Acción              Cuándo se propone (por defecto)
  ------------------- ---------------------------------------------------
  `inspect_urgently`  Hay revisión urgente (p. ej. SR-01).

  `needs_triage`      La ruta es `triage` y el estado es `reported`.

  `verify_on_site`    Datos incompletos, `data_conflict` o fuente sin
                      verificar, ya dentro de la cola.

  `repair_priority`   Prioridad final alta, datos suficientes.

  `repair_scheduled`  Prioridad final media o baja, datos suficientes.
  -----------------------------------------------------------------------

La recomendación incluye acción, justificación en lenguaje claro
generada por plantillas a partir de las reglas y factores reales, y la
clave de ordenación de la cola.

**Orden de la cola** (determinista, con desempate por `id`):

``` text
(urgent_review desc, rango de final_priority desc, score desc,
 age_hours desc, id asc)
```

Una puntuación `null` se ordena después de las demás con su misma
prioridad.

**Por qué A antes que B.** El motor expone `compare(a, b)`, que
devuelve el primer criterio de la clave en que difieren y los valores
de ambos, por ejemplo: "A tiene revisión urgente por SR-01; B no". La
interfaz muestra ese resultado tal cual.

### 7.6 Conflictos

Las reglas de seguridad solo pueden endurecer, de modo que casi nunca
chocan. Los conflictos que sí pueden darse se resuelven así, siempre de
forma determinista y registrándolos en `conflicts`:

-   **Suelo frente a puntuación:** gana el suelo (I-01).
-   **Varias reglas con suelos distintos:** se toma el más alto.
-   **Varias acciones propuestas:** gana la de mayor precedencia de la
    tabla 7.5; las demás quedan listadas como conflicto resuelto.
-   **Ruta `triage` frente a `urgent_review`:** se aplican ambas; el
    elemento entra en la bandeja de triaje en primera posición y marcado
    como urgente. Nunca se salta la validación humana.
-   **Dato frente a dato (p. ej. alumbrado y reporte):** el motor no
    elige; marca `data_conflict` y envía a triaje.

El resultado no depende del orden en que se evalúen las reglas: se
ordenan por ID antes de combinarlas.

### 7.7 Etapa 4: planificación de recursos

Fase posterior. Entrada: recomendaciones de la cola, técnicos ficticios,
capacidad por jornada y zona. Salida: sugerencia de asignación y
agrupación por zona, siempre como sugerencia que el técnico confirma. En
el MVP no hay optimización: la cola ordenada y la asignación manual
cubren la necesidad. Planificación avanzada o aprendizaje automático
clásico se evalúan solo al final del plan (sección 14) y tomarían el
motor determinista como referencia (*baseline*) con la que compararse.

### 7.8 Contrato de salida del motor

``` json
{
  "incident_id": "INC-001",
  "engine_version": "0.2.0",
  "config_version": "2026-10-13-default",
  "evaluated_at": "2026-10-13T10:00:00Z",
  "is_simulated": true,
  "is_estimate": true,
  "inputs": {
    "pedestrian_use": 95,
    "age_hours": 26,
    "sensitive_location": 92,
    "lighting_status": {"state": "unknown", "source": "null_provider"}
  },
  "safety": {
    "triggered_rules": [
      {
        "id": "SR-02",
        "reason": "Entorno de importancia 92/100 con luminaria apagada.",
        "effect": {"priority_floor": "high"}
      }
    ],
    "priority_floor": "high",
    "urgent_review": false,
    "route": "queue",
    "conflicts": []
  },
  "priority": {
    "score": 92.13,
    "score_priority": "high",
    "final_priority": "high",
    "complete": true,
    "missing_factors": [],
    "weights": {"pedestrian_use": 0.4, "age": 0.2, "sensitive_location": 0.4},
    "contributions": {"pedestrian_use": 38.0, "age": 17.33, "sensitive_location": 36.8},
    "warnings": []
  },
  "recommendation": {
    "action": "repair_priority",
    "rationale": [
      "Prioridad alta por la puntuación (92/100).",
      "La regla SR-02 fija un mínimo de prioridad alta."
    ],
    "queue_key": [false, 3, 92.13, 26, "INC-001"]
  },
  "explanation": [
    "Uso peatonal estimado elevado (95/100): aporta 38.0 puntos.",
    "Importancia del entorno elevada (92/100): aporta 36.8 puntos.",
    "Antigüedad elevada (87/100): aporta 17.3 puntos."
  ],
  "resource_plan": null
}
```

Los datos de ejemplo son ficticios. `queue_key` es un detalle interno de
ordenación que la API puede omitir.

### 7.9 Decisión humana

Cada vez que el técnico decide, se guarda un registro autocontenido:

``` json
{
  "id": "DEC-0001",
  "incident_id": "INC-001",
  "verdict": "modified",
  "final_action": "repair_scheduled",
  "final_priority": "medium",
  "reason": "La zona está cerrada al tráfico peatonal por obras.",
  "safety_override": false,
  "decided_by": "tecnico_demo",
  "decided_at": "2026-10-13T10:05:00Z",
  "engine_snapshot": { "...": "salida completa del motor que vio el técnico" }
}
```

Reglas:

-   `verdict` es `accepted`, `modified` o `rejected`.
-   `reason` es obligatorio si `verdict` no es `accepted`.
-   Si la decisión deja la prioridad por debajo del suelo de seguridad o
    descarta una revisión urgente, `safety_override` es `true`, el
    motivo es obligatorio y la excepción aparece destacada en el
    historial. El humano puede discrepar, pero no en silencio.
-   El motor no se modifica con la decisión humana: la salida del motor
    y la decisión del técnico se guardan por separado.
-   El `engine_snapshot` permite reproducir exactamente lo que el
    técnico vio y volver a ejecutar el motor con el mismo resultado.

------------------------------------------------------------------------

## 8. Persistencia JSON

### 8.1 Qué se guarda y dónde

Directorio `data/store/` (fuera de git; las semillas viven en
`data/synthetic/`):

  ------------------------------------------------------------------------
  Fichero            Formato            Contenido
  ------------------ ------------------ ----------------------------------
  `incidents.json`   JSON, reescrito    Estado actual de las incidencias,
                     de forma atómica   con `schema_version` y `revision`.

  `history.jsonl`    JSON Lines, solo   Eventos: creación, reporte, triaje,
                     añadir             cambio de estado, asignación,
                                        importación.

  `decisions.jsonl`  JSON Lines, solo   Decisiones humanas con la
                     añadir             instantánea del motor que las
                                        originó.
  ------------------------------------------------------------------------

La salida del motor no se guarda como estado: se recalcula de forma
determinista cuando hace falta. Solo se persiste la instantánea
asociada a una decisión humana.

### 8.2 Escrituras seguras

-   **Un único punto de escritura:** `repositories/json_store.py`. Ningún
    otro módulo toca los ficheros.
-   **Escritura atómica** de `incidents.json`: escribir en un fichero
    temporal del mismo directorio, `flush` y `fsync`, y después
    `os.replace` sobre el original. Un fallo a mitad de escritura deja
    el fichero anterior intacto.
-   **Exclusión mutua:** un bloqueo por operación de escritura. El MVP
    se ejecuta con un único proceso de `uvicorn`; si se usara más de
    uno, se añade bloqueo entre procesos.
-   **Registros de solo añadir:** `history.jsonl` y `decisions.jsonl`
    nunca se reescriben. Cada línea lleva un número de secuencia
    creciente y se fuerza a disco tras escribirla.
-   **Orden de una operación:** 1) validar, 2) añadir el evento a
    `history.jsonl`, 3) reemplazar `incidents.json` con la nueva
    `revision`. Al arrancar se comprueba que `revision` y la última
    secuencia del historial son coherentes; si no, se informa del
    desajuste en lugar de continuar en silencio.
-   **Fichero corrupto:** la aplicación se niega a arrancar con un error
    claro y no sobrescribe el fichero. Se conserva una copia de
    seguridad `.bak` de la última versión válida.
-   **Validación al leer y al escribir** con los esquemas Pydantic;
    `schema_version` permite migraciones futuras.
-   **Idempotencia:** importar dos veces la misma fuente no duplica
    registros (clave por `id` de origen).
-   **Sin secretos ni datos personales** en ninguno de los ficheros.

------------------------------------------------------------------------

## 9. API REST

Prefijo: `/api/v1`

### 9.1 Endpoints técnicos

  Método    Ruta                           Uso
  --------- ------------------------------ -------------------------------------------
  `GET`     `/health`                      Estado de la API
  `GET`     `/incidents`                   Listar incidencias, con filtros
  `GET`     `/incidents/{id}`              Detalle de la incidencia
  `GET`     `/incidents/{id}/decision`     Salida completa del motor (7.8)
  `GET`     `/queue`                       Cola ordenada con recomendaciones
  `GET`     `/queue/compare?a=&b=`         Por qué `a` va antes que `b`
  `POST`    `/incidents`                   Crear incidencia de demo
  `POST`    `/incidents/{id}/decisions`    Registrar decisión humana (7.9)
  `GET`     `/incidents/{id}/decisions`    Decisiones humanas de la incidencia
  `PATCH`   `/incidents/{id}/status`       Cambiar estado
  `POST`    `/incidents/{id}/assign`       Asignar técnico ficticio
  `GET`     `/alerts`                      Alertas derivadas de reglas y prioridad
  `GET`     `/history`                     Consultar actividad
  `GET`     `/meta/data-sources`           Procedencia de los datos
  `GET`     `/meta/engine`                 Versión, reglas, pesos y umbrales vigentes

### 9.2 Residentes y triaje

  Método    Ruta                           Uso
  --------- ------------------------------ -------------------------------------------
  `POST`    `/public/reports`              Crear reporte (público, limitado)
  `GET`     `/triage`                      Reportes pendientes con propuesta del motor
  `POST`    `/triage/{id}/resolve`         Aceptar, marcar duplicado o rechazar

`POST /public/reports` solo acepta datos y devuelve una referencia
opaca. No hay lectura pública de reportes. `POST /triage/{id}/resolve`
recibe `outcome` (`accepted`, `duplicate`, `rejected`), motivo, y para
`accepted` la prioridad y los factores confirmados, que quedan con
procedencia `technician`.

### 9.3 Reservado para fases posteriores

`GET /planning/suggestions` (etapa 4). Devuelve `501` hasta que exista.

### 9.4 Filtros de `GET /incidents` y `GET /queue`

-   `status`: `reported`, `pending`, `assigned`, `resolved`, `rejected`.
-   `priority`: `high`, `medium`, `low` (prioridad final).
-   `source_type`: `municipal_open_data`, `derived`, `synthetic`,
    `resident_report`.
-   `urgent`: `true` para incidencias con revisión urgente.
-   `limit` y `offset`.
-   `sort`: `queue` (por defecto), `score_desc`, `age_desc`,
    `created_desc`.

### 9.5 Requisitos de API

-   Esquemas de entrada y salida con Pydantic.
-   Las respuestas de incidencias y de cola incluyen procedencia,
    prioridad por puntuación, prioridad final, reglas activadas, datos
    ausentes y recomendación.
-   Códigos HTTP adecuados: 200, 201, 400, 404, 422, 429 y 501.
-   Errores JSON coherentes, sin trazas internas ni secretos.
-   CORS restringido al origen local del frontend en desarrollo.
-   Documentación automática disponible en `/docs`.
-   Validar todos los cambios de estado y todas las decisiones
    (`reason` obligatorio, `safety_override` coherente).
-   Acciones, triaje y decisiones generan siempre un registro de
    actividad.
-   Los endpoints públicos están separados de los técnicos y tienen
    límite de frecuencia.
-   En el MVP, la API se ejecuta en una única instancia local.

------------------------------------------------------------------------

## 10. Diseño funcional de pantallas

### 10.1 Inicio --- centro de operaciones

Resumen de incidencias activas, conteo de prioridad alta y de revisiones
urgentes, asignadas, resueltas en la sesión, mapa, cola de
recomendaciones y actividad reciente. Los totales se desglosan por
procedencia y llevan la etiqueta "simulado" cuando corresponda. Aviso
visible sobre datos históricos, sintéticos y carácter experimental.

### 10.2 Mapa de incidencias

Mapa centrado en Málaga, marcadores por prioridad final, leyenda,
filtros por estado, prioridad, procedencia y revisión urgente, y
popup con título, prioridad y enlace al detalle. Vista de lista para
accesibilidad y pantallas pequeñas.

Requisitos: cada marcador corresponde a un registro válido; no se
geocodifican direcciones inventadas; atribución de OpenStreetMap
visible; los marcadores sintéticos se identifican como simulados.

### 10.3 Cola de recomendaciones

Lista ordenada por la clave del motor. Cada fila muestra posición,
prioridad final, acción recomendada, etiqueta de procedencia y las
reglas activadas. Seleccionar dos filas abre **"¿Por qué A antes que
B?"**, que muestra el resultado de `compare` con el criterio
decisivo y los valores de ambas.

### 10.4 Detalle de incidencia y panel de decisión

-   Identificador, título, ubicación, coordenadas, estado y procedencia.
-   Antigüedad y fecha disponible.
-   Puntuación, prioridad por puntuación y prioridad final, con el
    desglose de factores y pesos.
-   **Reglas de seguridad activadas**, con su motivo.
-   **Datos ausentes** y advertencias, con su efecto en la puntuación.
-   Explicación de la recomendación generada por reglas.
-   **Panel de decisión:** `Aceptar`, `Modificar` y `Rechazar`.
    `Modificar` permite cambiar acción y prioridad; `Modificar` y
    `Rechazar` exigen motivo. Si la elección queda por debajo de un
    mínimo de seguridad, el panel lo avisa y pide confirmación
    explícita.
-   Botones de asignación, resolución y generación de alerta.
-   Historial de decisiones humanas de esa incidencia.

### 10.5 Alertas

Lista ordenada por prioridad con el motivo (regla activada o prioridad
alta), la acción recomendada expresada como sugerencia y acceso al
detalle. Las alertas se derivan de las reglas; no requieren un modelo
generativo.

### 10.6 Historial

Fecha y hora, acción, incidencia, usuario ficticio o sistema, estado
anterior y nuevo, y decisiones humanas con su veredicto. Las
excepciones a reglas de seguridad se destacan. Filtro básico y
exportación CSV opcional.

### 10.7 Bandeja de triaje

Reportes de residentes pendientes, con los urgentes primero. Para cada
uno: texto (escapado), ubicación en el mapa, propuesta provisional del
motor con sus datos ausentes, posibles duplicados cercanos y acciones
`Aceptar` (confirmando prioridad y factores), `Duplicado` y `Rechazar`
(con motivo).

### 10.8 Perfil y metodología

Rol de demostración, umbral de prioridad, orden de la lista y aviso de
que no existe autenticación real. Panel de metodología con fórmula,
pesos, umbrales, catálogo de reglas, versión del motor y el estado de
validación de cada regla.

### 10.9 Página pública de reporte

Ruta pública y aislada del resto (`/reportar`), con otro diseño y sin
navegación técnica. Mapa para ubicar el problema, categoría y
descripción breve. Texto claro de que es un aviso, no una emergencia
(y que ante un peligro inmediato debe llamarse a los servicios de
emergencia), que no se recogen datos personales y que el aviso será
revisado. Confirmación genérica con referencia opaca.

### 10.10 Reglas de interfaz y estados obligatorios

-   La interfaz no calcula prioridades ni reglas; muestra lo que
    devuelve la API.
-   Ninguna acción se muestra como completada antes de la confirmación
    de la API.
-   La etiqueta de procedencia y la de "simulado" son visibles junto a
    cada dato afectado.
-   Estados: cargando, sin resultados, error de API, datos parcialmente
    disponibles, fuente no accesible, acción completada, acción no
    completada, datos sintéticos en modo demo.

------------------------------------------------------------------------

## 11. Decisión sobre IA y LLM

### 11.1 Recomendación para el MVP

**No descargar ni integrar un LLM antes de tener funcionando el motor, la
API y la interfaz.** Reglas de seguridad, cálculo de prioridad,
recomendación, validación y cambios de estado funcionan sin IA. Un
modelo generativo no decide la puntuación, no inventa el estado de una
farola y no sustituye la validación de datos.

### 11.2 Opciones y decisión

  ------------------------------------------------------------------------------
  Opción             Ventajas            Riesgos/coste        Decisión
  ------------------ ------------------- -------------------- ------------------
  Reglas             Reproducible,       No interpreta        **Usar en MVP**
  deterministas      barato, auditable   lenguaje libre       

  Planificación      Mejora el reparto   Requiere datos y     Evaluar al final
  avanzada           de recursos         validación           del plan
  (optimización)                                              

  ML clásico         Puede aprender      Necesita etiquetas   Evaluar al final,
                     patrones si hay     reales y evaluación  con el motor como
                     datos                                    referencia

  LLM local          Datos locales,      Descarga, RAM/VRAM,  **Fase opcional
                     sin coste por       latencia             posterior**
                     llamada                                  

  API de LLM         Integración         Conexión,            Solo con motivo y
  externa            sencilla            credenciales, coste, autorización
                                         privacidad           
  ------------------------------------------------------------------------------

### 11.3 Funciones opcionales de un LLM (fase posterior)

1.  Resumen de texto libre de una incidencia o reporte.
2.  Sugerencia de categoría a partir de una descripción (el técnico la
    confirma).
3.  Reformulación en lenguaje natural de una explicación ya generada
    por reglas.
4.  Chat de consulta de incidencias: fuera de alcance hasta evaluar las
    anteriores.

### 11.4 Restricciones del LLM

Si se añade, cumple siempre estos requisitos:

-   **No puede saltarse las reglas de seguridad** ni alterar suelos de
    prioridad, rutas ni revisiones urgentes.
-   **No modifica directamente decisiones operativas:** no cambia
    estados, prioridades, asignaciones ni decisiones humanas. Solo
    produce texto de lectura.
-   La salida del motor es la fuente de verdad; el LLM recibe solo los
    campos que se le pasan y no accede al almacén JSON.
-   Todo texto generado se rotula como tal.
-   El texto de incidencias y reportes se trata como dato no confiable
    (riesgo de inyección de instrucciones).
-   No se envían datos personales ni información municipal no pública a
    proveedores externos sin autorización.
-   El sistema funciona con el LLM desactivado.

### 11.5 Contrato para futura integración

Interfaz independiente `IncidentAssistant`:

-   `summarize_incident(incident)`.
-   `suggest_category(text)`.
-   `rephrase_explanation(decision)`.

La implementación por defecto es `RuleBasedAssistant`. Un adaptador de
LLM se añade después sin alterar las rutas de API, el motor ni la
interfaz principal.

------------------------------------------------------------------------

## 12. Flujo de usuario y flujo de datos

### 12.1 Flujo de usuario técnico

``` text
Inicio
  ├── revisar KPIs (con etiqueta de simulado) y mapa
  ├── Cola de recomendaciones
  │     ├── ¿Por qué A antes que B?
  │     └── seleccionar incidencia → Detalle
  │           ├── ver factores, reglas activadas y datos ausentes
  │           ├── Aceptar / Modificar / Rechazar (con motivo)
  │           ├── asignar técnico
  │           └── marcar resuelta
  ├── Triaje → revisar reporte → aceptar / duplicado / rechazar
  ├── Alertas → Detalle
  ├── Mapa → filtrar → Detalle
  ├── Historial → revisar acciones y decisiones
  └── Perfil/Metodología → ajustar umbral, consultar reglas
```

### 12.2 Flujo de una decisión

``` text
Técnico pulsa "Aceptar / Modificar / Rechazar"
        │
        ▼
Frontend valida que haya motivo cuando corresponde
        │
        ▼
POST /incidents/{id}/decisions
        │
        ▼
Pydantic valida la petición
        │
        ▼
Servicio recalcula la decisión del motor (determinista)
y comprueba el suelo de seguridad → marca safety_override si procede
        │
        ▼
Almacén: añade evento al historial, guarda decisión con instantánea
del motor y actualiza incidents.json (escritura atómica)
        │
        ▼
API devuelve la decisión y la incidencia actualizada
        │
        ▼
Frontend actualiza detalle, cola y KPIs
```

La interfaz no muestra una acción como completada antes de recibir la
confirmación de la API.

### 12.3 Flujo de un reporte de residente

``` text
Residente envía formulario público
        │
        ▼
Validación y límite de frecuencia → incidencia "reported" / "unverified"
        │
        ▼
Motor: SR-03/SR-04 → ruta triaje; propuesta provisional con datos ausentes
        │
        ▼
Bandeja de triaje → técnico acepta / duplicado / rechaza (con motivo)
        │
        ├── acepta: factores confirmados (procedencia "technician") → "pending"
        │           → entra en la cola con su recomendación
        └── duplicado o rechazo: queda registrado; no entra en la cola
```

------------------------------------------------------------------------

## 13. Preparación del entorno en la torre

La torre de desarrollo es un equipo con **CachyOS** (Arch Linux). El
usuario trabaja desde ella, o en remoto desde un portátil conectado a
ella. Los comandos se ejecutan en un terminal de la torre. El shell por
defecto es fish.

### 13.1 Herramientas comprobadas

  Herramienta    Versión comprobada
  -------------- ----------------------------------
  Git            2.56.0
  Python         3.12.15 (gestionado por `uv`)
  Node.js        26.11.1
  npm            12.2.0
  uv             0.13.0

Si falta alguna: `sudo pacman -S --needed git nodejs npm uv`. No cambiar
el Python del sistema; el proyecto usa su propio entorno.

### 13.2 Carpeta y entorno Python

Carpeta del proyecto: `~/Proyectos/Lideres-digitales-telefonica`.

``` fish
cd ~/Proyectos/Lideres-digitales-telefonica
uv venv --python 3.12 .venv        # solo si .venv no existe
source .venv/bin/activate.fish
```

No mezclar entornos de sistemas operativos distintos ni compartir un
mismo `.venv` entre ellos.

### 13.3 Backend mínimo

``` fish
uv pip install fastapi "uvicorn[standard]" pydantic-settings pytest httpx ruff
uv pip freeze > backend/requirements-lock.txt
cd backend
pytest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`backend/pyproject.toml` debe incluir `[tool.pytest.ini_options]` con
`pythonpath = ["."]` y `testpaths = ["tests"]`. El lock es un registro
del entorno; conviene regenerarlo tras comprobar cambios.

### 13.4 Frontend

Desde la raíz del proyecto:

``` fish
node --version
npm --version
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install leaflet react-leaflet react-router-dom lucide-react
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom
```

Las versiones instaladas quedan en `package-lock.json`. Si npm propone
cambios incompatibles con la versión de Node, detenerse y revisar antes
de seguir.

### 13.5 Verificación de conectividad remota


-   Ejecutar los servidores en la torre, no en el portátil.
-   Mantener la sesión remota activa mientras se desarrolla.
-   Para Vite, escuchar en la interfaz adecuada para el túnel o red
    privada que se vaya a usar; no exponer el servidor a toda la red sin
    necesidad.
-   Para FastAPI, mantener el puerto de desarrollo accesible solo desde
    el entorno local o mediante el túnel remoto.
-   No abrir puertos del router.
-   No incluir contraseñas, claves ni tokens en comandos que queden
    guardados en el historial.
-   Si se usa Tailscale, comprobar conectividad y nombres de host antes
    de configurar enlaces directos entre dispositivos.

Puertos de desarrollo sugeridos: frontend `5173`, API `8000`. Son
valores convencionales, no una configuración de seguridad.

------------------------------------------------------------------------

## 14. Plan de desarrollo

Orden: **primero el motor de reglas y sus pruebas, después la API y la
interfaz, y al final la evaluación de planificación avanzada o
aprendizaje automático clásico.** El LLM, si se hace, va después de
todo lo anterior.

### Fase 0 --- Entorno y decisiones

-   [x] Confirmar Python, Node, npm, Git y uv en la torre (CachyOS).
-   [x] Crear entorno virtual y estructura base del backend.
-   [x] Elegir persistencia: JSON con escrituras seguras.
-   [x] Endpoint `/health` y primera prueba.
-   [ ] Actualizar `DESIGN.md` a la versión 0.2 y crear `docs/RULES.md`.
-   [ ] Verificar al menos un recurso de datos municipal descargable.

### Fase 1 --- Motor de decisiones y pruebas (sin API ni interfaz)

-   [ ] Esquemas de incidencia y de entrada/salida del motor.
-   [ ] Mover la prioridad a `engine/priority.py` con su política de
        datos ausentes.
-   [ ] Reglas de seguridad SR-01 a SR-05 y configuración versionada.
-   [ ] Recomendación de reparación, clave de cola y `compare`.
-   [ ] Orquestador `decide` con `evaluated_at` como parámetro.
-   [ ] Conjunto sintético etiquetado en `data/synthetic/`.
-   [ ] Pruebas: determinismo, reglas de seguridad, datos incompletos,
        conflictos y trazabilidad.

### Fase 2 --- Persistencia y API

-   [ ] `json_store` con escritura atómica, bloqueo, historial y
        decisiones de solo añadir.
-   [ ] Servicios de incidencias, decisiones humanas y auditoría.
-   [ ] Endpoints técnicos (cola, detalle, decisiones, estado,
        asignación, historial, meta).
-   [ ] Reportes de residentes y triaje, con límite de frecuencia.
-   [ ] Pruebas de persistencia y de API.

### Fase 3 --- Interfaz

-   [ ] Layout y navegación.
-   [ ] Cola de recomendaciones con "¿Por qué A antes que B?".
-   [ ] Detalle con reglas activadas, datos ausentes y panel
        Aceptar / Modificar / Rechazar.
-   [ ] Inicio con KPIs desglosados por procedencia, y mapa Leaflet.
-   [ ] Alertas, historial y metodología.
-   [ ] Página pública de reporte y bandeja de triaje.
-   [ ] Estados de error y carga.

### Fase 4 --- Datos reales y transparencia

-   [ ] Documentar fuente municipal.
-   [ ] Descargar el original y registrar procedencia.
-   [ ] Inspeccionar campos y CRS.
-   [ ] Normalizar datos y mostrar históricos como históricos.
-   [ ] Separar visualmente datos reales, derivados, sintéticos y
        reportes.

### Fase 5 --- Pulido de demo

-   [ ] Ejecutar todas las pruebas.
-   [ ] Comprobar responsive.
-   [ ] Revisar atribución de mapa y textos de limitaciones.
-   [ ] Preparar un guion de demo de 60--90 segundos.

### Fase 6 --- Evaluación avanzada (opcional)

Solo si las fases 1--5 están estables.

-   [ ] Evaluar planificación avanzada de recursos (agrupación por zona,
        rutas) con el motor determinista como referencia.
-   [ ] Evaluar aprendizaje automático clásico: exige etiquetas reales,
        partición de evaluación y comparación con la referencia. No
        entrenar con datos sintéticos.
-   [ ] Documentar resultados y decidir si algo se integra. Nada
        evaluado puede saltarse las reglas de seguridad.

### Fase 7 --- LLM (opcional, posterior)

-   [ ] Implementar `IncidentAssistant` con adaptador de LLM, solo
        lectura y con las restricciones de 11.4.
-   [ ] Comprobar que el sistema completo funciona con el LLM
        desactivado.

------------------------------------------------------------------------

## 15. Pruebas y criterios de aceptación

### 15.1 Determinismo

-   Misma entrada, configuración y `evaluated_at`: salida idéntica al
    serializar, repetida muchas veces.
-   El resultado no depende del orden de las reglas, del orden de las
    claves de entrada ni del orden de la lista de incidencias.
-   El motor no accede al reloj: cambiar la hora del sistema no cambia la
    salida; solo cambia si cambia `evaluated_at`.
-   La clave de cola es un orden total: ningún empate sin resolver.

### 15.2 Reglas de seguridad

-   Cada regla se activa con su condición y no se activa sin ella
    (casos límite incluidos, como `sensitive_location` = 89 y 90).
-   Una incidencia con SR-01 y puntuación 0 sale con prioridad final
    alta y revisión urgente.
-   Cambiar pesos o umbrales de puntuación no elimina un suelo de
    seguridad.
-   I-01 a I-04 se verifican con pruebas basadas en propiedades o en
    tablas de casos.
-   Una decisión humana por debajo del suelo marca `safety_override` y
    exige motivo.

### 15.3 Datos incompletos

-   Un factor ausente no cuenta como cero: puntuación parcial,
    `complete: false`, advertencia y `missing_factors`.
-   Sin ningún factor: `score` nulo, ruta `triage`, acción
    `needs_triage`.
-   Valores fuera de rango o negativos se rechazan.
-   Un reporte de residente sin contexto nunca sale como prioridad baja
    por defecto.
-   Sin coordenadas válidas no hay marcador en el mapa.

### 15.4 Conflictos entre reglas y datos

-   Suelo frente a puntuación: gana el suelo.
-   Dos reglas con suelos distintos: se aplica el más alto.
-   Dos acciones propuestas: gana la de mayor precedencia y el
    conflicto queda registrado.
-   Triaje más revisión urgente: ambas aplican, sin saltarse la
    validación humana.
-   Alumbrado en contradicción con el reporte: `data_conflict` y
    triaje; el reporte no se descarta.
-   El resultado es el mismo con cualquier orden de evaluación.

### 15.5 Trazabilidad

-   La salida incluye `engine_version`, `config_version`, entradas,
    reglas activadas y datos ausentes.
-   Cada decisión humana guarda la instantánea del motor; volver a
    ejecutar el motor con esa instantánea reproduce la misma
    recomendación.
-   Toda acción, triaje y decisión deja un evento en el historial, con
    secuencia creciente.
-   Los registros municipales conservan su fuente; los sintéticos
    muestran etiqueta visible y nunca se marcan `municipal_open_data`.
-   Las estadísticas sobre datos sintéticos aparecen etiquetadas.

### 15.6 Persistencia

-   Un fallo simulado a mitad de escritura deja intacto el fichero
    anterior.
-   Un JSON corrupto impide el arranque y no se sobrescribe.
-   Reiniciar conserva incidencias, historial y decisiones.
-   Dos escrituras concurrentes no se pierden ni se corrompen.
-   Importar dos veces el mismo fichero no duplica registros.
-   `history.jsonl` y `decisions.jsonl` nunca se reescriben.

### 15.7 API

-   `/health` responde correctamente.
-   Un ID inexistente devuelve 404; un estado o veredicto inválido
    devuelve 422.
-   `modified` o `rejected` sin motivo devuelve 422.
-   Aceptar, modificar o rechazar guarda la decisión y registra el
    historial.
-   `/queue` devuelve el orden del motor; `/queue/compare` devuelve el
    criterio decisivo.
-   El endpoint público solo crea reportes, aplica el límite de
    frecuencia (429) y no expone datos de otros reportes.
-   Un reporte con texto hostil (HTML, instrucciones) se almacena como
    texto y se muestra escapado.
-   Filtrar por procedencia funciona.

### 15.8 Frontend

-   Las pantallas principales se abren desde la navegación.
-   Los marcadores abren el detalle correcto.
-   El panel de decisión exige motivo en Modificar y Rechazar.
-   "¿Por qué A antes que B?" muestra el criterio devuelto por la API.
-   Los botones actualizan la interfaz solo tras confirmación.
-   Se muestran el aviso de modo demo y las etiquetas de simulado.
-   La página pública de reporte no muestra datos operativos.
-   Los errores de API no dejan la pantalla bloqueada.
-   El mapa conserva altura en escritorio y móvil.

------------------------------------------------------------------------

## 16. Limitaciones y validación profesional

-   **Las puntuaciones iniciales son experimentales.** Pesos, umbrales,
    referencia de antigüedad y reglas de seguridad son valores
    ilustrativos elegidos para construir el prototipo. No proceden de
    criterios municipales ni de estudios.
-   **Necesitan validación profesional antes de usarse en operaciones
    reales:** revisión por responsables de mantenimiento del
    alumbrado, por responsables de seguridad y prevención, y contraste
    con la normativa y los protocolos aplicables. La validación incluye
    análisis de sensibilidad de pesos y umbrales, y una comparación
    retrospectiva con casos reales.
-   `docs/RULES.md` registra para cada regla su estado
    (`experimental`, `en revisión`, `validada`), quién la revisó y
    cuándo. Mientras haya reglas `experimental`, la interfaz muestra el
    aviso correspondiente.
-   El índice no es una probabilidad de accidente ni predice delitos,
    lesiones o fallos futuros.
-   Los datos sintéticos no son evidencia; los históricos municipales no
    son averías abiertas; los reportes de residentes no están
    verificados hasta el triaje.
-   El prototipo no controla luminarias ni conoce su estado real.
-   El sistema no sustituye el criterio profesional ni los canales de
    emergencia.

------------------------------------------------------------------------

## 17. Riesgos y mitigaciones

  ---------------------------------------------------------------------
  Riesgo                             Mitigación
  ---------------------------------- ----------------------------------
  No existe inventario público de    No afirmar cobertura completa;
  luminarias                         usar datos sintéticos etiquetados

  Incidencias históricas confundidas Separar fuente, periodo y estado
  con averías abiertas               operativo

  Datos simulados tomados como       Etiquetas visibles, KPIs
  evidencia                          desglosados, sin calibrar con ellos

  Prioridad aparentemente oficial    Mostrar fórmula, pesos y carácter
                                     experimental; sección 16

  Sesgo de automatización (el        Motivo obligatorio al modificar o
  técnico acepta sin pensar)         rechazar; mostrar datos ausentes y
                                     reglas; registrar decisiones

  Regla de seguridad ignorada o      Reglas aplicadas antes de la
  compensada por la puntuación       puntuación; invariantes probados;
                                     excepciones marcadas

  Corrupción o pérdida de datos      Escritura atómica, registros de
  en JSON                            solo añadir, copia `.bak`,
                                     negativa a arrancar con datos
                                     corruptos

  Abuso del formulario público       Límite de frecuencia, validación,
  (spam, texto hostil)               texto escapado, sin lectura pública

  Datos personales en reportes       No pedirlos; sin fotos en el MVP;
                                     aviso en el formulario

  Conflicto entre reglas o datos     Precedencia determinista,
                                     conflictos registrados, triaje
                                     humano

  Geolocalización incorrecta         Validar CRS, coordenadas y ámbito
                                     geográfico

  Dependencia de un modelo IA        Motor y API funcionales sin LLM

  Un LLM salta reglas o altera       Solo lectura, sin acceso al
  decisiones                         almacén, restricciones de 11.4

  Caída de una fuente externa        Dataset de demo local y fecha de
                                     actualización

  Problemas por desarrollo remoto    Ejecutar todo en la torre, túnel o
                                     red privada, sin puertos públicos

  Sobrecarga de dependencias         No instalar bibliotecas
                                     geoespaciales, de optimización o ML
                                     hasta que sean necesarias

  Cambios incompatibles entre        Contratos de datos y de API, ramas
  agentes                            pequeñas y pruebas antes de
                                     integrar
  ---------------------------------------------------------------------

------------------------------------------------------------------------

## 18. Tareas para agentes de programación

Los agentes trabajan sobre tareas pequeñas y contratos estables. No
implementan toda la aplicación en paralelo sin acordar antes los tipos
de datos y el contrato del motor (7.8 y 7.9).

### Agente A --- Motor de decisiones (primero)

Responsable de: modelos del motor, reglas de seguridad, prioridad,
recomendación, cola, `compare`, configuración versionada y todas las
pruebas de la sección 15.1 a 15.5.

No debe: importar FastAPI, el repositorio, el sistema de ficheros o el
reloj; introducir un LLM; cambiar el contrato de salida sin actualizar
este documento.

### Agente B --- API y persistencia

Responsable de: esquemas Pydantic, `json_store`, servicios, endpoints,
triaje, reportes públicos, auditoría y pruebas 15.6 y 15.7.

No debe: reimplementar lógica del motor; escribir a disco fuera de
`json_store`; modificar componentes de frontend.

### Agente C --- Frontend

Responsable de: layout, pantallas, mapa, cola, panel de decisión,
página pública, cliente HTTP, estados de carga/error y pruebas de
componentes.

No debe: calcular una fórmula o regla distinta de la del motor;
inventar datos reales; simular éxito de una acción antes de recibir
respuesta.

### Agente D --- Datos y evaluación

Responsable de: investigar recursos descargables del portal de
Málaga, documentar licencias y procedencia, importador y validaciones,
y conjunto sintético etiquetado.

No debe: convertir registros resueltos en averías activas; cambiar
datos originales; afirmar que un campo existe sin inspeccionar el
fichero.

### Integración

-   Todos usan el mismo esquema de incidencia y el mismo contrato del
    motor.
-   Los cambios de API o de contrato se documentan antes de integrarse.
-   No se sobrescriben ficheros de otro agente sin coordinación.
-   Cada tarea termina con pruebas y resumen de archivos modificados.
-   El responsable de integración revisa el resultado antes de fusionar.

------------------------------------------------------------------------

## 19. Decisiones

### 19.1 Cerradas

1.  **Persistencia:** JSON con escrituras seguras (sección 8).
2.  **Arquitectura:** motor determinista independiente de la API y la
    interfaz.
3.  **Modelo de decisión:** cuatro etapas separadas (reglas de
    seguridad, prioridad, recomendación, planificación de recursos).
4.  **Humano en el circuito:** aceptar, modificar o rechazar, con
    registro.
5.  **Residentes:** reporte público sin datos personales y triaje
    humano antes de entrar en la cola.
6.  **IA:** sin LLM en el MVP; fase opcional posterior con
    restricciones.
7.  **Autenticación:** perfil ficticio, sin login real.
8.  **Despliegue:** local en la torre (CachyOS), sin publicación
    pública.
9.  **Stack:** FastAPI, React + TypeScript + Vite, Leaflet.
10. **Orden de desarrollo:** motor y pruebas, después API e interfaz,
    después evaluación avanzada.

### 19.2 Pendientes

1.  **Datos municipales:** confirmar URL directa de descarga, campos,
    licencia y coordenadas.
2.  **Estado del alumbrado:** verificar si existe una fuente real antes
    de implementar algo más que `NullProvider` y `SimulatedProvider`.
3.  **Reglas y pesos:** valores definitivos pendientes de validación
    profesional (sección 16).
4.  **Concurrencia del almacén JSON:** un único proceso con bloqueo, o
    bloqueo entre procesos si se necesita más de uno.
5.  **Mapa:** teselas estándar de OpenStreetMap para desarrollo; revisar
    políticas de uso antes de una demo con mucho tráfico.
6.  **Fotos en reportes:** fuera del MVP; requeriría revisión de
    privacidad.

------------------------------------------------------------------------

## 20. Fuentes de referencia

-   Portal de datos abiertos de Málaga: https://datosabiertos.malaga.eu/
-   Dataset municipal de incidencias resueltas de 2026:
    https://datosabiertos.malaga.eu/dataset/incidencias-resueltas-en-la-via-publica-para-el-ano-2026
-   Intensidades de tráfico de Málaga:
    https://movilidad.malaga.eu/es/servicios/intensidades/
-   FastAPI: https://fastapi.tiangolo.com/
-   React: https://react.dev/
-   Vite: https://vite.dev/
-   Leaflet: https://leafletjs.com/
-   React Leaflet: https://react-leaflet.js.org/
-   OpenStreetMap --- política de teselas:
    https://operations.osmfoundation.org/policies/tiles/

------------------------------------------------------------------------

## 21. Registro de cambios

-   **0.2:** el motor determinista de decisiones pasa a ser el núcleo,
    independiente de API e interfaz. Se separa el modelo de decisión en
    reglas de seguridad, cálculo de prioridad, recomendación de
    reparación y planificación de recursos (esta última como fase
    posterior). Se distinguen datos históricos municipales, sintéticos,
    derivados y reportes de residentes, y se establece que los datos
    simulados no son evidencia. Nuevo contrato de datos y de API con
    factores de prioridad, reglas activadas, explicación, datos ausentes
    y decisión del técnico. Persistencia en JSON con escrituras
    seguras. La interfaz muestra por qué una incidencia va antes que
    otra y permite aceptar, modificar o rechazar. Se añaden la ventana
    pública de reporte para residentes y la bandeja de triaje. Se
    amplían las pruebas (determinismo, reglas de seguridad, datos
    incompletos, conflictos, trazabilidad). Nuevo orden de desarrollo:
    motor y pruebas, después API e interfaz, y al final evaluación de
    planificación avanzada o aprendizaje automático clásico. El LLM
    queda como fase opcional posterior, sin capacidad de saltarse las
    reglas de seguridad ni de modificar decisiones operativas. Se
    documenta que las puntuaciones iniciales son experimentales y
    requieren validación profesional. Entorno actualizado a CachyOS.
-   **0.1:** primera especificación funcional y técnica; arquitectura
    propuesta, pipeline de datos, motor de prioridad, API, pantallas,
    opciones de IA, preparación de entorno remoto y criterios de
    aceptación.
