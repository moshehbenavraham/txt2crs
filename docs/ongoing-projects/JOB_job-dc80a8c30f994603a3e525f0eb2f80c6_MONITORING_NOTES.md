# Job Monitoring Notes: job-dc80a8c30f994603a3e525f0eb2f80c6

## Monitoring status

- Observation started: 2026-07-21 01:05:32 IDT (2026-07-20 22:05:32 UTC)
- Observation completed: 2026-07-21 01:28:15 IDT
- Current monitoring state: Complete
- Current job state: `failed`
- Last durable update observed: 2026-07-21 01:23:53 IDT
- Final revision: 10
- Terminal outcome: `generation_failed`

## Requested course

- Input: `python`
- Audience: College student coder
- Starting level: Intermediate
- Prior knowledge: Completed a beginner Python course
- Learning goal: Intermediate proficiency in Python coding
- Planned duration: 120 minutes
- Assessment size: 15 items
- Passing score: 70 percent
- Runtime: `gpt-5.6-sol`, high reasoning effort, research enabled

## Observation method

These notes are based on read-only inspection of the durable engine job store,
artifact directory, worker lifecycle logs, provider request logs, and public API
polling logs. Durable checkpoints are treated as authoritative for completed
stages. A stage can be actively running without a new checkpoint, so a quiet
interval alone is not treated as a stall.

## Timeline and live findings

### 2026-07-21 01:03:48 IDT - Submitted and claimed

- The API accepted the prompt and created revision 0.
- The serial worker claimed the job immediately and emitted
  `txt2crs.execution_started`.
- Input preparation completed in the same second as checkpoint 1.
- The normalized input remained `python`, language resolved to English, and
  post-ingestion policy evaluation allowed the request.
- No input warnings were recorded.

### 2026-07-21 01:04:11 IDT - Research plan completed

- Checkpoint 2 completed the `plan_research` stage.
- The plan defined six research questions covering intermediate Python scope,
  prerequisite review, a coherent 120-minute topic sequence, code exercises,
  common misconceptions, and assessment design.
- The plan capped evidence at 12 sources and required authoritative Python
  documentation plus computing pedagogy or assessment sources.
- Budget after this stage: 1 model turn, 8,861 input tokens, 581 output tokens,
  no retries, and about 19.9 seconds elapsed.

### 2026-07-21 01:04:30 IDT - Evidence collection completed

- Checkpoint 3 completed the `collect_evidence` stage.
- Provider logs show two successful Tavily search calls and two successful
  Tavily extract calls. No provider error or retry was observed.
- The evidence set reached the configured cap of 12 sources after four total
  research calls and 282,105 extracted bytes.
- Evidence version:
  `sha256:8044abf4f14e0fc3c29c6a518f77c7953c5add77a1d274d5d948d918a2e098d4`.
- Budget after this stage: 1 model turn, 8,861 input tokens, 581 output tokens,
  no retries or repairs, and about 38.9 seconds elapsed.
- Later evidence audit found that all 12 accepted sources are classified as
  secondary. The set contains no official Python documentation and no source
  classified as primary or authoritative, despite the research plan requiring
  at least three such sources.
- The accepted set includes two Reddit threads, two URLs carrying the same
  titled Medium article, one YouTube tutorial, one arXiv paper, and several
  commercial course or blog pages. Exact URL and content-hash deduplication did
  not flag duplicates, but the two Medium URLs appear semantically redundant.
- The plan also required at least two computing-pedagogy or assessment-design
  sources. That requirement is not evident in the accepted source set.

### 2026-07-21 01:05:00 IDT - Course design completed

- Checkpoint 4 completed the `design_course` stage and stored a course plan.
- The planned title is "Intermediate Python Coding: Foundational to Applied."
- The plan contains four modules and 12 sections. Coverage progresses through
  readiness and functions; data structures and exceptions; iterators,
  generators, classes, and modules; then an integrated exercise and assessment.
- Quality concern to watch: all five learning-objective records currently use
  the same broad description, "intermediate proficiency of python coding."
  Their IDs are mapped across modules, but the objectives are not yet
  independently measurable or distinguishable in the stored plan.
- Budget after this stage: 2 model turns, 22,730 input tokens, 1,753 output
  tokens, no retries or repairs, and about 66.4 seconds elapsed.
- The durable job moved to `drafting` at revision 5.
- No module draft checkpoint had been committed at this observation point.

