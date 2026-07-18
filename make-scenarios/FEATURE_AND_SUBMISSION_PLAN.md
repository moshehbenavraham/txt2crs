# Feature and Submission Plan

This plan converts the legacy system evidence into product decisions for the
txt2crs hackathon submission. It deliberately distinguishes:

- **legacy intent** — useful behavior visible in the Make blueprints;
- **engine capability** — behavior already evidenced in the current Python
  package;
- **application work** — FastAPI/browser functionality still needed;
- **optional expansion** — valuable after the core demo works.

The authoritative current-engine summaries are the
[package overview](../backend/packages/txt2crs/README_txt2crs.md) and
[implementation compliance matrix](../backend/packages/txt2crs/docs/IMPLEMENTATION_COMPLIANCE.md).
The submission requirements and deadline live in
[OPENAI_BUILD_WEEK_REQUIREMENTS.md](../docs/ongoing-projects/OPENAI_BUILD_WEEK_REQUIREMENTS.md).

## Product north star

A learner supplies almost any topic or source. txt2crs researches it, builds a
source-grounded course, derives a comprehensive review pack and aligned
assessment, then privately delivers polished artifacts through an interface
that makes a long-running AI job understandable and trustworthy.

The legacy workflow proves the value of the first and last moments—easy input
and tangible delivery. The current engine supplies the rigorous middle.

## Decision vocabulary

| Label | Meaning |
|---|---|
| **P0 — Demo critical** | Required for the working Education submission and under-three-minute demo |
| **P1 — Submission polish** | Add after the complete P0 journey is reliable |
| **P2 — Post-submission** | Valuable product work that should not displace P0/P1 |
| **Reject** | Historical behavior that should not be reproduced |
| **Engine exists** | Current repository documentation and tests claim this reusable behavior is implemented |
| **Shell needed** | Browser/API composition is still absent |

## Comprehensive feature decision matrix

### Intake, identity, and learner experience

| Feature | Legacy evidence | Current state | Decision |
|---|---|---|---|
| Pasted prompt/text | Paperform `Text Input` | Engine ingestion exists | **P0:** expose clearly in UI |
| URL, PDF, DOCX, PPTX, image, audio, video, YouTube | Not implemented | Engine adapters exist | **P0:** expose upload/URL modes supported by the package |
| Input preview and extraction warnings | Not implemented | Normalized input/warnings exist | **P0:** show before/while generating |
| Learner name/email | Stored in Airtable | App user/session absent | **P0:** establish a stable demo owner; do not use email alone as authorization |
| Returning learner | Email lookup and Onboarding row | Owner-scoped jobs exist | **P1:** job library/history |
| Level | Model infers 3 levels | Course plan supports beginner/intermediate/advanced/mixed | **P0:** learner choice plus “auto” fallback |
| Audience, goals, prerequisites | Model infers them | Structured course plan exists | **P0:** collect optional audience/goals; show inferred plan |
| Target duration/depth | Prompt notices time constraints; form does not map one | Course plan has bounded duration | **P1:** optional duration/depth control after defaults work |
| Output language and RTL | No explicit field or UI | Language contract and RTL evaluation case exist | **P0:** preserve/detect language; **P1:** explicit selector and RTL visual QA |
| Accessibility needs | Not implemented | Course plan contract supports them | **P1:** preferences with sensible defaults |
| Mobile/low-bandwidth access | Paperform and emailed download links | Application concern | **P0:** responsive, lightweight progress/results and downloadable artifacts |
| Payment/service/coupon | Captured, not enforced | Explicitly app-shell responsibility | **P2:** defer all commerce for the hackathon |
| Consent/learner age/high-risk review | Not implemented | Engine policy gates exist | **P0:** collect required consent/age context and render safe review states |

### Research and course creation

