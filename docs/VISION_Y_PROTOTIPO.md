# Luma Málaga: visión del producto y explicación del prototipo

**Estado:** prototipo funcional para demostración, con registros y actores ficticios.  
**Alcance geográfico ilustrativo:** distrito Centro de Málaga y otros puntos aproximados de la ciudad.  
**Diseño de referencia:** [diseño técnico v0.2](./design/diseno-tecnico-v0.2.md).

## 1. Qué es Luma Málaga

Luma Málaga es un prototipo web de apoyo a la gestión de incidencias de
alumbrado público. Reúne avisos geolocalizados, los muestra en un mapa, aplica
reglas deterministas para señalar casos que requieren atención y ofrece una
cola explicable para que las personas puedan revisar y actualizar su estado.

Su finalidad es explorar un flujo de trabajo más claro y trazable; no controlar
farolas, certificar riesgos ni sustituir el criterio de un técnico. El sistema
recomienda, pero la decisión es humana. Las puntuaciones y ubicaciones de la
demo son sintéticas y no describen incidencias reales de Málaga.

## 2. A quién sirve y por qué

| Usuario objetivo | Quién lo representa | Necesidad y valor |
| --- | --- | --- |
| Personal técnico de alumbrado | Perfil ficticio «Lucía Díaz» | Consultar una incidencia, entender su recomendación, localizarla, aceptar una asignación y reflejar su resolución. |
| Coordinación de operaciones | Perfil ficticio «Equipo de operaciones» | Revisar avisos sin verificar, observar alertas y actividad, y asignar casos a una persona responsable. |
| Residente | Persona que observa un posible problema | Enviar un aviso sintético con categoría, descripción y punto aproximado; en esta demo el aviso solo entra en una bandeja local de triaje. |
| Ayuntamiento y empresas mantenedoras | Actores del contexto futuro, no usuarios conectados | Son quienes podrían aportar datos y ejecutar trabajos si se acordara una integración real. No tienen conexión ni acceso en este prototipo. |

Los nombres y perfiles son utilería de demostración, no identidades reales ni
cuentas autenticadas. Cambiar de perfil modifica las ventanas visibles en el
navegador, pero no crea permisos de seguridad en la API.

## 3. Contexto urbano y situación de uso

### Escenario ilustrativo

Imaginemos una tarde-noche en el entorno de la Alameda Principal y el Centro
histórico de Málaga. Una persona observa una luminaria apagada en una zona
peatonal y comunica el punto aproximado desde el formulario. Más tarde, el
equipo de operaciones abre el aviso en triaje, comprueba la descripción y el
mapa, y decide si lo valida o lo rechaza. Si lo valida, el registro pasa a
pendiente, se asigna a una técnica y, tras una inspección ficticia, se marca
como resuelto.

El contexto urbano sirve para hacer comprensible el caso: convivencia de
peatones, comercios, actividad de tarde-noche, calles de distintas anchuras y
recorridos entre el centro histórico y el frente litoral. **No se incorporan
mediciones de afluencia ni se afirma que en ese lugar haya una avería real.**
El aviso, la hora, las coordenadas, el nivel de uso peatonal y cualquier factor
de entorno utilizados en el ejemplo son datos inventados para la demo.

El caso representa una situación de diseño plausible, no un incidente
documentado. Las zonas aproximadas del mapa tampoco constituyen límites
oficiales de barrios o distritos. La selección del Centro para el ejemplo no
significa que allí haya más averías que en otras zonas.

### Actores y responsabilidades

1. **Residente:** describe lo observado sin aportar datos personales y señala
   una ubicación aproximada. La página informa que no es un canal municipal.
2. **Persona de triaje:** examina el aviso, comprueba que tiene información
   suficiente y toma una decisión humana.
3. **Técnica asignada:** consulta la ubicación y los datos explicativos, y
   actualiza el estado de la tarea en el entorno de demostración.