### 2026-07-21 01:06:36 IDT - First direct monitoring snapshot

- Job remains `drafting` with four durable checkpoints.
- No durable failure record exists.
- No final artifact manifest exists yet, which is expected before rendering and
  completion.
- The worker remains active. System readiness reports `runtime_busy`, which is
  expected while the single serial runtime is occupied.

### 2026-07-21 01:06:52 IDT - Module 1 draft completed

- Checkpoint 5 completed `write_module:m1`; revision advanced to 6 while the
  job remained `drafting`.
- The module is "Readiness Review and Intermediate Functions" with three
  sections and nine content blocks.
- Coverage includes a readiness check, parameters and scope, return-value flow,
  higher-order functions, lambdas, and comprehensions.
- Two model-generated code or practice examples are embedded in the content.
- Six citations are marked supported, and the module records no unresolved or
  conflicting claims.
- Budget after this stage: 3 model turns, 92,911 input tokens, 4,669 output
  tokens, no retries or repairs, and about 171.5 seconds elapsed.
- Observation: module content is substantially more specific than the five
  duplicated learning-objective descriptions to which it is mapped. Later
  validation should ideally catch or compensate for that plan-level weakness.

### 2026-07-21 01:09:02 IDT - Module 2 draft completed

- Checkpoint 6 completed `write_module:m2`; revision advanced to 7 while the
  job remained `drafting`.
- The module is "Data Structures, Exceptions, and Robust Programs" with three
  sections and nine content blocks.
- Coverage includes nested data structures, exception handling and diagnosis,
  and an applied data-processing pipeline.
- Three model-generated code blocks are present, one per section.
- All six citations are marked supported, and no unresolved or conflicting
  claims are recorded.
- Budget after this stage: 4 model turns, 163,834 input tokens, 8,065 output
  tokens, no retries or repairs, and about 290.3 seconds elapsed.
- Quality concern to watch: the module records no explicit misconceptions even
  though exception handling and error diagnosis commonly benefit from them.

### 2026-07-21 01:11:00 IDT - Module 3 draft completed

- Checkpoint 7 completed `write_module:m3`; revision advanced to 8 while the
  job remained `drafting`.
- The module is "Iteration, Object-Oriented Programming, and Modules" with
  three sections and nine content blocks.
- Coverage includes iterables, iterators, generators, classes, inheritance,
  imports, entry points, and virtual environments.
- All nine citations are marked supported, and no unresolved or conflicting
  claims are recorded.
- The module includes three misconception notes, including mutable loop state,
  zero-based indexing, and the nonstandard nature of proficiency labels.
- Budget after this stage: 5 model turns, 234,371 input tokens, 10,961 output
  tokens, no retries or repairs, and about 399.9 seconds elapsed.
- Quality concern: no code block or model-generated example appears in this
  module. Iterators, generators, classes, and module organization are presented
  only through prose and one callout, which weakens applied learning.

### 2026-07-21 01:16:44 IDT - Active runtime diagnostics

- Module 4 had not yet committed, but the Codex process remained alive, its CPU
  time continued to advance, and its internal log database was receiving new
  writes. This indicates a long active turn rather than a dead worker.
- By 01:20:17 IDT, model-stream trace events were still arriving continuously.
  The stage was materially slower than modules 1 through 3 but remained active.
- Each model turn emits a warning that model-specific messages for the requested
  `pragmatic` personality are missing; the runtime falls back to base
  instructions. This warning was not the terminal failure signal.
- Before this job was submitted, Codex emitted error-level messages because
  system `bubblewrap` was absent. Those same messages state that the bundled
  `bubblewrap` is used instead. The fallback is operational, but the error
  severity can create misleading noise during incident review.

### 2026-07-21 01:23:53 IDT - Module 4 draft completed

- Checkpoint 8 completed `write_module:m4`; the checkpoint advanced the job to
  revision 9 while it remained `drafting`.
- The module is "Integrated Application and Proficiency Assessment" with three
  sections and nine content blocks.
- Coverage includes an integrated interactive coding exercise, structured
  debugging feedback, and a 15-item diagnostic/remediation section.
- The module contains one code block, one example block, three additional
  structured example records, five citations marked supported, and one
  disclosed unresolved claim about the lack of a universal intermediate
  proficiency definition.
- Budget after this stage: 7 turns, 304,857 input tokens, 14,712 output tokens,
  1 retry, no repairs, and about 1,118.6 seconds of budgeted elapsed time.

