import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bell,
  CheckCircle2,
  ChevronDown,
  ClipboardList,
  Clock3,
  FileText,
  Gauge,
  Lightbulb,
  Map,
  Menu,
  Search,
  Shield,
  UserRound,
  Users,
  X,
} from "lucide-react";
import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import IncidentDetails from "./components/IncidentDetails";
import { IncidentDataProvider, useIncidentData } from "./data/IncidentData";
import { fetchHistory, type ActivityEvent, type WorkflowAction } from "./data/api";
import MapView from "./components/MapView";
import MapPage from "./pages/MapPage";
import ReportPage from "./pages/ReportPage";
import {
  categoryLabels,
  filterDemoIncidents,
  priorityLabels,
  sourceLabel,
} from "./data/demo";
import type { DemoIncident, UserRole } from "./types";

const technicianNavigation = [
  { label: "Resumen", to: "/", icon: Gauge },
  { label: "Mapa de incidencias", to: "/mapa", icon: Map },
  { label: "Cola de trabajo", to: "/cola", icon: ClipboardList },
  { label: "Incidencias", to: "/incidencias", icon: Lightbulb },
  { label: "Perfil de demostración", to: "/perfil", icon: UserRound },
];

const operationsNavigation = [
  { label: "Alertas", to: "/alertas", icon: Bell },
  { label: "Bandeja de triaje", to: "/triaje", icon: Shield },
  { label: "Historial", to: "/historial", icon: Activity },
  { label: "Metodología", to: "/metodologia", icon: FileText },
  { label: "Perfil de demostración", to: "/perfil", icon: UserRound },
];

export default function App() {
  const location = useLocation();
  if (location.pathname === "/reportar") {
    return <IncidentDataProvider><ReportPage /></IncidentDataProvider>;
  }
  return (
    <IncidentDataProvider>
      <OperationsApp />
    </IncidentDataProvider>
  );
}

