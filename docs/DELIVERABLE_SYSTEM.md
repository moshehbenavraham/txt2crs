# Deliverable System

This document is the permanent source of truth for how txt2crs turns one final
validated education bundle into learner-facing publications, stores those
publications, and delivers them through the application.

It describes implemented behavior. Future improvement specs should cite this
document as their baseline instead of treating temporary project notes as a
current contract.

## Scope And Authority

This document owns the end-to-end deliverable lifecycle:

- the canonical output contract;
- the boundary between generated educational content and deterministic
  formatting;
- format-specific rendering behavior;
- rendered-output quality checks;
- private artifact storage and integrity verification;
- manifest and download delivery;
- HTML preview isolation; and
- the current publication design contract and its known limitations.

Related sources of truth remain authoritative for their narrower concerns:

- [Architecture](ARCHITECTURE.md) owns service and dependency boundaries.
- [API documentation](api/README_api.md) owns the public HTTP contract.
- [Engine documentation](../backend/packages/txt2crs/README_txt2crs.md) owns
  generation, research, and educational quality gates.
- [Security documentation](SECURITY.md) owns the broader security and privacy
  posture.
- [Release evidence](release/README_release.md) owns historical release
  inspection records.

## Terminology

| Term | Meaning |
|------|---------|
| Canonical bundle | The cross-validated `Course`, `ReviewPack`, `Assessment`, and `AnswerKey` models that contain accepted educational content. |
| Deliverable or publication | One user-facing product: course, review pack, student assessment, or instructor answer key. |
| Format | One portable representation: HTML, Markdown, PDF, or DOCX. |
| Rendered artifact | The immutable bytes, safe filename, and media type for one deliverable-format pair. |
| Artifact manifest | Path-free metadata describing the canonical artifact set, including identifiers, formats, filenames, sizes, and SHA-256 hashes. |
| Delivery | Private publication of the artifact set plus owner-authorized manifest and byte access. |

The structured canonical bundle is the content authority. A PDF, DOCX, HTML,
or Markdown file is a deterministic representation of that accepted bundle,
not a new model-generated interpretation of it.

## Output Contract

One successfully completed job publishes four deliverables in four formats,
for exactly sixteen canonical artifacts.

| Deliverable | Stable ID prefix | Intended use | Access presentation |
|-------------|------------------|--------------|---------------------|
| Course | `course_` | Source-grounded curriculum, modules, lessons, objectives, glossary, and bibliography | Normal owner publication |
| Review pack | `review_pack_` | Study guide, summaries, glossary, flashcards, worked examples, practice, and review sequence | Normal owner publication |
| Student assessment | `assessment_` | Blueprint-aligned learner test without instructor answers | Normal owner publication |
| Instructor answer key | `answer_key_` | Answers, evidence sources, grading criteria, and rubrics | Marked as instructor material and collapsed by default |

Each prefix is combined with `html`, `markdown`, `pdf`, or `docx`. For example,
`course_pdf` and `answer_key_docx` are stable artifact identifiers.

The job owner can access all sixteen artifacts. The instructor label is a
presentation and answer-separation boundary, not a distinct role-based access
control system.

## Ownership Boundaries

| Responsibility | Owner | Primary implementation |
|----------------|-------|------------------------|
| Canonical education models and cross-artifact invariants | txt2crs engine | `backend/packages/txt2crs/src/txt2crs/domain/` |
| Educational and assessment quality validation | txt2crs engine | `backend/packages/txt2crs/src/txt2crs/generation/quality.py` |
| Content-to-format rendering and rendered HTML QA | txt2crs engine | `backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py` |
| Cross-format publication design system | txt2crs engine | `backend/packages/txt2crs/src/txt2crs/rendering/publication_design.py` |
| Private persistence, manifest construction, and integrity checks | txt2crs engine | `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`, `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py`, and `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` |
| Owner authorization and public package queries | txt2crs application facade | `backend/packages/txt2crs/src/txt2crs/application/` and `backend/packages/txt2crs/src/txt2crs/jobs/service.py` |
| HTTP projection, headers, and ASGI streaming | FastAPI shell | `backend/app/api/routes/jobs.py` and `backend/app/api/artifact_response.py` |
| Publication cards, preview, and browser downloads | React frontend | `frontend/src/components/CourseResults/` |

