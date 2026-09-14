# TaskStudio AI — Powered by Antigravity

**TaskStudio AI** is a real-time, autonomous sprint canvas and AI project manager built using pure modern web technologies (semantic HTML5, Vanilla CSS design system, modular JavaScript) and an Antigravity Agent backend.

This application serves as the runnable reference implementation for **Chapter 17: Building Applications with Antigravity: From Idea to Production** in *Mastering Antigravity*.

---

## 🌟 Key Features

1. **Aesthetic Vanilla CSS Design System**:
   - Zero heavyweight CSS framework dependencies.
   - Deep dark-mode palette with glassmorphism (`backdrop-filter: blur(20px)`).
   - Dynamic accent borders, glowing status badges, and 60fps micro-animations.
   - Fully responsive CSS Grid and Flexbox layout.

2. **Autonomous Agent Telemetry**:
   - Live Server-Sent Events (SSE) stream (`/api/agent/stream`).
   - Real-time display of agent reasoning thoughts (`response.thoughts`), active tool invocations (grep, file edits, bash commands), and decomposed task cards.

3. **Sprint Kanban Board**:
   - Four execution lanes: *To Do*, *In Progress*, *Review & QA*, *Completed*.
   - Interactive task creation modal, priority tags, and lane progression.

---

## 🚀 Running Locally

### Option 1: Standalone Browser Mode (No Dependencies)
Simply open `index.html` directly in any modern web browser. The client-side application logic automatically detects when running offline and uses local seed state and simulation loops.

### Option 2: Full-Stack Mode with FastAPI Backend
Install dependencies and run the Uvicorn server:
```bash
pip install fastapi uvicorn pydantic
python3 server.py
```
Open your browser at `http://localhost:8000`.

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python3 -m unittest test_app.py
```
