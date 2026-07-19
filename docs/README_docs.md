# txt2crs Documentation

This directory contains product, engineering, operations, and planning
documentation for the txt2crs application. Package-specific engine documents
live under `backend/packages/txt2crs/docs/`.

## Start Here

- [Architecture](ARCHITECTURE.md) explains the FastAPI shell, reusable engine,
  React client, databases, and deployment boundaries.
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

- [Input-to-course system plan](ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md)
  is the phased end-to-end build plan.
- [TODO](ongoing-projects/TODO.md) contains prioritized current work.
- [Changelog](CHANGELOG.md) records completed user-visible and engineering
  changes.
- [Versioning](VERSIONING.md) defines release and version synchronization
  rules.
- [ADR index](adr/README_adr.md) records accepted architectural decisions.
- [File organization](FILE_ORGANIZATION.md) maps repository ownership.
- [Folder architecture](TXT2CRS_FOLDER_ARCHITECTURE.md) explains the
  library-first workspace and dependency rules.

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
