# bobai

AI bid-response system for an M&E consultancy.

Takes a brief (PDF / Word / email / pasted text) and a small library of past responses, and produces a draft RFP response in the firm's voice and structure.

## Status

- Thin end-to-end slice through the pipeline for one project (83 New Kent Road) is in `analysis/`, `sections/`, `scripts/`, `output/`.
- v0.1 web app scaffold (Day 1) is in `app/` — projects list + create + detail stub.

## Quickstart — v0.1 web app

```bash
python3 -m venv .venv
.venv/bin/pip install fastapi 'uvicorn[standard]' sqlmodel jinja2 python-multipart pdfplumber python-docx
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open <http://127.0.0.1:8000/>.

## Re-running the thin slice (one-off NKR draft)

```bash
.venv/bin/python scripts/assemble.py
# → output/scotch_response_draft.docx
```

## Layout

```
app/                  v0.1 web app (FastAPI + HTMX + SQLite)
  main.py             entry
  db.py models.py
  routes/             project routes
  templates/          Jinja + HTMX partials
  static/             CSS

analysis/             thinking artefacts from the thin slice
  example_analysis.md voice / structure profile from the example
  brief_summary.md    structured brief facts
  response_plan.md    section list, defaults, judgement calls
  _raw/               extracted plain text from the source PDFs

inputs/               raw uploads from the thin slice (PDFs)
sections/             generated section markdown (thin slice)
scripts/              thin-slice assembler
output/               assembled draft .docx
var/                  SQLite DB (ignored)
```
