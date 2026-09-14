"""
TaskStudio AI — Backend Server & Antigravity Agent Gateway
Exposes task REST APIs and Server-Sent Events (SSE) streaming thought loops.
"""

import asyncio
import json
import os
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="TaskStudio AI — Powered by Antigravity",
    description="Full-stack AI task orchestrator with real-time thought streaming",
    version="1.0.0"
)

# Enable CORS for decoupled dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task database
class TaskItem(BaseModel):
    id: str
    title: str
    desc: Optional[str] = ""
    lane: str = "todo"
    priority: str = "medium"

class TaskPatch(BaseModel):
    lane: Optional[str] = None
    title: Optional[str] = None
    desc: Optional[str] = None
    priority: Optional[str] = None

# Initial seed tasks
TASKS_DB: List[TaskItem] = [
    TaskItem(
        id="TSK-101",
        title="Implement Antigravity SSE thought streaming",
        desc="Stream agent token deltas and tool execution diffs to client UI in real time.",
        lane="done",
        priority="high"
    ),
    TaskItem(
        id="TSK-102",
        title="Design high-contrast glassmorphism board",
        desc="Create dark-mode design system with pure Vanilla CSS, custom tokens, and 60fps animations.",
        lane="in-progress",
        priority="medium"
    ),
    TaskItem(
        id="TSK-103",
        title="Write headless browser subagent smoke test",
        desc="Automate DOM verification, screenshot capture, and recording check.",
        lane="todo",
        priority="high"
    ),
    TaskItem(
        id="TSK-104",
        title="Benchmark API endpoint response latency",
        desc="Verify p95 response time is under 45ms under concurrent simulated loads.",
        lane="review",
        priority="low"
    )
]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Static Web Assets
# ---------------------------------------------------------------------------
@app.get("/")
async def get_index():
    """Serves the main application landing page."""
    return FileResponse(os.path.join(CURRENT_DIR, "index.html"))

@app.get("/style.css")
async def get_css():
    """Serves Vanilla CSS stylesheet."""
    return FileResponse(os.path.join(CURRENT_DIR, "style.css"), media_type="text/css")

@app.get("/app.js")
async def get_js():
    """Serves client JavaScript."""
    return FileResponse(os.path.join(CURRENT_DIR, "app.js"), media_type="application/javascript")

# ---------------------------------------------------------------------------
# Task Management REST APIs
# ---------------------------------------------------------------------------
@app.get("/api/tasks", response_model=List[TaskItem])
async def list_tasks():
    """Returns all sprint task cards."""
    return TASKS_DB

@app.post("/api/tasks", response_model=TaskItem, status_code=201)
async def create_task(task: TaskItem):
    """Creates a new task card."""
    # Ensure unique ID
    existing = [t for t in TASKS_DB if t.id == task.id]
    if existing:
        task.id = f"TSK-{random.randint(500, 999)}"
    TASKS_DB.append(task)
    return task

@app.patch("/api/tasks/{task_id}", response_model=TaskItem)
async def update_task(task_id: str, patch: TaskPatch):
    """Updates task status or attributes."""
    for item in TASKS_DB:
        if item.id == task_id:
            if patch.lane is not None:
                item.lane = patch.lane
            if patch.title is not None:
                item.title = patch.title
            if patch.desc is not None:
                item.desc = patch.desc
            if patch.priority is not None:
                item.priority = patch.priority
            return item
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Deletes a task by ID."""
    global TASKS_DB
    before_len = len(TASKS_DB)
    TASKS_DB = [t for t in TASKS_DB if t.id != task_id]
    if len(TASKS_DB) == before_len:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted", "id": task_id}

# ---------------------------------------------------------------------------
# Antigravity Agent SSE Stream Endpoint
# ---------------------------------------------------------------------------
async def agent_event_generator(goal: str):
    """
    Streams Antigravity reasoning loops:
    1. Yields real-time thoughts (response.thoughts)
    2. Emits tool executions (grep, replace, run_command)
    3. Emits resulting deliverables / decomposed task cards
    4. Emits completion signal
    """
    # 1. Initial Thought: Spec parsing & Planning Mode
    yield f"event: thought\ndata: {json.dumps({'text': f'Parsing objective: \"{goal}\"' })}\n\n"
    await asyncio.sleep(0.4)

    yield f"event: thought\ndata: {json.dumps({'text': 'Consulting workspace rules in .agents/rules/tech-stack.md and checking system invariants...' })}\n\n"
    await asyncio.sleep(0.5)

    # 2. Tool Call Emulation: Static analysis / DOM search
    yield f"event: tool_call\ndata: {json.dumps({'name': 'grep_search', 'summary': 'Searching workspace for key tokens', 'action': 'Searching codebase', 'diff': f'grep -r \"{goal[:12]}\" src/' })}\n\n"
    await asyncio.sleep(0.6)

    # 3. Intermediate Thought: Architectural decisions
    yield f"event: thought\ndata: {json.dumps({'text': 'Formulating zero-regression execution plan. Scaffolding dynamic task card with testable acceptance criteria.' })}\n\n"
    await asyncio.sleep(0.5)

    # 4. Action: Create actionable task in board
    new_task = TaskItem(
        id=f"TSK-{random.randint(600, 899)}",
        title=f"Autonomous Goal: {goal[:45]}",
        desc=f"Objective: {goal}\nAcceptance Criteria: All unit and visual regression tests pass.",
        lane="in-progress",
        priority="high"
    )
    TASKS_DB.append(new_task)
    yield f"event: task_created\ndata: {new_task.model_dump_json()}\n\n"
    await asyncio.sleep(0.5)

    # 5. Tool Call: Test Verification
    yield f"event: tool_call\ndata: {json.dumps({'name': 'run_command', 'summary': 'Executing headless smoke test', 'action': 'Running test suite', 'diff': 'pytest -v test_app.py\n✓ 5 passed in 0.24s' })}\n\n"
    await asyncio.sleep(0.5)

    # 6. Completion
    yield f"event: complete\ndata: {json.dumps({'status': 'fulfilled', 'goal': goal})}\n\n"

@app.get("/api/agent/stream")
async def stream_agent(goal: str):
    """
    Server-Sent Events endpoint streaming real-time Antigravity reasoning.
    """
    return StreamingResponse(
        agent_event_generator(goal),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
