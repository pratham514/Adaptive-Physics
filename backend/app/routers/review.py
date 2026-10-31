from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, Mastery, Student, utcnow
from ..schemas import ReviewItem
from ..services.mastery import review_priority

router = APIRouter(tags=["spaced review"])


@router.get("/students/{student_id}/review-queue", response_model=list[ReviewItem])
def review_queue(student_id: int, db: Session = Depends(get_db)):
    if not db.get(Student, student_id):
        raise HTTPException(404, "Student not found")
    now: datetime = utcnow()
    rows = (db.query(Mastery, Concept).join(Concept, Concept.id == Mastery.concept_id)
            .filter(Mastery.student_id == student_id).all())
    scored = []
    for m, c in rows:
        priority, reason = review_priority(m, now)
        scored.append((priority, m, c, reason))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [ReviewItem(rank=i + 1, concept_id=c.id, name=c.name, topic=c.topic, score=round(m.score, 3),
                       priority=round(p, 3), due_at=m.due_at, reason=reason)
            for i, (p, m, c, reason) in enumerate(scored)]
