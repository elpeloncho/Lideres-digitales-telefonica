import type {
  DemoIncident,
  IncidentCategory,
  IncidentStatus,
  Priority,
} from "../types";

interface ApiFactor {
  value: number | null;
  weight: number | null;
  contribution: number | null;
}

export interface ApiIncident {
  id: string;
  title: string;
  description: string;
  category: IncidentCategory;
  latitude: number | null;
  longitude: number | null;
  district: string | null;
  neighborhood: string | null;
  status: IncidentStatus;
  verification: "unverified" | "verified" | "rejected" | "not_applicable" | null;
  assignee: string | null;
  sourceType: DemoIncident["source"];
  sourceName: string;
  isSimulated: boolean;
  priority: Priority | null;
  score: number | null;
  factors: {
    pedestrianUse: ApiFactor;
    age: ApiFactor;
    sensitiveLocation: ApiFactor;
  };
  action: string;
  ageHours: number | null;
  urgent: boolean;
  rules: string[];
  missingFactors: string[];
  rationale: string[];
  createdAt: string | null;
}

interface ApiListResponse {
  items: ApiIncident[];
  total: number;
  limit: number;
  offset: number;
}

export type WorkflowAction = "accept" | "reject" | "assign" | "resolve" | "reopen";

export interface ReportInput {
  category: IncidentCategory;
  description: string;
  latitude: number;
  longitude: number;
}

export interface ActivityEvent {
  sequence: number;
  eventId: string;
  eventType: string;
  incidentId: string;
  actor: string;
  occurredAt: string;
  details: Record<string, unknown>;
}

export function toDemoIncident(item: ApiIncident): DemoIncident {
  return {
    id: item.id,
    title: item.title || "Incidencia sin título",
    description: item.description,
    category: item.category,
    latitude: item.latitude,
    longitude: item.longitude,
    district: item.district || "Zona sin clasificar",
    neighborhood: item.neighborhood || "Ubicación no clasificada",
    status: item.status,
    verification: item.verification,
    assignee: item.assignee,
    source: item.sourceType,
    isSimulated: item.isSimulated,
    priority: item.priority,
    score: item.score,
    factors: {
      pedestrianUse: item.factors.pedestrianUse,
      age: item.factors.age,
      sensitiveLocation: item.factors.sensitiveLocation,
    },
    action: item.action,
    ageHours: item.ageHours,
    urgent: item.urgent,
    rules: item.rules,
    missingFactors: item.missingFactors,
    rationale: item.rationale,
    createdAt: item.createdAt ?? "",
  };
}

export async function fetchIncidents(signal?: AbortSignal): Promise<DemoIncident[]> {
  const response = await fetch("/api/v1/incidents?limit=200&sort=queue", {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    throw new Error(`La API respondió HTTP ${response.status}.`);
  }
  const body: ApiListResponse = await response.json();
  if (!Array.isArray(body.items)) {
    throw new Error("La respuesta de incidencias de la API tiene un formato inválido.");
  }
  return body.items.map(toDemoIncident);
}

async function readIncidentResponse(response: Response): Promise<DemoIncident> {
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `La API respondió HTTP ${response.status}.`);
  }
  return toDemoIncident(await response.json() as ApiIncident);
}

export async function submitReport(input: ReportInput): Promise<DemoIncident> {
  const response = await fetch("/api/v1/reports", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return readIncidentResponse(response);
}

export async function updateWorkflow(
  incidentId: string,
  action: WorkflowAction,
  actor: "technician_demo" | "operations_demo",
  assignee?: string,
): Promise<DemoIncident> {
  const response = await fetch(`/api/v1/incidents/${encodeURIComponent(incidentId)}/workflow`, {
    method: "PATCH",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ action, actor, ...(assignee ? { assignee } : {}) }),
  });
  return readIncidentResponse(response);
}

export async function fetchHistory(signal?: AbortSignal): Promise<ActivityEvent[]> {
  const response = await fetch("/api/v1/history", {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    throw new Error(`No se pudo cargar el historial (HTTP ${response.status}).`);
  }
  const events: ActivityEvent[] = await response.json();
  if (!Array.isArray(events)) {
    throw new Error("La respuesta de historial de la API tiene un formato inválido.");
  }
  return events;
}
