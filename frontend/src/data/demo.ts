import type { DemoIncident, IncidentCategory, Priority } from "../types";

export interface IncidentFilters {
  district?: string;
  category?: string;
  priority?: string;
  status?: string;
  source?: string;
  search?: string;
}

export const districts = [
  { name: "Centro", center: [36.721, -4.421] as [number, number], zoom: 14 },
  { name: "Este", center: [36.718, -4.401] as [number, number], zoom: 13 },
  { name: "Ciudad Jardín", center: [36.746, -4.426] as [number, number], zoom: 13 },
  { name: "Bailén-Miraflores", center: [36.735, -4.438] as [number, number], zoom: 13 },
  { name: "Palma-Palmilla", center: [36.741, -4.432] as [number, number], zoom: 13 },
  { name: "Cruz de Humilladero", center: [36.711, -4.452] as [number, number], zoom: 13 },
  { name: "Carretera de Cádiz", center: [36.684, -4.438] as [number, number], zoom: 13 },
  { name: "Churriana", center: [36.665, -4.493] as [number, number], zoom: 13 },
  { name: "Campanillas", center: [36.674, -4.528] as [number, number], zoom: 13 },
  { name: "Puerto de la Torre", center: [36.741, -4.474] as [number, number], zoom: 13 },
  { name: "Teatinos-Universidad", center: [36.716, -4.483] as [number, number], zoom: 13 },
];

export function isWithinDemoArea(latitude: number, longitude: number) {
  return latitude >= 36.65 && latitude <= 36.8 && longitude >= -4.6 && longitude <= -4.3;
}

export const categoryLabels: Record<IncidentCategory, string> = {
  streetlight_failure: "Luminaria apagada",
  streetlight_flickering: "Luminaria intermitente",
  damaged_pole: "Poste dañado",
  electrical_hazard: "Riesgo eléctrico",
  other: "Otra incidencia",
};

export const priorityLabels: Record<Priority, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

const demoIncidentSeeds: Omit<
  DemoIncident,
  "isSimulated" | "verification" | "assignee"
