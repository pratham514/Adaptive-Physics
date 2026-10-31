import { useState } from "react";
import { api } from "../api.js";
import Reasoning from "./Reasoning.jsx";

export default function QuestionRunner({ studentId, question, context, conceptName, questionWhy, onNext, nextLabel }) {
  const [picked, setPicked] = useState(null);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [after, setAfter] = useState(null); // mastery after any reasoning refund

  async function check() {
    setBusy(true); setErr("");
    try {
      const r = await api.attempt({ student_id: studentId, question_id: question.id, selected_index: picked, context });
      setRes(r); setAfter(r.mastery_after);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  }

  return (
    <article className="question">
      <p className="muted small">{conceptName}</p>
      <h2 className="stem">{question.stem}</h2>
      {questionWhy && <p className="question-why">{questionWhy}</p>}
      <ol className="options" role="radiogroup" aria-label="Answer options">
        {question.options.map((o, i) => {
          let cls = "opt";
          if (res) {
            if (i === res.correct_index) cls += " right";
            else if (i === picked) cls += " wrong";
          } else if (i === picked) cls += " picked";
          return (
            <li key={i}>
              <button className={cls} disabled={!!res} role="radio" aria-checked={picked === i} onClick={() => setPicked(i)}>
                <span className="letter">{String.fromCharCode(65 + i)}</span>{o}
              </button>
            </li>
          );
        })}
      </ol>

      {!res && <button className="primary" disabled={picked === null || busy} onClick={check}>{busy ? "Checking…" : "Check my answer"}</button>}
      {err && <p className="error">{err}</p>}

      {res && (
        <>
          {res.is_correct ? (
            <>
              <p className="verdict good">You got it!</p>
              <p>{res.explanation}</p>
            </>
          ) : (
            <section className="miss-card" aria-live="polite">
              <p className="miss-title">Not quite — that’s part of learning.</p>
              <p className="miss-explanation">{res.explanation}</p>
              <p className="muted small">Your answer helps us choose a useful next step. Take a moment to tell us how you were thinking.</p>
            </section>
          )}
          <p className="delta small">
            Your {conceptName} snapshot is <b>{Math.round(after * 100)}%</b> (it was {Math.round(res.mastery_before * 100)}%). One answer is just one small clue.
          </p>
          {res.needs_reasoning && (
            <Reasoning attemptId={res.attempt_id} onFeedback={(f) => setAfter(f.mastery_after)} />
          )}
          <button className="primary" onClick={onNext}>{nextLabel}</button>
        </>
      )}
    </article>
  );
}