4. **Coordinación:** revisa alertas, cola e historial para seguir las acciones.
5. **Servicios municipales y contratistas:** son actores posibles de una
   integración futura; el prototipo no les envía avisos ni órdenes.

## 4. Casos de uso concretos

### CU-01. Encontrar una incidencia que requiere atención

La técnica abre el mapa, filtra por categoría, prioridad, estado y distrito,
selecciona un marcador y consulta los factores y reglas que explican la
recomendación. Los filtros ayudan a focalizar una zona; no aportan información
adicional a la evaluación del motor.

### CU-02. Revisar y clasificar un aviso ciudadano

Operaciones abre la bandeja de triaje, consulta el texto, categoría y punto, y
elige **Validar** o **Rechazar**. El aviso no pasa a la cola operativa mientras
siga como `reported` y sin verificar. Tanto la decisión como el actor de demo
y la hora quedan en el historial local.

### CU-03. Asignar y cerrar una tarea sintética

Una incidencia pendiente se asigna a una persona responsable ficticia. La
técnica puede marcarla como resuelta; una incidencia resuelta se puede reabrir.
Estas acciones ilustran el ciclo de vida, pero no notifican a una brigada ni
certifican una reparación.

### CU-04. Explicar una recomendación de prioridad

En el detalle se consultan puntuación, factores disponibles, factores ausentes,
reglas activadas y justificación. Por ejemplo, un poste dañado activa una regla
de revisión urgente y un suelo de prioridad alta aunque la puntuación heurística
resultase baja.

### CU-05. Seguir la trazabilidad

La vista de historial presenta la inicialización de registros y las acciones
de reporte, validación, rechazo, asignación, resolución y reapertura. El
historial corresponde al almacén JSON local de la demo; no es una auditoría
municipal ni una identidad autenticada.

## 5. Diseño de la solución tecnológica

### Arquitectura de la aplicación

```text
┌──────────────────────────────────────────────────────┐
│ Frontend React + TypeScript                          │
│ Perfiles demo · mapa Leaflet · triaje · reporte       │
└─────────────────────────┬────────────────────────────┘
                          │ HTTP / JSON (/api → proxy Vite)
┌─────────────────────────▼────────────────────────────┐
│ API FastAPI + Pydantic                               │
│ Lectura · reportes sintéticos · flujo · historial    │
└──────────────┬──────────────────────────┬────────────┘
               │                          │
┌──────────────▼─────────────┐  ┌─────────▼───────────┐
│ Motor determinista puro    │  │ Almacén JSON        │
│ reglas → prioridad →       │  │ incidents.json      │
│ recomendación explicable   │  │ history.jsonl       │
└────────────────────────────┘  └─────────────────────┘
                                       ▲
                              data/synthetic/seed.json
```

El motor se mantiene separado de la red y de la persistencia: recibe una
incidencia, la hora de evaluación y una configuración, y devuelve una decisión
explicable. La API adapta sus resultados al contrato HTTP y el frontend
presenta los datos y envía las acciones elegidas.

### Tecnologías usadas

- **Interfaz:** React, TypeScript y Vite; React Router organiza las páginas.
- **Mapa:** Leaflet/React-Leaflet muestra puntos sintéticos y un mapa base de
  OpenStreetMap con atribución. El mapa base no es un sensor ni una fuente de
  incidencias de alumbrado.
- **API:** FastAPI y Pydantic validan y serializan las peticiones y respuestas.
- **Persistencia de demo:** JSON para el conjunto vigente y JSON Lines para la
  secuencia de eventos. El almacén runtime vive bajo `data/store/`, ignorado
  por Git.
- **Pruebas:** pytest y Ruff para backend; Vitest y TypeScript para frontend.

### Sensores y fuentes de datos

**No hay sensores ni telemetría de luminarias conectados.** El estado de
alumbrado disponible es desconocido, no una observación en tiempo real.

