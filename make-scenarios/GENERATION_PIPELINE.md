# Generation Pipeline

The legacy workflow makes four generative-model calls in Scenario 3. This
document captures their exact responsibilities and the quality behavior implied
by their prompts, then distinguishes requested behavior from behavior the
automation actually verifies.

## Model-call summary

| Order | Module | Provider/model | Parameters | Input | Expected output |
|---:|---|---|---|---|---|
| 1 | `35` — Create Course | Anthropic `claude-sonnet-4-5-20250929` | `max_tokens: 64000`, `temperature: 1` | Onboarding `Last Text Input` | Complete course text |
| 2 | `11` — File Naming | OpenAI `gpt-5-mini` | `temperature: 1.3`, `top_p: 1`, low reasoning | Full course text | Parsed JSON object with `file_name` |
| 3 | `31` — Create HTML | OpenAI `gpt-5` | `temperature: 1`, `top_p: 1`, low reasoning | Full course text | Standalone print-oriented HTML |
| 4 | `33` — Create Quiz Questions | Anthropic `claude-sonnet-4-5-20250929` | `max_tokens: 64000`, `temperature: 1` | Full course text | Plain-text quiz followed by answer key |

The model IDs describe the exported snapshot, not a requirement for the new
application. The current hackathon project should use its approved
OpenAI/Codex runtime and required submission model rather than preserve a
multi-provider dependency for historical parity.

Scenario 3 also defines a roundtrip variable named `MAX_TOKENS` with value
`64000`, but neither Claude module references it. Each module repeats the
number directly in its own mapper, so changing the variable alone would not
change either output limit.

## Instruction placement

The course and quiz directives are sent in messages with the `assistant` role,
not a provider-level `system` role. The learner input follows in a `user`
message with a decorative delimiter. The HTML directive is also an assistant
message.

The blueprints contain no explicit:

- prompt-injection warning or untrusted-content boundary;
- instruction priority statement;
- XML/JSON delimiter contract around source text;
- source length/token preflight;
- schema for course, HTML, or quiz content;
- content safety or high-risk-domain policy.

The file-name call is the only schema-like response: OpenAI JSON mode plus
Make’s parsed response option.

## Course-generation specification

The course prompt is stored at JSON path
`.flow[2].mapper.variables[0].value` in the
[Part 3 blueprint](<[STUDY] Create Course Material from Plain Text (3-3).blueprint.json>).

### Objective

Transform either a “video transcript” or a “course request” into a
comprehensive curriculum that is:

- assigned a beginner, intermediate, or advanced level;
- comprehensive relative to the supplied source;
- enhanced with examples, definitions, and practical insight;
- ordered for a sensible learning progression.

Although the prompt mentions video transcripts, the workflow passes only the
plain text stored in Airtable. Transcript retrieval or media processing is
outside the automation.

### Source analysis

For transcript-like input, the model is asked to:

1. analyze the entire transcript;
2. identify the main topic and subtopics;
3. extract explicit and implicit learning objectives;
4. identify terminology needing definitions;
5. infer speaker expertise and audience.

For request-like input, it is asked to:

1. identify stated learning goals;
2. identify requested subtopics/skills;
3. infer current learner knowledge when possible;
4. identify practical applications;
5. notice time or format preferences.

There is no classifier that decides which branch applies, and no stored
analysis artifact. The model silently performs the interpretation inside one
generation call.

### Level rubric

| Level | Prompt expectations |
|---|---|
| Beginner | No prior knowledge; fundamentals; everyday analogies; defined jargon; step-by-step processes |
| Intermediate | Foundational knowledge assumed; specialized terms; concept relationships; theory; nuanced applications |
| Advanced | Strong prior knowledge; complex theory; specialized/cutting-edge use; edge cases; cross-field connections |

The inferred level must be stated in the course. The learner cannot explicitly
confirm or override it in the exported form mapping.

### Required course structure

The generated document is asked to contain:

- an engaging title;
- prominent complexity level;
- learning objectives;
- source context;
- prerequisites;
- 3–7 logical sections in sequential order;
- descriptive headings and consistent H1/H2/H3 hierarchy;
- transition statements;
- subheadings where needed;
- a Quick Reference summary;
- further resources.

For each key concept, the model should provide:

- a definition/explanation;
- at least one practical example;
- a text description of a useful visual when appropriate;
- a connection to previous concepts;
- common misconceptions.

Enhancement labels include:

