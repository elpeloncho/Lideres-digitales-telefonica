import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import type { DemoIncident } from "../types";
import { demoIncidents } from "./demo";
import {
  fetchIncidents,
  submitReport,
  updateWorkflow,
  type ReportInput,
  type WorkflowAction,
} from "./api";

export type DataMode = "loading" | "api" | "demo-fallback";

interface IncidentDataValue {
  incidents: DemoIncident[];
  mode: DataMode;
  error: string | null;
  createReport: (input: ReportInput) => Promise<DemoIncident>;
  applyWorkflow: (
    incidentId: string,
    action: WorkflowAction,
    actor: "technician_demo" | "operations_demo",
    assignee?: string,
  ) => Promise<DemoIncident>;
}

const IncidentDataContext = createContext<IncidentDataValue | null>(null);

export function IncidentDataProvider({ children }: PropsWithChildren) {
  const [incidents, setIncidents] = useState<DemoIncident[]>([]);
  const [mode, setMode] = useState<DataMode>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchIncidents(controller.signal)
      .then((apiIncidents) => {
        setIncidents(apiIncidents);
        setMode("api");
        setError(null);
      })
      .catch((requestError: unknown) => {
        if (controller.signal.aborted) return;
        setIncidents(demoIncidents);
        setMode("demo-fallback");
        setError(
          requestError instanceof Error
            ? requestError.message
            : "No se pudo conectar con la API.",
        );
      });
    return () => controller.abort();
  }, []);

  const createReport = useCallback(async (input: ReportInput) => {
    const created = await submitReport(input);
    setIncidents((current) => [created, ...current.filter((item) => item.id !== created.id)]);
    setMode("api");
    setError(null);
    return created;
  }, []);

  const applyWorkflow = useCallback(async (
    incidentId: string,
    action: WorkflowAction,
    actor: "technician_demo" | "operations_demo",
    assignee?: string,
  ) => {
    const updated = await updateWorkflow(incidentId, action, actor, assignee);
    setIncidents((current) => current.map((item) => item.id === updated.id ? updated : item));
    setMode("api");
    setError(null);
    return updated;
  }, []);

  const value = useMemo(
    () => ({ incidents, mode, error, createReport, applyWorkflow }),
    [applyWorkflow, createReport, error, incidents, mode],
  );
  return (
    <IncidentDataContext.Provider value={value}>
      {children}
    </IncidentDataContext.Provider>
  );
}

export function useIncidentData() {
  const value = useContext(IncidentDataContext);
  if (!value) {
    throw new Error("useIncidentData debe usarse dentro de IncidentDataProvider.");
  }
  return value;
}