>[] = [
  {
    id: "DEMO-001",
    title: "Luminaria apagada en zona de paso",
    category: "streetlight_failure",
    description: "Incidencia ficticia de demostración en el entorno de la Alameda.",
    latitude: 36.7213,
    longitude: -4.4214,
    district: "Centro",
    neighborhood: "Centro histórico",
    status: "pending",
    source: "synthetic",
    priority: "high",
    score: 92.13,
    factors: {
      pedestrianUse: { value: 95, weight: 0.4, contribution: 38 },
      age: { value: 86.67, weight: 0.2, contribution: 17.33 },
      sensitiveLocation: { value: 92, weight: 0.4, contribution: 36.8 },
    },
    action: "repair_priority",
    ageHours: 26,
    urgent: false,
    rules: ["SR-02"],
    missingFactors: [],
    rationale: ["Prioridad alta por la puntuación.", "SR-02 fija un mínimo de prioridad alta."],
    createdAt: "2026-10-12T08:00:00Z",
  },
  {
    id: "DEMO-002",
    title: "Poste dañado junto a una plaza",
    category: "damaged_pole",
    description: "Poste con daños visibles; caso ficticio para probar la revisión urgente.",
    latitude: 36.7194,
    longitude: -4.4197,
    district: "Centro",
    neighborhood: "Soho",
    status: "assigned",
    source: "synthetic",
    priority: "high",
    score: 22.67,
    factors: {
      pedestrianUse: { value: 30, weight: 0.4, contribution: 12 },
      age: { value: 13.33, weight: 0.2, contribution: 2.67 },
      sensitiveLocation: { value: 20, weight: 0.4, contribution: 8 },
    },
    action: "inspect_urgently",
    ageHours: 4,
    urgent: true,
    rules: ["SR-01"],
    missingFactors: [],
    rationale: ["SR-01 requiere inspección humana urgente."],
    createdAt: "2026-10-13T06:00:00Z",
  },
  {
    id: "DEMO-003",
    title: "Aviso pendiente de verificación",
    category: "streetlight_failure",
    description: "Reporte de demostración; necesita triaje antes de entrar en la cola.",
    latitude: 36.7231,
    longitude: -4.4179,
    district: "Centro",
    neighborhood: "La Merced",
    status: "reported",
    source: "resident_report",
    priority: null,
    score: null,
    factors: {
      pedestrianUse: { value: null, weight: null, contribution: null },
      age: { value: null, weight: null, contribution: null },
      sensitiveLocation: { value: null, weight: null, contribution: null },
    },
    action: "needs_triage",
    ageHours: 1,
    urgent: false,
    rules: ["SR-03", "SR-04"],
    missingFactors: ["pedestrian_use", "sensitive_location"],
    rationale: ["El reporte está sin verificar.", "No hay puntuación disponible."],
    createdAt: "2026-10-13T09:00:00Z",
  },
  {
    id: "DEMO-004",
    title: "Luminaria intermitente en paseo marítimo",
    category: "streetlight_flickering",
    description: "Registro artificial situado en el distrito Este.",
    latitude: 36.7187,
    longitude: -4.3981,
    district: "Este",
    neighborhood: "La Malagueta",
    status: "pending",
    source: "synthetic",
    priority: "medium",
    score: 68.4,
    factors: {
      pedestrianUse: { value: 61, weight: 0.4, contribution: 24.4 },
      age: { value: 60, weight: 0.2, contribution: 12 },
      sensitiveLocation: { value: 80, weight: 0.4, contribution: 32 },
    },
    action: "repair_scheduled",
    ageHours: 18,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad media por la puntuación."],
    createdAt: "2026-10-12T15:00:00Z",
  },
  {
    id: "DEMO-005",
    title: "Incidencia de alumbrado en zona residencial",
    category: "streetlight_failure",
    description: "Punto y factores simulados; no representa una avería real.",
    latitude: 36.7452,
    longitude: -4.4268,
    district: "Ciudad Jardín",
    neighborhood: "Jardín de Málaga",
    status: "pending",
    source: "synthetic",
    priority: "low",
    score: 41.2,
    factors: {
      pedestrianUse: { value: 40, weight: 0.4, contribution: 16 },
      age: { value: 20, weight: 0.2, contribution: 4 },
      sensitiveLocation: { value: 53, weight: 0.4, contribution: 21.2 },
    },
    action: "repair_scheduled",
    ageHours: 8,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad baja por la puntuación."],
    createdAt: "2026-10-13T02:00:00Z",
  },
  {
    id: "DEMO-006",
    title: "Poste con daños en la vía",
    category: "damaged_pole",
    description: "Caso sintético para mostrar una regla de seguridad.",
    latitude: 36.7341,
    longitude: -4.4352,
    district: "Bailén-Miraflores",
    neighborhood: "Bailén",
    status: "pending",
    source: "synthetic",
    priority: "high",
    score: 48,
    factors: {
      pedestrianUse: { value: 60, weight: 0.4, contribution: 24 },
      age: { value: 20, weight: 0.2, contribution: 4 },
      sensitiveLocation: { value: 50, weight: 0.4, contribution: 20 },
    },
    action: "inspect_urgently",
    ageHours: 13,
    urgent: true,
    rules: ["SR-01"],
    missingFactors: [],
    rationale: ["SR-01 requiere inspección humana urgente."],
    createdAt: "2026-10-12T21:00:00Z",
  },
  {
    id: "DEMO-007",
    title: "Aviso de luminaria apagada",
    category: "streetlight_failure",
    description: "Incidencia simulada sin contexto suficiente para priorizar.",
    latitude: 36.7415,
    longitude: -4.431,
    district: "Palma-Palmilla",
    neighborhood: "La Palma",
    status: "pending",
    source: "synthetic",
    priority: "medium",
    score: 57.5,
    factors: {
      pedestrianUse: { value: 60, weight: 0.5, contribution: 30 },
      age: { value: null, weight: null, contribution: null },
      sensitiveLocation: { value: 55, weight: 0.5, contribution: 27.5 },
    },
    action: "verify_on_site",
    ageHours: null,
    urgent: false,
    rules: [],
    missingFactors: ["age"],
    rationale: ["Antigüedad no disponible; verificar en sitio."],
    createdAt: "2026-10-13T08:00:00Z",
  },
  {
    id: "DEMO-008",
    title: "Luminaria intermitente",
    category: "streetlight_flickering",
    description: "Punto aproximado y puntuación creados para la demo.",
    latitude: 36.7109,
    longitude: -4.4508,
    district: "Cruz de Humilladero",
    neighborhood: "La Unión",
    status: "resolved",
    source: "synthetic",
    priority: "low",
    score: 33.33,
    factors: {
      pedestrianUse: { value: 40, weight: 0.4, contribution: 16 },
      age: { value: 16.67, weight: 0.2, contribution: 3.33 },
      sensitiveLocation: { value: 35, weight: 0.4, contribution: 14 },
    },
    action: "repair_scheduled",
    ageHours: 5,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad baja por la puntuación."],
    createdAt: "2026-10-13T05:00:00Z",
  },
  {
    id: "DEMO-009",
    title: "Fallo de alumbrado en calle residencial",
    category: "streetlight_failure",
    description: "Incidencia completamente ficticia para la vista de mapa.",
    latitude: 36.6841,
    longitude: -4.4382,
    district: "Carretera de Cádiz",
    neighborhood: "Huelin",
    status: "pending",
    source: "synthetic",
    priority: "high",
    score: 78.6,
    factors: {
      pedestrianUse: { value: 72, weight: 0.4, contribution: 28.8 },
      age: { value: 100, weight: 0.2, contribution: 20 },
      sensitiveLocation: { value: 74.5, weight: 0.4, contribution: 29.8 },
    },
    action: "repair_priority",
    ageHours: 31,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad alta por la puntuación."],
    createdAt: "2026-10-12T03:00:00Z",
  },
  {
    id: "DEMO-010",
    title: "Aviso de alumbrado para revisión",
    category: "streetlight_failure",
    description: "Ubicación y demás datos sintéticos; requiere validación.",
    latitude: 36.665,
    longitude: -4.493,
    district: "Churriana",
    neighborhood: "Churriana",
    status: "reported",
    source: "resident_report",
    priority: null,
    score: null,
    factors: {
      pedestrianUse: { value: null, weight: null, contribution: null },
      age: { value: null, weight: null, contribution: null },
      sensitiveLocation: { value: null, weight: null, contribution: null },
    },
    action: "needs_triage",
    ageHours: 2,
    urgent: false,
    rules: ["SR-04"],
    missingFactors: ["pedestrian_use", "sensitive_location"],
    rationale: ["El reporte está sin verificar."],
    createdAt: "2026-10-13T08:00:00Z",
  },
  {
    id: "DEMO-011",
    title: "Incidencia de alumbrado en el entorno del parque",
    category: "streetlight_failure",
    description: "Punto de prueba del distrito de Campanillas.",
    latitude: 36.6742,
    longitude: -4.5281,
    district: "Campanillas",
    neighborhood: "Campanillas",
    status: "pending",
    source: "synthetic",
    priority: "medium",
    score: 62.5,
    factors: {
      pedestrianUse: { value: 70, weight: 0.4, contribution: 28 },
      age: { value: 50, weight: 0.2, contribution: 10 },
      sensitiveLocation: { value: 61.25, weight: 0.4, contribution: 24.5 },
    },
    action: "repair_scheduled",
    ageHours: 17,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad media por la puntuación."],
    createdAt: "2026-10-12T17:00:00Z",
  },
  {
    id: "DEMO-012",
    title: "Riesgo eléctrico junto a una farola",
    category: "electrical_hazard",
    description: "Registro sintético con revisión urgente activada.",
    latitude: 36.741,
    longitude: -4.4735,
    district: "Puerto de la Torre",
    neighborhood: "Puerto de la Torre",
    status: "pending",
    source: "synthetic",
    priority: "high",
    score: 32.67,
    factors: {
      pedestrianUse: { value: 50, weight: 0.4, contribution: 20 },
      age: { value: 23.33, weight: 0.2, contribution: 4.67 },
      sensitiveLocation: { value: 20, weight: 0.4, contribution: 8 },
    },
    action: "inspect_urgently",
    ageHours: 7,
    urgent: true,
    rules: ["SR-01"],
    missingFactors: [],
    rationale: ["SR-01 requiere inspección humana urgente."],
    createdAt: "2026-10-13T03:00:00Z",
  },
  {
    id: "DEMO-013",
    title: "Luminaria apagada en zona universitaria",
    category: "streetlight_failure",
    description: "Coordenadas aproximadas generadas para la demo.",
    latitude: 36.716,
    longitude: -4.4828,
    district: "Teatinos-Universidad",
    neighborhood: "Teatinos",
    status: "assigned",
    source: "synthetic",
    priority: "medium",
    score: 66.67,
    factors: {
      pedestrianUse: { value: 80, weight: 0.4, contribution: 32 },
      age: { value: 73.33, weight: 0.2, contribution: 14.67 },
      sensitiveLocation: { value: 50, weight: 0.4, contribution: 20 },
    },
    action: "repair_scheduled",
    ageHours: 22,
    urgent: false,
    rules: [],
    missingFactors: [],
    rationale: ["Prioridad media por la puntuación."],
    createdAt: "2026-10-12T12:00:00Z",
  },
];