### 2026-07-21 01:23:53 IDT - Terminal generation failure

- About 0.13 seconds after checkpoint 8, the job moved to `failed` at revision
  10 with failure code `generation_failed`.
- The failure occurred before the `verify_course` checkpoint. No review pack,
  standalone assessment, answer key, rendered artifact, manifest, or delivery
  record was created.
- Worker logs emitted `txt2crs.execution_failed` and
  `txt2crs.worker_failed`, both with the bounded reason `execution_failed`.
- Read-only deterministic replay against checkpoint 8 isolated the exact
  boundary: course assembly passed, course-to-plan matching passed, and course
  quality validation failed.
- The first rejected invariant was citation `cit-m1s1-b2`: its stored SHA-256
  did not match the exact `claim_text`.
- A complete hash audit found 15 mismatches among 26 citations:
  module 1 had 5 of 6, module 2 had 0 of 6, module 3 had 6 of 9, and module 4
  had 4 of 5.
- Module-level checkpoint validation verified citation locations and evidence
  references but did not recompute claim hashes. As a result, invalid hashes
  were allowed into durable module checkpoints and detected only after all four
  costly module turns completed.
- A second in-memory replay with all claim hashes recomputed exposed another
  latent failure: `citation-m2-004` lacks independent text support. Its claim
  groups exception handling with logging, testing, and external-service
  mocking, but its only evidence is a secondary Reddit excerpt that does not
  meet the deterministic overlap threshold.
- Total wall-clock time from submission to failure was about 20 minutes and 5
  seconds.

### 2026-07-21 01:24:58 IDT - Platform recovered to ready

- The post-failure readiness probe completed successfully with status `ready`.
- The backend container remained healthy. This was a job-specific content
  validation failure, not a worker-process or application outage.

## Final findings

- Input preparation, research planning, evidence collection, course planning,
  and all four module drafts completed and are durable.
- The job failed correctly at the aggregate course-quality gate because citation
  integrity was invalid. It did not publish an unverified course.
- The principal engineering weakness is validation timing: claim hashes should
  be host-computed from accepted claim text or verified inside each module's
  validator before the module checkpoint is committed.
- Repair should occur while the failing module is still in scope. Detecting the
  problem only after all modules caused avoidable token use and roughly 20
  minutes of latency.
- Correcting hashes alone is insufficient because at least one citation also
  fails the independent text-support gate.
- Research-plan stop criteria were not enforced: the source set exhausted its
  12-source cap without the required official, authoritative, and pedagogy or
  assessment coverage.
- The course plan's five duplicated learning-objective descriptions were not
  the terminal cause, but they remain a significant curriculum-quality issue.
- Module 3 lacks applied code examples, and module 2 lacks explicit
  misconception entries. These are content-quality concerns independent of the
  terminal citation failure.
- The single model retry and personality fallback warning did not directly
  cause the failure. The bundled `bubblewrap` fallback also remained
  operational.

## Final outcome

Failed with `generation_failed` after all module drafts but before aggregate
course verification. No learner-facing course bundle, review pack, test, answer
key, or downloadable artifact was delivered.

## Suggested follow-up

1. Compute or verify every citation `claim_hash` inside the module acceptance
   boundary, before checkpointing.
2. Run the same independent text-support check per module so repair can target
   the failing claim immediately.
3. Enforce research-plan authority and source-type requirements before freezing
   evidence; do not treat reaching the source cap as sufficient completion.
4. Add semantic source deduplication for mirrored articles and review whether
   Reddit should be labeled `reputable_secondary`.
5. Require distinct, measurable learning-objective descriptions and minimum
   applied-example coverage for coding-heavy modules.

## Remediation progress

- Current remediation state: Complete

### 2026-07-21 - Audit and implementation session started

- Worktree baseline: clean at commit `62e56dd` before remediation edits.
- Workflow: autonomous backend remediation using this document as the durable
  work file. The completed spec-system sessions remain read-only.
- Confirmed primary defect in code: `_validate_module_draft()` checks citation
  locations and evidence references but does not call the deterministic
  citation acceptance gates. `validate_course_quality()` calls those gates only
  after every module has been generated and assembled.
- Confirmed the fix must cover all recorded findings, not merely rewrite
  `claim_hash`: early hash and independent-support validation, research-plan
  source requirements and semantic duplicates, objective distinctness and
  measurability, applied coding examples, misconception coverage, and
  actionable runtime warning/error noise.
