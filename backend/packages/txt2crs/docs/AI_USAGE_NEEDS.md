# AI Usage Needs Derived from the Make.com Scenarios

**Study date:** 2026-07-17

**Scope:** The three exported Make.com blueprints in `make-scenarios/`

**Purpose:** Identify what the current automation uses AI for, where it falls short of
the product goal, and what AI capabilities the txt2crs application needs next.

## Executive Summary

The current Make.com workflow is a useful proof of concept for turning one plain-text
input into a course PDF and a short-answer quiz. Its AI work is concentrated in the
third scenario and consists of four serial model calls:

1. Claude creates the course.
2. GPT-5 mini names the file.
3. GPT-5 converts the course to HTML.
4. Claude creates 5-10 short-answer questions and an answer key.

The workflow does **not** currently perform deep research. It has no search, retrieval,
source-selection, citation, or fact-verification stage. Instructions such as "factually
correct," "current," and `[Updated: YYYY]` ask the course-writing model to supply
knowledge from its own context without evidence. This creates a material gap between
the existing automation and the project's promise of a "full deep-researched course."

Research must therefore be implemented as an **additional, net-new product feature**.
It is not a capability that can be migrated or reproduced from the current Make.com
scenarios. The new application will need its own research workflow, source-management
system, citation model, and verification checks.

The workflow also does not yet generate comprehensive review materials or a full test.
The only separate study artifact is a 5-10 question short-answer quiz. There are no
flashcards, glossary, study guide, practice set, assessment blueprint, varied question
types, grading rubric, or coverage check.

The recommended direction is a source-grounded, schema-driven pipeline:

`normalize input -> plan -> research -> write -> verify -> create review pack -> create
assessment -> render deterministically -> deliver`

The most urgent needs are research with citations, structured and validated outputs,
prompt-injection defenses, privacy and webhook protection, idempotent job processing,
and measurable quality gates.

## Evidence Reviewed

