"""Diagnostic, attempts, adaptive practice."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Attempt, Concept, Mastery, Misconception, Question, Student
from ..schemas import (AttemptCreate, AttemptResult, DiagnosticNext, PracticeRequest, PracticeResponse,
                       QuestionPublic)
from ..services import nvidia
from ..services.mastery import record_attempt, target_difficulty, weakest_concept

router = APIRouter(tags=["quiz"])

DIAGNOSTIC_TOTAL = 5


@router.get("/diagnostic/next", response_model=DiagnosticNext)
def diagnostic_next(student_id: int, db: Session = Depends(get_db)):
    if not db.get(Student, student_id):
        raise HTTPException(404, "Student not found")
    diag_qs = (db.query(Question).filter(Question.diagnostic_order.isnot(None))
               .order_by(Question.diagnostic_order).all())
    answered_ids = {a.question_id for a in db.query(Attempt)
                    .filter(Attempt.student_id == student_id, Attempt.context == "diagnostic").all()}
    remaining = [q for q in diag_qs if q.id not in answered_ids]
    return DiagnosticNext(done=not remaining, answered=len(diag_qs) - len(remaining), total=len(diag_qs),
                          question=QuestionPublic.model_validate(remaining[0]) if remaining else None)


@router.post("/attempts", response_model=AttemptResult)
def submit_attempt(body: AttemptCreate, db: Session = Depends(get_db)):
    if not db.get(Student, body.student_id):
        raise HTTPException(404, "Student not found")
    question = db.get(Question, body.question_id)
    if not question:
        raise HTTPException(404, "Question not found")
    already = db.query(Attempt).filter(Attempt.student_id == body.student_id,
                                       Attempt.question_id == body.question_id).first()
    if already:
        raise HTTPException(409, "This question was already answered")

    attempt = record_attempt(db, body.student_id, question, body.selected_index, body.context)
    return AttemptResult(attempt_id=attempt.id, is_correct=attempt.is_correct, correct_index=question.correct_index,
                         explanation=question.explanation, concept_id=question.concept_id,
                         mastery_before=round(attempt.mastery_before, 3), mastery_after=round(attempt.mastery_after, 3),
                         needs_reasoning=not attempt.is_correct)


@router.post("/practice/next", response_model=PracticeResponse)
def practice_next(body: PracticeRequest, db: Session = Depends(get_db)):
    if not db.get(Student, body.student_id):
        raise HTTPException(404, "Student not found")

    if body.concept_id:
        m = db.get(Mastery, (body.student_id, body.concept_id))
        if not m:
            raise HTTPException(404, "Concept not found")
        reason = "Chosen by you"
    else:
        m = weakest_concept(db, body.student_id)
        reason = "Your weakest concept right now"
    concept = db.get(Concept, m.concept_id)
    label, difficulty = target_difficulty(m.score)

    seen = (db.query(Question).join(Attempt, Attempt.question_id == Question.id)
            .filter(Attempt.student_id == body.student_id, Question.concept_id == concept.id)
            .order_by(Attempt.id.desc()).all())
    recent_misc = [x.misconception_tag for x in
                   db.query(Misconception).filter(Misconception.student_id == body.student_id,
                                                  Misconception.concept_id == concept.id)
                   .order_by(Misconception.id.desc()).limit(3).all()
                   if x.misconception_tag and x.misconception_tag != "none"]

    question: Question | None = None
    try:
        g = nvidia.generate_question(concept, label, [q.stem for q in seen[:5]], recent_misc)
        question = Question(concept_id=concept.id, stem=g.stem, options=g.options, correct_index=g.correct_index,
                            explanation=g.explanation, difficulty=difficulty, source="nvidia")
        db.add(question)
        db.commit()
    except nvidia.AIUnavailable:
        # Offline fallback: closest-difficulty bank question the student hasn't answered yet.
        seen_ids = {q.id for q in seen}
        bank = db.query(Question).filter(Question.concept_id == concept.id, Question.source == "seed").all()
        pool = [q for q in bank if q.id not in seen_ids] or bank
        if not pool:
            raise HTTPException(503, "No question available for this concept")
        question = min(pool, key=lambda q: abs(q.difficulty - difficulty))
        reason += " (served from the built-in bank: AI unavailable)"

    return PracticeResponse(question=QuestionPublic.model_validate(question), concept_id=concept.id,
                            concept_name=concept.name, concept_score=round(m.score, 3),
                            difficulty_label=label, reason=f"{reason}: {concept.name}, mastery {m.score:.2f}")