| Feature | Legacy evidence | Current state | Decision |
|---|---|---|---|
| Source interpretation | One course prompt | Engine ingestion/research planning exists | **P0:** automatic with visible input type |
| Deep research | Prompt asks for accuracy but no tools | Bounded search/extract pipeline exists | **P0:** run and communicate research stage |
| Reliable sources/citations | Not implemented | Evidence ledger and citation checks exist | **P0:** include sources in outputs/results |
| Conflict/uncertainty disclosure | Not implemented | Structured unresolved/conflicting claims exist | **P0:** display without hiding uncertainty |
| Course plan | Hidden inside one call | Versioned plan exists | **P0:** use as internal checkpoint; optionally summarize in progress UI |
| Level-appropriate curriculum | Detailed legacy rubric | Structured level/audience fields exist | **P0:** preserve |
| Objectives and prerequisites | Required by prompt | Structured contracts exist | **P0:** preserve and display |
| Modules/sections and progression | Prompt asks for 3–7 sections | Module-sized generation exists | **P0:** let planning determine shape within budgets |
| Definitions/glossary | Prompt requests definitions | Structured glossary exists | **P0:** preserve |
| Examples/applications | Prompt requests both | Structured module examples/content blocks exist | **P0:** preserve |
| Misconceptions | Prompt requests them | Structured module misconceptions exist | **P0:** preserve |
| Expert insights/quick reference | Prompt labels | Equivalent structured content/review summaries exist | **P1:** style these as learner-friendly callouts |
| Dated/updated/emerging labels | Prompt labels without research | Evidence/freshness pipeline exists | **P1:** derive trustworthy currency notes from evidence instead of decorative tags |
| Human plan approval/edit | Not implemented | Package produces strict plans; UI absent | **P2:** instructor workflow after the demo |

### Review and assessment

| Feature | Legacy evidence | Current state | Decision |
|---|---|---|---|
| Standalone review pack | Not implemented | Full review pack exists | **P0:** make it a first-class result card |
| Summaries/quick reference | Embedded in course prompt | Review structures exist | **P0:** include in review pack |
| Glossary/misconceptions | Embedded in course | Review structures exist | **P0:** include |
| Flashcards/worked examples/practice/review sequence | Not implemented | Engine support is documented | **P0:** include and demonstrate one |
| Short-answer questions | 5–10 generated | Assessment contracts exist | **P0:** retain as one supported item style, not the entire test |
| Assessment blueprint | Prompt-only distribution planning | Separately approved blueprint exists | **P0:** use |
| Objective/evidence alignment | Requested but not encoded | Deterministic checks exist | **P0:** preserve |
| Student assessment | Combined with answers | Separate artifact exists | **P0:** deliver separately |
| Instructor answer key/rubrics | Combined 1–3 sentence answers | Separate evidence-backed key exists | **P0:** deliberate instructor download |
| Automatic grading | Not implemented | Not claimed by engine | **P2:** do not add for submission |
| Interactive quiz-taking | Not implemented | Rendered artifacts exist | **P2:** downloadable assessment is sufficient |

### Rendering, storage, and delivery

| Feature | Legacy evidence | Current state | Decision |
|---|---|---|---|
| Course PDF | Model HTML → third-party PDF | Deterministic PDF exists | **P0:** downloadable |
| HTML | Model-generated and stored | Deterministic safe HTML exists | **P0:** browser preview |
| Markdown and DOCX | Not implemented | Deterministic renderers exist | **P0:** format choices/downloads |
| Four deliverables × four formats | Not implemented | 16 private artifacts exist | **P0:** organize without overwhelming the user |
| Descriptive file names | Separate model call | Deterministic app concern | **P0:** safe slugs/display names without another model turn |
| Private artifact storage | Public Drive links | Owner-scoped filesystem store exists | **P0:** authenticated/owner-checked download |
| Google Drive export | Primary legacy storage | App integration absent | **P2:** optional export, never core persistence |
| Course library/history | Airtable relationships + folder | Durable jobs exist; UI absent | **P1:** result history and reopen |
| Completion email | Terminal Gmail module | Notification interface/idempotency exists | **P1:** email only after in-app success works |
| Public share links | Anyone-with-link files | Conflicts with private default | **Reject** as default; consider explicit expiring share later |
| Deletion/retention | Not implemented | Engine store supports both | **P1:** expose delete and retention notice |

### Reliability, safety, and operations

