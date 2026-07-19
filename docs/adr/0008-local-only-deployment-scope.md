# ADR-0008: Local-Only Deployment Scope

## Status

Accepted; supersedes ADR-0007

## Date

2026-07-19

## Context

txt2crs is a deadline-bound OpenAI and Devpost Education Hackathon project.
Its required delivery target is a reproducible application running on the
developer or judge's machine. The repository inherited hosted deployment
automation and a Coolify decision from the donor shell, but neither reflects
the project owner's intended scope.

Hosted infrastructure would add credentials, domains, platform operations,
remote state, and release paths that are not required to prove the product.
Assuming one platform now would also constrain a future production decision
before its requirements are known.

## Decision

Repository-root Docker Compose is the only deployment target in the current
project scope.

- `docker compose up --detach --build --wait` is the release and judge
  execution path.
- Backend, frontend, PostgreSQL, and private engine state are validated as one
  local topology.
- GitHub Actions may validate code but does not deploy an environment.
- The repository carries no active hosted deployment workflow, hosted
  platform script, or platform-specific environment variables.
- `local`, `staging`, and `production` remain application configuration
  profiles; they do not imply that a hosted environment exists.
- Selecting any future hosted production platform requires new requirements,
  a new ADR, and explicit owner approval. Coolify is not the default or
  preferred assumption.

## Consequences

### Positive

- Product effort stays on the learner workflow and submission proof.
- One documented topology is testable without external infrastructure.
- Secrets and state remain within operator-controlled local boundaries.
- Future hosting remains an open decision rather than inherited policy.

### Negative

- There is no public URL, remote rollout, hosted rollback, or managed scaling
  in the current scope.
- Judges or reviewers must run the documented local Docker stack.
- Local backup and recovery procedures remain the operator's responsibility.

### Constraints

- Preserve exactly one backend process and one serial engine worker while the
  SQLite job topology remains.
- Do not add a hosted deployment file as a convenience or fallback.
- Do not describe production hosting as planned unless the project owner
  explicitly expands the scope.

## Verification

The static backend container contract rejects active hosted deployment
workflows, the removed Coolify script, and Coolify variables in
`.env.example`. Local image and Compose health checks remain required.

## References

- [Deployment policy](../deployment-policy.md)
- [Local deployment](../deployment.md)
- [System plan](../ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md)
