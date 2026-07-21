# txt2crs Job Migrations

Migration files are immutable, ordered SQL resources applied by
`SqliteJobStore`. `001_jobs.sql` creates tenant-owned jobs, accepted
checkpoints, and the idempotent delivery outbox. `002_job_admissions.sql` adds
atomic per-user/global rolling reservations for job count, model tokens, and
paid research allowance. `003_generation_requests.sql` adds one exact,
versioned generation-request envelope for every newly accepted job so a
replacement worker never reconstructs input or execution defaults. Add a new
numbered migration for future schema changes; never rewrite an already
released migration.

`004_delivery_notifications.sql` makes disabled notification decisions
explicit. `005_runtime_activity.sql` adds a content-free worker heartbeat
timestamp without changing a job's durable checkpoint revision or update time.
