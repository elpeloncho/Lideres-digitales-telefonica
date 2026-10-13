export type Priority = "high" | "medium" | "low";
export type IncidentStatus =
  | "reported"
  | "pending"
  | "assigned"
  | "resolved"
  | "rejected";
export type IncidentCategory =
  | "streetlight_failure"
  | "streetlight_flickering"
  | "damaged_pole"
  | "electrical_hazard"
  | "other";
export type UserRole = "technician" | "operations";
export type IncidentSource =
  | "municipal_open_data"
  | "derived"
  | "synthetic"
  | "resident_report";

export interface PriorityFactor {
  value: number | null;
  weight: number | null;
  contribution: number | null;
}

export interface DemoIncident {
  id: string;
  title: string;
  category: IncidentCategory;
  description: string;
  latitude: number | null;
  longitude: number | null;
  district: string;
  neighborhood: string;
  status: IncidentStatus;
  verification: "unverified" | "verified" | "rejected" | "not_applicable" | null;
  assignee: string | null;
  source: IncidentSource;
  isSimulated: boolean;
  priority: Priority | null;
  score: number | null;
  factors: {
    pedestrianUse: PriorityFactor;
    age: PriorityFactor;
    sensitiveLocation: PriorityFactor;
  };
  action: string;
  ageHours: number | null;
  urgent: boolean;
  rules: string[];
  missingFactors: string[];
  rationale: string[];
  createdAt: string;
}