The FastAPI shell must not reproduce generation, validation, rendering,
artifact-integrity, or persistence behavior. It translates the package-owned
contracts into authenticated HTTP responses.

## End-To-End Lifecycle

```text
accepted generation request
    |
    v
final cross-validated canonical bundle checkpoint
    |
    v
bundle and assessment quality revalidation
    |
    v
deterministic semantic HTML and Markdown rendering
    |
    +--> publication-designed searchable PDF rendering from Markdown
    |
    `--> styled native DOCX rendering from Markdown
    |
    v
rendered HTML safety and structure QA
    |
    v
durable job status: delivering
    |
    v
atomic private artifact-set and manifest publication
    |
    v
durable delivery record and completed job status
    |
    v
owner-authorized manifest read
    |
    +--> verified file download
    |
    `--> verified and isolated HTML preview
```

### 1. Final Bundle Recovery And Revalidation

Rendering starts only from the final `cross_validate_artifacts` checkpoint.
The executor requires all four canonical models, rebuilds the `ArtifactBundle`,
and reruns bundle and assessment quality validation before any output bytes are
created.

This checkpoint is durable before rendering. A replacement worker can resume
rendering or delivery without repeating research or model generation. It uses
the same accepted canonical content rather than current defaults or a newly
generated interpretation.

Primary implementation:

- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/domain/validation.py`
- `backend/packages/txt2crs/src/txt2crs/generation/quality.py`

### 2. Deterministic Rendering

`ArtifactRenderer.render_bundle()` creates the complete sixteen-artifact map
in memory. No model and no remote document-conversion service participates in
this step.

The renderer derives an ASCII, path-safe filename slug from the course title.
It renders HTML and Markdown directly from the canonical models, then uses the
corresponding Markdown as the content input for independent PDF and DOCX layout
engines. `publication_design.py` owns the shared brand vocabulary and each
format's native presentation rules. Filenames use the following shapes:

```text
<course-slug>-course.<format>
<course-slug>-review-pack.<format>
<course-slug>-assessment.<format>
<course-slug>-answer-key.<format>
```

The stable artifact ID, not the filename, identifies an artifact throughout
storage, recovery, public projection, and download.

### 3. Rendered Output QA

Before any artifacts leave the renderer, every HTML document is checked for:

- its required publication container;
- the course bibliography where applicable;
- script, iframe, event-handler, and JavaScript URL patterns;
- remote media and remote CSS URL patterns; and
- credential-shaped or private-path-shaped content.

HTML validation rejects the complete render operation if any issue is found.
The HTML renderer also escapes canonical text before inserting it into markup.

The renderer suite then reopens representative PDF and DOCX bytes to verify
searchable text, cover and heading hierarchy, PDF outlines and folios, Word
styles and page fields, native link relationships, code treatment, worksheet
space, and instructor-answer separation. PDF page images and LibreOffice DOCX
conversions remain release-time visual checks because aesthetic judgment cannot
be reduced to a byte-level runtime gate.

PDF and DOCX generation still fails the complete render operation when their
local libraries cannot create valid bytes. The live runtime does not launch a
browser or office suite before storage; that would make job completion depend
on heavyweight, platform-specific applications.

### 4. Durable Delivery And Atomic Publication

After rendering, `JobService.complete()` moves the durable job to
`delivering`, saves the artifact set, records the delivery state, and only then
moves the job to `completed`.

The filesystem store:

- hashes the owner and job identifiers for non-identifying directory names;
- creates directories with owner-only permissions;
- creates artifact and manifest files with owner-only permissions;
- validates filenames, media types, byte values, uniqueness, and the configured
  complete-job byte limit before publication;
- records each artifact's exact byte count and SHA-256 hash;
- writes all artifacts and `manifest.json` into a staging directory; and
- publishes the complete directory with one rename only after every write has
  succeeded.

A retry with the identical artifact set is idempotent. An existing job
directory with a different artifact set is rejected rather than overwritten.

The shell default limits a complete artifact bundle to 100 MiB. Configuration
remains authoritative; see [Configuration](CONFIGURATION.md).

#### Retention And Deletion

The artifact store has a bounded retention field and a maintenance purge
operation. The current shell supplies the package maximum of 36,500 days so
routine time-based artifact expiry is effectively disabled. No scheduled
artifact-retention purge is part of the current application flow.

Current owner account deletion uses the engine's coordinated owner purge. It
removes the owner's private artifact tree first and then deletes the durable
engine job records. An artifact failure leaves the job records available for a
safe retry; a later job-store failure can retry the already idempotent artifact
removal. Success is reported only after both stores have completed.

Primary implementation:

- `backend/app/services/txt2crs_application.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`
- `backend/packages/txt2crs/src/txt2crs/application/owner_lifecycle.py`

### 5. Manifest Projection

The package exposes a verified, path-free manifest. It contains:

- schema and job identity;
- creation time;
- stable artifact ID;
- deliverable and format;
- safe filename;
- exact media type;
- exact byte count; and
- `sha256:` content hash.

Only the sixteen reviewed deliverable-format identifiers can enter the public
manifest. A private, debug, malformed, duplicate, or unknown artifact cannot
become downloadable merely because it exists in a private directory.

The FastAPI shell groups the entries into the four canonical publications and
adds stable owner-scoped download URLs. No private storage path crosses the
package or HTTP boundary.

### 6. Artifact Read And HTTP Streaming

Every manifest and artifact read independently supplies the authenticated
owner ID. Missing jobs, foreign jobs, and missing artifact IDs use the same
public not-found contract.

Before an artifact stream is opened, the package:

- verifies the directory is confined and contains no symlink substitution;
- validates manifest structure, topology, filenames, types, and declared
  sizes;
- opens the artifact without following symlinks where the platform supports
  that protection;
- verifies the open descriptor is a regular file of the declared size;
- reads and hashes the complete descriptor;
- compares the observed size and SHA-256 hash to the manifest;
- verifies the descriptor identity did not change during validation; and
- rewinds that same verified descriptor for streaming.

The HTTP response supplies the exact `Content-Type`, `Content-Length`, and safe
RFC 5987 attachment filename. It also supplies private/no-store, no-sniff, and
no-referrer headers. The ASGI response owns the entered artifact context and
closes it once on success, disconnect, iterator error, send error, or response
construction failure.

### 7. Frontend Presentation And Transfer

The frontend requests the manifest only for a completed job that advertises
available artifacts. It validates the public manifest again before creating
publication cards. The cards use stable deliverable ordering and stable format
ordering.

Each publication card offers:

- PDF as the primary download action when present;
- HTML preview when present and within the configured preview byte limit;
- all available formats in the format menu;
- exact format labels and human-readable size labels; and
- bounded loading and learner-safe error states.

The answer key card is visibly marked as instructor material and hides its
download controls until the owner opens them.

For a download, the generated client fetches the owner-private artifact. The
frontend verifies the response representation against manifest media type,
format, filename, and byte count before creating a temporary object URL. The
browser download uses the verified manifest filename, and the temporary URL is
revoked after the action or during component cleanup.

The browser does not recompute SHA-256. The package has already verified the
stored hash from the same open descriptor before the shell streams it.

### 8. HTML Preview Isolation

Preview uses the authenticated HTML artifact transfer; it never requests a
public artifact URL. The browser parses the HTML into a separate document and
removes active, navigational, form, embedded-object, remote-resource, and
interaction capabilities. It prepends a restrictive preview Content Security
Policy and supplies the sanitized document to an iframe with an empty
`sandbox` attribute.

The preview document is never inserted into the React application document
with `dangerouslySetInnerHTML`.

For isolation, preview processing removes hyperlink navigation attributes.
The downloaded original HTML retains the renderer's safe HTTP(S) bibliography
links; the inert preview presents their text without making them navigable.

## Publication Design System

The four publications share one restrained editorial identity derived from the
application experience: warm paper, deep forest green, champagne gold, a serif
display face, and a compact sans-serif reading face. Presentation never changes
the canonical educational content or the student/instructor answer boundary.

| Role | Value | Purpose |
|------|-------|---------|
| Foundation | Forest `#1A5038` | Covers, headings, running furniture, and trusted callouts |
| Highlight | Gold `#B8832A` | Kicker text, rules, numbered contents, and small emphasis |
| Paper | Warm cream `#FBF8F0` | Low-glare screen reading surface |
| Course accent | Green `#2D6B4A` | Curriculum and lesson identity |
| Review accent | Blue `#3E6485` | Recall and practice identity |
| Assessment accent | Ochre `#A06D18` | Learner worksheet identity |
| Answer-key accent | Brick `#8A4738` | Instructor-only identity and separation cue |