| Feature | Legacy evidence | Current state | Decision |
|---|---|---|---|
| Durable job state | Implicit Make execution | SQLite job state exists | **P0:** wire through API |
| Progress states | Not learner-visible | Safe progress projection exists | **P0:** research/draft/validate/render/deliver UI |
| Crash resume | Make partial state only | Cumulative checkpoints exist | **P0:** resume safely after restart |
| Idempotent submission | Not implemented | Job idempotency key exists | **P0:** prevent double-click duplicate work |
| Cancellation | Not implemented | Runtime/job status supports cancellation | **P1:** cancel action and clear state |
| Retry policy | Two OpenAI calls only | Finite transient retries/repair exist | **P0:** surface retrying versus failed |
| Spend/admission limits | Not implemented | Per-user/global reservations exist | **P0:** configure finite demo limits |
| Prompt-injection/content safety | Not implemented | Tool/content boundaries exist | **P0:** preserve; never render raw model HTML |
| Authenticated ownership | Email only | Owner-scoped services exist | **P0:** app must establish and enforce `user_id` |
| System OpenAI readiness | Hidden Make connection | Dedicated-system authentication service exists | **P0:** operator setup/status screen or preflight |
| Observability | Make execution logs only | Safe/private event contracts exist | **P1:** operator diagnostics without secrets |
| Evaluation/feedback | Not implemented | Fixed evaluation corpus and private ratings exist | **P1:** run pre-demo evals; optional learner feedback control |

## The P0 submission slice

The smallest complete submission should have four product surfaces.

### 1. Operator setup/readiness

- Start or inspect the dedicated ChatGPT device-code connection.
- Show safe provider/account/model readiness without exposing tokens.
- Verify research-provider configuration and writable private storage.
- Refuse new work with a clear operator-facing reason when the system is not
  ready.

This can be preconfigured for the demo, but the readiness state must still be
checked before a learner submits.

### 2. Learner intake

- A polished landing page that explains the four deliverables.
- Input modes for prompt/text, URL, and file/media uploads supported by the
  package.
- Optional audience, level (`Auto` plus four explicit values), learning goals,
  and accessibility/context fields.
- Required consent and any policy context needed by the executor.
- File/type/size validation and a clear sample input.
- A stable owner/session and an idempotency key generated before submission.

### 3. Trustworthy progress

- One durable job URL that survives refresh.
- Stages matching the real state machine: accepted, researching, drafting,
  validating, rendering, delivering, completed/failed/cancelled.
- Plain-language explanations and safe progress, never raw prompts, provider
  events, credentials, or private research text.
- Recoverable error UX with retry/resume guidance.
- A clear warning when human review is required.

### 4. Results workspace

- Four primary cards: Course, Review Pack, Student Assessment, Instructor
  Answer Key.
- Browser-safe HTML preview where useful.
- HTML, Markdown, PDF, and DOCX downloads grouped under each card.
- Source/citation visibility and unresolved-conflict disclosure.
- Owner-checked artifact URLs; no direct filesystem paths or public Drive
  permissions.
- Clear separation and labeling of student versus instructor material.
- Usage/quality summary appropriate for a demo, without internal secrets.

## Suggested FastAPI surface

Names may change, but the product needs equivalent responsibilities:

| Method/path | Priority | Responsibility |
|---|---|---|
| `GET /api/v1/system/readiness` | P0 | Safe operator/runtime readiness |
| `POST /api/v1/system/auth/start` | P0 | Begin dedicated device-code setup when authorized |
| `GET /api/v1/system/auth/status` | P0 | Poll browser-safe setup state |
| `POST /api/v1/jobs` | P0 | Validate input, establish owner/idempotency, reserve limits, start generation |
| `GET /api/v1/jobs/{job_id}` | P0 | Owner-scoped status and public-safe progress |
| `GET /api/v1/jobs/{job_id}/artifacts` | P0 | Completed artifact manifest |
| `GET /api/v1/jobs/{job_id}/artifacts/{artifact_id}` | P0 | Authorized preview/download |
| `POST /api/v1/jobs/{job_id}/cancel` | P1 | Owner-scoped cancellation |
| `DELETE /api/v1/jobs/{job_id}` | P1 | Owner deletion |

The application should call the package boundary. It should not duplicate
generation, research, validation, persistence, or rendering logic in route
handlers.

## Suggested browser routes

| Route | P0/P1 | Experience |
|---|---|---|
| `/` | P0 | Story, capabilities, input form, sample |
| `/jobs/:jobId` | P0 | Live progress transitioning into results |
| `/setup` | P0 operator-only | Dedicated OpenAI connection/readiness |
| `/library` | P1 | Previous jobs, status, reopen, delete |
| `/about/how-it-works` | P1 | Research/citation/privacy explanation |

The visual design should protect the core story: one input becomes four aligned
learning deliverables. Avoid exposing 16 format files as an undifferentiated
list.

## Recommended defaults for unresolved decisions

