const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:5000";

export async function getLatest() {
  const res = await fetch(`${BASE_URL}/latest`);
  if (!res.ok) throw new Error("Failed to fetch latest state");
  return res.json();
}

export async function getHistory(limit = 60) {
  const res = await fetch(`${BASE_URL}/history?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export async function getPoints() {
  const res = await fetch(`${BASE_URL}/points`);
  if (!res.ok) throw new Error("Failed to fetch life points");
  return res.json();
}
