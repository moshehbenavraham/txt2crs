-- SPDX-License-Identifier: MIT-0
-- Persist content-free worker liveness without advancing checkpoint state.

ALTER TABLE jobs
ADD COLUMN runtime_activity_at TEXT;
