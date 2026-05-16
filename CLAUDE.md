# bobai — project context for Claude

> This file is read automatically when Claude Code starts in this repo. Keep it skim-able. Update it when major decisions change.

## What this is

An AI bid-response system for Scotch Partners, an M&E consultancy. Takes a brief (PDF / Word / email / pasted text) plus a small library of past responses, and produces a draft RFP response in Scotch's voice and structure. The end user is the bid lead, who edits in the app and exports a `.docx`.

The original ask was a one-off NKR (83 New Kent Road) response. After completing that as a thin end-to-end slice, the project pivoted to building the general system that produced it. The NKR slice stays in the repo as a reference implementation and benchmark.

## Where we are

| Day | Status | Output |
|---|---|---|
| Thin slice (steps 1–5) | Done | `analysis/`, `sections/`, `scripts/assemble.py`, `output/scotch_response_draft.docx` |
| **Day 1** — FastAPI scaffold | Done | `app/` — project create/list, HTMX UI, SQLite |
| **Day 2** — Upload + ingestion | Done | `pipeline/ingest.py` (PDF/DOCX/EML/paste), `app/routes/uploads.py` |
| Day 3 — Brief extraction (LLM) | Next | Pydantic schema, prompt-driven extraction, editable facts UI |
| Day 4 — Response plan UI | | Sections list, four judgement calls, locked-in defaults |
| Day 5 — Section generation | | One prompt per section, regenerate inline, streaming if API-key path |
| Day 6 — Editors for placeholders | | Fee tables, named team, insurance, time-charge rates |
| Day 7 — Voice profile pipeline | | Build/load voice profile from example library |
| Day 8 — `.docx` export | | Refactor `scripts/assemble.py` into the app, refined built-in styles |
| Day 9–10 | | Polish, run history per project |

## Stack (locked in)

- Python 3.11, FastAPI + HTMX, Jinja2 templates, SQLite via SQLModel
- pdfplumber + python-docx + mail-parser for ingestion
- Anthropic Claude for LLM work — **see "LLM auth route" below**
- Run locally for now; hosting decision deferred

## Pipeline (what the general system needs to be good at)

| Stage | Thin-slice artefact | Production module |
|---|---|---|
| 1. Voice profile | `analysis/example_analysis.md` (hand-written) | `pipeline/voice_profile.py` — build from `inputs/example/`, persist to `voice_profile.json` |
| 2. Ingestion | `analysis/_raw/*.txt` | `pipeline/ingest.py` — PDF/DOCX/EML/paste ✅ |
| 3. Brief extraction | `analysis/brief_summary.md` (hand-written) | `pipeline/brief_extract.py` — LLM → Pydantic schema |
| 4. Response plan | `analysis/response_plan.md` (hand-written) | `pipeline/plan.py` — section list + defaults + four judgement calls |
| 5. Section generation | `sections/*.md` (hand-written via the chat) | `pipeline/generate.py` — one LLM call per section |
| 6. Assembly | `scripts/assemble.py` | refactor into `pipeline/assemble.py`, called by the export route |

## Decisions locked in for the NKR slice (4 judgement calls)

These are project-level defaults — surface them as toggles in the plan UI (Day 4):

1. **Acoustics**: optional strand, mirror R02. Override: "promote to core".
2. **BREEAM**: optional strand, mirror R02. Override: "drop BREEAM".
3. **Fees / team / insurance / rates**: reuse R02 verbatim — these aren't derivable from the brief. Override: "use placeholders".
4. **Introduction opener**: mirror R02 stock opener ("delighted to have been invited by…"). Override: "open as a revision".

## LLM auth route

User has a Claude Max consumer subscription, no Anthropic API key. Settled approach for v0.1:

- App will shell out to the `claude` CLI in headless mode (`claude -p "prompt..."`) — uses the Max plan's quota.
- Build a thin `pipeline/llm.py` abstraction (`generate(prompt: str, model: str | None = None) -> str`) so the call site stays clean.
- Known trade-offs (documented in chat with the user):
  - Per-call subprocess overhead (~2–5s).
  - No prompt caching → voice profile resent every call.
  - No streaming to the browser.
  - JSON outputs are brittle — Claude Code's own system prompt nudges toward conversational replies; will need strict prompting and forgiving parsing.
  - Rate limits eat into the user's personal Max quota.
  - Throwaway code when we eventually switch to an API key — but the abstraction makes that a one-module swap.
