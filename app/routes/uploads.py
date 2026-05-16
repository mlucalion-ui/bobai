"""Upload routes — file upload and pasted-text upload.

File and paste flows share the same POST endpoint; both produce an Upload
row and return the rendered card partial for HTMX append.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import get_session
from app.models import Project, Upload
from pipeline.ingest import UnsupportedFormat, detect_kind, extract_text

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_ROOT = Path("var/uploads")


def _project_dir(project_id: int) -> Path:
    d = UPLOAD_ROOT / str(project_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


@router.post("/projects/{project_id}/uploads", response_class=HTMLResponse)
async def create_upload(
    request: Request,
    project_id: int,
    file: UploadFile | None = File(default=None),
    paste_name: str = Form(default=""),
    paste_text: str = Form(default=""),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "project not found")

    is_paste = bool(paste_text.strip())
    is_file = file is not None and file.filename

    if not is_paste and not is_file:
        raise HTTPException(400, "Provide a file or pasted text")

    if is_file:
        filename = file.filename
        kind = detect_kind(filename)
        ext = Path(filename).suffix or ".bin"
        stored_path = _project_dir(project_id) / f"{uuid.uuid4().hex}{ext}"
        data = await file.read()
        stored_path.write_bytes(data)
        try:
            text = extract_text(stored_path)
        except UnsupportedFormat as exc:
            text = f"[ingestion not yet supported for this format: {exc}]"
        upload = Upload(
            project_id=project_id,
            filename=filename,
            path=str(stored_path),
            kind=kind,
            size_bytes=len(data),
            text=text,
        )
    else:
        name = paste_name.strip() or "Pasted text"
        stored_path = _project_dir(project_id) / f"paste_{uuid.uuid4().hex}.txt"
        stored_path.write_text(paste_text)
        upload = Upload(
            project_id=project_id,
            filename=name if name.endswith(".txt") else f"{name}.txt",
            path=str(stored_path),
            kind="paste",
            size_bytes=len(paste_text.encode()),
            text=paste_text.strip(),
        )

    session.add(upload)
    session.commit()
    session.refresh(upload)

    return templates.TemplateResponse(
        request, "projects/_upload_card.html", {"upload": upload}
    )


@router.post("/projects/{project_id}/uploads/{upload_id}/delete", response_class=HTMLResponse)
def delete_upload(
    request: Request,
    project_id: int,
    upload_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    upload = session.get(Upload, upload_id)
    if not upload or upload.project_id != project_id:
        raise HTTPException(404, "upload not found")
    try:
        Path(upload.path).unlink(missing_ok=True)
    except OSError:
        pass
    session.delete(upload)
    session.commit()
    return HTMLResponse("", status_code=200)


@router.get("/projects/{project_id}/uploads/{upload_id}", response_class=HTMLResponse)
def view_upload(
    request: Request,
    project_id: int,
    upload_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    upload = session.get(Upload, upload_id)
    if not upload or upload.project_id != project_id:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    project = session.get(Project, project_id)
    return templates.TemplateResponse(
        request,
        "projects/upload_detail.html",
        {"project": project, "upload": upload},
    )