- `[Expert Insight]`;
- `[Practical Application]`;
- `[Resource]`;
- `[Quick Reference]`.

Currency labels include:

- `[Dated: YYYY]` for outdated source information;
- `[Updated: YYYY]` for current information;
- `[Emerging]` for likely future change.

### Writing and learning-design standards

The prompt further asks the model to:

- use clear, precise, level-appropriate language;
- define every technical term on first use;
- use analogies for abstract concepts;
- break complex processes into sequential steps;
- use active voice and address the learner directly;
- build each concept on earlier concepts and explicitly connect them;
- avoid circular explanations and logical gaps;
- signpost key learning moments;
- summarize complex sections;
- provide worked examples for theoretical concepts;
- use scenarios to demonstrate real-world relevance;
- suggest exercises or thought experiments;
- include troubleshooting guidance where appropriate;
- connect theory to practical skills.

These are distinct pedagogical requirements even though the prompt places all
of them inside one unconstrained course-writing turn.

### Quality checklist embedded in the prompt

The model is told to self-check:

- completeness;
- accuracy;
- logical structure;
- level-appropriate readability;
- one example for every key concept;
- enhancement elements;
- scannable navigation;
- currency labeling.

It is also told to output only course material and no meta-commentary.

### Important distinction

Every item above is a prompt request, not an enforced invariant. No module:

- verifies source coverage;
- checks a claim against current information;
- confirms examples for every concept;
- counts sections;
- validates heading hierarchy;
- checks resource URLs;
- detects missing misconceptions;
- rejects meta-commentary.

The course prompt asks for “current and factually correct” material but gives
the model no search tool, retrieved sources, or date context. Its resource and
updated-information sections can therefore be unsupported model knowledge.

## File-name generation

The full course is sent to `gpt-5-mini` with one job: return a descriptive,
properly capitalized name without an extension, dashes, or underscores.

Required shape:

```json
{
  "file_name": "Introduction to HTML for Web Scraping"
}
```

Make enables JSON response mode and parsed JSON output. It does not enforce a
maximum filename length, forbidden filesystem characters, empty strings,
reserved names, or a deterministic normalization policy.

The call uses the highest temperature of the four (`1.3`) even though naming
is a deterministic utility task. Both file-name and HTML calls have an
automatic retry handler configured for count `5`, interval `3`.

## HTML-generation specification

The HTML prompt is stored at
`.flow[2].mapper.variables[2].value` in the Part 3 blueprint.

It instructs the model to reproduce the full course as:

- pure output beginning with `<!DOCTYPE html>` and ending with `</html>`;
- a complete `<html>`, `<head>`, and `<body>`;
- UTF-8 metadata;
- a self-contained `<style>` block and no external dependencies;
- print-safe fonts, at least 11pt, with 1.5 line height;
- clear heading hierarchy and section spacing;
- optional definition boxes, footnotes, sidebars, and margin notes;
- no buttons, forms, scripts, or interactive behavior;
- print-protected images, captions, and figure numbers;
- a document intended for later PDF conversion.

The prompt also asks for 300-DPI-equivalent images, CMYK-friendly colors,
vector graphics, embedded fonts, and a CMYK color mode. Plain HTML/CSS and a
text-only model cannot guarantee several of those print-production properties.
It also alternates between asking for “all inline CSS” and asking for one
`<style>` block; those are different CSS placement strategies.

### HTML quality boundary

The model response is sent directly to the PDF service and stored in Airtable.
There is no configured parser, sanitizer, allowlist, completeness comparison,
HTML validator, CSS validator, or active-content rejection. “No scripts” is
only an instruction.

Using a model to transform the course creates a second generative copy of the
same artifact. It can omit, paraphrase, or add content. The new application
should render the canonical structured course deterministically, which the
current Python library already does.

## PDF conversion

The HTML response is sent to the 0-CodeKit/OneSAAS `pdfhtml` module with:

- source type `html`;
- margins set to `50` on all four sides;
- URL output enabled.

The returned URL is downloaded over HTTP and the bytes are uploaded to Drive.
The same service URL is also stored in Airtable and used as an Airtable
attachment source. The export does not state URL expiry, data retention,
rendering engine/version, page size, margin units, font availability, or
access control.

## Quiz-and-answer-key specification

The quiz prompt is embedded directly in Scenario 3 module `33`.

### Required assessment behavior