function OperationsApp() {
  const { incidents, mode, error, applyWorkflow } = useIncidentData();
  const [role, setRole] = useState<UserRole>("technician");
  const [selected, setSelected] = useState<DemoIncident | null>(null);
  const [workflowError, setWorkflowError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const navigation = role === "technician" ? technicianNavigation : operationsNavigation;

  const handleWorkflow = async (
    incidentId: string,
    action: WorkflowAction,
    assignee?: string,
  ) => {
    setWorkflowError(null);
    try {
      const updated = await applyWorkflow(
        incidentId,
        action,
        role === "technician" ? "technician_demo" : "operations_demo",
        assignee,
      );
      setSelected((current) => current?.id === updated.id ? updated : current);
    } catch (requestError: unknown) {
      setWorkflowError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo guardar la acción.",
      );
    }
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`}>
        <Link to="/" className="brand-lockup" onClick={() => setMobileNavOpen(false)}>
          <span className="brand-mark">L</span><span>Luma <b>Málaga</b></span>
        </Link>
        <div className="workspace-label">ESPACIO DE TRABAJO</div>
        <nav className="primary-navigation" aria-label="Navegación principal">
          {navigation.map(({ label, to, icon: Icon }) => (
            <NavLink
              to={to}
              end={to === "/"}
              key={to}
              className={({ isActive }) => `nav-link ${isActive ? "nav-active" : ""}`}
              onClick={() => setMobileNavOpen(false)}
            >
              <Icon size={18} strokeWidth={1.9} /><span>{label}</span>
              {label === "Bandeja de triaje" && (
                <span className="nav-count">{incidents.filter((item) => item.status === "reported").length}</span>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <Link to="/reportar" className="public-link" onClick={() => setMobileNavOpen(false)}>
          <Users size={17} /><span>Vista para residentes</span><ArrowRight size={15} />
        </Link>
        <div className="sidebar-disclaimer">
          <span className="tiny-status" />
          <div><strong>Entorno de demostración</strong><small>Procedencia visible en cada incidencia</small></div>
        </div>
        <div className="sidebar-user">
          <span className="avatar">LD</span>
          <div><strong>{role === "technician" ? "Lucía Díaz" : "Equipo de operaciones"}</strong><small>{roleLabel(role)}</small></div>
          <ChevronDown size={15} />
        </div>
      </aside>

      {mobileNavOpen && <button className="mobile-scrim" onClick={() => setMobileNavOpen(false)} aria-label="Cerrar navegación" />}
      <main className="main-area">
        <header className="topbar">
          <button className="icon-button mobile-menu" onClick={() => setMobileNavOpen(!mobileNavOpen)} aria-label="Abrir navegación">
            {mobileNavOpen ? <X size={19} /> : <Menu size={19} />}
          </button>
          <div className="breadcrumb"><span>Operaciones</span><span>/</span><strong>{currentPageName(location.pathname)}</strong></div>
          <div className="topbar-actions">
            <label className="role-picker">
              <Users size={15} />
              <select aria-label="Cambiar perfil de demostración" value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
                <option value="technician">Perfil técnico</option>
                <option value="operations">Perfil operaciones</option>
              </select>
            </label>
            <button className="icon-button notification-button" aria-label="Notificaciones">
              <Bell size={18} /><i />
            </button>
            <span className="topbar-avatar">{role === "technician" ? "LD" : "OP"}</span>
          </div>
        </header>
        <div className="demo-banner">
          <AlertTriangle size={16} />
          <span>
            {mode === "loading" ? (
              <><strong>Conectando:</strong> cargando incidencias de la API…</>
            ) : mode === "demo-fallback" ? (
              <><strong>API no disponible:</strong> se muestran datos locales de demo. {error}</>
            ) : (
              <><strong>Datos cargados desde la API.</strong> Consulta la procedencia y la etiqueta de cada incidencia.</>
            )}
          </span>
          <Link to="/metodologia">Cómo funciona</Link>
        </div>
        <div className="content-area">
          {workflowError && <div className="workflow-error" role="alert">{workflowError}</div>}
          <Routes>
            <Route path="/" element={<Dashboard role={role} incidents={incidents} onSelect={setSelected} />} />
            <Route path="/mapa" element={<MapPage />} />
            <Route path="/cola" element={<IncidentListPage title="Cola de trabajo" subtitle="Recomendaciones experimentales del motor; la decisión siempre es humana." incidents={incidents.filter((item) => !["reported", "resolved", "rejected"].includes(item.status))} onSelect={setSelected} search={search} setSearch={setSearch} />} />
            <Route path="/incidencias" element={<IncidentListPage title="Incidencias" subtitle="Explora los registros y su procedencia." incidents={incidents} onSelect={setSelected} search={search} setSearch={setSearch} />} />
            <Route path="/alertas" element={<IncidentListPage title="Alertas" subtitle="Casos que requieren atención según reglas experimentales." incidents={incidents.filter((item) => item.urgent || item.priority === "high")} onSelect={setSelected} search={search} setSearch={setSearch} />} />
            <Route path="/triaje" element={<TriagePage incidents={incidents} onSelect={setSelected} onWorkflow={(id, action) => handleWorkflow(id, action)} />} />
            <Route path="/historial" element={<HistoryPage />} />
            <Route path="/metodologia" element={<MethodologyPage />} />
            <Route path="/perfil" element={<ProfilePage role={role} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        {selected && <div className="details-scrim" onClick={() => setSelected(null)}><div onClick={(event) => event.stopPropagation()}><IncidentDetails incident={selected} onClose={() => setSelected(null)} onWorkflow={(action, assignee) => handleWorkflow(selected.id, action, assignee)} /></div></div>}
      </main>
    </div>
  );
}

function Dashboard({
  role,
  incidents,
  onSelect,
}: {
  role: UserRole;
  incidents: DemoIncident[];
  onSelect: (incident: DemoIncident) => void;
}) {
  const [recentEvents, setRecentEvents] = useState<ActivityEvent[]>([]);
  const [activityError, setActivityError] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetchHistory(controller.signal)
      .then(setRecentEvents)
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) return;
        setActivityError(requestError instanceof Error ? requestError.message : "No se pudo cargar la actividad.");
      });
    return () => controller.abort();
  }, []);

  const active = incidents.filter((item) => !["resolved", "rejected"].includes(item.status));
  const urgent = active.filter((item) => item.urgent);
  const assigned = incidents.filter((item) => item.status === "assigned");
  const resolved = incidents.filter((item) => item.status === "resolved");
  const priorityHigh = active.filter((item) => item.priority === "high");
  const queue = [...active].sort((a, b) => Number(b.urgent) - Number(a.urgent) || (b.score ?? -1) - (a.score ?? -1)).slice(0, 5);

  return (
    <div className="page-stack">
      <div className="page-heading dashboard-heading">
        <div><span className="eyebrow">Martes, 13 de octubre de 2026 · Centro de operaciones</span><h1>{role === "technician" ? "Buenos días, Lucía" : "Vista de operaciones"}</h1><p>Un resumen de las incidencias y recomendaciones del entorno de demostración.</p></div>
        <Link to="/mapa" className="button button-primary">Abrir mapa <ArrowRight size={16} /></Link>
      </div>
      <div className="stats-grid">
        <StatCard icon={<Lightbulb size={17} />} label="Incidencias activas" value={String(active.length).padStart(2, "0")} note="Todas sintéticas o ficticias" tone="mint" />
        <StatCard icon={<AlertTriangle size={17} />} label="Prioridad alta" value={String(priorityHigh.length).padStart(2, "0")} note={`${urgent.length} con revisión urgente`} tone="rose" />
        <StatCard icon={<Users size={17} />} label="Asignadas" value={String(assigned.length).padStart(2, "0")} note="Asignación de demostración" tone="blue" />
        <StatCard icon={<CheckCircle2 size={17} />} label="Resueltas en demo" value={String(resolved.length).padStart(2, "0")} note="No implica reparación real" tone="amber" />
      </div>
      <div className="dashboard-grid">
        <section className="surface-card dashboard-map-card">
          <div className="card-heading"><div><span className="eyebrow">Geografía</span><h2>Incidencias por Málaga</h2></div><Link to="/mapa" className="subtle-link">Ver mapa <ArrowRight size={15} /></Link></div>
          <div className="dashboard-map"><MapView incidents={active} district="all" onSelectIncident={onSelect} /></div>
          <div className="card-footnote"><span><i className="legend-dot high" /> Alta</span><span><i className="legend-dot medium" /> Media</span><span><i className="legend-dot low" /> Baja</span><small>Ubicaciones ficticias · OSM</small></div>
        </section>
        <section className="surface-card queue-card">
          <div className="card-heading"><div><span className="eyebrow">Sugerencias, no órdenes</span><h2>Cola recomendada</h2></div><Link to="/cola" className="icon-link" aria-label="Ver cola"><ArrowRight size={17} /></Link></div>
          <div className="queue-list">
            {queue.map((incident, index) => (
              <button className="queue-row" key={incident.id} onClick={() => onSelect(incident)}>
                <span className="queue-index">{String(index + 1).padStart(2, "0")}</span>
                <span className={`queue-priority-dot ${incident.priority ?? "none"}`} />
                <span className="queue-row-main"><strong>{incident.title}</strong><small>{incident.district} · {sourceLabel(incident.source, incident.isSimulated)}</small></span>
                <span className="queue-score">{incident.score === null ? "—" : incident.score.toFixed(0)}</span>
              </button>
            ))}
          </div>
          <div className="queue-foot"><span><Clock3 size={14} /> Actualizado para la demo</span><Link to="/cola">Revisar cola</Link></div>
        </section>
      </div>
      <div className="dashboard-bottom-grid">
        <section className="surface-card activity-card">
          <div className="card-heading"><div><span className="eyebrow">Última actividad</span><h2>Registro de demostración</h2></div><Link to="/historial" className="subtle-link">Ver historial <ArrowRight size={15} /></Link></div>
          {recentEvents.slice(0, 3).map((event) => (
            <div className="activity-row" key={event.eventId}>
              <span className={`activity-icon ${activityTone(event.eventType)}`}>
                {event.eventType.includes("reject") ? <AlertTriangle size={16} /> : event.eventType.includes("assign") ? <Users size={16} /> : <Activity size={16} />}
              </span>
              <span>
                <strong>{activityTitle(event.eventType)}</strong>
                <small>{event.incidentId} · {event.actor}</small>
              </span>
              <span className="activity-status">{new Date(event.occurredAt).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })}</span>
            </div>
          ))}
          {activityError && <p className="muted-copy" role="alert">{activityError}</p>}
          {!activityError && recentEvents.length === 0 && <p className="muted-copy">Todavía no hay actividad registrada.</p>}
        </section>
        <section className="method-card">
          <span className="method-icon"><Shield size={19} /></span><span className="eyebrow">Transparencia</span><h2>El sistema recomienda. Tú decides.</h2><p>Las prioridades son experimentales y muestran los factores disponibles, las reglas activadas y los datos ausentes.</p><Link to="/metodologia">Ver metodología <ArrowRight size={15} /></Link>
        </section>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, note, tone }: { icon: React.ReactNode; label: string; value: string; note: string; tone: string }) {
  return <article className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><span className="stat-label">{label}</span><strong className="stat-value">{value}</strong><span className="stat-note">{note}</span></article>;
}

function IncidentListPage({ title, subtitle, incidents, onSelect, search, setSearch }: { title: string; subtitle: string; incidents: DemoIncident[]; onSelect: (incident: DemoIncident) => void; search: string; setSearch: (search: string) => void }) {
  const filtered = useMemo(
    () => filterDemoIncidents(incidents, { search }),
    [incidents, search],
  );
  return (
    <div className="page-stack">
      <div className="page-heading"><div><span className="eyebrow">Gestión técnica</span><h1>{title}</h1><p>{subtitle}</p></div><span className="demo-indicator"><span /> Datos simulados</span></div>
      <section className="surface-card table-card">
        <div className="table-toolbar"><div className="table-count">{filtered.length} registros</div><label className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar incidencia o distrito" /></label></div>
        {filtered.length ? (
          <div className="incident-table">
            <div className="incident-table-head"><span>Incidencia</span><span>Zona</span><span>Prioridad</span><span>Estado</span><span>Procedencia</span><span /></div>
            {filtered.map((incident) => (
              <button className="incident-table-row" key={incident.id} onClick={() => onSelect(incident)}>
                <span className="incident-name"><i className={`queue-priority-dot ${incident.priority ?? "none"}`} /><span><strong>{incident.title}</strong><small>{incident.id} · {categoryLabels[incident.category]}</small></span></span>
                <span className="table-zone">{incident.neighborhood}<small>{incident.district}</small></span>
                <span>{incident.priority ? <span className={`priority-tag priority-${incident.priority}`}>{priorityLabels[incident.priority]}</span> : <span className="priority-tag priority-none">Sin puntuar</span>}</span>
                <span className={`status-text status-${incident.status}`}>{statusLabel(incident.status)}</span>
                <span className="source-tag">{sourceLabel(incident.source, incident.isSimulated)}</span>
                <ArrowRight size={16} className="row-arrow" />
              </button>
            ))}
          </div>
        ) : <div className="empty-state"><Search size={22} /><strong>No se encontraron incidencias</strong><span>Prueba con otro término de búsqueda.</span></div>}
      </section>
    </div>
  );
}

function TriagePage({
  incidents,
  onSelect,
  onWorkflow,
}: {
  incidents: DemoIncident[];
  onSelect: (incident: DemoIncident) => void;
  onWorkflow: (incidentId: string, action: WorkflowAction) => void;
}) {
  const reports = incidents.filter((incident) => incident.status === "reported");
  return (
    <div className="page-stack">
      <div className="page-heading"><div><span className="eyebrow">Revisión humana requerida</span><h1>Bandeja de triaje</h1><p>Los avisos ciudadanos no pasan a la cola operativa sin validación.</p></div><span className="demo-indicator"><span /> Datos simulados</span></div>
      <div className="triage-callout"><Shield size={18} /><span><strong>Sin automatismos de aceptación.</strong> Revisa la ubicación y la información disponible antes de cualquier acción.</span></div>
      <section className="surface-card triage-list">
        {reports.map((incident) => (
          <article className="triage-row" key={incident.id}>
            <span className="triage-alert"><AlertTriangle size={17} /></span>
            <div className="triage-main"><span className="eyebrow">{incident.id} · {incident.district}</span><h2>{incident.title}</h2><p>{incident.description}</p><div className="tag-row"><span className="source-tag">Aviso simulado</span><span className="priority-tag priority-none">Sin prioridad asignada</span><span className="missing-tag">{incident.missingFactors.length} factores ausentes</span></div></div>
            <div className="triage-actions">
              <button className="button button-secondary" onClick={() => onSelect(incident)}>Revisar <ArrowRight size={15} /></button>
              <button className="button button-primary" onClick={() => onWorkflow(incident.id, "accept")}>Validar</button>
              <button className="button button-secondary" onClick={() => onWorkflow(incident.id, "reject")}>Rechazar</button>
            </div>
          </article>
        ))}
        {!reports.length && <div className="empty-state"><CheckCircle2 size={22} /><strong>La bandeja está vacía</strong><span>No hay reportes que requieran triaje.</span></div>}
      </section>
    </div>
  );
}

function HistoryPage() {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchHistory(controller.signal)
      .then(setEvents)
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) return;
        setError(requestError instanceof Error ? requestError.message : "No se pudo cargar el historial.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);

  return (
    <div className="page-stack">
      <div className="page-heading">
        <div><span className="eyebrow">Trazabilidad</span><h1>Historial</h1><p>Acciones persistidas en el almacén sintético local de la demo.</p></div>
      </div>
      {error && <div className="workflow-error" role="alert">{error}</div>}
      <section className="surface-card history-list">
        {events.map((event) => (
          <div className="history-row" key={event.eventId}>
            <span className={`activity-icon ${event.eventType.includes("reject") ? "red" : event.eventType.includes("assign") ? "orange" : "green"}`}>
              {event.eventType.includes("reject") ? <AlertTriangle size={16} /> : event.eventType.includes("assign") ? <Users size={16} /> : <Activity size={16} />}
            </span>
            <span className="history-main">
              <strong>{activityTitle(event.eventType)}</strong>
              <small>{event.incidentId} · {event.actor}{typeof event.details.assignee === "string" ? ` · ${event.details.assignee}` : ""}</small>
            </span>
            <span className="history-time">{new Date(event.occurredAt).toLocaleString("es-ES")}</span>
            <span className="source-tag">Demo</span>
          </div>
        ))}
        {!loading && !error && events.length === 0 && <div className="empty-state"><Activity size={22} /><strong>Aún no hay actividad</strong><span>Las acciones aparecerán aquí al reportar o actualizar incidencias.</span></div>}
        {loading && <div className="empty-state">Cargando historial…</div>}
      </section>
    </div>
  );
}

function activityTitle(eventType: string) {
  const titles: Record<string, string> = {
    incident_seeded: "Incidencia sintética inicializada",
    resident_report_created: "Aviso sintético recibido y enviado a triaje",
    incident_accept: "Aviso validado por una persona",
    incident_reject: "Aviso rechazado tras revisión",
    incident_assign: "Incidencia asignada",
    incident_resolve: "Incidencia marcada como resuelta",
    incident_reopen: "Incidencia reabierta",
  };
  return titles[eventType] ?? "Actividad de incidencia";
}

function activityTone(eventType: string) {
  if (eventType.includes("reject")) return "red";
  if (eventType.includes("assign")) return "orange";
  return "green";
}

function MethodologyPage() {
  return (
    <div className="page-stack">
      <div className="page-heading"><div><span className="eyebrow">Explicabilidad</span><h1>Metodología y límites</h1><p>Las recomendaciones sirven para explorar el prototipo; no sustituyen el criterio profesional.</p></div></div>
      <div className="methodology-grid">
        <section className="surface-card methodology-card"><span className="method-icon"><Gauge size={18} /></span><span className="eyebrow">Índice heurístico experimental</span><h2>Una puntuación explicable, no una predicción</h2><div className="formula">0,40 × uso peatonal<br />+ 0,20 × antigüedad<br />+ 0,40 × importancia del entorno</div><div className="thresholds"><span><i className="legend-dot high" /> Alta <b>≥ 75</b></span><span><i className="legend-dot medium" /> Media <b>55–74</b></span><span><i className="legend-dot low" /> Baja <b>&lt; 55</b></span></div><p>La antigüedad se normaliza con una referencia de 30 horas. Si faltan datos, no se sustituyen por cero: la puntuación es parcial o queda sin calcular.</p></section>
        <section className="surface-card methodology-card"><span className="method-icon"><Shield size={18} /></span><span className="eyebrow">Reglas de seguridad</span><h2>Primero revisión y cautela</h2><div className="rule-method"><strong>SR-01</strong><span>Poste dañado o riesgo eléctrico: prioridad mínima alta y revisión urgente.</span></div><div className="rule-method"><strong>SR-02</strong><span>Fallo en entorno de importancia alta: suelo de prioridad alta.</span></div><div className="rule-method"><strong>SR-03–05</strong><span>Datos incompletos, aviso sin verificar o conflicto: derivar a triaje humano.</span></div><p>Las reglas y los pesos son ilustrativos y están pendientes de validación profesional.</p></section>
      </div>
      <div className="method-disclaimer"><AlertTriangle size={17} /><span><strong>No es una probabilidad de accidente.</strong> Ningún registro, puntuación o ubicación de esta demo constituye evidencia sobre Málaga.</span></div>
    </div>
  );
}

function ProfilePage({ role }: { role: UserRole }) {
  return (
    <div className="page-stack">
      <div className="page-heading">
        <div><span className="eyebrow">Sesión local</span><h1>Perfil de demostración</h1><p>La selección de rol solo cambia las ventanas visibles en este navegador.</p></div>
        <span className="demo-indicator"><span /> Sin autenticación</span>
      </div>
      <section className="surface-card profile-card">
        <span className="profile-avatar">{role === "technician" ? "LD" : "OP"}</span>
        <div className="profile-info"><span className="eyebrow">Usuario activo</span><h2>{role === "technician" ? "Lucía Díaz" : "Equipo de operaciones"}</h2><p>{roleLabel(role)} · Perfil ficticio</p></div>
        <div className="profile-role"><span>Ventanas disponibles</span><strong>{role === "technician" ? "Resumen, mapa, cola e incidencias" : "Alertas, triaje, historial y metodología"}</strong></div>
      </section>
      <div className="profile-info-grid">
        <section className="surface-card methodology-card"><span className="eyebrow">Configuración del motor</span><h2>Valores experimentales</h2><div className="rule-method"><strong>Versión</strong><span>Motor determinista 0.2.0</span></div><div className="rule-method"><strong>Umbrales</strong><span>Alta ≥ 75 · Media ≥ 55</span></div><div className="rule-method"><strong>Pesos</strong><span>Uso 0,40 · Antigüedad 0,20 · Entorno 0,40</span></div><p>La interfaz muestra la instantánea estática de demo; estos valores todavía no se editan ni se recalculan desde el navegador.</p></section>
        <section className="profile-notice"><Shield size={18} /><h2>Sin cuenta ni datos personales</h2><p>No existe inicio de sesión real. Las acciones y perfiles sirven para recorrer las distintas vistas del prototipo y no se guardan al recargar.</p><Link to="/metodologia">Revisar metodología <ArrowRight size={15} /></Link></section>
      </div>
    </div>
  );
}

function statusLabel(status: DemoIncident["status"]) {
  return { reported: "Triaje", pending: "Pendiente", assigned: "Asignada", resolved: "Resuelta", rejected: "Rechazada" }[status];
}

function roleLabel(role: UserRole) {
  return role === "technician" ? "Técnica de mantenimiento" : "Responsable de operaciones";
}

function currentPageName(path: string) {
  const names: Record<string, string> = {
    "/": "Resumen",
    "/mapa": "Mapa de incidencias",
    "/cola": "Cola de trabajo",
    "/incidencias": "Incidencias",
    "/alertas": "Alertas",
    "/triaje": "Bandeja de triaje",
    "/historial": "Historial",
    "/metodologia": "Metodología",
    "/perfil": "Perfil de demostración",
  };
  return names[path] ?? "Operaciones";
}