export const demoIncidents: DemoIncident[] = demoIncidentSeeds.map((incident) => ({
  ...incident,
  verification: incident.status === "reported"
    ? "unverified"
    : incident.status === "rejected"
      ? "rejected"
      : "verified",
  assignee: incident.status === "assigned" ? "Lucía Díaz" : null,
  isSimulated: true,
}));

export const sourceLabel = (
  source: DemoIncident["source"],
  isSimulated = source === "synthetic" || source === "resident_report",
) => {
  const label = {
    municipal_open_data: "Datos municipales",
    derived: "Dato derivado",
    synthetic: "Simulado",
    resident_report: "Aviso residente",
  }[source];
  return isSimulated ? `${label} · demo` : label;
};

export function filterDemoIncidents(
  incidents: DemoIncident[],
  filters: IncidentFilters,
) {
  const search = filters.search?.trim().toLocaleLowerCase("es");
  return incidents.filter(
    (incident) =>
      (!filters.district || filters.district === "all" || incident.district === filters.district) &&
      (!filters.category || filters.category === "all" || incident.category === filters.category) &&
      (!filters.priority ||
        filters.priority === "all" ||
        (filters.priority === "none" && incident.priority === null) ||
        incident.priority === filters.priority) &&
      (!filters.status || filters.status === "all" || incident.status === filters.status) &&
      (!filters.source || filters.source === "all" || incident.source === filters.source) &&
      (!search ||
        `${incident.id} ${incident.title} ${incident.district} ${incident.neighborhood}`
          .toLocaleLowerCase("es")
          .includes(search)),
  );
}
