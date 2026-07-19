import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getPoints } from "./api";

// default Leaflet marker icons don't load correctly with bundlers unless
// pointed at the CDN explicitly
const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const POLL_MS = 2000;

export default function LifeMap() {
  const [points, setPoints] = useState([]);

  useEffect(() => {
    async function poll() {
      try {
        const pts = await getPoints();
        setPoints(pts);
      } catch (e) {
        // stay silent here — the main dashboard already surfaces connection errors
      }
    }
    poll();
    const id = setInterval(poll, POLL_MS);
    return () => clearInterval(id);
  }, []);

  const center = points.length
    ? [points[points.length - 1].lat, points[points.length - 1].lon]
    : [20.5937, 78.9629]; // fallback center until the first point arrives

  return (
    <div className="chart-panel" style={{ padding: 0, overflow: "hidden" }}>
      <h2 style={{ padding: "1.25rem 1.25rem 0" }}>
        Life Detection Points — {points.length} marked
      </h2>
      <MapContainer
        center={center}
        zoom={points.length ? 16 : 5}
        style={{ height: "360px", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {points.map((p) => (
          <Marker key={p.label} position={[p.lat, p.lon]} icon={markerIcon}>
            <Popup>
              <strong>Point {p.label}</strong>
              <br />
              confidence: {p.confidence ? `${Math.round(p.confidence * 100)}%` : "—"}
              <br />
              {new Date(p.timestamp * 1000).toLocaleString()}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