| Dato | Situación en el prototipo |
| --- | --- |
| Incidencias iniciales | Tres registros ficticios en `data/synthetic/seed.json`; incluyen dos incidencias sintéticas y un aviso de demo pendiente de triaje. |
| Reportes del formulario | Se guardan localmente como `resident_report`, se marcan como simulados y comienzan sin verificar. |
| Uso peatonal e importancia del entorno | Valores artificiales de algunos registros semilla. En avisos nuevos quedan ausentes; no se inventan silenciosamente. |
| Cartografía | Teselas de OpenStreetMap como fondo y asignaciones aproximadas a zonas. |
| GECOR municipal | El documento de investigación identifica registros de incidencias resueltas, no averías abiertas. Licencia, CRS y otros detalles continúan pendientes de verificar; no se importan a la demo. |
| Capas EMT, equipamientos o estado de luminarias | Posibles fuentes futuras; disponibilidad, vigencia, licencia y aptitud deben verificarse antes de incorporarlas. |

La evaluación de fuentes y sus incertidumbres se mantiene en
[docs/DATA.md](./DATA.md). Hasta que se verifiquen fuentes apropiadas, no se
presentan datos históricos como estado actual y no se utilizan datos sintéticos
como evidencia o para calibrar el motor.

## 6. Flujo de datos y lógica principal

### Flujo de lectura

1. Al primer acceso, el almacén inicializa `data/store/incidents.json` desde
   `data/synthetic/seed.json` y crea los eventos iniciales.
2. El frontend solicita `GET /api/v1/incidents`; en desarrollo, Vite reenvía
   `/api` a FastAPI. Si la API no está disponible, la interfaz avisa y usa su
   conjunto de respaldo local.
3. La API valida los registros y llama al motor con una hora de evaluación.
4. El motor evalúa seguridad, calcula la prioridad disponible y crea una
   recomendación ordenable.
5. El frontend muestra la salida, procedencia, ubicación y limitaciones.

### Flujo de reporte y operación

1. El formulario valida categoría, descripción y coordenadas dentro del ámbito
   aproximado de Málaga.
2. `POST /api/v1/reports` crea un identificador `RPT-*`, establece el origen
   `resident_report`, lo marca sintético y no verificado, le asigna una zona
   aproximada y lo deja en estado `reported`.
3. La creación añade un evento a `history.jsonl`; el aviso no entra en la cola.
4. Una acción `PATCH /api/v1/incidents/{id}/workflow` permite validar, rechazar,
   asignar, resolver o reabrir cuando la transición es válida.
5. El almacén persiste el estado y anota la acción con actor de demostración,
   fecha y datos asociados. `GET /api/v1/history` alimenta el historial.

Rutas adicionales de consulta: `/api/v1/queue`, `/api/v1/alerts`,
`/api/v1/meta/engine` y `/api/v1/meta/data-sources`. La especificación
interactiva está disponible en `/docs` mientras corre la API.

### Prioridad y tratamiento de datos ausentes

El índice experimental usa:

```text
antiguedad = min(horas_desde_reporte / 30, 1) * 100
puntuacion = 0.40 * uso_peatonal
           + 0.20 * antiguedad
           + 0.40 * importancia_del_entorno
```

Los factores que faltan se excluyen y los pesos disponibles se redistribuyen
proporcionalmente. La salida lista los factores ausentes. Si no hay factores
suficientes, no se fabrica una puntuación. Los umbrales iniciales son alta
desde 75, media desde 55 y baja por debajo de 55; una regla de seguridad puede
imponer un mínimo de prioridad.

## 7. Reglas: explicación y pseudocódigo

Las reglas se ejecutan de forma determinista antes de la puntuación. Sus
condiciones y efectos completos están en el [catálogo de reglas](./RULES.md).
Resumen operativo:

