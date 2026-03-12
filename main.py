from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Web Nova Crew - Autonomous AI Company",
    description=(
        "An API-first operating system for a fully AI-agent-operated company "
        "with departments, autonomous workflows, and delivery tracking."
    ),
    version="1.0.0",
)


class Department(str, Enum):
    executive = "executive"
    product = "product"
    engineering = "engineering"
    design = "design"
    growth = "growth"
    operations = "operations"
    qa = "qa"


class AgentStatus(str, Enum):
    idle = "idle"
    busy = "busy"
    paused = "paused"


class TaskStatus(str, Enum):
    backlog = "backlog"
    assigned = "assigned"
    in_progress = "in_progress"
    review = "review"
    done = "done"


class Agent(BaseModel):
    id: str
    name: str
    role: str
    department: Department
    objective: str
    tools: List[str] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.idle
    active_tasks: List[str] = Field(default_factory=list)


class Task(BaseModel):
    id: str
    title: str
    description: str
    priority: int = Field(ge=1, le=5, description="1 is highest, 5 is lowest")
    requested_by: str
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.backlog
    deliverables: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Company(BaseModel):
    name: str
    mission: str
    departments: List[Department]
    agents: Dict[str, Agent] = Field(default_factory=dict)
    tasks: Dict[str, Task] = Field(default_factory=dict)
    delivery_history: List[str] = Field(default_factory=list)


class BootstrapRequest(BaseModel):
    company_name: str = "Web Nova Crew"
    mission: str = (
        "Build, ship, and scale modern digital experiences through autonomous AI teams."
    )


class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: int = Field(ge=1, le=5)
    requested_by: str
    deliverables: List[str] = Field(default_factory=list)


class AssignTaskRequest(BaseModel):
    agent_id: str


class TransitionTaskRequest(BaseModel):
    next_status: TaskStatus


class CycleResult(BaseModel):
    promoted_to_review: List[str]
    completed: List[str]
    assigned: List[str]


DEFAULT_AGENT_BLUEPRINTS = [
    {
        "name": "Astra",
        "role": "Chief Strategy Agent",
        "department": Department.executive,
        "objective": "Set company strategy and allocate resources.",
        "tools": ["roadmap-planner", "market-intel", "risk-engine"],
    },
    {
        "name": "Nova",
        "role": "Product Manager Agent",
        "department": Department.product,
        "objective": "Convert goals into product specs and prioritized roadmaps.",
        "tools": ["user-story-generator", "backlog-prioritizer"],
    },
    {
        "name": "Vector",
        "role": "Tech Lead Agent",
        "department": Department.engineering,
        "objective": "Architect reliable web platforms and API systems.",
        "tools": ["system-design", "codegen", "infra-planner"],
    },
    {
        "name": "Pixel",
        "role": "Design Agent",
        "department": Department.design,
        "objective": "Design UI/UX systems optimized for conversion and retention.",
        "tools": ["design-system", "persona-engine", "ux-reviewer"],
    },
    {
        "name": "Orbit",
        "role": "Growth Agent",
        "department": Department.growth,
        "objective": "Run acquisition campaigns and optimize funnels.",
        "tools": ["seo-orchestrator", "ad-copy-agent", "analytics"],
    },
    {
        "name": "Pulse",
        "role": "Operations Agent",
        "department": Department.operations,
        "objective": "Automate workflows, SLAs, and client communication.",
        "tools": ["workflow-automation", "notifier", "crm-sync"],
    },
    {
        "name": "Sentinel",
        "role": "QA Agent",
        "department": Department.qa,
        "objective": "Protect quality through autonomous validation and guardrails.",
        "tools": ["test-generator", "security-scan", "regression-monitor"],
    },
]


company_state: Optional[Company] = None


def _require_company() -> Company:
    if company_state is None:
        raise HTTPException(
            status_code=400,
            detail="Company not initialized. Call /company/bootstrap first.",
        )
    return company_state


def _first_idle_agent(company: Company) -> Optional[Agent]:
    for agent in company.agents.values():
        if agent.status == AgentStatus.idle:
            return agent
    return None


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Welcome to the Web Nova Crew Autonomous AI Company API.",
        "next_step": "POST /company/bootstrap to initialize autonomous operations.",
    }


