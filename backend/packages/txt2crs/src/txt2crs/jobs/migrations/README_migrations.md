# txt2crs Job Migrations

Migration files are immutable, ordered SQL resources applied by
`SqliteJobStore`. `001_jobs.sql` creates tenant-owned jobs, accepted
checkpoints, and the idempotent delivery outbox. `002_job_admissions.sql` adds
atomic per-user/global rolling reservations for job count, model tokens, and
paid research allowance. Add a new numbered migration for future schema
changes; never rewrite an already released migration.
