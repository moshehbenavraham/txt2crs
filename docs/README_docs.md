# txt2crs Documentation

This directory contains product, engineering, operations, and planning
documentation for the txt2crs application. Package-specific engine documents
live under `backend/packages/txt2crs/docs/`.

## Start Here

- [Architecture](ARCHITECTURE.md) explains the FastAPI shell, reusable engine,
  React client, databases, and deployment boundaries.
- [Deliverable system](DELIVERABLE_SYSTEM.md) traces the complete publication
  lifecycle from validated education models through rendering, private storage,
  integrity verification, preview, and download. It also defines the shared
  publication design system and format-specific quality contract for HTML,
  Markdown, PDF, and DOCX.
- [Onboarding](onboarding.md) provides the shortest verified local setup.
- [Development](development.md) lists local endpoints, commands, and validation.
- [Configuration](CONFIGURATION.md) catalogs environment variables and
  validation rules.
- [Environment behavior](environments.md) describes source-backed differences
  between local, staging, and production.
- [API](api/README_api.md) documents the currently exposed HTTP contract.
- [Deployment](deployment.md) and
  [deployment policy](deployment-policy.md) define supported release paths.
- [Incident response](runbooks/incident-response.md) is the operational
  response runbook.
- [Security](SECURITY.md) states the reporting policy and known gaps.

## Planning and Project History

- [Product requirements](../.spec_system/PRD/PRD.md) contain the completed
  phased build plan and current durable requirements.
- [Course generation logging plan](ongoing-projects/COURSE_GENERATION_LOGGING_PLAN.md)
  defines the proposed test-first work needed for safe, correlated, high-quality
  generation diagnostics.
- [PostgreSQL artifact storage plan](ongoing-projects/POSTGRES_ARTIFACT_STORAGE_PLAN.md)
  defines the future decision gates, schema direction, migration phases,
  recovery semantics, and rollback requirements for storing rendered files in
  PostgreSQL.
- [Apex considerations](../.spec_system/CONSIDERATIONS.md) retain active
  architecture constraints and institutional memory.
- [Changelog](CHANGELOG.md) records completed user-visible and engineering
  changes.
- [Versioning](VERSIONING.md) defines release and version synchronization
  rules.
- [Port allocations](PORTS.md) lists every host-bound and container-internal
  listener used by local, test, and optional proxy workflows.
- [ADR index](adr/README_adr.md) records accepted architectural decisions.
- [File organization](FILE_ORGANIZATION.md) maps repository ownership.
- [Folder architecture](TXT2CRS_FOLDER_ARCHITECTURE.md) explains the
  library-first workspace and dependency rules.
- [Archive](archive/README_archive.md) preserves retired changelogs and the
  non-authoritative Build Week submission record.

## Engine Research and Design

- [AI usage needs](../backend/packages/txt2crs/docs/AI_USAGE_NEEDS.md)
- [Hermes reuse evaluation](../backend/packages/txt2crs/docs/HERMES_MINIMUM_CODE_PULL_EVALUATION.md)
- [AIOS runtime findings](../backend/packages/txt2crs/docs/AIOS_RUNTIME_SUPPLEMENT.md)
- [Engine implementation compliance](../backend/packages/txt2crs/docs/IMPLEMENTATION_COMPLIANCE.md)

## Documentation Rules

`README.md` is reserved for the repository root. Directory indexes use a
descriptive filename such as `README_docs.md` or `README_api.md`. Update
documentation in the same change that alters a public interface, command,
environment variable, runtime boundary, or operational procedure.