@app.post("/company/bootstrap", response_model=Company)
def bootstrap_company(payload: BootstrapRequest) -> Company:
    global company_state

    agents: Dict[str, Agent] = {}
    for blueprint in DEFAULT_AGENT_BLUEPRINTS:
        agent_id = str(uuid4())
        agents[agent_id] = Agent(id=agent_id, **blueprint)

    company_state = Company(
        name=payload.company_name,
        mission=payload.mission,
        departments=list(Department),
        agents=agents,
    )
    return company_state


@app.get("/company/status", response_model=Company)
def company_status() -> Company:
    return _require_company()


@app.post("/tasks/create", response_model=Task)
def create_task(payload: CreateTaskRequest) -> Task:
    company = _require_company()

    task_id = str(uuid4())
    task = Task(
        id=task_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        requested_by=payload.requested_by,
        deliverables=payload.deliverables,
    )
    company.tasks[task_id] = task
    return task


@app.post("/tasks/{task_id}/assign", response_model=Task)
def assign_task(task_id: str, payload: AssignTaskRequest) -> Task:
    company = _require_company()

    if task_id not in company.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.agent_id not in company.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    task = company.tasks[task_id]
    agent = company.agents[payload.agent_id]

    if task.status == TaskStatus.done:
        raise HTTPException(status_code=400, detail="Task is already completed")

    task.assigned_agent_id = payload.agent_id
    task.status = TaskStatus.assigned
    if task.id not in agent.active_tasks:
        agent.active_tasks.append(task.id)
    agent.status = AgentStatus.busy

    return task


@app.post("/tasks/{task_id}/advance", response_model=Task)
def advance_task(task_id: str, payload: TransitionTaskRequest) -> Task:
    company = _require_company()

    if task_id not in company.tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = company.tasks[task_id]
    task.status = payload.next_status

    if task.assigned_agent_id:
        agent = company.agents[task.assigned_agent_id]
        if payload.next_status == TaskStatus.done:
            if task.id in agent.active_tasks:
                agent.active_tasks.remove(task.id)
            if not agent.active_tasks:
                agent.status = AgentStatus.idle

    if payload.next_status == TaskStatus.done:
        company.delivery_history.append(f"Delivered: {task.title}")

    return task


@app.post("/run-cycle", response_model=CycleResult)
def run_autonomous_cycle() -> CycleResult:
    company = _require_company()

    promoted_to_review: List[str] = []
    completed: List[str] = []
    assigned: List[str] = []

    for task in company.tasks.values():
        if task.status == TaskStatus.backlog:
            idle_agent = _first_idle_agent(company)
            if idle_agent:
                task.assigned_agent_id = idle_agent.id
                task.status = TaskStatus.in_progress
                idle_agent.status = AgentStatus.busy
                idle_agent.active_tasks.append(task.id)
                assigned.append(task.id)
        elif task.status == TaskStatus.in_progress:
            task.status = TaskStatus.review
            promoted_to_review.append(task.id)
        elif task.status == TaskStatus.review:
            task.status = TaskStatus.done
            completed.append(task.id)
            if task.assigned_agent_id:
                agent = company.agents[task.assigned_agent_id]
                if task.id in agent.active_tasks:
                    agent.active_tasks.remove(task.id)
                if not agent.active_tasks:
                    agent.status = AgentStatus.idle
            company.delivery_history.append(f"Delivered: {task.title}")

    return CycleResult(
        promoted_to_review=promoted_to_review,
        completed=completed,
        assigned=assigned,
    )


@app.get("/dashboard")
def dashboard() -> dict:
    company = _require_company()

    total_tasks = len(company.tasks)
    completed_tasks = len([t for t in company.tasks.values() if t.status == TaskStatus.done])
    in_progress = len(
        [
            t
            for t in company.tasks.values()
            if t.status in {TaskStatus.assigned, TaskStatus.in_progress, TaskStatus.review}
        ]
    )

    return {
        "company": company.name,
        "mission": company.mission,
        "department_count": len(company.departments),
        "agent_count": len(company.agents),
        "task_count": total_tasks,
        "tasks_in_flight": in_progress,
        "tasks_completed": completed_tasks,
        "delivery_history": company.delivery_history[-10:],
    }
