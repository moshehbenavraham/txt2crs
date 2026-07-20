# `1.0.0` Deterministic Course Sample

This credential-free sample is the stable judge and regression example. It
uses the public deterministic application factory, real request/checkpoint/
validation/rendering/artifact stores, a frozen local research ledger, and six
strict local model turns. It does not call OpenAI or Tavily and must never be
presented as the live provider proof.

## Synthetic Input

| Field | Value |
|-------|-------|
| Input type | Topic prompt |
| Topic | Teach Python variables. |
| Learning goal | Explain and use Python variables. |
| Audience | Adult learner |
| Provider processing consent | Enabled for parity with the learner contract |
| Desired depth | Introductory |
| Duration | 60 minutes |
| Assessment items | 1 |
| Accessibility | Semantic headings |

## Expected Journey

1. The owner submits one strict request with an idempotency key.
2. Admission commits the request before returning the accepted job.
3. The serial executor moves through bounded ingestion, policy, preference,
   research, drafting, validation, rendering, and delivery checkpoints.
4. Public status remains owner-scoped, monotonic, and path-free.
5. Completion returns four distinct publications and exactly sixteen private
   artifacts.

## Expected Publications

| Publication | Purpose | Formats |
|-------------|---------|---------|
| Course | Introductory lesson aligned to the learning goal | HTML, Markdown, PDF, DOCX |
| Review pack | Study and recall material derived from the course | HTML, Markdown, PDF, DOCX |
| Student assessment | One learner-facing assessment without solutions | HTML, Markdown, PDF, DOCX |
| Instructor answer key | Separate corresponding solutions and rationale | HTML, Markdown, PDF, DOCX |

The deterministic scenario uses a compact one-module course titled
`Python Basics`, one primary-source evidence record, and one research question
about how Python assignment binds names. The sample intentionally records only
the public shape, not complete publication bodies.

## Reproduce The Engine Lifecycle

From `backend/packages/txt2crs/`:

```bash
uv run --package txt2crs pytest \
  tests/integration/test_application_lifecycle.py -q
```

The test proves:

- public-factory submission and execution;
- terminal completion and durable public recovery;
- exactly sixteen artifact manifest entries;
- integrity-checked private artifact access; and
- idempotent owner purge of job and artifact state.

## Reproduce The Full Browser Journey

From `frontend/`:

```bash
npx playwright test \
  --config=playwright.jobs.config.ts \
  --project=chromium-complete
```

The browser submits the same topic, double-clicks the create action to prove
duplicate prevention, refreshes the durable progress URL, waits for completion,
and checks the four-publication results workspace and all sixteen manifest
entries through the real FastAPI/public-engine boundary.

## Safety Boundary

This file contains synthetic input and deterministic public facts only. It has
no account identifier, credential, provider response, prompt transcript,
private path, artifact body, or live-job link. The real GPT-5.6 plus Tavily
proof is recorded separately only after its redaction and sixteen-artifact
inspection gates pass.
