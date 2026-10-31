// Fixed layout so the prerequisite structure reads the same every time.
const POS = {
  electric_current: [70, 70], ohms_law: [230, 70], resistance_factors: [400, 30], series_parallel: [400, 110],
  electric_power: [570, 110], magnetic_effect: [230, 170],
  reflection: [70, 270], spherical_mirrors: [250, 235], refraction: [250, 305], lenses: [430, 270],
};
const SHORT = {
  electric_current: "Current", ohms_law: "Ohm's law", resistance_factors: "Resistivity", series_parallel: "Series / parallel",
  electric_power: "Power", magnetic_effect: "Magnetism", reflection: "Reflection", spherical_mirrors: "Mirrors",
  refraction: "Refraction", lenses: "Lenses",
};
export const scoreColor = () => "#3FAF91";

export default function ConceptGraph({ graph, mastery }) {
  const byId = Object.fromEntries(mastery.map((m) => [m.concept_id, m]));
  return (
    <svg viewBox="0 0 660 350" className="graph" role="img" aria-label="Concept graph: arrows point from a concept to the ones that build on it">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0 0L10 5L0 10z" fill="#a7b2aa" />
        </marker>
      </defs>
      {graph.edges.map((e) => {
        const [x1, y1] = POS[e.source], [x2, y2] = POS[e.target];
        const dx = x2 - x1, dy = y2 - y1, d = Math.hypot(dx, dy);
        return <line key={e.source + e.target} x1={x1 + (dx / d) * 24} y1={y1 + (dy / d) * 24}
          x2={x2 - (dx / d) * 28} y2={y2 - (dy / d) * 28} stroke="#a7b2aa" strokeWidth="1.5" markerEnd="url(#arrow)" />;
      })}
      {graph.nodes.map((n) => {
        const [x, y] = POS[n.id];
        const m = byId[n.id];
        const assessed = m?.assessed;
        return (
          <g key={n.id}>
            <circle cx={x} cy={y} r="22" fill={assessed ? scoreColor(m.score) : "#102c58"} stroke={assessed ? "none" : "#9DB4D8"}
              strokeDasharray={assessed ? "" : "4 3"} strokeWidth="1.5" />
            <text x={x} y={y + 4} textAnchor="middle" fontSize="12" fontWeight="700" fill={assessed ? "#fff" : "#9DB4D8"}>
              {m ? m.score.toFixed(2).replace(/^0/, "") : ""}
            </text>
            <text x={x} y={y + 40} textAnchor="middle" fontSize="12" fill="#EAF2FF">{SHORT[n.id]}</text>
          </g>
        );
      })}
    </svg>
  );
}
