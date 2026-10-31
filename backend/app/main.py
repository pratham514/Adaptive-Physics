from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import misconceptions, quiz, review, students, teacher
from .seed import seed_if_empty
from .services import nvidia


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(title="Adaptive Physics (Class 10)", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])

for r in (students.router, quiz.router, misconceptions.router, review.router, teacher.router):
    app.include_router(r)


@app.get("/health")
def health():
    return {"status": "ok", "nvidia_configured": nvidia.is_configured(),
            "provider": "nvidia", "model": settings.nvidia_model}
