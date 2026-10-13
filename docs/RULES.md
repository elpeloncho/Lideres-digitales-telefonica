# Catálogo de reglas de Luma Málaga

**Versión del motor:** `0.2.0`  
**Configuración inicial:** `2026-10-13-default`  
**Estado:** experimental; requiere validación profesional antes de cualquier
uso operativo.

Las reglas se evalúan de forma determinista en `backend/app/engine/safety_rules.py`.
Sus efectos solo pueden elevar el suelo de prioridad, marcar revisión urgente o
enviar la incidencia a triaje; no pueden reducir la prioridad calculada. Si
coinciden varias reglas, se combinan de forma determinista y se conservan los
conflictos en la salida.

| ID | Condición | Efecto |
| --- | --- | --- |
| SR-01 | Categoría `electrical_hazard` o `damaged_pole`. | Suelo `high`, revisión urgente y propuesta `inspect_urgently`. |
| SR-02 | `streetlight_failure` y `sensitive_location` igual o superior al umbral configurado (90 por defecto). | Suelo `high`. |
| SR-03 | Faltan coordenadas válidas o todos los factores de prioridad. | Ruta `triage`; la recomendación requiere verificación humana. |
| SR-04 | Reporte `resident_report` que no está verificado. | Ruta `triage`; no se resuelve, rechaza ni incorpora a la cola automáticamente. |
| SR-05 | El reporte `streetlight_failure` contradice un estado contextual `on`. | Marca conflicto de datos y ruta `triage`; no descarta el reporte. |

## Prioridad heurística

La puntuación entre 0 y 100 usa estos pesos iniciales:

```text
score = 0.40 × pedestrian_use
      + 0.20 × age_score
      + 0.40 × sensitive_location

age_score = min(age_hours / 30, 1) × 100
```

La clasificación es `high` desde 75, `medium` desde 55 y `low` por debajo de
55. Si falta un factor, se redistribuyen proporcionalmente los pesos disponibles
y se informan el factor ausente y las advertencias. Si faltan todos, no se
inventa una puntuación. Un suelo de seguridad prevalece sobre la clasificación
del índice.

## Salvaguardas y límites

- Una puntuación no es probabilidad de accidente ni predicción de fallos,
  delitos o lesiones.
- Los valores de reglas, pesos y umbrales son ilustrativos y no se calibran
  utilizando los registros sintéticos.
- Los datos sintéticos y sus puntuaciones deben identificarse como simulados;
  no son evidencia sobre Málaga.
- Los reportes de residentes permanecen sin verificar hasta una decisión
  humana. Un estado contextual contradictorio genera triaje, no descarte.
- La cola ordena por revisión urgente, prioridad final, puntuación, antigüedad
  e identificador estable; `compare` expone el primer criterio que difiere.
