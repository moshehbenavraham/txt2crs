# txt2crs - Devpost Submission

**Status**: Ready for human entry
**Category**: Education
**Project name**: txt2crs
**Tagline**: Turn one bounded source into a complete, source-grounded learning package.

## Elevator Pitch

txt2crs turns a topic, pasted text, public link, YouTube URL, or bounded
document into four coordinated publications: a deep-researched course, a
review pack, a student assessment, and a separate instructor answer key.
Every publication is available in HTML, Markdown, PDF, and DOCX, giving a
learner or instructor sixteen private, integrity-checked artifacts from one
durable request.

## Inspiration

Two days after I joined OpenAI Build Week, my Zimbabwean wife asked me:
"How can we bring AI to Africa?"

That question brought me back to an IBM AI Developer certification project I
had built with Make.com. The workflow could expand learning material, create
study guides, and generate review questions, but it was still an automation
experiment rather than a durable learning product.

txt2crs rebuilds that idea around a more useful education promise: a learner
should be able to start with the material they already have, understand where
new information came from, review it in several ways, and take an assessment
whose answers remain separate for the instructor.

## What It Does

An authenticated learner starts with one of five bounded source modes:

- a topic prompt;
- pasted text;
- a public website;
- a public YouTube URL; or
- one PDF, DOCX, or PPTX document.

The learner can add learning goals, audience, desired depth, duration,
assessment size, and accessibility preferences. txt2crs then:

1. validates and durably commits the exact request before accepting the job;
2. ingests and policy-checks the source;
3. performs bounded Tavily research through a loopback MCP boundary;
4. generates the learning structure with exact `gpt-5.6-sol`;
5. validates and checkpoints accepted work;
6. renders a course, review pack, student assessment, and instructor answer
   key in HTML, Markdown, PDF, and DOCX; and
7. delivers exactly sixteen owner-private artifacts.

Progress is real server-owned state, not a browser timer. The learner can
refresh or revisit the private job URL and recover the same monotonic
progress. Results include bounded source summaries and unresolved conflict
disclosures. HTML preview is parsed and shown inertly, downloads are
integrity-checked, and the student assessment never contains its solutions.

## How We Built It

The project has three deliberate layers:

- A reusable Python `txt2crs` engine owns ingestion, policy, research,
  generation, checkpoints, validation, rendering, and private artifacts.
- A FastAPI shell owns HTTP transport, PostgreSQL-backed application
  identities, settings, lifecycle, and bounded RFC 9457 errors. Route handlers
  call the engine facade instead of copying engine logic.
- A React 19 application provides public discovery, strict multimode intake,
  refresh-safe progress, a four-publication result workspace, private
  downloads, source disclosure, and inert preview.

PostgreSQL stores application users. Tenant-scoped SQLite is the only
generation-job source of truth, and a private filesystem stores immutable
artifacts. The current local Docker release intentionally runs one non-root
FastAPI process and one serial worker so runtime ownership remains
unambiguous until a real external queue exists.

The release was developed tests-first and validated across engine, backend,
frontend, browser, security, distribution, production-image, health, and
container-replacement gates. A deterministic synthetic Python sample
reproduces the complete journey without credentials. A separately identified
live proof used synthetic nonpersonal input, exact `gpt-5.6-sol`, real Tavily
research, six sources, nine durable checkpoints, four publications, and
sixteen inspected artifacts.

## How Codex And GPT-5.6 Were Used

Codex was the development collaborator. It helped turn the product plan into
dependency-ordered specifications, write tests before implementation,
preserve the engine/application boundary, implement the FastAPI and React
journey, investigate exact model naming, review security and privacy
boundaries, reproduce failures, and assemble validation evidence tied to
specific repository revisions.

GPT-5.6 has a separate job inside the shipped product. The package-owned Codex
runtime authenticates a dedicated ChatGPT subscription, discovers an exact
reviewed GPT-5.6 model, and executes the course-generation protocol. The
default is `gpt-5.6-sol`; `gpt-5.6-terra` and `gpt-5.6-luna` are the other
accepted exact identifiers. Bare `gpt-5.6` is treated as a family name, not a
selectable runtime model. Readiness and execution fail closed rather than
silently choosing an older or first-available model.

Tavily supplies bounded web research through a two-tool MCP server on
loopback. The engine requires explicit provider-processing consent, owns both
provider lifecycles, checkpoints accepted work, validates generated
structures, and deterministically renders only accepted content.

Primary Codex feedback Session ID:
`019f7990-e049-7242-9d36-dc1eb4462d69`

## Challenges

