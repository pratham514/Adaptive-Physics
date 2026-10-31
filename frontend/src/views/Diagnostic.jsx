import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import QuestionRunner from "../components/QuestionRunner.jsx";

export default function Diagnostic({ student, concepts, onDone }) {
  const [state, setState] = useState(null);
  const [err, setErr] = useState("");
  const load = useCallback(async () => {
    try { setState(await api.diagNext(student.id)); } catch (e) { setErr(e.message); }
  }, [student.id]);
  useEffect(() => { load(); }, [load]);

  if (err) return <p className="error">{err}</p>;
  if (!state) return <p className="muted">Getting your first question ready…</p>;
  if (state.done) {
    return (
      <div className="welcome">
        <h2>That’s your first five done!</h2>
        <p>You’ve got a helpful starting snapshot. Let’s take a look at what to practise next.</p>
        <button className="primary" onClick={onDone}>See my study plan</button>
      </div>
    );
  }
  const name = concepts.nodes.find((c) => c.id === state.question.concept_id)?.name;
  return (
    <>
      <p className="progress" aria-label={`Question ${state.answered + 1} of ${state.total}`}>
        {Array.from({ length: state.total }, (_, i) => <i key={i} className={i < state.answered ? "done" : i === state.answered ? "now" : ""} />)}
        <span>A few questions to get us started · {state.answered + 1} of {state.total}</span>
      </p>
      <QuestionRunner key={state.question.id} studentId={student.id} question={state.question} context="diagnostic"
        conceptName={name} onNext={load} nextLabel={state.answered + 1 === state.total ? "See my study plan" : "Next question"} />
    </>
  );
}
