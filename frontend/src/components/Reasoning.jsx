import { useRef, useState } from "react";
import { api } from "../api.js";

const SR = typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);

const VERDICT = {
  sound: "Your idea was on track — maybe just a small slip.",
  partially_sound: "You have part of the idea. Let’s fill in one small gap.",
  flawed: "This is a common mix-up. Let’s untangle it together.",
  unclear: "Could you share a little more about what you were thinking?",
};

export default function Reasoning({ attemptId, onFeedback }) {
  const [text, setText] = useState("");
  const [usedVoice, setUsedVoice] = useState(false);
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [fb, setFb] = useState(null);
  const rec = useRef(null);

  function toggleMic() {
    if (listening) { rec.current?.stop(); return; }
    const r = new SR();
    r.lang = "en-IN";
    r.continuous = true;
    r.interimResults = false;
    r.onresult = (e) => {
      let t = "";
      for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript + " ";
      setText((p) => (p + " " + t).trim());
      setUsedVoice(true);
    };
    r.onend = () => setListening(false);
    r.onerror = () => { setListening(false); setErr("The microphone didn't work. You can type instead."); };
    r.start();
    rec.current = r;
    setListening(true);
  }

  async function send() {
    setBusy(true); setErr("");
    try {
      const out = await api.analyze({ attempt_id: attemptId, reasoning: text, input_mode: usedVoice ? "voice" : "text" });
      setFb(out);
      onFeedback?.(out);
    } catch (e) {
      const message = String(e.message || "");
      setErr(message.includes("NVIDIA_API_KEY")
        ? "Your AI tutor isn’t connected yet. Add your NVIDIA key to backend/.env and restart the backend. Your answer is still here."
        : message);
    }
    setBusy(false);
  }

  if (fb) {
    return (
      <section className="margin-note" aria-live="polite">
        {fb.misconception_tag === "demo_sample" && <p className="eyebrow">Prototype sample feedback</p>}
        <h3>{fb.misconception_tag === "demo_sample" ? "Thanks for sharing your thinking." : VERDICT[fb.verdict]}</h3>
        <p className="muted small">Here’s what we heard: {fb.cleaned_reasoning}</p>
        {fb.verdict !== "sound" && fb.what_went_wrong && <p>{fb.what_went_wrong}</p>}
        {fb.correct_idea && <p><strong>The idea:</strong> {fb.correct_idea}</p>}
        {fb.hint && <p><strong>Try this:</strong> {fb.hint}</p>}
        {fb.mastery_refund > 0 && <p className="small good">Your score got a small boost back.</p>}
      </section>
    );
  }

  return (
    <section className="margin-note">
      <h3>What was going through your mind?</h3>
      <p className="muted small">You can type or speak naturally. Pauses, “um”s and changing your mind are all okay.</p>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4}
        placeholder="I chose this answer because…" aria-label="Your reasoning" />
      <div className="row">
        {SR && (
          <button type="button" className={listening ? "ghost live" : "ghost"} onClick={toggleMic}>
            {listening ? "Stop speaking" : "Use my voice"}
          </button>
        )}
        <button className="primary" disabled={busy || !text.trim()} onClick={send}>{busy ? "Thinking it through…" : "Get a little guidance"}</button>
      </div>
      {err && <p className="error">{err}</p>}
    </section>
  );
}