The design system follows five rules:

1. The document title and publication type must be unmistakable before content.
2. Heading hierarchy, code, callouts, lists, and sources must remain recognizable
   in every format.
3. Screen HTML and paper formats must each use their native layout capabilities.
4. Assessment files must be usable as worksheets, not merely readable question
   lists.
5. No visual treatment may introduce a remote runtime dependency or active
   content surface.

## Format-Specific Rendering Contract

### HTML

Each HTML artifact is a UTF-8 standalone publication with:

- language and left-to-right or right-to-left document metadata;
- one self-contained screen and print stylesheet;
- a branded cover, publication-specific accent, balanced title hierarchy, and
  responsive reading width;
- styled metadata, chapters, lesson cards, summaries, code, misconceptions,
  glossaries, flashcards, practice solutions, and bibliography regions;
- printable learner-name, date, and response areas in the assessment;
- semantic `main`, `section`, `article`, heading, paragraph, list, definition
  list, `details`, and bibliography structures where applicable;
- escaped canonical content, local fragment citations, and safe HTTP(S) links;
  and
- no script, iframe, remote font, remote media, or remote stylesheet dependency.

The mobile layout collapses two-column metadata and card grids below `42rem`.
The print stylesheet uses A4 geometry, forces the cover onto its own page,
preserves color where supported, and avoids breaking short semantic blocks.
Reduced-motion preferences disable smooth scrolling.

### Markdown

Markdown remains the most direct portable text representation. It provides:

- UTF-8 headings, lists, emphasis, fenced code, and links;
- stable learner-facing section order;
- reader-facing labels instead of canonical internal identifiers;
- explicit student/instructor content separation; and
- a final newline.

Its exact typography still depends on the selected Markdown viewer. The engine
does not bundle an executable renderer or a viewer-specific theme into a text
file. The same reviewed Markdown vocabulary is the content input for PDF and
DOCX layout.

### PDF

Each PDF is a locally generated, searchable A4 publication with:

- a full-page forest cover, publication accent rail, label, title, deck, and
  provenance line;
- a multilevel heading scale, retained list markers, dedicated monospaced code
  treatment, and shaded semantic callouts;
- consistent page furniture, including running document labels and accurate
  current/total folios;
- a PDF outline built from the rendered heading structure;
- printed HTTP(S) targets plus native click annotations when a complete URL
  fits on one rendered line;
- learner-name, date, and ruled response areas in the assessment;
- title, subject, author, creator, keyword, and publication metadata; and
- deterministic local rendering through PyMuPDF only.

