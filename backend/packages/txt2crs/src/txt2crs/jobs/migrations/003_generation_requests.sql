-- SPDX-License-Identifier: MIT-0
-- Exact immutable request envelopes required to execute accepted jobs.

CREATE TABLE IF NOT EXISTS generation_requests (
    job_id TEXT PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    request_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS generation_requests_owner_job_idx
ON generation_requests(user_id, job_id);