- At this point, test-first implementation and verification were in progress;
  no production behavior had been changed yet.

| Finding | Current remediation state | Required proof |
|---|---|---|
| Citation hashes accepted until aggregate validation | Fixed; targeted test passed | Host code recomputes every claim hash before the module checkpoint without spending a repair turn |
| Independently unsupported citation accepted until aggregate validation | Fixed; targeted test passed | The module gate runs deterministic citation acceptance and spends one bounded repair before checkpointing |
| Research authority and pedagogy requirements ignored at source cap | Fixed; live proof passed | Structured plan floors, required pedagogy question, balanced question allocation, and frozen-set gates pass integration and live tests |
| Semantically duplicate source URLs accepted | Fixed; integration test passed | Canonical URL and near-mirror text deduplication run before evidence ranking |
| Reddit classified as `reputable_secondary` | Fixed; integration test passed | Reddit and reviewed discussion platforms are classified as `community` with a one-source cap |
| Duplicate broad learning objectives accepted | Fixed; targeted tests passed | Course-plan validation rejects normalized duplicates and broad non-observable proficiency labels during plan repair |
| Coding-heavy module without applied code example | Fixed; targeted test passed | Module-stage validation requires at least one applied example before checkpointing |
| Module without explicit misconceptions | Fixed; targeted test passed | Module-stage validation requires misconception guidance before checkpointing |
| Missing `pragmatic` personality messages warning | Fixed; focused live log proof passed | Stage policy uses developer instructions so Codex retains model metadata; a live research turn recorded zero warnings or errors |
| Missing system `bubblewrap` logged as an error despite working fallback | Fixed; production image verified | Production image contains `/usr/bin/bwrap` 0.11.0 under UID 1001 |

The next implementation step at this point was to inspect the exact module validator, stage-repair
mechanism, research coordinator, source policy, and plan-quality validators;
then add the smallest comprehensive set of failing regression tests before
changing production code.

### 2026-07-21 - Early module and curriculum gates implemented

- Added regression coverage proving invalid model-supplied SHA-256 values are
  replaced with hashes computed from the exact accepted claim text by host
  code. This canonicalization does not consume the one allowed repair turn.
- Added module-stage independent text-support validation. An unrelated claim
  now receives safe rejection code `module_citation_quality_rejected`, is
  repaired while that module remains in scope, and only the repaired draft is
  checkpointed.
- Added module-stage requirements for an applied example and explicit
  misconception guidance, each with a stable local repair code.
- Added course-plan rejection for normalized duplicate objective descriptions
  and vague English proficiency labels without an observable action verb.
- Changed goal alignment so a broad learner goal can map by stable topic words
  to several distinct measurable objectives instead of forcing verbatim copies.
- Changed the course-design prompt to request distinct measurable objectives
  and the module prompt to disclose the host-owned hash and local pedagogy gates.
- Targeted verification passed: four pipeline regressions and three learning
  preference regressions. Full engine quality gates have not run yet.

The next implementation step at this point was to make research requirements structured and locally
enforceable, prefer official/authoritative and education-research sources,
classify community sources honestly, and deduplicate canonical and near-mirror
documents before the evidence set is frozen.

### 2026-07-21 - Research, compatibility, and runtime remediation

- Added structured `minimum_authoritative_sources` and
  `minimum_education_sources` to the durable research plan. Local plan
  acceptance calculates non-optional floors from the selected source cap and
  requires a real pedagogy, learning-science, or assessment question whenever
  the education floor is positive.
- Search requests now include preferred source types and only include a
  configured authoritative domain when its meaningful domain label appears in
  the question or requested source types. This prevents the Python default
  domain from polluting unrelated research.
- Source slots are balanced across all research questions. For the failed
  job's shape, six questions receive two slots each instead of the first
  question consuming ten of twelve and starving later pedagogy questions.
- Failed extracts no longer consume accepted-source capacity. Separate tool
  budgets still bound every provider call.
- Added canonical URL normalization, tracking-parameter removal, and exact or
  high-overlap text deduplication before evidence ranking.
- Community platforms including Reddit are labeled `community`, never
  `reputable_secondary`, and at most one community source can enter a set.
- Government, configured official, standards, and academic domains receive
  explicit authority classifications. Frozen evidence is rejected unless it
  satisfies the accepted research plan's authority and education floors.
