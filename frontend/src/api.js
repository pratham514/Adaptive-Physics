const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req(path, opts = {}) {
  let res;
  try {
    res = await fetch(BASE + path, { headers: { "Content-Type": "application/json" }, ...opts });
  } catch {
    throw new Error("Can't reach the server. Is the backend running on " + BASE + "?");
  }
  if (!res.ok) {
    let detail;
    try { detail = (await res.json()).detail; } catch { /* not json */ }
    throw new Error(detail || res.statusText);
  }
  return res.json();
}
const post = (path, body) => req(path, { method: "POST", body: JSON.stringify(body) });

export const api = {
  concepts: () => req("/concepts"),
  student: (id) => req(`/students/${id}`),
  createStudent: (name) => post("/students", { name }),
  mastery: (id) => req(`/students/${id}/mastery`),
  diagNext: (id) => req(`/diagnostic/next?student_id=${id}`),
  attempt: (body) => post("/attempts", body),
  practiceNext: (student_id, concept_id) => post("/practice/next", { student_id, concept_id }),
  analyze: (body) => post("/misconceptions/analyze", body),
  review: (id) => req(`/students/${id}/review-queue`),
  gaps: () => req("/teacher/class-gaps"),
  roster: () => req("/teacher/roster"),
};