Common English smart punctuation is normalized for reliable Base 14 font
output. A URL too long to fit on one line remains visible text but may not have a
single native annotation. The PDF is not currently tagged for PDF/UA, and HTML
remains the authoritative multilingual and RTL presentation.

### DOCX

Each DOCX is real, editable OOXML generated locally with `python-docx`. It has:

- explicit A4 geometry, reviewed margins, and a full-page branded cover panel;
- document metadata for title, subject, author, category, and keywords;
- versioned-in-code paragraph styles for title, four heading levels, metadata,
  contents, code, callouts, and response space;
- native Word heading levels for navigation, keep-with-next and keep-together
  heading controls, widow control, and explicit cover/page breaks;
- a static contents page only when the publication has enough sections to make
  one useful;
- running headers, current/total page fields, and an update-fields-on-open hint;
- native external hyperlink relationships with visible targets for printed
  copies;
- shaded callouts and code blocks; and
- student-name, date, and ruled response areas in assessment documents.

Word, LibreOffice, and other editors can substitute locally available fonts,
so pagination can vary slightly between applications. The semantic heading and
field structure, content, colors, page geometry, and answer separation remain
part of the generated OOXML contract.

## Deliverable Content Mapping

| Deliverable | Required rendered content |
|-------------|---------------------------|
| Course | Title, audience, level, prerequisites, learning objectives, modules, sections, content blocks, summaries, optional misconceptions and examples, glossary, optional unresolved claims, and bibliography |
| Review pack | Review sequence, objective study guide, key takeaways, misconceptions, sources, glossary, flashcards, worked examples, practice with solutions, section summaries, and cumulative summary |
| Student assessment | Title, learner-name and date fields in designed formats, instructions, passing score, ordered questions, point values, options where applicable, and printable response space; no answers, evidence, grading criteria, or rubrics |
| Instructor answer key | Corresponding question prompt, correct answers, explanation, evidence sources, grading criteria, and rubric for each assessment item |

Canonical internal identifiers support validation and cross-artifact alignment.
Renderers replace or humanize those identifiers so learner-facing documents do
not expose schema field names or stale internal references.

## Quality Gates And Evidence

### Runtime Gates

| Gate | What it proves | What it does not prove |
|------|----------------|------------------------|
| Canonical model validation | Required fields, schema versions, identifiers, bounds, and domain invariants are valid | Visual presentation |
| Cross-artifact validation | Course, review, assessment, answer key, objective coverage, and answer separation agree | Page layout |
| Assessment quality validation | Assessment and answer-key quality rules pass | Final page geometry |
| Rendered HTML QA | Required HTML structure exists and active/private content patterns are absent | Browser-specific layout fidelity |
| PDF structure tests | Searchable content, cover artwork, hierarchy, outline, folios, code, worksheet space, and link annotations exist | Subjective visual balance for every possible content length |
| DOCX structure tests | Native styles, A4 geometry, cover, page fields, navigation, links, code, and worksheet space exist | Identical pagination across office suites |
| Artifact metadata validation | Names, media types, byte values, uniqueness, and configured total size are valid | Document aesthetics |
| Manifest and descriptor verification | Stored topology, file identity, size, and SHA-256 hash match | Content pedagogy or layout |
| HTTP and frontend transfer checks | The authorized verified artifact is represented with the expected type, size, and filename | Visual fidelity in external office applications |

### Automated Tests

The current renderer suite checks:

- all sixteen deliverable-format pairs;
- semantic and escaped HTML;
- embedded responsive, print, and reduced-motion CSS in every HTML publication;
- branded HTML covers and distinct course, review, assessment, and answer-key
  identities;
- required content presence;
- student and instructor answer separation;
- usable instructor evidence disclosure;
- searchable PDF text, cover artwork, heading-size hierarchy, outlines, running
  furniture, exact folios, and native source links;
- multi-page long-lesson pagination with preserved tail content and exact
  folios;
