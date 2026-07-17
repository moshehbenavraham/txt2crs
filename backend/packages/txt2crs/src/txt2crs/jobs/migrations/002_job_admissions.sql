-- SPDX-License-Identifier: MIT-0
-- Atomic per-user/global rolling reservations for AI and research resources.

CREATE TABLE IF NOT EXISTS job_admissions (
    job_id TEXT PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    reserved_tokens INTEGER NOT NULL CHECK(reserved_tokens > 0),
    reserved_research_cost_microusd INTEGER NOT NULL
        CHECK(reserved_research_cost_microusd >= 0),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS job_admissions_window_idx
ON job_admissions(created_at);

CREATE INDEX IF NOT EXISTS job_admissions_owner_window_idx
ON job_admissions(user_id, created_at);
