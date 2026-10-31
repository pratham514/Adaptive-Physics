from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Concept, ConceptEdge, Mastery, Student
from ..schemas import ConceptGraph, ConceptOut, EdgeOut, MasteryOut, StudentCreate, StudentOut

router = APIRouter(tags=["students & concepts"])


@router.get("/concepts", response_model=ConceptGraph)
def concept_graph(db: Session = Depends(get_db)):
    nodes = db.query(Concept).order_by(Concept.position).all()
    edges = db.query(ConceptEdge).all()
    return ConceptGraph(nodes=[ConceptOut.model_validate(n) for n in nodes],
                        edges=[EdgeOut(source=e.prerequisite_id, target=e.concept_id) for e in edges])


@router.post("/students", response_model=StudentOut, status_code=201)
def create_student(body: StudentCreate, db: Session = Depends(get_db)):
    student = Student(name=body.name.strip())
    db.add(student)
    db.flush()
    for c in db.query(Concept).all():
        db.add(Mastery(student_id=student.id, concept_id=c.id))  # 0.5 prior
    db.commit()
    return student


@router.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student


@router.get("/students/{student_id}/mastery", response_model=list[MasteryOut])
def get_mastery(student_id: int, db: Session = Depends(get_db)):
    if not db.get(Student, student_id):
        raise HTTPException(404, "Student not found")
    rows = (db.query(Mastery, Concept).join(Concept, Concept.id == Mastery.concept_id)
            .filter(Mastery.student_id == student_id).order_by(Concept.position).all())
    return [MasteryOut(concept_id=c.id, name=c.name, topic=c.topic, score=round(m.score, 3),
                       attempts=m.attempts, correct_count=m.correct_count, assessed=m.attempts > 0)
            for m, c in rows]