- PDF assessment learner fields and ruled response space;
- parseable DOCX content, explicit A4 geometry, branded covers, custom styles,
  page fields, heading pagination rules, native links, and useful contents-page
  behavior;
- format-native fenced-code treatment in HTML, Markdown, PDF, and DOCX;
- reader-facing replacement of internal identifiers;
- optional-section omission;
- Markdown marker cleanup in PDF and DOCX;
- common punctuation behavior;
- singular and plural point labels;
- HTML direction metadata; and
- rendered HTML safety and required-section rejection.

Storage, package integration, shell API, frontend transfer, preview, and browser
journey tests cover the later lifecycle boundaries.

Focused renderer verification:

```bash
cd backend/packages/txt2crs
uv run --package txt2crs pytest tests/unit/test_rendering.py -q
```

Broader engine verification:

```bash
cd backend/packages/txt2crs
uv run --package txt2crs pytest
```

Frontend transfer and preview verification:

```bash
cd frontend
npm run test:unit
```

### Human Release Inspection

The `1.2.1` publication inspection renders one deterministic bundle into all
sixteen artifacts. HTML is inspected at desktop and mobile widths, each native
PDF page is rasterized and reviewed, every DOCX is converted through
LibreOffice and reviewed page by page, and text/metadata/link structure is read
back programmatically. See
[Publication design inspection](release/PUBLICATION_DESIGN_INSPECTION_1_2_1.md).

The older `1.0.0` evidence remains historical proof for the original readable
baseline. Neither inspection proves arbitrary future content lengths or
renderer upgrades; the same release check must be repeated after layout logic
or dependencies change.

## Current Formatting Guarantees

The current system guarantees that artifacts are:

- deterministic representations of accepted canonical content;
- complete according to the renderer's section mapping;
- separated correctly between student assessment and instructor answer key;
- safe from model-produced active HTML;
- portable in the four advertised file formats;
- governed by one publication identity across HTML, PDF, and DOCX;
- responsive and print-aware as self-contained semantic HTML;
- readable as portable Markdown with format-native fenced code;
- searchable, outlined, publication-designed A4 PDFs with accurate folios;
- valid, styled, editable DOCX with native headings, page fields, and links;
- usable as printable assessment worksheets in HTML, PDF, and DOCX;
- visually distinct between learner assessment and instructor answer key;
- immutable and integrity-checked after private publication; and
- available only through owner-authorized manifest and artifact reads.

The current system does not guarantee:

- tagged PDF accessibility or PDF/UA conformance;
- robust multilingual font coverage in PDF;
- interactive PDF form fields;
- native PDF link annotations for URLs that wrap across lines;
- pixel-identical pagination across browsers, Word, and LibreOffice;
- custom diagrams, charts, or generated images;
- automatic visual comparison against approved reference pages; or
- unchanged rendering across upgrades to PyMuPDF, `python-docx`, browsers, Word,
  or LibreOffice without renewed inspection.

In current release terminology, a formatting `PASS` means the file opens,
preserves publication meaning and answer separation, satisfies the structural
design checks above, and passes rendered page inspection at the recorded
reference sizes. It is a bounded release judgment, not a claim of PDF/UA or
pixel identity in every external viewer.

## Improvement Planning Baseline

This section is a baseline for future specifications, not an active backlog.
A future spec should select a bounded subset and define measurable acceptance
criteria before changing a renderer.

### Candidate Improvement Areas

1. Define multilingual and RTL requirements, including local font selection,
   embedding rights, shaping, fallback, and test fixtures.
2. Define document accessibility targets separately for HTML, DOCX, and PDF,
   including whether PDF/UA is required.
3. Add image-based layout regression checks using representative long, short,
   code-heavy, citation-heavy, assessment, and RTL fixtures.
4. Add robust native PDF link regions for URLs that wrap across rendered lines.
5. Decide whether interactive PDF form fields improve assessment usability
   without weakening portability or accessibility.