| Decision | Recommended submission default | Reason |
|---|---|---|
| Identity | Stable demo session/user with enforced owner ID | Enough to prove privacy boundary without building a full identity product |
| Persistence | Existing SQLite job store + private artifact store | Already implemented and demo-friendly |
| Background work | One bounded durable worker/executor | Avoid adding a queue platform before the core flow works |
| Delivery | Results page first | More demoable and reliable than email-only delivery |
| Sharing | Private downloads | Avoid repeating public Drive exposure |
| Drive | Defer export | Not required to prove education value |
| Email | P1 idempotent notification | Useful polish after results UI |
| Payments | Defer | Legacy metadata never influenced generation; not a judging requirement |
| Level | `Auto` with learner override | Preserves easy intake and user control |
| Answer key | Separate, clearly marked instructor artifact | Meets the goal and prevents accidental learner exposure |
| Research | Required before drafting | Central differentiator from the legacy prototype |
| Rendering | Deterministic package renderers | Prevents model drift and unsafe HTML |
| Providers | Approved OpenAI/Codex stack | Aligns with hackathon requirements; avoids historical vendor lock-in |

## Explicit non-goals for the submission

Unless all P0 work is complete and verified, do not spend submission time on:

- recreating Make.com scenarios;
- recreating Airtable tables or linked fields;
- Paperform checkout, products, or coupons;
- arbitrary public sharing;
- Google Drive folder synchronization;
- automatic grading or an LMS;
- collaborative course editing;
- a generalized prompt editor;
- multi-organization administration;
- model/provider switching;
- analytics dashboards beyond required operational evidence.

## Build sequence

### Phase A — application contract

1. Write acceptance tests for the complete browser/API job lifecycle.
2. Compose the existing package services in FastAPI.
3. Establish owner/session, idempotency, policy context, and finite admission.
4. Implement the P0 readiness, submit, status, and artifact boundaries.

### Phase B — core learner UI

1. Build the input experience and validation.
2. Build refresh-safe progress around real job states.
3. Build the four-deliverable results workspace and secure downloads.
4. Add failure, review-required, cancelled, and expired states.

### Phase C — demo hardening

1. Run the complete default package suite and application acceptance tests.
2. Exercise at least one live, representative course end to end.
3. Verify refresh/resume, duplicate-submit protection, and artifact ownership.
4. Review output quality, citations, mobile layout, accessibility, and timing.
5. Prepare a deterministic sample and recovery plan for the recorded demo.

### Phase D — submission polish

1. Add library/history, delete, feedback, or email in that order as time allows.
2. Complete README setup/sample/run and AI-usage details.
3. Record a narrated under-three-minute demo.
4. Capture the primary Codex `/feedback` Session ID.
5. Complete the Devpost fields and repository access/license requirement.

## Acceptance criteria for the working demo

- [ ] A new visitor can understand the product and four outputs without
  reading documentation.
- [ ] The system accepts at least the showcased input and visibly validates it.
- [ ] Submitting twice with the same idempotency key does not create two paid
  jobs.
- [ ] Research occurs before drafting and sources appear in the completed
  experience.
- [ ] Refreshing the job page does not lose progress.
- [ ] A provider/runtime failure becomes a safe, actionable state.
- [ ] One completed job contains a course, review pack, student assessment,
  and separate answer key.
- [ ] Each deliverable offers the formats actually produced by the engine.
- [ ] Artifact access is owner-scoped and does not rely on public Drive links.
- [ ] The UI works at desktop and mobile widths and supports keyboard use.
- [ ] No credential, raw provider event, private path, or webhook secret is
  rendered to the browser.
- [ ] The recorded path completes within the demo narrative and clearly
  explains Codex/GPT-5.6 use.

## Legacy-to-submission traceability

| Legacy product idea | Submission expression |
|---|---|
| “Give us text” | Give txt2crs a topic, text, URL, document, image, audio, or video |
| Automatic course level | Auto-detect or select level and audience |
| Structured curriculum | Evidence-backed course plan and module generation |
| Examples/misconceptions/applications | Canonical course and review components |
| Quick reference | Comprehensive review pack |
| Quiz | Blueprint-aligned student assessment |
| Answer key | Separate instructor artifact |
| Printable PDF | Deterministic PDF plus HTML/Markdown/DOCX |
| Personal folder | Private owner-scoped results workspace/library |
| “Your course is ready” email | Live results first, optional idempotent email |
| Returning customer record | Durable authenticated job history |

The strongest submission is not a prettier clone of the Make automation. It is
the original idea completed: broader input, real research, aligned educational
artifacts, private durable delivery, and an interface that lets a learner see
and trust the transformation.
