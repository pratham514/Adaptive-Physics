from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, Mastery, Student
from ..schemas import ClassGaps, ClassRoster, ConceptGap, StudentRow

router = APIRouter(prefix="/teacher", tags=["teacher"])

STRUGGLING_BELOW = 0.1


@router.get("/class-gaps", response_model=ClassGaps)
def class_gaps(db: Session = Depends(get_db)):
    concepts = db.query(Concept).order_by(Concept.position).all()
    # Only count scores backed by at least one attempt, so a brand-new student doesn't dilute the class.
    rows = db.query(Mastery).filter(Mastery.attempts > 0).all()
    by_concept: dict[str, list[float]] = defaultdict(list)
    students = set()
    for m in rows:
        by_concept[m.concept_id].append(m.score)
        students.add(m.student_id)
    out = []
    for c in concepts:
        scores = by_concept.get(c.id, [])
        avg = sum(scores) / len(scores) if scores else 0.0
        out.append(ConceptGap(concept_id=c.id, name=c.name, topic=c.topic, avg_mastery=round(avg, 3),
                              gap=round(1 - avg, 3) if scores else 0.0,
                              struggling_count=sum(s < STRUGGLING_BELOW for s in scores),
                              students_assessed=len(scores)))
    return ClassGaps(student_count=len(students), concepts=out)


@router.get("/roster", response_model=ClassRoster)
def roster(db: Session = Depends(get_db)):
    concepts = db.query(Concept).order_by(Concept.position).all()
    students = db.query(Student).order_by(Student.id).all()
    mastery = defaultdict(dict)
    for m in db.query(Mastery).filter(Mastery.attempts > 0).all():
        mastery[m.student_id][m.concept_id] = round(m.score, 3)
    rows = []
    for s in students:
        # Keep newly added learners visible in the roster before their first
        # answer; the empty cells in the dashboard mean "not assessed yet".
        scores = mastery.get(s.id, {})
        average = round(sum(scores.values()) / len(scores), 3) if scores else 0.0
        rows.append(StudentRow(id=s.id, name=s.name, average=average, scores=scores))
    return ClassRoster(concepts=[c.id for c in concepts], students=rows)