- We tried Codespaces. `claude` wasn't installed there and the OAuth flow proved fiddly enough that the user moved to running locally on Windows (PowerShell). Local has `claude` already installed and authenticated.

## How to run it (local)

### macOS / Linux
```bash
python3 -m venv .venv
.venv/bin/pip install fastapi 'uvicorn[standard]' sqlmodel jinja2 python-multipart pdfplumber python-docx mail-parser
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\pip install fastapi "uvicorn[standard]" sqlmodel jinja2 python-multipart pdfplumber python-docx mail-parser
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/>.

### Re-running the thin slice
```bash
.venv/bin/python scripts/assemble.py
# → output/scotch_response_draft.docx
```

## Repo map

```
app/                  v0.1 web app
  main.py             FastAPI entry
  db.py               SQLite engine + idempotent column migrations
  models.py           SQLModel: Project, Upload
  routes/
    projects.py       /, /projects, /projects/{id}
    uploads.py        /projects/{id}/uploads (POST file or paste), delete, view
  templates/          Jinja + HTMX partials
  static/styles.css   dark theme

pipeline/
  __init__.py
  ingest.py           PDF/DOCX/EML/paste → plain text
  # Day 3+: brief_extract.py, plan.py, generate.py, voice_profile.py, llm.py

analysis/             thinking artefacts from the thin slice
  example_analysis.md voice / structure / phrase library from the example
  brief_summary.md    structured brief facts (what brief_extract.py will produce)
  response_plan.md    section list + defaults + judgement calls
  _raw/*.txt          extracted text from input PDFs (debug)

inputs/
  example/scotch_response_example.pdf
  briefing/*.pdf      the three NKR documents

sections/             generated section markdown (thin slice)
scripts/assemble.py   markdown → .docx (will fold into pipeline/ in Day 8)
output/               assembled draft .docx
var/                  SQLite DB + saved uploads (gitignored)
```

## Conventions

- **Voice for generated text**: match Scotch's R02 — first-person plural, British English, technical abbreviations expanded once then reused (MEP, RIBA, EPC, BREEAM, BSRIA, ER/CP/URS, AHU, ASHP). Bullets are short clauses, no terminal punctuation. Use tables wherever a table will do. Don't over-polish.
- **Voice profile content**: when prompting the LLM, include short signature phrases from the example (the stock opener, the practice-definition sentence, the culture paragraph, the financial-standing one-liner), not large verbatim chunks.
- **What not to invent**: fee figures, named team members, insurance values/providers/expiries, time-charge rates, accreditation numbers. These come from R02 verbatim or from a UI override.
- **What not to claim**: capabilities Scotch doesn't demonstrate in the example (BMS depth, specific net-zero certifications, etc.).
- **Word-count targets per section**: see `analysis/example_analysis.md` §1. Aim within ±20% of the example's envelope.
- **Tone of these docs**: complete sentences, no marketing voice, no emojis unless explicitly asked.

## Open items / blockers

- **`claude` CLI auth survival**: the Max-funded subprocess approach works on the user's local machine. If we move bobai to a hosted environment later, this falls over and we need an API key.
- **Scotch `.dotx` template**: not available yet. Day 8 export uses refined built-in python-docx styles; real template drops in later.
- **OneDrive path**: user has the repo under a OneDrive-synced folder on Windows. `.venv\` is large and will sync; not a blocker, just slower.
- **Run / version history**: deferred. Day-2 schema doesn't model regen history; we'll add a `Run` table when section generation needs it.
- **Auth**: none in v0.1 (single user). Add real auth when more than one person uses it.

## How to pick this up in a new Claude session

1. Read this file (you're doing it).
2. Skim `analysis/example_analysis.md` and `analysis/brief_summary.md` for the NKR reference.
3. Look at the latest section of "Where we are" — that's the next thing to build.
4. Check the latest commit on `claude/ai-bid-response-system-gDCzQ` to see what shape the code is currently in.
