import { useEffect, useState, useRef } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { getLatest, getHistory } from "./api";
import LifeMap from "./LifeMap";
import LiveCamera from "./LiveCamera";

const POLL_MS = 2000;

function Card({ label, value, unit, alert }) {
  return (
    <div className={`card ${alert ? "alert" : ""}`}>
      <div className="label">{label}</div>
      <div className="value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
    </div>
  );
}

export default function App() {
  const [state, setState] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    async function poll() {
      try {
        const [latest, hist] = await Promise.all([getLatest(), getHistory(60)]);
        setState(latest);
        setHistory(
          hist.map((r) => ({
            ...r,
            time: new Date(r.timestamp * 1000).toLocaleTimeString(),
          }))
        );
        setError(null);
      } catch (e) {
        setError("Backend unreachable — is Flask running on port 5000?");
      }
    }
    poll();
    timerRef.current = setInterval(poll, POLL_MS);
    return () => clearInterval(timerRef.current);
  }, []);

  const risk = state?.risk || "SAFE";
  const personFound = Boolean(state?.person);
  const fmt = (v, digits = 1) =>
    v === null || v === undefined || Number.isNaN(v) ? "—" : Number(v).toFixed(digits);

  return (
    <div className="dashboard">
      <div className="header">
        <h1>OMNI SIGHT XR // TELEMETRY</h1>
        <span className="subtitle">
          {state?.updated_at
            ? `last update ${new Date(state.updated_at * 1000).toLocaleTimeString()}`
            : "waiting for data..."}
        </span>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className={`risk-banner risk-${risk}`}>
        <span>Environmental Risk</span>
        <span>{risk}</span>
      </div>

      <div className={`risk-banner ${personFound ? "risk-WARNING" : "risk-SAFE"}`}>
        <span>Person Status</span>
        <span>{state?.person_status || "CLEAR"}</span>
      </div>

      <div className="grid">
        <Card label="Temperature" value={fmt(state?.temperature)} unit="°C" />
        <Card label="Humidity" value={fmt(state?.humidity)} unit="%" />
        <Card
          label="Gas"
          value={state?.gas ?? "—"}
          unit="ppm"
          alert={state?.gas > 400}
        />
        <Card
          label="Distance"
          value={fmt(state?.distance_cm)}
          unit="cm"
          alert={state?.distance_cm !== null && state?.distance_cm !== -1 && state?.distance_cm < 15}
        />
        <Card
          label="Obstacle"
          value={state?.obstacle_detected ? "YES" : "NO"}
          alert={state?.obstacle_detected}
        />
        <Card
          label="Person"
          value={state?.person ? "DETECTED" : "NONE"}
          unit={state?.person_confidence ? `${Math.round(state.person_confidence * 100)}%` : ""}
          alert={state?.person}
        />
      </div>

      <LiveCamera />

      <LifeMap />

      <div className="chart-panel">
        <h2>Temperature &amp; Humidity — last 60 readings</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c3634" />
            <XAxis dataKey="time" stroke="#7fa39d" tick={{ fontSize: 10 }} minTickGap={30} />
            <YAxis stroke="#7fa39d" tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{ background: "#0f201f", border: "1px solid #1c3634", fontFamily: "monospace" }}
            />
            <Line type="monotone" dataKey="temperature" stroke="#2dd4bf" dot={false} strokeWidth={2} name="Temp (°C)" />
            <Line type="monotone" dataKey="humidity" stroke="#fbbf24" dot={false} strokeWidth={2} name="Humidity (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-panel">
        <h2>Gas &amp; Distance — last 60 readings</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c3634" />
            <XAxis dataKey="time" stroke="#7fa39d" tick={{ fontSize: 10 }} minTickGap={30} />
            <YAxis stroke="#7fa39d" tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{ background: "#0f201f", border: "1px solid #1c3634", fontFamily: "monospace" }}
            />
            <Line type="monotone" dataKey="gas" stroke="#d97706" dot={false} strokeWidth={2} name="Gas (ppm)" />
            <Line type="monotone" dataKey="distance_cm" stroke="#0f766e" dot={false} strokeWidth={2} name="Distance (cm)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="status-line">polling every {POLL_MS / 1000}s</div>
    </div>
  );
}