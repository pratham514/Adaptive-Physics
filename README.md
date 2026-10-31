# Adaptive Physics

An adaptive Class 10 Physics prototype built with React, FastAPI, and SQLite. It tracks concept mastery, selects practice based on weaker areas, and gives students and teachers separate views of progress and class gaps.

## Run locally

Use two terminals from the project folder.

**Terminal 1 — backend:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend:**

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. The backend API docs are at http://127.0.0.1:8000/docs. No API key is needed for this prototype: practice uses the built-in question bank, and the reasoning step clearly labels its sample feedback. The NVIDIA integration can be connected later by adding a key to `backend/.env`; never put a real key in source code or `.env.example`.

The SQLite database is created and seeded at `backend/adaptive_physics.db` on the first backend start. The seed contains 10 linked concepts, 10 questions, and 10 demo students.

## Features

- Five-question diagnostic and mastery scores from 0 to 1 across ten Physics concepts.
- Difficulty-aware mastery updates and practice targeted at the student's weakest concept.
- A typed or voice-transcribed reflection step after wrong answers, with clearly labeled sample feedback while no AI provider is connected.
- Concept graph and spaced-review queue.
- Student progress compared with the fictional sample class.
- Teacher dashboard with class-wide concept gaps and a student mastery matrix, including students who have not answered yet.

## Project layout

```text
backend/
  app/             FastAPI routes, SQLite models, seed data, and adaptive services
frontend/
  src/             React app, student and teacher views, and responsive styles
```
