import { useEffect } from "react";
import {
  Circle,
  MapContainer,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import { divIcon } from "leaflet";
import { Marker } from "react-leaflet";
import { districts, isWithinDemoArea } from "../data/demo";
import type { DemoIncident, Priority } from "../types";

const priorityColors: Record<Priority, string> = {
  high: "#d84b42",
  medium: "#e6a331",
  low: "#318b68",
};

const markerIcon = (priority: Priority | null, urgent: boolean) =>
  divIcon({
    className: "incident-marker-wrapper",
    html: `<span class="incident-marker ${urgent ? "is-urgent" : ""}" style="--marker-color:${priority ? priorityColors[priority] : "#737b89"}"><span></span></span>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });

function DistrictFocus({ district }: { district: string }) {
  const map = useMap();
  useEffect(() => {
    if (district === "all") {
      map.setView([36.72, -4.43], 12);
      return;
    }
    const selected = districts.find((item) => item.name === district);
    if (selected) map.flyTo(selected.center, selected.zoom, { duration: 0.55 });
  }, [district, map]);
  return null;
}

function MapClick({
  onSelect,
  onInvalidPoint,
}: {
  onSelect?: (point: [number, number]) => void;
  onInvalidPoint?: () => void;
}) {
  useMapEvents({
    click(event) {
      if (isWithinDemoArea(event.latlng.lat, event.latlng.lng)) {
        onSelect?.([event.latlng.lat, event.latlng.lng]);
      } else {
        onInvalidPoint?.();
      }
    },
  });
  return null;
}

interface MapViewProps {
  incidents: DemoIncident[];
  district: string;
  onSelectIncident?: (incident: DemoIncident) => void;
  onSelectPoint?: (point: [number, number]) => void;
  onInvalidPoint?: () => void;
  selectedPoint?: [number, number] | null;
}

export default function MapView({
  incidents,
  district,
  onSelectIncident,
  onSelectPoint,
  onInvalidPoint,
  selectedPoint,
}: MapViewProps) {
  return (
    <MapContainer
      center={[36.72, -4.43]}
      zoom={12}
      scrollWheelZoom
      className="luma-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <DistrictFocus district={district} />
      <MapClick onSelect={onSelectPoint} onInvalidPoint={onInvalidPoint} />
      {district !== "all" &&
        districts
          .filter((item) => item.name === district)
          .map((item) => (
            <Circle
              key={item.name}
              center={item.center}
              radius={900}
              pathOptions={{
                color: "#447b6a",
                weight: 1,
                dashArray: "5 7",
                fillColor: "#8bb9a5",
                fillOpacity: 0.08,
              }}
            />
          ))}
      {incidents
        .filter(
          (incident): incident is DemoIncident & { latitude: number; longitude: number } =>
            incident.latitude !== null && incident.longitude !== null,
        )
        .map((incident) => (
          <Marker
            key={incident.id}
            position={[incident.latitude, incident.longitude]}
            icon={markerIcon(incident.priority, incident.urgent)}
            eventHandlers={{
              click: () => onSelectIncident?.(incident),
            }}
          />
        ))}
      {selectedPoint && (
        <Circle
          center={selectedPoint}
          radius={22}
          pathOptions={{ color: "#315f51", fillColor: "#538c79", fillOpacity: 0.7 }}
        />
      )}
    </MapContainer>
  );
}
