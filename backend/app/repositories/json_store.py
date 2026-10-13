import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from pydantic import ValidationError

from app.engine.models import (
    DecisionInput,
    IncidentStatus,
    SourceType,
    VerificationStatus,
)
from app.services.geography import classify_demo_district


class StoreError(RuntimeError):
    """The persistent store cannot be safely read or updated."""


class IncidentNotFound(StoreError):
    """The requested incident does not exist."""


class WorkflowConflict(StoreError):
    """The requested workflow action is invalid for the current incident."""


class JsonStore:
    schema_version = 1

    def __init__(self, store_dir: Path, seed_file: Path):
        self.store_dir = store_dir
        self.seed_file = seed_file
        self.incidents_path = store_dir / "incidents.json"
        self.history_path = store_dir / "history.jsonl"
        self.decisions_path = store_dir / "decisions.jsonl"
        self._lock = RLock()

    def list_incidents(self) -> list[DecisionInput]:
        with self._lock:
            document = self._read_document()
            return [DecisionInput.model_validate(item) for item in document["incidents"]]

    def get_incident(self, incident_id: str) -> DecisionInput | None:
        return next(
            (item for item in self.list_incidents() if item.id == incident_id),
            None,
        )

    def list_history(self) -> list[dict[str, Any]]:
        with self._lock:
            self._read_document()
            return self._read_jsonl(self.history_path)

    def create_report(
        self,
        *,
        category: str,
        description: str,
        latitude: float,
        longitude: float,
    ) -> DecisionInput:
        with self._lock:
            document = self._read_document()
            ids = {item["id"] for item in document["incidents"]}
            index = 1
            while f"RPT-{index:04d}" in ids:
                index += 1
            incident = DecisionInput(
                id=f"RPT-{index:04d}",
                title="Aviso ciudadano de demostración",
                description=description,
                category=category,
                status=IncidentStatus.REPORTED,
                source_type=SourceType.RESIDENT_REPORT,
                source_name="public_demo_form",
                is_synthetic=True,
                verification=VerificationStatus.UNVERIFIED,
                latitude=latitude,
                longitude=longitude,
                district=classify_demo_district(latitude, longitude),
                created_at=datetime.now(UTC),
            )
            document["incidents"].append(
                incident.model_dump(mode="json", exclude={"age_hours"})
                | {"age_hours": None}
            )
            self._commit(
                document,
                event_type="resident_report_created",
                incident=incident,
                actor="public_demo",
                details={"source": "synthetic_demo_form"},
            )
            return incident

    def apply_workflow_action(
        self,
        incident_id: str,
        *,
        action: str,
        actor: str,
        assignee: str | None = None,
        note: str | None = None,
    ) -> DecisionInput:
        with self._lock:
            document = self._read_document()
            records = document["incidents"]
            index = next(
                (i for i, item in enumerate(records) if item["id"] == incident_id),
                None,
            )
            if index is None:
                raise IncidentNotFound(f"No existe la incidencia {incident_id}.")
            current = DecisionInput.model_validate(records[index])
            if not current.is_simulated:
                raise WorkflowConflict(
                    "Las acciones de la demo solo se permiten sobre registros sintéticos."
                )
            changes: dict[str, Any]
            event_details: dict[str, Any] = {"note": note} if note else {}
            if action == "accept" and current.status == IncidentStatus.REPORTED:
                changes = {
                    "status": IncidentStatus.PENDING,
                    "verification": VerificationStatus.VERIFIED,
                }
            elif action == "reject" and current.status == IncidentStatus.REPORTED:
                changes = {
                    "status": IncidentStatus.REJECTED,
                    "verification": VerificationStatus.REJECTED,
                }
            elif action == "assign" and current.status in {
                IncidentStatus.PENDING,
                IncidentStatus.ASSIGNED,
            }:
                if not assignee:
                    raise WorkflowConflict("La asignación requiere una persona responsable.")
                changes = {
                    "status": IncidentStatus.ASSIGNED,
                    "assignee": assignee,
                }
                event_details["assignee"] = assignee
            elif action == "resolve" and current.status == IncidentStatus.ASSIGNED:
                changes = {"status": IncidentStatus.RESOLVED}
            elif action == "reopen" and current.status == IncidentStatus.RESOLVED:
                changes = {"status": IncidentStatus.PENDING, "assignee": None}
            else:
                raise WorkflowConflict(
                    f"La acción {action} no está permitida para el estado "
                    f"{current.status.value}."
                )

            updated = current.model_copy(update=changes)
            records[index] = updated.model_dump(mode="json", exclude={"age_hours"}) | {
                "age_hours": current.age_hours
            }
            self._commit(
                document,
                event_type=f"incident_{action}",
                incident=updated,
                actor=actor,
                details=event_details,
            )
            return updated

    def _commit(
        self,
        document: dict[str, Any],
        *,
        event_type: str,
        incident: DecisionInput,
        actor: str,
        details: dict[str, Any],
    ) -> None:
        self._read_jsonl(self.history_path)
        previous_document = self.incidents_path.read_bytes()
        previous_history = self.history_path.read_bytes()
        sequence = document["revision"] + 1
        event = {
            "sequence": sequence,
            "event_id": f"event-{sequence:06d}",
            "event_type": event_type,
            "incident_id": incident.id,
            "actor": actor,
            "occurred_at": datetime.now(UTC).isoformat(),
            "details": details,
        }
        document["revision"] = sequence
        try:
            self._write_jsonl(self.history_path, [event])
            self._write_document(document)
        except OSError as exc:
            try:
                self._restore_file(self.incidents_path, previous_document)
                self._restore_file(self.history_path, previous_history)
            except OSError as restore_error:
                raise StoreError(
                    "Falló una escritura y no se pudo restaurar completamente el almacén."
                ) from restore_error
            raise StoreError(
                "No se pudo guardar la acción; el almacén se restauró al estado anterior."
            ) from exc

    def _restore_file(self, path: Path, content: bytes) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.restore.", suffix=".tmp", dir=self.store_dir
        )
        try:
            with os.fdopen(descriptor, "wb") as file:
                file.write(content)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_name, path)
        except OSError:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def _read_document(self) -> dict[str, Any]:
        if not self.incidents_path.exists():
            self._initialize_from_seed()

        try:
            document = json.loads(self.incidents_path.read_text(encoding="utf-8"))
            if document.get("schema_version") != self.schema_version:
                raise StoreError(
                    f"Versión de esquema no soportada en {self.incidents_path}."
                )
            revision = document["revision"]
            records = document["incidents"]
            if not isinstance(revision, int) or revision < 0 or not isinstance(records, list):
                raise StoreError(f"Estructura inválida en {self.incidents_path}.")
            for record in records:
                DecisionInput.model_validate(record)
        except StoreError:
            raise
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
            raise StoreError(
                f"No se puede leer el almacén de incidencias {self.incidents_path}; "
                "no se sobrescribieron sus datos."
            ) from exc

        events = self._read_jsonl(self.history_path)
        last_sequence = events[-1]["sequence"] if events else 0
        if last_sequence != revision:
            raise StoreError(
                "El almacén y el historial no son coherentes "
                f"(revision={revision}, última secuencia={last_sequence})."
            )
        return document

    def _initialize_from_seed(self) -> None:
        existing = [
            path
            for path in (self.history_path, self.decisions_path)
            if path.exists()
        ]
        if existing:
            raise StoreError(
                "El almacén está incompleto; se conserva el contenido existente: "
                + ", ".join(str(path) for path in existing)
            )
        if not self.seed_file.is_file():
            raise StoreError(f"No se encuentra el conjunto inicial {self.seed_file}.")
        try:
            seed_records = json.loads(self.seed_file.read_text(encoding="utf-8"))
            records = [DecisionInput.model_validate(item) for item in seed_records]
        except (OSError, json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise StoreError(
                f"El conjunto inicial {self.seed_file} no contiene incidencias válidas."
            ) from exc
        ids = [record.id for record in records]
        if len(ids) != len(set(ids)):
            raise StoreError("El conjunto inicial contiene identificadores duplicados.")

        self.store_dir.mkdir(parents=True, exist_ok=True)
        events = [
            {
                "sequence": index,
                "event_id": f"seed-{record.id}",
                "event_type": "incident_seeded",
                "incident_id": record.id,
                "actor": "system",
                "occurred_at": datetime.now(UTC).isoformat(),
                "details": {"source": record.source_name},
            }
            for index, record in enumerate(records, start=1)
        ]
        self._write_jsonl(self.history_path, events)
        self._write_document(
            {
                "schema_version": self.schema_version,
                "revision": len(records),
                "incidents": [
                    record.model_dump(mode="json", exclude={"age_hours"})
                    | {"age_hours": record.age_hours}
                    for record in records
                ],
            }
        )

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            if self.incidents_path.exists():
                raise StoreError(f"Falta el registro de actividad {path}.")
            return []
        events: list[dict[str, Any]] = []
        try:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                event = json.loads(line)
                if not isinstance(event, dict) or event.get("sequence") != len(events) + 1:
                    raise StoreError(f"Secuencia inválida en {path}, línea {line_number}.")
                events.append(event)
        except (OSError, json.JSONDecodeError) as exc:
            raise StoreError(f"El registro {path} está corrupto; no se sobrescribió.") from exc
        return events

    def _write_jsonl(self, path: Path, events: list[dict[str, Any]]) -> None:
        with path.open("a", encoding="utf-8") as file:
            for event in events:
                file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            file.flush()
            os.fsync(file.fileno())

    def _write_document(self, document: dict[str, Any]) -> None:
        self.store_dir.mkdir(parents=True, exist_ok=True)
        if self.incidents_path.exists():
            backup = self.incidents_path.with_suffix(".json.bak")
            shutil.copy2(self.incidents_path, backup)

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".incidents.", suffix=".tmp", dir=self.store_dir
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                json.dump(document, file, ensure_ascii=False, indent=2, sort_keys=True)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_name, self.incidents_path)
            directory_fd = os.open(self.store_dir, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
