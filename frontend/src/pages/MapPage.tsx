import { useMemo, useState } from "react";
import { MapPin, SlidersHorizontal } from "lucide-react";
import IncidentDetails from "../components/IncidentDetails";
import { useIncidentData } from "../data/IncidentData";
import MapView from "../components/MapView";
import {
  categoryLabels,
  districts,
  filterDemoIncidents,
  priorityLabels,
  sourceLabel,
} from "../data/demo";
import type { DemoIncident, IncidentStatus, Priority } from "../types";

const all = "all";

export default function MapPage() {
  const { incidents, mode } = useIncidentData();
  const [district, setDistrict] = useState(all);
  const [category, setCategory] = useState(all);
  const [priority, setPriority] = useState(all);
  const [status, setStatus] = useState(all);
  const [source, setSource] = useState(all);
  const [selected, setSelected] = useState<DemoIncident | null>(null);
  const filtered = useMemo(
    () => filterDemoIncidents(incidents, { district, category, priority, status, source }),
    [category, district, incidents, priority, source, status],
  );
  const categories = [...new Set(incidents.map((incident) => incident.category))];
  const sources = [...new Set(incidents.map((incident) => incident.source))];

  return (
    <div className="page-stack map-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">Vista geográfica</span>
          <h1>Mapa de incidencias</h1>
          <p>Explora las incidencias disponibles y filtra por tipo, prioridad, estado o distrito.</p>
        </div>
        <span className="demo-indicator"><span /> {
          mode === "loading"
            ? "Conectando con la API"
            : mode === "api"
              ? "Datos de API"
              : "Datos simulados"
        }</span>
      </div>

      <div className="map-layout">
        <section className="map-card">
          <div className="filter-bar">
            <div className="filter-title"><SlidersHorizontal size={16} /> Filtros</div>
            <label>
              Distrito
              <select value={district} onChange={(event) => setDistrict(event.target.value)}>
                <option value={all}>Toda Málaga</option>
                {districts.map((item) => <option key={item.name}>{item.name}</option>)}
              </select>
            </label>
            <label>
              Tipo de incidencia
              <select value={category} onChange={(event) => setCategory(event.target.value)}>
                <option value={all}>Todos los tipos</option>
                {categories.map((item) => <option key={item} value={item}>{categoryLabels[item]}</option>)}
              </select>
            </label>
            <label>
              Prioridad
              <select value={priority} onChange={(event) => setPriority(event.target.value)}>
                <option value={all}>Todas</option>
                {(["high", "medium", "low"] as Priority[]).map((item) => (
                  <option key={item} value={item}>{priorityLabels[item]}</option>
                ))}
                <option value="none">Pendiente de triaje</option>
              </select>
            </label>
            <label>
              Estado
              <select value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value={all}>Todos</option>
                {(["reported", "pending", "assigned", "resolved"] as IncidentStatus[]).map((item) => (
                  <option key={item} value={item}>{statusLabel(item)}</option>
                ))}
              </select>
            </label>
            <label>
              Procedencia
              <select value={source} onChange={(event) => setSource(event.target.value)}>
                <option value={all}>Todas</option>
                {sources.map((item) => {
                  const sourceIncidents = incidents.filter(
                    (incident) => incident.source === item,
                  );
                  const isSimulated = sourceIncidents.every(
                    (incident) => incident.isSimulated,
                  );
                  return <option key={item} value={item}>{sourceLabel(item, isSimulated)}</option>;
                })}
              </select>
            </label>
          </div>
          <div className="map-canvas">
            <MapView
              incidents={filtered}
              district={district}
              onSelectIncident={setSelected}
            />
            {filtered.length === 0 ? (
              <div className="map-empty">No hay incidencias con estos filtros.</div>
            ) : !filtered.some(
              (incident) => incident.latitude !== null && incident.longitude !== null,
            ) ? (
              <div className="map-empty">Hay incidencias, pero no tienen coordenadas para mostrarlas.</div>
            ) : null}
            {selected && (
              <IncidentDetails incident={selected} onClose={() => setSelected(null)} />
            )}
          </div>
          <div className="map-footer">
            <div className="map-legend">
              <span><i className="legend-dot high" /> Alta</span>
              <span><i className="legend-dot medium" /> Media</span>
              <span><i className="legend-dot low" /> Baja</span>
              <span><i className="legend-dot none" /> Triaje</span>
              <span><i className="legend-ring" /> Revisión urgente</span>
            </div>
            <span>{filtered.length} {filtered.length === 1 ? "incidencia" : "incidencias"}</span>
          </div>
        </section>

        <aside className="map-side-card">
          <div className="side-card-heading">
            <div><span className="eyebrow">En esta vista</span><h2>{district === all ? "Toda Málaga" : district}</h2></div>
            <MapPin size={19} />
          </div>
          <p className="district-disclaimer">
            Las zonas y ubicaciones de esta demo son aproximadas y ficticias. Los círculos no representan límites oficiales de distritos o barrios.
          </p>
          <div className="district-list">
            {districts.map((item) => {
              const count = incidents.filter((incident) => incident.district === item.name).length;
              return (
                <button
                  className={`district-row ${district === item.name ? "is-selected" : ""}`}
                  key={item.name}
                  onClick={() => setDistrict(item.name)}
                >
                  <span>{item.name}</span><strong>{count}</strong>
                </button>
              );
            })}
          </div>
          <button className="text-button" onClick={() => setDistrict(all)}>Mostrar todos los distritos</button>
        </aside>
      </div>

      <div className="map-lower-note">
        <span>© OpenStreetMap contributors</span>
        <span>Las teselas requieren conexión a Internet. Las zonas de demo son aproximadas; consulta la procedencia de cada punto.</span>
      </div>
    </div>
  );
}

function statusLabel(status: IncidentStatus) {
  return {
    reported: "Reportada",
    pending: "Pendiente",
    assigned: "Asignada",
    resolved: "Resuelta",
    rejected: "Rechazada",
  }[status];
}
