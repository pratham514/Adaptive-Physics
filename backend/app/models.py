from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow() -> datetime:
    """Naive UTC timestamps everywhere (SQLite has no tz support)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    topic: Mapped[str] = mapped_column(String(80))  # NCERT chapter grouping
    summary: Mapped[str] = mapped_column(Text)
    key_ideas: Mapped[list] = mapped_column(JSON)
    position: Mapped[int] = mapped_column(Integer)


class ConceptEdge(Base):
    """Directed edge: `prerequisite_id` should be understood before `concept_id`."""

    __tablename__ = "concept_edges"

    prerequisite_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"), primary_key=True)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"), index=True)
    stem: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[float] = mapped_column(Float)  # 0 (easy) .. 1 (hard)
    source: Mapped[str] = mapped_column(String(10), default="seed")  # seed | nvidia
    diagnostic_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Mastery(Base):
    """One row per (student, concept): score plus spaced-review state."""

    __tablename__ = "mastery"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    score: Mapped[float] = mapped_column(Float, default=0.5)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    interval_days: Mapped[float] = mapped_column(Float, default=0.0)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"))
    selected_index: Mapped[int] = mapped_column(Integer)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    context: Mapped[str] = mapped_column(String(12))  # diagnostic | practice
    mastery_before: Mapped[float] = mapped_column(Float)
    mastery_after: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Misconception(Base):
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), unique=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id"))
    input_mode: Mapped[str] = mapped_column(String(6))  # text | voice
    raw_reasoning: Mapped[str] = mapped_column(Text)
    cleaned_reasoning: Mapped[str] = mapped_column(Text)
    verdict: Mapped[str] = mapped_column(String(20))
    misconception_tag: Mapped[str] = mapped_column(String(60))
    what_went_wrong: Mapped[str] = mapped_column(Text)
    correct_idea: Mapped[str] = mapped_column(Text)
    hint: Mapped[str] = mapped_column(Text)
    mastery_refund: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