- [Project goals](https://github.com/moshehbenavraham/txt2crs/blob/main/AGENTS.md)
- [Scenario 1: intake](https://github.com/moshehbenavraham/txt2crs/blob/main/make-scenarios/%5BSTUDY%5D%20Create%20Course%20Material%20from%20Plain%20Text%20%281-3%29.blueprint.json)
- [Scenario 2: onboarding](https://github.com/moshehbenavraham/txt2crs/blob/main/make-scenarios/%5BSTUDY%5D%20Create%20Course%20Material%20from%20Plain%20Text%20%282-3%29.blueprint.json)
- [Scenario 3: generation and delivery](https://github.com/moshehbenavraham/txt2crs/blob/main/make-scenarios/%5BSTUDY%5D%20Create%20Course%20Material%20from%20Plain%20Text%20%283-3%29.blueprint.json)

The findings below are based on the exported blueprints only. They do not assume the
existence of unexported Make.com settings, provider-side policies, or separate manual
processes.

## Current Workflow

### Scenario 1: Intake

Paperform receives a name, email address, text input, service, product summary, and
coupon. The scenario stores the submission in Airtable and calls the second scenario
through a Make webhook.

There is no AI usage in this scenario.

### Scenario 2: Customer and Folder Setup

The scenario looks up the submission and matches the customer by normalized email. It
creates or updates an Airtable onboarding record, creates a Google Drive folder when
needed, links the submission to the customer, and calls the third scenario through
another Make webhook.

There is no AI usage in this scenario.

### Scenario 3: AI Generation and Delivery

The scenario loads the customer's latest text input, defines two large prompts, runs
the four AI calls, converts generated HTML to a PDF, saves the course and quiz to
Google Drive, stores generated text and links in Airtable, creates public share links,
and emails them to the customer.

## AI Call Inventory

| Order | Module | Model and settings | Input | Output | Observations |
| --- | --- | --- | --- | --- | --- |
| 1 | 35, `Create Course` | `claude-sonnet-4-5-20250929`; temperature `1`; maximum output `64,000` tokens | The full `Last Text Input` plus a course-authoring prompt | Unstructured course text | One call is expected to analyze, level, expand, update, and author the entire course. It has no research tools or source evidence. |
| 2 | 11, `File Naming` | `gpt-5-mini`; reasoning effort `low`; temperature `1.3`; JSON-object response | The entire generated course | `{ "file_name": "..." }` | This is the only AI step with a machine-readable output contract. A high temperature is unnecessary for a utility naming task. |
| 3 | 31, `Create HTML` | `gpt-5`; reasoning effort `low`; temperature `1`; raw-text response | The entire generated course plus a long formatting prompt | Standalone HTML | AI is being used as a renderer. The output is neither schema-validated nor sanitized before the PDF service receives it. |
| 4 | 33, `Create Quiz Questions` | `claude-sonnet-4-5-20250929`; temperature `1`; maximum output `64,000` tokens | The entire generated course plus a quiz prompt | Plain-text quiz and answer key | The prompt limits the artifact to 5-10 short-answer questions. There is no assessment blueprint or independent answer validation. |

At least three downstream calls receive a complete copy of the generated course:
filename generation, HTML generation, and quiz generation. If the course contains
`C` tokens, these calls consume approximately `3C` input tokens before counting their
instructions or outputs. The course is also processed by both Anthropic and OpenAI.

The `MAX_TOKENS` Make variable is set to `64000`, but module 35 hard-codes the same
number rather than referencing the variable. This is a small sign of configuration
drift.

## What the Existing Design Does Well

- It separates customer onboarding from the expensive generation workflow.
- It preserves the original input and generated artifacts in Airtable and Drive.
- It uses a JSON response for the filename, reducing parsing ambiguity at that step.
- It keeps course generation and assessment generation as separate AI tasks.
- It retries the two OpenAI modules on module errors.
- The course prompt contains useful pedagogical instructions about prerequisites,
  learning objectives, progression, examples, misconceptions, and practical use.

These are sound proof-of-concept choices, but they need stronger contracts and quality
controls before the workflow can reliably support arbitrary inputs.

## Findings and AI Requirements

### Explicit New Feature: Research Capability

The ability to research a course topic is **not present in any of the three Make.com
scenarios**. The scenarios contain no general web search, academic search, document
retrieval, source evaluation, citation capture, or evidence-verification module.
Airtable record searches in Scenario 2 are customer-data lookups and do not constitute
course research.

Research must be added to txt2crs as a separate product capability. At a minimum, this
feature must be able to:

- Turn a course request into focused research questions.
- Search the web, approved databases, or a curated knowledge collection.
- Evaluate source relevance, authority, freshness, and conflicts.
- Preserve source metadata and the evidence used from each source.
- Connect sources to the course outline and individual factual claims.
- Produce visible citations and a bibliography for the learner.
- Verify that cited sources actually support the generated material.
- Clearly disclose when research is unavailable, incomplete, or inconclusive.

This feature should run before course drafting so that the course, review materials,
test, and answer sheet are all generated from the same verified evidence base.

### P0: Add Real Research, Grounding, and Provenance

**Evidence:** Module 35 receives only the user's text and a static prompt. No module in
any scenario searches the web, queries a trusted corpus, retrieves documents, or
captures citations.

**Risk:** A fluent response may be mistaken for a researched course. Claims can be
outdated, invented, or unsupported. The prompt's dated/updated labels can increase
false confidence because the labels are not backed by sources.

**Need:**

- Create a research plan from the user's topic, audience, objectives, and desired
  depth.
- Search or retrieve from approved sources and retain title, author/publisher, URL,
  publication date, retrieval date, and relevant excerpt for each source.
- Prefer primary and authoritative sources where the subject permits.
- Attach source identifiers to the outline and to factual claims during drafting.
- Run a citation-completeness and citation-entailment check before delivery.
- Clearly distinguish facts derived from the user's input, externally researched
  facts, and model-generated examples or explanations.
- Provide a "research unavailable" mode that is labeled honestly instead of presenting
  an ungrounded result as deep research.

### P0: Replace Free-Form Handoffs with Structured Contracts

**Evidence:** Course, HTML, and quiz outputs are raw text. Only the filename uses a JSON
object. The generated course is treated as both a human document and an API payload.

**Risk:** Missing sections, malformed HTML, mismatched question and answer numbers, and
provider formatting changes can silently reach the customer.

**Need:**

- Define versioned schemas for `CoursePlan`, `ResearchSource`, `Course`,
  `ReviewPack`, `Assessment`, and `AnswerKey`.
- Require stable identifiers for learning objectives, course sections, sources, and
  assessment items.
- Validate every AI response before allowing the next stage to run.
- Retry invalid responses with validation feedback and a bounded retry count.
- Persist the validated structured artifact as the source of truth.
- Render Markdown, HTML, PDF, and Google Docs from that artifact with normal code and
  templates rather than asking a second model to reproduce the entire course.

### P0: Treat User and Model Content as Untrusted

**Evidence:** The submitted text is inserted directly into a user message, while the
main instructions are sent as an `assistant` message rather than a system/developer
instruction. The generated course is then placed directly into later AI prompts and
raw HTML is sent to a PDF converter.

**Risk:** Instructions embedded in a transcript can redirect the model, suppress
required sections, request data disclosure, or inject unsafe HTML and remote resource
references.

**Need:**

- Place invariant application rules in the highest-priority instruction role supported
  by the provider.
- Delimit submitted and retrieved content as data and explicitly prohibit following
  instructions found inside that data.
- Sanitize rendered HTML with an allowlist; reject scripts, event handlers, iframes,
  remote resource loading, and unsafe URLs.
- Validate outbound links and citations.
- Add policy checks for disallowed content, dangerous instruction, copyright-sensitive
  transformations, and age-inappropriate educational material.
- Offer a human-review path for high-risk domains such as medical, legal, financial,
  or safety-critical instruction.

### P0: Protect Content, Identity, and AI Spend

**Evidence:** Both scenario-to-scenario webhook URLs are embedded in the blueprints and
requests contain only an Airtable record identifier. There is no visible signature,
authentication header, authorization check, rate limit, or idempotency key. Drive
folders are created with "anyone" commenter access, and course and quiz files receive
"anyone" reader links.

**Risk:** An exposed webhook can be abused to create model spend, retrieve jobs by
identifier, produce duplicate artifacts, or trigger email. Public sharing can expose
private, proprietary, or personally sensitive course input and output.

**Need:**

- Rotate webhook URLs exposed by blueprint exports.
- Authenticate and sign internal workflow calls, validate timestamps, and reject
  replays.
- Authorize every job against the requesting user rather than trusting a record ID.
- Add per-user and global rate, token, and cost limits.
- Use a stable idempotency key across generation, storage, and email delivery.
- Make Drive artifacts private by default and grant access to the intended recipient.
- Obtain clear consent for sending submitted content to each AI provider.
- Define retention, deletion, redaction, and no-training/data-processing policies.
- Avoid logging raw user content unless it is necessary and explicitly protected.

### P0: Make Failures Recoverable and Delivery Idempotent

**Evidence:** Only modules 11 and 31 have five retries at three-second intervals.
Course generation and quiz generation have no module-level retry handlers. There is no
visible job state machine, dead-letter recovery UI, duplicate-delivery guard, or
quality-failure path.

**Risk:** A transient failure can abandon a paid job. Replaying a webhook can create
duplicate files, Airtable records, AI charges, and customer emails.

**Need:**

- Track a job through explicit states such as `accepted`, `researching`, `drafting`,
  `validating`, `rendering`, `delivering`, `completed`, and `failed`.
- Checkpoint each validated stage so a retry resumes instead of regenerating
  everything.
- Use exponential backoff with jitter for retryable errors and do not retry permanent
  validation, authentication, or policy failures blindly.
- Apply consistent provider timeouts, cancellation, retry, and fallback behavior.
- Send the completion email once, only after all required artifacts pass validation.
- Surface an actionable failure reason and permit a safe manual retry.

### P1: Support "Any Input" Explicitly

**Evidence:** The current form and AI prompt accept a single plain-text field described
as a transcript or course request. There is no extraction or normalization stage.

**Need:**

- Define supported input types: prompt, pasted text, URL, PDF, document, slides, image,
  audio, and video.
- Extract text with the appropriate parser, OCR, or transcription process.
- Detect language, document type, encoding problems, and extraction quality.
- Preserve page, timestamp, and source boundaries for citations.
- Reject unsupported or empty inputs with a useful explanation.
- Chunk long inputs and retrieve relevant chunks per course section rather than
  repeatedly sending the whole source.

### P1: Separate Planning, Writing, and Verification

**Evidence:** Module 35 performs analysis, level selection, curriculum design, factual
expansion, and final writing in one call at temperature `1`.

**Risk:** A single very large response is difficult to verify, retry selectively, or
keep internally consistent. A maximum output of 64,000 tokens can also exceed
downstream Make, Airtable, provider-context, or document limits.

**Need:**

- Collect or infer audience, prior knowledge, desired depth, duration, language,
  accessibility needs, and learning outcomes.
- Generate and validate an outline before drafting.
- Research and draft one module at a time with shared course terminology and state.
- Set token budgets per stage and section rather than one maximum-size response.
- Run coverage, duplication, prerequisite, terminology, and cross-reference checks
  after assembly.
- Let the user approve or edit the outline for long or costly courses.

### P1: Generate a Complete Review Pack

**Evidence:** The workflow creates only the course and one short-answer quiz. A "Quick
Reference" section may appear inside the course, but no independent comprehensive
review material is required or validated.

**Need:** Generate a structured review pack containing:

- A concise study guide organized by learning objective.
- A glossary with definitions and course-section references.
- Key takeaways and common misconceptions.
- Flashcards with stable prompt/answer pairs.
- Worked examples and practice exercises.
- Section summaries and a final cumulative summary.
- A recommended review sequence or spaced-practice plan.
- Source links for claims that depend on external research.

### P1: Generate a Full, Valid Assessment

**Evidence:** Module 33 is explicitly limited to 5-10 short-answer questions. Questions
and answers are generated in the same free-form response from the generated course.

**Need:**

- Build an assessment blueprint before writing questions.
- Map every item to a learning objective, course section, difficulty, and cognitive
  skill.
- Support an intentional mix of multiple-choice, short-answer, application, analysis,
  and practical tasks where appropriate.
- Produce separate student and instructor versions.
- Include correct answers, explanations, grading criteria, point values, and rubrics.
- Check that every answer is supported by the validated course and cited sources.
- Detect ambiguous wording, duplicate items, answer leakage, and accidental clues.
- Set configurable length and passing criteria rather than a fixed 5-10 questions.

### P1: Reduce Cost and Latency with Task-Appropriate Tools

**Evidence:** Four serial AI calls are made per course. The complete course is sent to
three downstream model calls. GPT-5 is used to render HTML, and GPT-5 mini receives the
whole course only to produce a filename.

**Need:**

- Derive the filename deterministically from the validated course title.
- Render HTML and PDF from a tested template without an AI call.
- Give the assessment model only the structured objectives and relevant course
  sections needed for each item.
- Cache research and normalized source content when policy permits.
- Route tasks by capability, latency, and cost; keep provider and model identifiers
  configurable rather than embedded throughout the workflow.
- Record tokens, estimated cost, latency, retries, and model version per stage.

Removing AI-based naming and HTML conversion would reduce the normal path from four
model calls to two core generation calls, before adding deliberate research and
verification stages. The saved calls can be exchanged for higher-value research and
quality control rather than formatting work.

### P1: Add Quality Evaluation and Observability

**Evidence:** There is no automated rubric, factuality check, citation check, assessment
coverage report, or user-feedback loop. Retry handlers react to module failure, not
low-quality content.

**Need:**

- Maintain a fixed evaluation set covering short prompts, long transcripts, noisy
  extraction, conflicting sources, prompt injection, multiple languages, and
  specialist topics.
- Score research quality, citation support, objective coverage, pedagogy, readability,
  assessment validity, format correctness, and safety.
- Use deterministic checks first and a separate model-based evaluator only where human
  judgment is required.
- Prevent the same model response from grading itself without independent evidence.
- Capture user ratings and correction reasons without exposing private content.
- Version prompts, schemas, templates, provider settings, and evaluation results.

### P2: Improve Personalization, Accessibility, and Internationalization

**Evidence:** The course model infers a beginner/intermediate/advanced level from free
text. Intake fields such as `Service` and `Product Summary` are stored but not used by
the generation prompt. There are no explicit language, accessibility, or output
preferences.

**Need:**

- Ask for audience, current knowledge, goals, time budget, preferred language, tone,
  assessment type, and accessibility needs.
- Show inferred settings to the user and allow correction.
- Keep reading level and terminology consistent across the course, review materials,
  and assessment.
- Produce semantic headings, alt text or textual equivalents, accessible tables, and
  PDF output suitable for assistive technology.
- Support right-to-left and multilingual course generation and evaluation.

## Recommended Target Pipeline

1. **Accept and authorize the job.** Validate the user, payment/entitlement, input
   type, size, and idempotency key.
2. **Normalize the input.** Extract, transcribe, OCR, classify, detect language, and
   preserve source locations.
3. **Clarify the learning contract.** Establish audience, prerequisites, outcomes,
   scope, depth, duration, and assessment preferences.
4. **Plan the curriculum.** Produce a structured outline and research questions.
5. **Research and collect evidence.** Retrieve approved sources and build a
   deduplicated source ledger.
6. **Draft by module.** Write sections against approved objectives and source IDs.
7. **Verify and assemble.** Check claims, citations, coverage, consistency, safety,
   and schema validity.
8. **Create the review pack.** Derive summaries, glossary, flashcards, examples, and
   practice material from the validated course.
9. **Create and validate the assessment.** Use an objective-aligned blueprint,
   independent answer checks, and separate student/instructor artifacts.
10. **Render deterministically.** Produce accessible web, Markdown, PDF, and document
    formats from templates.
11. **Deliver once.** Store private artifacts, notify the user, and record completion
    metrics without duplicating side effects.

## Minimum Structured Artifact

The course-generation contract should contain at least:

```text
Course
  schema_version
  title
  language
  audience
  level
  prerequisites[]
  learning_objectives[]
    objective_id
    description
  sources[]
    source_id
    title
    publisher_or_author
    url_or_input_location
    publication_date
    retrieved_at
  modules[]
    module_id
    title
    objective_ids[]
    sections[]
      section_id
      content_blocks[]
      source_ids[]
    summary
    misconceptions[]
    examples[]
  glossary[]
  unresolved_or_conflicting_claims[]
```

Review and assessment artifacts should reference the same `objective_id`, `module_id`,
`section_id`, and `source_id` values. That shared identity makes coverage and factual
support testable instead of relying on visual inspection.

## Suggested Acceptance Criteria

- Every delivered job has authenticated ownership and one idempotency key.
- Replaying any internal request does not duplicate AI work, files, records, or email.
- Every AI output passes its versioned schema before the next stage begins.
- Every externally verifiable course claim has supporting source metadata, or is
  explicitly labeled as an example, inference, opinion, or unresolved claim.
- Every learning objective maps to course content, review material, and at least one
  assessment item unless intentionally marked non-assessed.
- Every assessment item maps to an objective and has a course-supported answer,
  explanation, difficulty, and grading rule.
- Malformed HTML or unsafe embedded content cannot reach the PDF converter.
- Long and unsupported inputs fail gracefully or use chunking; they are never silently
  truncated.
- Private input and generated materials are not publicly shared by default.
- Per-stage model, prompt version, token count, cost, latency, retry, validation, and
  quality status are observable.
- A user can see job progress and receive a clear recovery path when a stage fails.

## Recommended Implementation Order

1. Secure the webhooks, sharing defaults, authorization, and idempotency.
2. Define structured course, review, assessment, answer-key, and source schemas.
3. Replace AI filename and HTML generation with deterministic code and templates.
4. Add research/source collection and citation-aware course drafting.
5. Add validation, checkpoints, retries, and job-state observability.
6. Expand the quiz into the review pack and assessment blueprint described above.
7. Add long-input ingestion, personalization, accessibility, and multilingual support.
8. Build a repeatable evaluation suite and use it to govern prompt/model changes.

This order first removes the largest security and reliability risks, then aligns the
AI pipeline with the product's education promise, and finally broadens input and user
experience capabilities.
