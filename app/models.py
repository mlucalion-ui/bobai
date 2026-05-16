"""SQLModel data model. Day-1 surface: Project + Upload only.

Run, Section and BriefFact arrive on later days; their tables don't exist yet
so we leave them out of the metadata to avoid empty stubs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    client: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Upload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    filename: str
    path: str
    kind: str = Field(default="pdf")  # 'pdf' | 'docx' | 'eml' | 'text' | 'paste'
    size_bytes: Optional[int] = None
    text: Optional[str] = None  # extracted plain text
    created_at: datetime = Field(default_factory=datetime.utcnow)
