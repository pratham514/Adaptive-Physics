import { useEffect, useState } from "react";
import { api } from "./api.js";
import Diagnostic from "./views/Diagnostic.jsx";
import Practice from "./views/Practice.jsx";
import Plan from "./views/Plan.jsx";
import Teacher from "./views/Teacher.jsx";
import Backdrop from "./components/Backdrop.jsx";

const STUDENT_TABS = [
  ["diagnostic", "Quick check"],
  ["practice", "Practice"],
  ["plan", "My study plan"],
];

function RoleChoice({ onChoose }) {
  return <section className="role-chooser">
    <p className="eyebrow">A calm place to practise</p>
    <h2>How would you like to use Adaptive Physics?</h2>
    <p>Choose a view to get started. This prototype uses sample class data and built-in questions, so no AI key is needed.</p>
    <div className="role-grid">
      <button className="role-card" onClick={() => onChoose("student")}>
        <span className="role-icon" aria-hidden="true">✦</span>
        <strong>I’m a student</strong>
        <span>Try a quick check, practise tricky topics, and see how your progress compares with the sample class.</span>
        <span className="role-action">Go to student view →</span>
      </button>
      <button className="role-card" onClick={() => onChoose("teacher")}>
        <span className="role-icon" aria-hidden="true">▤</span>
        <strong>I’m a teacher</strong>
        <span>Explore the class snapshot, topic gaps, and each student’s progress.</span>
        <span className="role-action">Go to teacher view →</span>
      </button>
    </div>
    <p className="muted small prototype-note">The teacher view includes fictional students for demonstration.</p>
  </section>;
}

function Welcome({ onStart }) {
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  async function go(e) {
    e.preventDefault();
    try { onStart(await api.createStudent(name)); } catch (x) { setErr(x.message); }
  }
  return (
    <form className="welcome" onSubmit={go}>
        <h2>Let’s find a good place to start.</h2>
        <p>Try five short questions, then we’ll make a study plan that fits what you already know. No pressure—this is just a starting point.</p>
      <label htmlFor="name">What should we call you?</label>
      <input id="name" value={name} onChange={(e) => setName(e.target.value)} maxLength={60} autoFocus />
      <button className="primary" disabled={!name.trim()}>Try the first five questions</button>
      {err && <p className="error">{err}</p>}
    </form>
  );
}

export default function App() {
  const [tab, setTab] = useState("diagnostic");
  const [role, setRole] = useState(null);
  const [student, setStudent] = useState(null);
  const [concepts, setConcepts] = useState(null);
  const [ready, setReady] = useState(false);
  const [practiceConcept, setPracticeConcept] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setConcepts(await api.concepts());
        const id = localStorage.getItem("studentId");
        if (id) {
          try { setStudent(await api.student(id)); } catch { localStorage.removeItem("studentId"); }
        }
      } catch (e) { setError(e.message); }
      setReady(true);
    })();
  }, []);

  function start(s) {
    localStorage.setItem("studentId", s.id);
    setStudent(s);
  }
  function practiceThis(conceptId) {
    setPracticeConcept(conceptId);
    setTab("practice");
  }
  function switchStudent() {
    localStorage.removeItem("studentId");
    setStudent(null);
    setTab("diagnostic");
  }
  function chooseRole(nextRole) {
    setRole(nextRole);
    setTab(nextRole === "teacher" ? "teacher" : "diagnostic");
  }

  return (
    <div className="shell">
      <Backdrop />
      <header>
        <h1>Adaptive Physics</h1>
        <span className="sub">Class 10 physics · one step at a time</span>
        {role && <nav aria-label="Sections">
          {(role === "teacher" ? [["teacher", "Class overview"]] : STUDENT_TABS).map(([id, label]) => (
            <button key={id} className={tab === id ? "tab on" : "tab"} onClick={() => setTab(id)}>{label}</button>
          ))}
        </nav>}
        {role && <button className="role-switch" onClick={() => chooseRole(role === "teacher" ? "student" : "teacher")}>
          Switch to {role === "teacher" ? "student" : "teacher"} view
        </button>}
        {student && role === "student" && (
          <div className="who">Hi, {student.name} <button className="link" onClick={switchStudent}>change student</button></div>
        )}
      </header>
      <main>
        {role === null ? <RoleChoice onChoose={chooseRole} /> : error && <p className="error">{error}</p>}
        {role !== null && (!ready ? <p className="muted">Getting your study space ready…</p> : !concepts ? null : role === "teacher" ? (
          <Teacher />
        ) : !student ? (
          <Welcome onStart={start} />
        ) : tab === "diagnostic" ? (
          <Diagnostic student={student} concepts={concepts} onDone={() => setTab("plan")} />
        ) : tab === "practice" ? (
          <Practice student={student} concepts={concepts} conceptId={practiceConcept} clearConcept={() => setPracticeConcept(null)} />
        ) : tab === "plan" ? (
          <Plan student={student} concepts={concepts} onPractice={practiceThis} />
        ) : null)}
      </main>
    </div>
  );
}
