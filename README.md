# Web Nova Crew Agents

A complete API backend for a **fully AI-agent-operated company** named Web Nova Crew.

## What this includes

- Company bootstrap with cross-functional AI departments.
- Autonomous AI agents with roles, objectives, and tool stacks.
- Task pipeline from backlog to done.
- Autonomous execution cycle (`/run-cycle`) for assignment, review, and delivery.
- Dashboard metrics for operations and delivery visibility.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:
- `http://127.0.0.1:8000/docs` for Swagger UI.

## Key endpoints

- `POST /company/bootstrap` Initialize Web Nova Crew AI company.
- `GET /company/status` View agents, departments, and tasks.
- `POST /tasks/create` Add new client/project tasks.
- `POST /tasks/{task_id}/assign` Assign specific tasks to an agent.
- `POST /tasks/{task_id}/advance` Move a task to another workflow state.
- `POST /run-cycle` Run one autonomous company execution cycle.
- `GET /dashboard` KPI snapshot of company operations.
