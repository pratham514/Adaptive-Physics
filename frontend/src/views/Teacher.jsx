import { useEffect, useState } from "react";
import { api } from "../api.js";
const heatShade = (score) => `hsl(210 72% ${18 + score * 38}%)`;

export default function Teacher() {
  const [gaps, setGaps] = useState(null);
  const [roster, setRoster] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    Promise.all([api.gaps(), api.roster()]).then(([g, r]) => { setGaps(g); setRoster(r); }).catch((e) => setErr(e.message));
  }, []);

  if (err) return <p className="error">{err}</p>;
  if (!gaps) return <p className="muted">Gathering the class picture…</p>;

  const sorted = [...gaps.concepts].sort((a, b) => b.gap - a.gap);
  const names = Object.fromEntries(gaps.concepts.map((c) => [c.concept_id, c.name]));

  return (
    <>
      <h2>Class learning snapshot</h2>
      <p>{gaps.student_count} students in this view. Longer bars show topics where the class could use a little more practice.</p>

      <ul className="gapchart">
        {sorted.map((c) => (
          <li key={c.concept_id}>
            <span className="label">{c.name}</span>
            <span className="track">
              {[25, 50, 75].map((t) => <b key={t} className="grid" style={{ left: `${t}%` }} />)}
              <i style={{ width: `${c.gap * 100}%`, background: "var(--accent)" }} />
            </span>
            <span className="val">{Math.round(c.gap * 100)}%</span>
            <span className="muted small struggle">{c.struggling_count} of {c.students_assessed} below 0.10</span>
          </li>
        ))}
      </ul>

      <h3 className="section">Class by topic</h3>
      <p className="muted small">Darker shades show stronger mastery. A ! marks a score below 0.10 that needs attention.</p>
      <div className="scroll">
        <table className="heat">
          <thead>
            <tr><th>Student</th>{roster.concepts.map((id) => <th key={id} title={names[id]}>{names[id].split(/[ &]/)[0]}</th>)}<th>Avg</th></tr>
          </thead>
          <tbody>
            {roster.students.map((s) => (
              <tr key={s.id}>
                <th scope="row">{s.name}</th>
                {roster.concepts.map((id) => {
                  const v = s.scores[id];
                  const concern = v != null && v < 0.1;
                  return <td key={id} title={concern ? `${names[id]} needs attention: ${v.toFixed(2)}` : undefined}
                    aria-label={v == null ? `${names[id]}: not assessed` : `${names[id]}: ${v.toFixed(2)}${concern ? ", needs attention" : ""}`}
                    style={v == null ? {} : { background: heatShade(v), color: "#EAF2FF" }}>
                    {v == null ? "·" : <>{v.toFixed(2).replace(/^0/, "")}{concern && <span className="concern-mark" aria-hidden="true">!</span>}</>}
                  </td>;
                })}
                <td className="avg">{s.average.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