6. Add reviewed diagram, table, chart, and image components when canonical
   models can represent them without inventing content during rendering.
7. Record an explicit publication-template version in artifact metadata and
   manifests if re-rendering becomes a supported product operation.
8. Decide whether already-published artifacts remain immutable forever or can
   be explicitly re-rendered under a versioned template without repeating
   model work.

### Required Questions For A Renderer Improvement Spec

Every formatting improvement spec should answer:

- Which deliverables and formats change?
- Which current guarantees must remain unchanged?
- What exact visual and accessibility acceptance criteria are added?
- Does canonical content or only presentation change?
- Is a renderer or template version recorded, and where?
- Are existing artifacts immutable, migrated, or eligible for explicit
  re-rendering?
- Which fonts, templates, or assets are local, licensed, and reproducible?
- How are long titles, long URLs, code, tables, page breaks, and empty optional
  sections handled?
- How are student assessment and instructor answer-key visual separation
  preserved?
- Which automated render-to-image or document-structure checks prevent
  regression?
- Which human inspection remains necessary before release?
- Do preview sanitization, CSP, artifact size, or deployment dependencies
  change?

## Change Control

Update this document in the same change whenever any of the following changes:

- deliverable count, names, audience, or answer-separation behavior;
- supported format count or media type;
- canonical content-to-document mapping;
- renderer implementation or formatting guarantee;
- HTML safety validation;
- artifact ID, filename, manifest, storage, or integrity behavior;
- retention or deletion behavior;
- API artifact headers or streaming ownership;
- frontend format ordering, primary download, transfer validation, or preview
  isolation; or
- automated or human formatting acceptance criteria.

Active implementation plans belong in `.spec_system/`. Completed behavior and
its stable constraints belong here.

## Implementation And Test Map

| Area | Source or test |
|------|----------------|
| Canonical models | `backend/packages/txt2crs/src/txt2crs/domain/models.py` |
| Cross-artifact validation | `backend/packages/txt2crs/src/txt2crs/domain/validation.py` |
| Assessment quality | `backend/packages/txt2crs/src/txt2crs/generation/quality.py` |
| Content-to-format rendering | `backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py` |
| Publication design and layout | `backend/packages/txt2crs/src/txt2crs/rendering/publication_design.py` |
| Completion orchestration | `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` and `backend/packages/txt2crs/src/txt2crs/jobs/service.py` |
| Artifact storage | `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` |
| Artifact reads | `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py` |
| Manifest contracts | `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` |
| Public response schemas | `backend/app/schemas/jobs.py` |
| Manifest and download routes | `backend/app/api/routes/jobs.py` |
| Stream lifetime | `backend/app/api/artifact_response.py` |
| Frontend presentation | `frontend/src/components/CourseResults/presentation.ts` |
| Frontend transfer | `frontend/src/components/CourseResults/artifact-transfer.ts` and `frontend/src/components/CourseResults/useArtifactTransfer.ts` |
| HTML preview | `frontend/src/components/CourseResults/HtmlArtifactPreview.tsx` and `frontend/src/components/CourseResults/preview-document.ts` |
| Renderer tests | `backend/packages/txt2crs/tests/unit/test_rendering.py` |
| Storage tests | `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py` |
| End-to-end engine delivery | `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` |
| Shell artifact tests | `backend/tests/api/routes/test_jobs_results.py` and `backend/tests/api/test_artifact_response.py` |
| Frontend manifest and transfer tests | `frontend/src/components/CourseResults/presentation.test.ts`, `frontend/src/components/CourseResults/artifact-transfer.test.ts`, and `frontend/src/components/CourseResults/useArtifactTransfer.test.tsx` |
| Frontend preview tests | `frontend/src/components/CourseResults/preview-document.test.ts` and `frontend/src/components/CourseResults/CourseResultsWorkspace.test.tsx` |
