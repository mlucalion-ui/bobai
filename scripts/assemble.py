"""Assemble sections/*.md into output/scotch_response_draft.docx.

Thin-slice assembler. Markdown features supported:
- # / ## / ### → Heading 1/2/3
- - item        → bulleted list (one nesting level via two-space indent)
- 1. item       → numbered list
- | a | b |     → table (header row detected by following |---|---| separator)
- [TABLE: name] → placeholder, replaced by a pre-defined table
- > line        → note callout (italic indented paragraph)
- blank line    → paragraph break
- otherwise     → body paragraph
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parents[1]
SECTIONS_DIR = ROOT / "sections"
OUTPUT_PATH = ROOT / "output" / "scotch_response_draft.docx"

PROJECT_NAME = "83 New Kent Road"
CLIENT_NAME = "LGL Properties"
DOC_TITLE = "Scotch Partners RFP Return – Building Services, Sustainability and Acoustics"
REV = "R03 (DRAFT — AI-generated prototype)"
DOC_DATE = date.today().strftime("%d/%m/%Y")

SECTION_FILES = [
    "01_introduction.md",
    "02_scotch_introduction.md",
    "03_team_and_roles.md",
    "04_fees.md",
    "05_appendix_a_scope.md",
    "06_appendix_b_terms.md",
    "07_contact.md",
]

CONTENTS = [
    ("1. Introduction", 3),
    ("2. Scotch Partners Introduction", 4),
    ("3. Team and Proposed Roles", 6),
    ("4. Fees", 7),
    ("Appendix A — MEP and Energy Scope of Services", 11),
    ("Appendix B — Scotch Partners Terms & Conditions", 17),
    ("Contact", 19),
]

# Pre-defined tables that section markdown references via [TABLE: name].
TABLES = {
    "mep_energy_fees": {
        "headers": ["RIBA Stage", "MEP Fee (£)", "Energy Modelling (EPC) (£)", "Notes"],
        "rows": [
            ["Stage 2", "15,000", "6,800", "Assumes picking up from acquisition study with same client brief"],
            ["Stage 3 Plus (tender documents)", "35,000", "5,500", "Tender documents"],
            ["Stage 4 i/ii/iii", "4,000", "—", "Client monitoring"],
            ["Stage 5 / 6", "32,500", "—", "Client monitoring"],
            ["Total", "86,500", "12,300", "Combined total £98,800"],
        ],
    },
    "acoustics_fees": {
        "headers": ["RIBA Stage", "Noise Survey (£)", "Acoustics (£)", "Notes"],
        "rows": [
            ["Stage 2", "4,000", "3,750", "Optional noise assessment"],
            ["Stage 3 Plus (tender documents)", "—", "7,000", "Tender documents"],
            ["Stage 4 i/ii/iii", "—", "1,500", "Client monitoring"],
            ["Stage 5 / 6", "—", "5,000", "Client monitoring"],
            ["Total", "", "", "Combined total £21,500"],
        ],
    },
    "breeam_fees": {
        "headers": ["RIBA Stage", "BREEAM (£)", "BREEAM AP (£)", "Notes"],
        "rows": [
            ["Stage 2", "1,700", "2,400", ""],
            ["Stage 3 Plus (tender documents)", "nil", "3,600", ""],
            ["Stage 4 i/ii/iii", "9,000", "3,600", ""],
            ["Stage 5 / 6", "8,000", "10,800", ""],
            ["Total", "", "", "Combined total £39,100"],
        ],
    },
    "time_charge_rates": {
        "headers": ["Grade", "Rate £/hour"],
        "rows": [
            ["Partner", "135.00"],
            ["Technical Director", "105.00"],
            ["Principal Engineer / Consultant", "92.00"],
            ["Senior Engineer / Consultant", "80.00"],
            ["Engineer / Consultant", "65.00"],
            ["Assistant / Graduate", "55.00"],
        ],
    },
    "insurance": {
        "headers": ["Cover", "Value", "Provider", "Expiry"],
        "rows": [
            [
                "Professional Indemnity Insurance",
                "£10M — for each and every",
                "Allied World Assurance Company (through Dixons Commercial Insurance Brokers)",
                "9 September 2025",
            ],
            [
                "Employer Liability Insurance",
                "£10M",
                "Aviva Insurance Group (through Dixons Commercial Insurance Brokers)",
                "20 July 2025",
            ],
            [
                "Public Liability Insurance",
                "£10M",
                "Aviva Insurance Group (through Dixons Commercial Insurance Brokers)",
                "20 July 2025",
            ],
        ],
    },
}


def add_cover(doc: Document) -> None:
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(PROJECT_NAME)
    r.bold = True
    r.font.size = Pt(36)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(CLIENT_NAME)
    r.font.size = Pt(20)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(DOC_TITLE)
    r.italic = True
    r.font.size = Pt(14)

    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"{REV}    {DOC_DATE}").font.size = Pt(11)


def add_contents(doc: Document) -> None:
    doc.add_page_break()
    doc.add_heading("Contents", level=1)
    for title, page in CONTENTS:
        p = doc.add_paragraph()
        p.add_run(f"{title}").font.size = Pt(11)
        tab = p.add_run(f"\t{page}")
        tab.font.size = Pt(11)


def add_table(doc: Document, name: str) -> None:
    spec = TABLES.get(name)
    if not spec:
        doc.add_paragraph(f"[Missing table: {name}]")
        return
    headers = spec["headers"]
    rows = spec["rows"]
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Light Grid Accent 1"
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            t.rows[i].cells[j].text = val
    doc.add_paragraph()


def parse_inline_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    """Parse a contiguous markdown table starting at lines[start]. Returns (rows, end_index)."""
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        raw = lines[i].strip()
        if re.match(r"^\|[\s\-:|]+\|$", raw):
            i += 1
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        # Strip markdown bold ** from cells
        cells = [re.sub(r"^\*\*(.*)\*\*$", r"\1", c) for c in cells]
        rows.append(cells)
        i += 1
    return rows, i


def add_inline_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    cols = max(len(r) for r in rows)
    t = doc.add_table(rows=len(rows), cols=cols)
    t.style = "Light Grid Accent 1"
    for i, row in enumerate(rows):
        for j in range(cols):
            val = row[j] if j < len(row) else ""
            cell = t.rows[i].cells[j]
            cell.text = val
            if i == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    doc.add_paragraph()


def inline_emphasis(paragraph, text: str) -> None:
    """Render text into a paragraph, honouring **bold** and *italic* markers."""
    pos = 0
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")
    for m in pattern.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        token = m.group(0)
        if token.startswith("**"):
            paragraph.add_run(token[2:-2]).bold = True
        else:
            paragraph.add_run(token[1:-1]).italic = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def render_markdown(doc: Document, md: str) -> None:
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Table block
        if stripped.startswith("|"):
            rows, j = parse_inline_table(lines, i)
            add_inline_table(doc, rows)
            i = j
            continue

        # [TABLE: name] placeholder
        m = re.match(r"\[TABLE:\s*(\w+)\s*\]", stripped)
        if m:
            add_table(doc, m.group(1))
            i += 1
            continue

        # Heading
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
            i += 1
            continue
        if stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
            i += 1
            continue
        if stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
            i += 1
            continue

        # Note callout
        if stripped.startswith("> "):
            p = doc.add_paragraph(style="Intense Quote")
            inline_emphasis(p, stripped[2:])
            i += 1
            continue

        # Bullet
        bullet_match = re.match(r"^(\s*)-\s+(.*)$", line)
        if bullet_match:
            indent = len(bullet_match.group(1))
            text = bullet_match.group(2)
            style = "List Bullet 2" if indent >= 2 else "List Bullet"
            p = doc.add_paragraph(style=style)
            inline_emphasis(p, text)
            i += 1
            continue

        # Numbered list
        num_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if num_match:
            p = doc.add_paragraph(style="List Number")
            inline_emphasis(p, num_match.group(1))
            i += 1
            continue

        # Body paragraph — collect contiguous lines until blank
        chunk = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not (
            lines[i].lstrip().startswith(("#", "-", ">", "|"))
            or re.match(r"^\s*\d+\.\s", lines[i])
            or re.match(r"\[TABLE:", lines[i].strip())
        ):
            chunk.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        inline_emphasis(p, " ".join(chunk))


def main() -> None:
    doc = Document()

    # Tighten default margins
    for section in doc.sections:
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

    add_cover(doc)
    add_contents(doc)

    for filename in SECTION_FILES:
        doc.add_page_break()
        md = (SECTIONS_DIR / filename).read_text()
        render_markdown(doc, md)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT_PATH)
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
