# Codex Feedback Reference

**Primary Session ID**: `019f7990-e049-7242-9d36-dc1eb4462d69`

## Why This Session

This is the active primary Codex project session for the end-to-end txt2crs
build goal. Local Codex session metadata identifies the same UUID as the
active thread and binds it to this repository. The filename identity and
metadata identity agree.

The session carried the specification-driven work through the final hardening
and submission phase while retaining the earlier architectural and product
context. It is the best single feedback reference for how Codex helped turn
the imported application shell and reusable education engine into one
validated learner journey.

The event form receives this one bounded identifier. The repository does not
copy the conversation transcript, hidden reasoning, account state, tool
credentials, or private provider data.

## How Codex Accelerated Development

Codex helped with:

- turning the product plan into dependency-ordered 2-4 hour specifications
  with explicit success criteria and tests;
- preserving the public engine boundary while composing durable FastAPI jobs,
  owner-scoped reads, restart recovery, and account erasure;
- building the React learner journey from public discovery through bounded
  intake, refresh-safe progress, four results, private downloads, and inert
  preview;
- correcting exact model policy to the reviewed `gpt-5.6-sol`,
  `gpt-5.6-terra`, and `gpt-5.6-luna` identifiers without accepting bare
  family text as a selection;
- writing tests before implementation and repairing code-review findings
  before validation;
- reproducing engine, backend, frontend, browser, security, distribution,
  production-image, and container-replacement gates; and
- keeping the historical live proof, reviewed candidate, and intended final
  judge-asset commit and tag truthfully separate.

Codex was used as a development collaborator. The shipped product's runtime
course generation is a separate package-owned capability that authenticates a
dedicated ChatGPT subscription, discovers an exact GPT-5.6 model, performs
bounded Tavily research, and validates its outputs before deterministic
rendering.

## Key Decisions Made With Codex

1. Keep generation, research, validation, persistence, policy, and rendering
   inside the reusable `txt2crs` package.
2. Accept a job only after the exact request and admission reservation are
   durable.
3. Expose constructed public allowlists rather than filtering private models
   after serialization.
4. Run one non-root backend process and one serial worker until a real queue
   can own concurrent execution.
5. Fail readiness and execution closed when the exact reviewed model or
   research dependency is unavailable.
6. Keep local Docker Compose as the complete release target instead of
   implying an unapproved hosted deployment.
7. Use synthetic evidence because formal public personal-data policy and
   provider-transfer records are incomplete.
8. Tag only the exact commit containing all tracked judge assets.

## Feedback Boundary

The Session ID is a routing reference required by OpenAI Build Week. It is not
an authentication secret, but it is still kept to the single identifier the
event requests. No transcript excerpts or account-private fields are included
in the submission package.
