# Publication Design Inspection 1.2.1

## Decision

**PASS** - the deterministic sample produces sixteen complete artifacts with a
cohesive editorial identity, format-native structure, readable layout, and
clear learner/instructor separation.

This is a bounded, public-safe release record. It contains no generated course
body, learner input, owner identity, private storage path, or authenticated URL.

## Inspection Scope

| Publication | HTML | Markdown | PDF | DOCX |
|-------------|------|----------|-----|------|
| Course | PASS | PASS | PASS | PASS |
| Review pack | PASS | PASS | PASS | PASS |
| Student assessment | PASS | PASS | PASS | PASS |
| Instructor answer key | PASS | PASS | PASS | PASS |

The test input is the synthetic `Python Basics` bundle already used by the
credential-free renderer suite. The inspection evaluates presentation only;
the canonical model and cross-artifact validators remain the authority for
educational completeness.

## Acceptance Matrix

| Dimension | Evidence | Result |
|-----------|----------|--------|
| Shared identity | Forest-and-gold cover language, publication-specific accents, consistent heading hierarchy, and stable running furniture | PASS |
| HTML screen layout | Standalone files opened with local file access at desktop width; covers, metadata, cards, callouts, links, and footer rendered without overflow | PASS |
| HTML responsive layout | Course rendered at `390 x 844`; document width matched viewport width and two-column regions collapsed to one column | PASS |
| HTML print contract | Embedded A4 print rules, cover break, block break protection, and reduced-motion rule verified in generated source | PASS |
| Native PDF | All four files opened as A4 PDF 1.7 with searchable text, metadata, full cover artwork, heading hierarchy, outline entries, and accurate current/total folios | PASS |
| Long-content pagination | A 700-item synthetic lesson crossed several PDF pages without losing its final marker or producing an incorrect folio | PASS |
| PDF worksheet | Student assessment includes learner-name, date, and five ruled response lines | PASS |
| PDF links and code | Source URLs retain printed text and native annotations when unwrapped; fenced code uses Courier treatment | PASS |
| Native DOCX | All four OOXML packages reopened with `python-docx`; custom styles, A4 geometry, cover panel, heading rules, page fields, and external link relationships were present | PASS |
| DOCX office rendering | All four DOCX files converted with LibreOffice and every resulting page was visually inspected | PASS |
| Assessment separation | Student files contain no answer, explanation, evidence, grading criterion, or rubric; answer-key files are visibly marked as instructor material | PASS |
| Offline and active-content boundary | HTML uses no remote font, stylesheet, media, script, iframe, event handler, or JavaScript URL | PASS |

## Rendered Page Record

| Publication | Native PDF pages | LibreOffice-rendered DOCX pages |
|-------------|------------------|---------------------------------|
| Course | 2 | 3 |
| Review pack | 3 | 4 |
| Student assessment | 2 | 2 |
| Instructor answer key | 2 | 2 |

The extra Word pages are intentional: long publications receive a native cover
and a conditional contents page. Compact assessment and answer-key samples skip
the contents page and move directly from cover to content.

## Verification Commands

From `backend/packages/txt2crs/`:

```bash
uv run --package txt2crs pytest tests/unit/test_rendering.py -q
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy
uv run --package txt2crs pytest -q
```

Release inspection also used:

```bash
pdfinfo <artifact.pdf>
pdftoppm -png -r 110 <artifact.pdf> <page-prefix>
libreoffice --headless --convert-to pdf --outdir <inspection-dir> <artifact.docx>
```

Standalone HTML files were opened through a local Chromium session, captured at
desktop and mobile widths, and checked for horizontal overflow and stylesheet
application.

## Known Boundaries

- PDF is not tagged for PDF/UA.
- Base 14 PDF fonts do not provide the HTML artifact's multilingual coverage.
- A PDF URL that wraps across lines remains printed text but may not receive one
  native click annotation.
- Office applications can substitute local fonts, causing small pagination
  differences without changing semantic styles or content.
- This release inspection must be repeated after renderer, font, PyMuPDF,
  `python-docx`, browser, Word, or LibreOffice changes.
