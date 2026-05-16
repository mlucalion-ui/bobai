"""Project CRUD routes. Day-1 scope: list + create + detail stub."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import get_session
from app.models import Project

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    projects = session.exec(select(Project).order_by(Project.created_at.desc())).all()
    return templates.TemplateResponse(
        request, "projects/list.html", {"projects": projects}
    )


@router.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    name: str = Form(...),
    client: str = Form(...),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    project = Project(name=name.strip(), client=client.strip())
    session.add(project)
    session.commit()
    session.refresh(project)
    return templates.TemplateResponse(
        request, "projects/_card.html", {"project": project}
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(
    request: Request,
    project_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    project = session.get(Project, project_id)
    if not project:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request, "projects/detail.html", {"project": project}
    )