- Education-source classification is derived from immutable source titles and
  excerpts. It is not stored in `EvidenceCandidate`; this preserves historical
  evidence hashes and checkpoint compatibility.
- Explicitly disabled interactive Codex personality selection for schema-only
  generation turns. Trusted stage policy now uses the supported developer
  instruction channel instead of replacing model base instructions; replacing
  them caused Codex to discard personality metadata and emit a false fallback
  warning even for `Personality.none`.
- Installed Debian `bubblewrap` in the shared backend image base. A clean
  production build completed, and the resulting non-root image reported UID
  1001, `/usr/bin/bwrap`, and `bubblewrap 0.11.0`.
- Full engine verification after the final research tightening: 507 passed, 2
  live tests skipped;
  `ruff check`, `ruff format --check`, and strict `mypy` passed. All 16 static
  backend container-contract tests passed.
- Read-only replay against the actual revision-8 checkpoint now preserves its
  evidence hash and shows the intended early outcomes: the all-secondary
  evidence set fails the new authority gate; module 1 passes; module 2 fails
  misconception coverage and independent support for `citation-m2-004`;
  module 3 fails applied-example coverage; module 4 passes.

### 2026-07-21 - First remediated live course completed

- A fresh compact researched-course acceptance job,
  `job-162f4ac895c24f6382a5a956f5e24649`, completed with no failure code.
- End-to-end generation took 317 seconds and the acceptance test completed in
  318.69 seconds. The job committed eight checkpoints and delivered all 16
  required artifacts, including course, review, assessment, answer key,
  rendered outputs, manifest, and delivery records.
- The live research plan required one authoritative and one education source.
  Its frozen set contained five sources, including two authoritative sources,
  and passed the new immutable research-requirement gate.
- A post-run Codex log audit found no error-level records, but found five
  warning-level personality fallbacks. This disproved the first attempt to
  silence that warning by setting `Personality.none` while still replacing
  model base instructions, so remediation remained open.
- A test-first correction moved trusted stage policy to
  `developer_instructions`, preserving the model metadata Codex needs for the
  explicit no-personality selection. It also selects file-backed MCP OAuth
  state directly in headless workers instead of warning before keyring
  fallback.
- A focused live research-tool turn passed in 17.46 seconds after that
  correction. Its new Codex log interval contained 657 records with zero
  `WARN` and zero `ERROR` records.

At this point, the remaining verification was one final fresh full-course run
on the exact final worker configuration, its isolated log audit, the changelog,
and the requirement-by-requirement handoff audit completed below.

### 2026-07-21 - Final remediation verification completed

- Final live job `job-7c0858634c414ce4a4a7e63c0b395884` completed on the
  exact final worker configuration with no failure code, eight checkpoints,
  and all 16 required artifacts.
- Generation took 253 seconds; the acceptance test passed in 254.54 seconds.
  This compact-course proof is well below the configured 2,700-second hard
  ceiling. Normal multi-module courses should be planned around 5 to 15
  minutes, with deeper courses around 15 to 30 minutes; the 45-minute limit is
  a safety ceiling, not an expected duration.
- The final run's isolated Codex log interval contained 1,272 records: 1,172
  trace, 62 debug, and 38 info. It contained zero warnings, zero errors, zero
  personality fallbacks, and zero `bubblewrap` fallbacks.
- Final engine verification passed with 507 tests and two explicitly gated
  live tests skipped in the default suite. The separately enabled live
  research-tool and full-course tests both passed.
- Ruff lint, Ruff format checking, and strict mypy passed across all 138 engine
  files. All 16 static backend container-contract tests had already passed.
- A final production image was built from the remediated source. Its non-root
  smoke proof reported UID 1001, `txt2crs` 1.1.1, `/usr/bin/bwrap`, the trusted
  developer-instruction fix, and the file-backed MCP OAuth fix.
- The actual failed revision-8 checkpoint remains readable and hash-compatible.
  Replaying it against the new gates rejects its all-secondary evidence before
  drafting and identifies the recorded module 2 citation/misconception and
  module 3 applied-example defects at their local module boundaries.
- `docs/CHANGELOG.md` records the complete remediation in release 1.1.1. No
  existing TODO item represented this incident, so no TODO entry was moved.

Remediation outcome: complete. The late aggregate failure path, recorded source
quality defects, curriculum defects, and actionable runtime warning/error noise
all have test-first fixes and final live evidence.
