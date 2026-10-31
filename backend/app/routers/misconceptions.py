from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Attempt, Concept, Mastery, Misconception, Question
from ..schemas import MisconceptionOut, ReasoningSubmit
from ..services import nvidia
from ..services.mastery import clamp

router = APIRouter(prefix="/misconceptions", tags=["misconceptions"])

# A wrong answer backed by correct reasoning was a slip, so give back part of the penalty.
REFUND_SHARE = {"sound": 0.5, "partially_sound": 0.25}


def _to_out(row: Misconception, mastery_after: float) -> MisconceptionOut:
    return MisconceptionOut(attempt_id=row.attempt_id, cleaned_reasoning=row.cleaned_reasoning, verdict=row.verdict,
                            misconception_tag=row.misconception_tag, what_went_wrong=row.what_went_wrong,
                            correct_idea=row.correct_idea, hint=row.hint, mastery_refund=round(row.mastery_refund, 3),
                            mastery_after=round(mastery_after, 3))


@router.post("/analyze", response_model=MisconceptionOut)
def analyze(body: ReasoningSubmit, db: Session = Depends(get_db)):
    attempt = db.get(Attempt, body.attempt_id)
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    if attempt.is_correct:
        raise HTTPException(400, "Reasoning review is only for wrong answers")

    m = db.get(Mastery, (attempt.student_id, attempt.concept_id))
    existing = db.query(Misconception).filter(Misconception.attempt_id == attempt.id).first()
    if existing:
        return _to_out(existing, m.score)

    question = db.get(Question, attempt.question_id)
    concept = db.get(Concept, attempt.concept_id)
    try:
        if not nvidia.is_configured():
            raise nvidia.AIUnavailable("Prototype feedback mode")
        result = nvidia.analyze_reasoning(concept, question.stem, question.options, question.correct_index,
                                          attempt.selected_index, body.reasoning)
    except nvidia.AIUnavailable:
        # Let the prototype demonstrate the complete reflection step without
        # requiring a live provider. Be explicit that this is sample guidance.
        result = nvidia.ReasoningAnalysis(
            cleaned_reasoning=body.reasoning.strip(),
            verdict="unclear",
            misconception_tag="demo_sample",
            what_went_wrong="This prototype is not connected to an AI provider yet, so it cannot diagnose your reasoning. Here is the question explanation to help you review.",
            correct_idea=question.explanation,
            hint="Compare your steps with the explanation, then try another question.",
        )

    lost = max(0.0, attempt.mastery_before - attempt.mastery_after)
    refund = lost * REFUND_SHARE.get(result.verdict, 0.0)
    m.score = clamp(m.score + refund)

    row = Misconception(attempt_id=attempt.id, student_id=attempt.student_id, concept_id=attempt.concept_id,
                        input_mode=body.input_mode, raw_reasoning=body.reasoning,
                        cleaned_reasoning=result.cleaned_reasoning, verdict=result.verdict,
                        misconception_tag=(result.misconception_tag or "none")[:60],
                        what_went_wrong=result.what_went_wrong, correct_idea=result.correct_idea,
                        hint=result.hint, mastery_refund=refund)
    db.add(row)
    db.commit()
    return _to_out(row, m.score)