- **SR-01:** poste dañado o riesgo eléctrico → revisión urgente y suelo alto.
- **SR-02:** luminaria apagada en entorno de sensibilidad alta → suelo alto.
- **SR-03:** faltan coordenadas o todos los factores → triaje humano.
- **SR-04:** aviso de residente aún no verificado → triaje humano.
- **SR-05:** el reporte de luminaria apagada contradice un contexto que indica
  encendida → conflicto y triaje; no se descarta automáticamente.

```text
funcion evaluar(incidencia, configuracion):
    reglas = []

    si incidencia.tipo es "poste_dañado" o "riesgo_electrico":
        reglas.agregar(
            id="SR-01",
            prioridad_minima="alta",
            revision_urgente=verdadero
        )

    si incidencia.tipo es "luminaria_apagada"
       y incidencia.importancia_entorno existe
       y incidencia.importancia_entorno >= configuracion.umbral_entorno:
        reglas.agregar(id="SR-02", prioridad_minima="alta")

    si faltan_coordenadas(incidencia)
       o faltan_todos_los_factores(incidencia):
        reglas.agregar(id="SR-03", ruta="triaje")

    si incidencia.origen es "residente"
       y incidencia.verificacion != "verificada":
        reglas.agregar(id="SR-04", ruta="triaje")

    si incidencia.tipo es "luminaria_apagada"
       y incidencia.estado_contextual == "encendida":
        reglas.agregar(id="SR-05", ruta="triaje", conflicto=verdadero)

    puntuacion = calcular_con_factores_disponibles(incidencia)
    prioridad = clasificar(puntuacion)
    prioridad = max(prioridad, suelos_de_prioridad(reglas))
    ruta = "triaje" si alguna_regla_pide_triaje(reglas)
           en_otro_caso "cola"

    devolver recomendacion_explicada(
        prioridad, ruta, reglas, factores_ausentes(incidencia)
    )
```

El pseudocódigo es una explicación conceptual; la implementación concreta y
sus pruebas viven en `backend/app/engine/`.

## 8. Qué permite demostrar el prototipo

- **Resumen:** contadores y cola sugerida para los perfiles ficticios.
- **Mapa:** marcadores por prioridad, selección de incidencia y filtros por
  categoría, prioridad, estado, procedencia y distrito aproximado.
- **Cola, incidencias y alertas:** exploración de los registros y sus detalles.
- **Triaje:** validación o rechazo de avisos sintéticos.
- **Detalle de incidencia:** factores, datos ausentes, reglas y cambios de
  estado permitidos.
- **Historial:** seguimiento persistente de eventos de demostración.
- **Reporte público:** formulario de prueba que genera avisos sintéticos
  únicamente en el almacén local.
- **Metodología:** explicación de las reglas, puntuación y límites.

Los perfiles solo cambian la navegación. El sistema no implementa inicio de
sesión, permisos por rol ni aislamiento de datos entre usuarios.

## 9. Límites, seguridad y siguiente validación

- No hay conexión municipal, inventario de luminarias, sensor, despacho de
  personal ni notificación real.
- El API de escritura no está autenticado. Debe ejecutarse en un entorno
  privado de demostración, nunca exponerse como canal público real.
- Los campos y acciones del flujo describen un ejemplo de software; marcar una
  incidencia como resuelta no comprueba físicamente una reparación.
- Las reglas y pesos son experimentales, no normativa ni evaluación de riesgo.
- Los reportes no deben incluir datos personales; el texto libre se limita y
  se trata como dato no confiable.
- Antes de cualquier uso real harían falta validación profesional, fuentes y
  licencias comprobadas, autenticación/autorización, controles de abuso,
  política de privacidad, monitorización y una auditoría adecuada.

Para ejecutar y probar la demo, sigue el [README](../README.md). El diseño
completo, incluidos los requisitos futuros, decisiones y plan por fases, está
en [docs/design/diseno-tecnico-v0.2.md](./design/diseno-tecnico-v0.2.md).
