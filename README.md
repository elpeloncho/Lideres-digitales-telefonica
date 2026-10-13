# Lideres-digitales-telefonica

## Estado del prototipo

El repositorio contiene el motor determinista, una API de lectura y escritura,
y una interfaz de demostración de Luma Málaga. La API expone incidencias,
cola, alertas, decisiones, metadatos e historial; permite registrar reportes
sintéticos y validar, rechazar, asignar, resolver o reabrir incidencias. La
interfaz carga las incidencias desde la API y muestra los datos locales de
demostración si no está disponible. Los registros no describen el estado real
del alumbrado de Málaga.

Consulta la [visión del producto y explicación del prototipo](docs/VISION_Y_PROTOTIPO.md)
para conocer los usuarios, escenarios, arquitectura y reglas. El documento de
[diseño técnico v0.2](docs/design/diseno-tecnico-v0.2.md) conserva la propuesta
detallada y el [estado de las fuentes de datos](docs/DATA.md) distingue lo
comprobado de lo pendiente.

Las reglas y puntuaciones son experimentales, no constituyen criterios oficiales
ni una evaluación de riesgo. Consulta el [catálogo de reglas](docs/RULES.md).

## Estructura del repositorio

```text
backend/app/engine/       Motor determinista y reglas
backend/app/api/          Endpoints FastAPI
backend/app/repositories/ Almacén JSON e historial
backend/tests/            Pruebas del motor, API y persistencia
frontend/src/             Interfaz React, mapa y flujos de demo
data/synthetic/           Semilla de incidencias ficticias
data/store/               Estado local de ejecución (ignorado por Git)
docs/                     Visión, diseño técnico, reglas y datos
```

## Backend

Desde la raíz del repositorio, crea un entorno virtual e instala las
dependencias fijadas:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-lock.txt
```

Ejecuta las pruebas desde `backend/`:

```bash
cd backend
../.venv/bin/python -m pytest -q
../.venv/bin/ruff check app tests
```

Para arrancar la API localmente:

```bash
cd backend
../.venv/bin/python -m uvicorn app.main:app --reload
```

La documentación OpenAPI queda disponible en `http://127.0.0.1:8000/docs`.
El servidor de desarrollo debe mantenerse en local y no exponerse a Internet.
Los datos de ejecución se guardan en `data/store/` y se inicializan desde el
conjunto sintético cuando aún no existe un almacén.
Las acciones se guardan en `incidents.json` y se anotan en `history.jsonl`.
Los reportes públicos de esta fase se almacenan únicamente como datos
sintéticos locales; no se envían a servicios municipales. No hay autenticación,
por lo que esta API de demostración debe permanecer en un entorno privado.

## Frontend

Instala y arranca la interfaz desde `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

El frontend requiere Node.js 20 o superior.
Con la API activa en el puerto `8000`, Vite reenvía las peticiones `/api` al
backend. Si la API no responde, la interfaz informa del problema y usa los
registros locales de demostración.

El prototipo incluye perfiles ficticios de técnico y operaciones, un mapa
filtrable por distrito, tipo, prioridad y estado, un flujo de triaje y la
página `/reportar`, que crea avisos sintéticos persistidos en el almacén local.
Los perfiles no son cuentas autenticadas. Las ubicaciones y la asignación de
datos de demo a distritos son aproximadas y artificiales; no representan
límites oficiales ni incidencias reales.