### Durable work behind an HTTP request

Returning `202 Accepted` is easy; proving the exact request is committed
before acceptance, preventing duplicate work, and recovering after process
replacement is harder. We made the tenant job store authoritative and exposed
only monotonic public checkpoints.

### Keeping one reusable engine boundary

The FastAPI/React shell began from a strong application boilerplate, while the
course engine needed to remain independently installable. The hardest
architectural discipline was keeping research, generation, validation,
persistence, and rendering inside the engine while letting the shell own
identity and transport.

### Treating model selection as policy

The available GPT-5.6 runtime identifiers include exact suffixes. We had to
separate a family label from a valid selectable model and ensure a broad text
replacement could not weaken runtime behavior. Tests now enforce the exact
allowlist and reject silent fallback.

### Publishing rich artifacts without leaking private state

Four publications in four formats create many opportunities to expose a path,
artifact body, prompt, source excerpt, or provider payload. Public response
models are constructed from explicit allowlists, downloads are owner-scoped
and hash-checked, and preview uses an empty sandbox.

### Honest release evidence

The live provider proof and the final judge-asset commit are different source
revisions. The evidence keeps those identities separate instead of implying
that later documentation changes were part of the paid provider run.

## Accomplishments

- One learner request produces four distinct, coordinated publications and
  exactly sixteen private artifacts.
- Progress survives browser refresh and persistent backend container
  replacement.
- The student assessment and instructor answer key are structurally separate.
- Research evidence, source summaries, and unresolved conflicts remain
  reviewable.
- Exact-model readiness and execution fail closed.
- Deterministic generation can reproduce the full engine and browser journey
  without provider credentials or network access.
- The production Docker path runs non-root and passes health, persistence,
  replacement, distribution, and image checks.
- The live synthetic proof completed with real GPT-5.6 and Tavily research
  while preserving a bounded public evidence record.

## What We Learned

AI course generation is not mainly a prompt-writing problem. The difficult
parts are admission durability, evidence ownership, output validation,
artifact integrity, privacy boundaries, and giving the learner enough
visibility to trust what happened.

We also learned that exact model naming belongs in typed configuration and
tests, not documentation alone. A readiness screen is valuable only when it
checks the same capabilities the worker will actually use. Finally, release
evidence is strongest when deterministic regression proof, paid live proof,
and final source identity are explicit instead of blended together.

## What Is Next

The current `1.0.2` release is deliberately a local Docker product for
synthetic demonstrations. The next responsible steps are:

- define formal retention, deletion, provider-transfer, and public
  personal-data policies before accepting real learner content;
- move generation ownership to an external queue before enabling concurrent
  backend workers;
- add LMS exports such as SCORM or Common Cartridge;
- add instructor review and revision controls before final publication;
- support collaborative course workspaces and versioned updates;
- add richer accessibility checks and multilingual learning packages; and
- evaluate learning quality with educators and students across different
  connectivity and classroom settings.

## Links And Media

- Source repository: <https://github.com/moshehbenavraham/txt2crs>
- Intended immutable release:
  <https://github.com/moshehbenavraham/txt2crs/tree/v1.0.2>
- Public evidence map:
  [screenshots and release evidence](PUBLIC_EVIDENCE_INDEX.md)
- Deterministic judge sample:
  [complete reproducible journey](../release/DETERMINISTIC_SAMPLE_1_0_0.md)
- Codex feedback reference:
  [bounded Session ID and development summary](CODEX_FEEDBACK.md)
- Demo publication record:
  [storyboard, narration, and verification](VIDEO_STORYBOARD.md)

The human operator adds the stable public YouTube URL directly to Devpost.
Platform URLs and confirmation details remain outside tracked repository files.

## Credits And Acknowledgements

- OpenAI Codex was the development collaborator, and the packaged Codex
  runtime executes exact GPT-5.6 course generation through a ChatGPT
  subscription.
- Tavily provides bounded web research through the engine-owned MCP boundary.
- FastAPI, Pydantic, SQLModel, Alembic, PostgreSQL, React, TanStack,
  Tailwind CSS, shadcn/ui, Playwright, uv, and the wider open-source ecosystem
  provide the product foundation.
- The AIwithApex Python/React boilerplate provided the original application
  shell that was adapted around the reusable `txt2crs` engine.
- My wife supplied the question that gave the project its purpose.

Third-party licenses and provenance remain in the repository license and
package metadata.

## Account-Only Fields

Submitter type and country of residence are completed only in the private
Devpost account flow. They are intentionally not copied into repository
evidence, screenshots, logs, or platform confirmation notes.
