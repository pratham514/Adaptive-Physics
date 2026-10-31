import { useEffect, useState } from "react";
import { api } from "../api.js";
import ConceptGraph, { scoreColor } from "../components/ConceptGraph.jsx";

export default function Plan({ student, concepts, onPractice }) {
  const [mastery, setMastery] = useState(null);
  const [queue, setQueue] = useState(null);
  const [roster, setRoster] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    Promise.all([api.mastery(student.id), api.review(student.id), api.roster()])
      .then(([m, q, r]) => { setMastery(m); setQueue(q); setRoster(r); })
      .catch((e) => setErr(e.message));
  }, [student.id]);

  if (err) return <p className="error">{err}</p>;
  if (!mastery) return <p className="muted">Putting your study plan together…</p>;

  const top = queue[0];
  const anyAssessed = mastery.some((m) => m.assessed);
  const practiced = mastery.filter((m) => m.attempts > 0);
  const averageMastery = practiced.length
    ? practiced.reduce((sum, m) => sum + m.score, 0) / practiced.length
    : 0;
  const progressPercent = Math.round(averageMastery * 100);
  const classPeers = (roster?.students || []).filter((s) => s.id !== student.id);
  const classAverage = classPeers.length
    ? Math.round(classPeers.reduce((sum, s) => sum + s.average, 0) / classPeers.length * 100)
    : null;

  return (
    <>
      <section className="mastery-summary" aria-label="Your learning progress">
        <p>{practiced.length
          ? <>You’ve practised <strong>{practiced.length} of {mastery.length} topics</strong> so far. Your average mastery is <strong>{progressPercent}%</strong>.</>
          : "Your progress will take shape as you try a few questions. Every answer helps."}</p>
        <div className="mastery-progress" role="progressbar" aria-label="Average mastery on practised topics"
          aria-valuemin="0" aria-valuemax="100" aria-valuenow={progressPercent}>
          <span style={{ width: `${progressPercent}%` }} />
        </div>
      </section>

      <section className="compare-card" aria-label="Progress compared with the sample class">
        <div>
          <p className="eyebrow">A little context</p>
          <h3>Your progress in the sample class</h3>
          <p className="muted small">A friendly snapshot to help you see how you’re doing. Everyone learns at their own pace.</p>
        </div>
        <div className="compare-bars">
          <div><span>You</span><b>{progressPercent}%</b><span className="compare-track"><i style={{ width: `${progressPercent}%` }} /></span></div>
          <div><span>Sample class average</span><b>{classAverage == null ? "—" : `${classAverage}%`}</b><span className="compare-track"><i style={{ width: `${classAverage ?? 0}%` }} /></span></div>
        </div>
        <p className="muted small">The comparison uses fictional demo students and is only here to illustrate the prototype.</p>
      </section>

      <section className="next-up">
        <p className="muted small">A good next step</p>
        <h2>{top.name}</h2>
        <p>Let’s spend a little time with this topic next.</p>
        <button className="primary" onClick={() => onPractice(top.concept_id)}>Practise this topic</button>
      </section>

      {!anyAssessed && <p className="note-line">Try a few questions and your study plan will start to take shape.</p>}

      <h3 className="section">How each topic is going</h3>
      <ul className="bars">
        {mastery.map((m) => (
          <li key={m.concept_id}>
            <span className="label">{m.name}</span>
            <span className={m.assessed ? "track" : "track est"} title={m.assessed ? "" : "Estimated: not tested directly yet"}>
              <i style={{ width: `${m.score * 100}%`, background: scoreColor(m.score) }} />
              <b className="tick" style={{ left: "40%" }} />
            </span>
            <span className="val">{m.score.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <p className="muted small">The small marker is a gentle reminder to revisit. Hatched bars are estimates from connected topics you haven’t tried directly yet.</p>

      <h3 className="section">Topics to come back to</h3>
      <ol className="queue">
        {queue.map((q) => (
          <li key={q.concept_id}>
            <span><b>{q.name}</b><br /><span className="muted small">
              {mastery.find((m) => m.concept_id === q.concept_id)?.attempts === 0
                ? "Let’s get to know this topic with a first question."
                : q.score < 0.4 ? "A little extra practice here could help." : "A quick revisit can help keep this fresh."}
            </span></span>
            <button className="link" onClick={() => onPractice(q.concept_id)}>Try a question</button>
          </li>
        ))}
      </ol>

      <h3 className="section">How the topics connect</h3>
      <ConceptGraph graph={concepts} mastery={mastery} />
      <p className="muted small">Arrows show which ideas build on earlier ones. If a topic feels tricky, one of its neighbours may be a helpful place to start.</p>
    </>
  );
}
