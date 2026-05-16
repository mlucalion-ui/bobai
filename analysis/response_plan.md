# Response plan — 83 New Kent Road / LGL (Step 3)

## Context

This plan covers Steps 3–5 of a thin end-to-end slice through the bid-response pipeline that will become a general system. Steps 1 (example analysis) and 2 (brief summary) are complete. Two properties of this run are unusual and worth holding in mind while executing:

1. The example response (R02) and the new brief are for the same site. The draft will resemble R02 in places — that is the right benchmark.
2. Several R02 inputs (fees, named team, insurance, time-charge rates) are not derivable from the brief. The plan reuses them verbatim rather than inventing; flagged below.

## Defaults locked in

| # | Decision | Default | Override |
|---|---|---|---|
| 1 | Acoustics | Optional strand, mirror R02 | "Promote acoustics to core" |
| 2 | BREEAM | Optional strand, mirror R02 | "Drop BREEAM" |
| 3 | Fees / team / insurance / rates | Reuse R02 verbatim | "Use placeholders" |
| 4 | Introduction opener | Mirror R02 stock opener | "Open as a revision" |

## Section-by-section plan

| # | Section | Target | Mode | Deltas vs R02 |
|---|---|---|---|---|
| Cover | Project / client / rev | 1 pg | Adapt | New rev date |
| 1 | Introduction | ~250w | Fresh, anchored on brief | Quote scheme objectives (a)–(f) verbatim; reference Scotch's 31/01/2025 EPC report cited in brief; new programme dates |
| 2 | Scotch Partners Introduction | ~600w | Boilerplate (80–90% verbatim) | Sector framing lightly tuned |
| 3 | Team and Proposed Roles | ~220w | Adapt with names verbatim | Organogram placeholder |
| 4 | Fees | ~700w + tables | Adapt with figures verbatim | Clarifications updated for Ben Green / Semper, evacuation lifts backup power, CCTV / flow tests as contractor scope |
| Appx A | Scope of Services | ~1500w | Boilerplate (80–90% verbatim) | Stage 1 framing reused |
| Appx B | Terms & Conditions | ~1000w | Verbatim | None |
| End | Contact block | 1 pg | Verbatim | None |

## Execution order

1. Generate `sections/01_introduction.md` … `sections/08_contact.md`.
2. Write `scripts/assemble.py` using python-docx (already installed in `.venv/`).
3. Run assembler to produce `output/scotch_response_draft.docx`.
4. Verify (per the verification checklist in the plan file).

## Verification

1. Open `output/scotch_response_draft.docx`, confirm 8 sections present in order, fee/rate/insurance tables render, lengths within ±20% of example targets.
2. Diff boilerplate sections vs `analysis/_raw/scotch_example_full.txt` — confirm 80–90% similarity.
3. Confirm each quoted brief passage is present verbatim in `analysis/_raw/NKR_RFP_20250217.txt`.
4. Commit, push, update PR #1.
