import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import QuestionRunner from "../components/QuestionRunner.jsx";

export default function Practice({ student, conceptId, clearConcept }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);

  const next = useCallback(async (forced) => {
    setLoading(true); setErr("");
    try { setData(await api.practiceNext(student.id, forced)); } catch (e) { setErr(e.message); }
    setLoading(false);
  }, [student.id]);

  useEffect(() => { next(conceptId || undefined); if (conceptId) clearConcept(); }, []); // eslint-disable-line

  if (loading) return <p className="muted">Finding a useful question for you…</p>;
  if (err) return <><p className="error">{err}</p><button className="ghost" onClick={() => next()}>Try again</button></>;
  const why = data.reason.startsWith("Chosen by you")
    ? `Picked because you chose ${data.concept_name} to practise.`
    : `Picked because ${data.concept_name} is a good topic to strengthen next.`;
  return (
    <>
      <QuestionRunner key={data.question.id} studentId={student.id} question={data.question} context="practice"
        conceptName={data.concept_name} questionWhy={`${why} ${data.difficulty_label[0].toUpperCase()}${data.difficulty_label.slice(1)} level.`}
        onNext={() => next()} nextLabel="Try another question" />
    </>
  );
}
