import { describe, expect, it } from "vitest";
import { demoIncidents, filterDemoIncidents, isWithinDemoArea } from "./demo";

describe("filterDemoIncidents", () => {
  it("narrows the map to a selected district", () => {
    const incidents = filterDemoIncidents(demoIncidents, { district: "Este" });
    expect(incidents.length).toBeGreaterThan(0);
    expect(incidents.every((incident) => incident.district === "Este")).toBe(true);
  });

  it("combines category and priority filters", () => {
    const incidents = filterDemoIncidents(demoIncidents, {
      category: "streetlight_failure",
      priority: "high",
    });
    expect(incidents.length).toBeGreaterThan(0);
    expect(
      incidents.every(
        (incident) =>
          incident.category === "streetlight_failure" && incident.priority === "high",
      ),
    ).toBe(true);
  });

  it("can select reports that have not been scored", () => {
    const incidents = filterDemoIncidents(demoIncidents, { priority: "none" });
    expect(incidents.length).toBeGreaterThan(0);
    expect(incidents.every((incident) => incident.priority === null)).toBe(true);
  });

  it("filters incidents by source", () => {
    const incidents = filterDemoIncidents(demoIncidents, {
      source: "resident_report",
    });
    expect(incidents.length).toBeGreaterThan(0);
    expect(incidents.every((incident) => incident.source === "resident_report")).toBe(
      true,
    );
  });

  it("matches a district or neighborhood by search", () => {
    const incidents = filterDemoIncidents(demoIncidents, { search: "huelin" });
    expect(incidents.map((incident) => incident.id)).toEqual(["DEMO-009"]);
  });

  it("keeps precomputed complete demo scores consistent with their breakdown", () => {
    for (const incident of demoIncidents.filter((item) => item.score !== null)) {
      const factors = Object.values(incident.factors);
      expect(factors.every((factor) => factor.contribution !== null)).toBe(
        incident.missingFactors.length === 0,
      );
      const total = factors.reduce(
        (sum, factor) => sum + (factor.contribution ?? 0),
        0,
      );
      expect(total).toBeCloseTo(incident.score ?? 0, 2);
    }
  });

  it("keeps every artificial map point inside the demo bounds", () => {
    for (const incident of demoIncidents) {
      expect(incident.latitude).not.toBeNull();
      expect(incident.longitude).not.toBeNull();
      if (incident.latitude === null || incident.longitude === null) continue;
      expect(isWithinDemoArea(incident.latitude, incident.longitude)).toBe(true);
    }
  });

  it("rejects map points outside the demo area", () => {
    expect(isWithinDemoArea(36.64, -4.42)).toBe(false);
    expect(isWithinDemoArea(36.72, -4.29)).toBe(false);
  });
});
