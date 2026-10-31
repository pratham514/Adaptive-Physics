"""Mastery scoring (0..1) and spaced-review scheduling.

Score update is Elo/IRT-flavoured: compare the outcome with how likely a student at
this mastery level was to get a question of this difficulty right.
  - correct on a hard question  -> big rise (outcome was unlikely)
  - correct on an easy question -> small rise
  - wrong on an easy question   -> big drop
  - wrong on a hard question    -> small drop
"""
import math
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import Attempt, ConceptEdge, Mastery, Question, utcnow

GUESS_FLOOR = 0.25  # 4-option MCQ
SLOPE = 6.0
PREREQ_SHARE = 0.25  # share of a positive gain passed to prerequisite concepts


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def expected_correct(mastery: float, difficulty: float) -> float:
    p = 1.0 / (1.0 + math.exp(-SLOPE * (mastery - difficulty)))
    return GUESS_FLOOR + (1 - GUESS_FLOOR) * p


def learning_rate(attempts: int) -> float:
    # Move fast on little evidence, settle as evidence accumulates.
    return max(0.08, 0.35 / (1 + 0.3 * attempts))


def new_score(mastery: float, difficulty: float, correct: bool, attempts: int) -> float:
    delta = learning_rate(attempts) * ((1.0 if correct else 0.0) - expected_correct(mastery, difficulty))
    return clamp(mastery + delta)


def schedule_next_review(m: Mastery, correct: bool, now: datetime) -> None:
    if correct:
        m.interval_days = max(1.0, m.interval_days * (1.5 + m.score))  # stronger => longer gaps
    else:
        m.interval_days = 0.25  # revisit within ~6 hours
    m.due_at = now + timedelta(days=m.interval_days)


def record_attempt(db: Session, student_id: int, question: Question, selected_index: int, context: str) -> Attempt:
    now = utcnow()
    m = db.get(Mastery, (student_id, question.concept_id))
    correct = selected_index == question.correct_index
    before = m.score
    m.score = new_score(before, question.difficulty, correct, m.attempts)
    m.attempts += 1
    m.correct_count += int(correct)
    m.last_practiced = now
    schedule_next_review(m, correct, now)

    gain = m.score - before
    if gain > 0:
        # Succeeding at a concept is weak evidence its prerequisites are OK.
        prereqs = db.query(ConceptEdge).filter(ConceptEdge.concept_id == question.concept_id).all()
        for edge in prereqs:
            pm = db.get(Mastery, (student_id, edge.prerequisite_id))
            pm.score = clamp(pm.score + PREREQ_SHARE * gain)

    attempt = Attempt(student_id=student_id, question_id=question.id, concept_id=question.concept_id,
                      selected_index=selected_index, is_correct=correct, context=context,
                      mastery_before=before, mastery_after=m.score)
    db.add(attempt)
    db.commit()
    return attempt


# ---- picking what to practise ------------------------------------------------
def weakest_concept(db: Session, student_id: int) -> Mastery:
    rows = db.query(Mastery).filter(Mastery.student_id == student_id).all()
    return min(rows, key=lambda m: (m.score, m.attempts))


def target_difficulty(score: float) -> tuple[str, float]:
    """Aim slightly above current mastery (zone of proximal development)."""
    target = clamp(score + 0.1, 0.15, 0.9)
    if target < 0.4:
        return "easy", 0.25
    if target < 0.65:
        return "medium", 0.5
    return "hard", 0.8


# ---- spaced review -----------------------------------------------------------
def review_priority(m: Mastery, now: datetime) -> tuple[float, str]:
    weakness = 1.0 - m.score
    if m.due_at is None:
        return weakness * 1.0, "Not assessed yet"
    interval = max(m.interval_days, 0.25)
    ratio = (now - m.due_at).total_seconds() / 86400 / interval  # >0 overdue, <0 not due yet
    factor = clamp(1 + ratio, 0.3, 3.0)
    if ratio >= 0:
        hours = (now - m.due_at).total_seconds() / 3600
        when = "due now" if hours < 1 else f"overdue by {hours / 24:.1f} days" if hours >= 24 else f"overdue by {hours:.0f} h"
    else:
        hours = (m.due_at - now).total_seconds() / 3600
        when = f"due in {hours / 24:.1f} days" if hours >= 24 else f"due in {hours:.0f} h"
    return weakness * factor, f"Mastery {m.score:.2f}, {when}"
