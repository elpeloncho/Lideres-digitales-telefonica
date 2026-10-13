import { useState } from "react";
import { ArrowLeft, MapPin, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import MapView from "../components/MapView";
import { useIncidentData } from "../data/IncidentData";
import { categoryLabels } from "../data/demo";
import type { IncidentCategory } from "../types";

export default function ReportPage() {
  const { createReport } = useIncidentData();
  const [point, setPoint] = useState<[number, number] | null>(null);
  const [invalidPoint, setInvalidPoint] = useState(false);
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<IncidentCategory>("streetlight_failure");
  const [submitting, setSubmitting] = useState(false);
  const [submittedId, setSubmittedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <main className="public-shell">
      <header className="public-header">
        <Link to="/" className="brand-lockup"><span className="brand-mark">L</span><span>Luma <b>Málaga</b></span></Link>
        <span className="public-badge"><ShieldCheck size={15} /> Formulario de demostración</span>
      </header>
      <div className="public-content">
        <Link to="/" className="back-link"><ArrowLeft size={15} /> Volver a la aplicación</Link>
        <span className="eyebrow">Canal ciudadano</span>
        <h1>Comunica una incidencia</h1>
        <p className="public-intro">Ayúdanos a localizar una incidencia de alumbrado. No se solicitan datos personales.</p>
        <div className="public-warning">
          <strong>Este formulario solo registra avisos sintéticos de demostración.</strong>
          Si existe un peligro inmediato, contacta con los servicios de emergencia.
        </div>
        <form
          className="report-form"
          onSubmit={(event) => {
            event.preventDefault();
            if (!point) return;
            setSubmitting(true);
            setError(null);
            createReport({
              category,
              description: description.trim(),
              latitude: point[0],
              longitude: point[1],
            })
              .then((incident) => setSubmittedId(incident.id))
              .catch((requestError: unknown) => {
                setError(
                  requestError instanceof Error
                    ? requestError.message
                    : "No se pudo guardar el aviso sintético.",
                );
              })
              .finally(() => setSubmitting(false));
          }}
        >
          <label className="form-label">
            Tipo de incidencia
            <select value={category} onChange={(event) => {
              setCategory(event.target.value as IncidentCategory);
              setSubmittedId(null);
            }}>
              {Object.entries(categoryLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <label className="form-label">
            Descripción breve
            <textarea
              value={description}
              onChange={(event) => {
                setDescription(event.target.value.slice(0, 500));
                setSubmittedId(null);
                setError(null);
              }}
              minLength={10}
              maxLength={500}
              required
              placeholder="Describe lo que observas (10-500 caracteres)"
            />
            <span className="field-hint">{description.length}/500 caracteres. No incluyas información personal.</span>
          </label>
          <div className="form-label">
            <span>Ubicación aproximada</span>
            <div className="report-map">
              <MapView
                incidents={[]}
                district="all"
                onSelectPoint={(selectedPoint) => {
                  setPoint(selectedPoint);
                  setInvalidPoint(false);
                  setSubmittedId(null);
                  setError(null);
                }}
                onInvalidPoint={() => {
                  setPoint(null);
                  setInvalidPoint(true);
                  setSubmittedId(null);
                }}
                selectedPoint={point}
              />
            </div>
            <span className="field-hint"><MapPin size={14} /> {point ? `${point[0].toFixed(4)}, ${point[1].toFixed(4)}` : "Selecciona el punto en el mapa."}</span>
            {invalidPoint && <span className="location-error">Selecciona un punto dentro del área aproximada de la demo en Málaga.</span>}
          </div>
          <button className="button button-primary report-submit" type="submit" disabled={description.trim().length < 10 || !point || submitting}>
            {submitting ? "Guardando aviso sintético…" : "Enviar aviso de demostración"}
          </button>
          {submittedId && (
            <div className="preview-notice" role="status">
              <strong>Aviso de demostración guardado: {submittedId}.</strong>
              Se ha añadido al triaje operativo. Es un registro sintético y no se transmite a ningún servicio municipal.
            </div>
          )}
          {error && <div className="location-error" role="alert">{error}</div>}
        </form>
        <p className="privacy-note">Este formulario guarda solo avisos sintéticos en el almacén local de la demo. No hay autenticación ni conexión con servicios municipales.</p>
      </div>
    </main>
  );
}