- Generate 5–10 short-answer questions.
- Cover all major course sections and learning objectives.
- Weight complex/emphasized topics more heavily.
- Match the course’s inferred difficulty.
- Use definition, application, analysis, integration, and critical-thinking
  questions.
- Begin with action verbs such as Define, Explain, Compare, Apply, or Analyze.
- Prefer understanding and application over simple memorization.
- State an expected answer length where that would clarify scope.
- Keep each question focused and answerable from the course.
- Avoid ambiguous wording or multiple plausible interpretations.
- Mark essential questions `[KEY]`.
- Limit `[KEY]` questions to 30–40 percent.
- Provide concise 1–3 sentence answers.
- Keep question and answer numbering/order aligned.

The required logical output is:

```text
SHORT ANSWER QUESTIONS:

1. ...

ANSWER KEY:

1. ...
```

The prompt says “plain text only” and “no special characters,” while its own
example uses `[KEY]` and Markdown-style fenced formatting. No parser verifies
the two sections, count, key percentage, answer alignment, or source support.

### Pedagogical and access limitations

The output is a single Google Doc shared with the learner. Therefore:

- answers are visible alongside questions;
- there is no student/instructor access boundary;
- there are no points, rubrics, acceptable-answer variants, or grading rules;
- there is no separate assessment blueprint;
- questions have no durable objective/section/source IDs;
- the assessment cannot be validated mechanically against the course.

The legacy “quiz” is useful inspiration, but it does not satisfy the current
requirement for a full test with a separate answer sheet.

## Quality claims versus enforcement

| Desired property | Prompt requests it? | Deterministically checked? | Legacy evidence |
|---|---:|---:|---|
| Correct level | Yes | No | Course prompt rubric |
| Complete source coverage | Yes | No | Course self-check only |
| Current facts | Yes | No | No research/tool call |
| Examples for key concepts | Yes | No | Course self-check only |
| Misconceptions | Yes | No | Prompt directive |
| Valid standalone HTML | Yes | No | Raw model text sent to PDF |
| No active HTML | Yes | No | Prompt directive only |
| Course text preserved in HTML | Yes | No | Second generative transform |
| 5–10 quiz questions | Yes | No | Plain-text response |
| Balanced objective coverage | Yes | No | No objective IDs/blueprint |
| Answer alignment | Yes | No | No parser |
| Separate answer sheet | No | No | One combined document |
| Source citations | No | No | No evidence layer |

## Cost, latency, and data-flow implications

For one successful course, the workflow makes four serial model calls. Three
of them receive the full course text. The pipeline then performs PDF
conversion, PDF download, PDF upload, Google Doc creation, two permission
changes, an Airtable write, and an email.

Consequences:

- latency grows with full course length at every downstream model call;
- the same learner-derived content crosses four vendor boundaries
  (Anthropic, OpenAI, PDF service, Google) plus Make/Airtable;
- a 64,000-token maximum is configured for each Claude call without a visible
  per-user/global reservation or cost gate;
- retries protect only the two OpenAI transformations;
- a late failure wastes all preceding model and rendering work;
- replay can regenerate different content because temperatures are non-zero
  and no accepted artifact checkpoint is reused.

## Features hidden inside the prompts

The prompts contain product ideas that are easy to miss if only the delivered
files are considered:

- automatic source-type interpretation;
- audience and expertise inference;
- learner-level adaptation;
- prerequisites and measurable objectives;
- concept definitions, examples, connections, and misconceptions;
- practical applications and expert insights;
- currency/dated-information signaling;
- quick-reference summaries and further resources;
- assessment difficulty/coverage planning;
- key-question designation.

These should be evaluated as pedagogical requirements, not copied as one giant
prompt. The current library’s versioned plans, structured artifacts, evidence,
and validation gates are the appropriate place to implement them.

## Recommended migration principles

1. Store learner input as untrusted, immutable job data.
2. Research before drafting and freeze the accepted evidence set.
3. Generate and approve a course plan before module writing.
4. Write bounded modules and checkpoint each accepted result.
5. Represent objectives, sections, evidence, questions, and answers with
   stable IDs.
6. Derive review and assessment artifacts only from the accepted course.
7. Render every format deterministically from canonical structured data.
8. Keep the student test and instructor key separate.
9. Validate quality claims with code where possible and expose unresolved
   uncertainty where it is not.
10. Treat naming, HTML, PDF, storage, and notification as deterministic
    application responsibilities rather than creative model tasks.
