import { useState } from "react";
import { Clock3, MapPin, ShieldAlert, X } from "lucide-react";
import { categoryLabels, priorityLabels, sourceLabel } from "../data/demo";
import type { WorkflowAction } from "../data/api";
import type { DemoIncident } from "../types";

export default function IncidentDetails({
  incident,
  onClose,
  onWorkflow,
}: {
  incident: DemoIncident;
  onClose: () => void;
  onWorkflow?: (action: WorkflowAction, assignee?: string) => void | Promise<void>;
}) {
  const [assignee, setAssignee] = useState(incident.assignee ?? "Lucía Díaz");
  return (
    <aside className="detail-panel" aria-label={`Detalle ${incident.id}`}>
      <div className="detail-topline">
        <span className="eyebrow">{incident.id}</span>
        <button className="icon-button" onClick={onClose} aria-label="Cerrar detalle">
          <X size={18} />
        </button>
      </div>
      <h2>{incident.title}</h2>
      <div className="tag-row">
        <span className={`priority-tag priority-${incident.priority ?? "none"}`}>
          {incident.priority ? `Prioridad ${priorityLabels[incident.priority].toLowerCase()}` : "Pendiente de triaje"}
        </span>
        <span className="source-tag">{sourceLabel(incident.source, incident.isSimulated)}</span>
      </div>
      <p className="detail-description">{incident.description}</p>
      <div className="detail-meta">
        <span><MapPin size={15} /> {incident.neighborhood}, {incident.district}</span>
        <span><Clock3 size={15} /> {incident.ageHours === null ? "Antigüedad no disponible" : `${incident.ageHours} h de antigüedad`}</span>
        <span>{categoryLabels[incident.category]}</span>
      </div>
      <div className="detail-score">
        <div>
          <span className="eyebrow">Índice experimental</span>
          <strong>{incident.score === null ? "—" : incident.score.toFixed(1)}</strong>
        </div>
        <span className="score-caption">No es una probabilidad ni una evaluación oficial de riesgo.</span>
      </div>
      <section className="detail-section">
        <h3>Factores de prioridad</h3>
        <div className="factor-list">
          {(
            [
              ["Uso peatonal", incident.factors.pedestrianUse],
              ["Antigüedad normalizada", incident.factors.age],
              ["Importancia del entorno", incident.factors.sensitiveLocation],
            ] as const
          ).map(([label, factor]) => (
            <div className="factor-row" key={label}>
              <span>{label}</span>
              {factor.value === null ? (
                <strong>Sin dato</strong>
              ) : (
                <strong>
                  {factor.value.toFixed(1)} · peso {factor.weight?.toFixed(2)} · +
                  {factor.contribution?.toFixed(1)}
                </strong>
              )}
            </div>
          ))}
        </div>
        <p className="muted-copy">
          {incident.isSimulated
            ? "Los factores de este registro pertenecen al conjunto artificial de demostración."
            : "Los factores y pesos se calculan con la configuración vigente del motor."}
        </p>
      </section>
      <section className="detail-section">
        <h3><ShieldAlert size={16} /> Reglas y revisión</h3>
        {incident.rules.length > 0 ? (
          <div className="rule-list">
            {incident.rules.map((rule) => (
              <span key={rule} className="rule-pill">{rule}</span>
            ))}
          </div>
        ) : (
          <p className="muted-copy">No hay reglas de seguridad activadas.</p>
        )}
        {incident.urgent && <p className="urgent-note">Requiere revisión humana urgente.</p>}
      </section>
      <section className="detail-section">
        <h3>Datos ausentes</h3>
        {incident.missingFactors.length ? (
          <p className="muted-copy">{incident.missingFactors.join(", ")}. No se han convertido en cero.</p>
        ) : (
          <p className="muted-copy">No faltan factores en este registro de demostración.</p>
        )}
      </section>
      <section className="detail-section">
        <h3>Recomendación del motor</h3>
        <p className="recommendation-text">{incident.rationale.join(" ")}</p>
      </section>
      {onWorkflow && (
        <section className="detail-section">
          <h3>Acción de demostración</h3>
          {incident.status === "reported" && (
            <div className="tag-row">
              <button className="button button-primary" onClick={() => onWorkflow("accept")}>Validar aviso</button>
              <button className="button button-secondary" onClick={() => onWorkflow("reject")}>Rechazar aviso</button>
            </div>
          )}
          {incident.status === "pending" && (
            <div className="workflow-assignment">
              <label className="form-label">
                Responsable
                <input value={assignee} onChange={(event) => setAssignee(event.target.value)} maxLength={80} />
              </label>
              <button className="button button-primary" disabled={assignee.trim().length < 2} onClick={() => onWorkflow("assign", assignee.trim())}>Asignar incidencia</button>
            </div>
          )}
          {incident.status === "assigned" && (
            <>
              <p className="muted-copy">Responsable: {incident.assignee ?? "Sin asignar"}</p>
              <button className="button button-primary" onClick={() => onWorkflow("resolve")}>Marcar como resuelta</button>
            </>
          )}
          {incident.status === "resolved" && (
            <button className="button button-secondary" onClick={() => onWorkflow("reopen")}>Reabrir incidencia</button>
          )}
          {incident.status === "rejected" && <p className="muted-copy">Este aviso fue rechazado y permanece en el historial.</p>}
        </section>
      )}
      <button className="button button-secondary detail-action" onClick={onClose}>
        Cerrar detalle <X size={15} />
      </button>
    </aside>
  );
}
