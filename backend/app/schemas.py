from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- concepts / graph -------------------------------------------------------
class ConceptOut(ORM):
    id: str
    name: str
    topic: str
    summary: str
    key_ideas: list[str]
    position: int


class EdgeOut(BaseModel):
    source: str  # prerequisite
    target: str  # concept that builds on it


class ConceptGraph(BaseModel):
    nodes: list[ConceptOut]
    edges: list[EdgeOut]


# ---- students / mastery -----------------------------------------------------
class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class StudentOut(ORM):
    id: int
    name: str
    is_demo: bool


class MasteryOut(BaseModel):
    concept_id: str
    name: str
    topic: str
    score: float
    attempts: int
    correct_count: int
    assessed: bool  # False => score is still the 0.5 prior or only inferred from prerequisites


# ---- questions / attempts ---------------------------------------------------
class QuestionPublic(ORM):
    """What the student sees: never includes the answer."""

    id: int
    concept_id: str
    stem: str
    options: list[str]
    difficulty: float
    source: str


class AttemptCreate(BaseModel):
    student_id: int
    question_id: int
    selected_index: int = Field(ge=0, le=3)
    context: Literal["diagnostic", "practice"]


class AttemptResult(BaseModel):
    attempt_id: int
    is_correct: bool
    correct_index: int
    explanation: str
    concept_id: str
    mastery_before: float
    mastery_after: float
    needs_reasoning: bool  # True when wrong: frontend should ask "walk me through your thinking"


class DiagnosticNext(BaseModel):
    done: bool
    answered: int
    total: int
    question: QuestionPublic | None = None


# ---- practice ---------------------------------------------------------------
class PracticeRequest(BaseModel):
    student_id: int
    concept_id: str | None = None  # override; default = weakest concept


class PracticeResponse(BaseModel):
    question: QuestionPublic
    concept_id: str
    concept_name: str
    concept_score: float
    difficulty_label: Literal["easy", "medium", "hard"]
    reason: str


# ---- misconceptions ---------------------------------------------------------
class ReasoningSubmit(BaseModel):
    attempt_id: int
    reasoning: str = Field(min_length=1, max_length=3000)
    input_mode: Literal["text", "voice"] = "text"


class MisconceptionOut(BaseModel):
    attempt_id: int
    cleaned_reasoning: str
    verdict: Literal["sound", "partially_sound", "flawed", "unclear"]
    misconception_tag: str
    what_went_wrong: str
    correct_idea: str
    hint: str
    mastery_refund: float
    mastery_after: float


# ---- spaced review ----------------------------------------------------------
class ReviewItem(BaseModel):
    rank: int
    concept_id: str
    name: str
    topic: str
    score: float
    priority: float
    due_at: datetime | None
    reason: str


# ---- teacher ----------------------------------------------------------------
class ConceptGap(BaseModel):
    concept_id: str
    name: str
    topic: str
    avg_mastery: float
    gap: float  # 1 - avg_mastery
    struggling_count: int  # students below 0.4
    students_assessed: int


class ClassGaps(BaseModel):
    student_count: int
    concepts: list[ConceptGap]


class StudentRow(BaseModel):
    id: int
    name: str
    average: float
    scores: dict[str, float]


class ClassRoster(BaseModel):
    concepts: list[str]
    students: list[StudentRow]
