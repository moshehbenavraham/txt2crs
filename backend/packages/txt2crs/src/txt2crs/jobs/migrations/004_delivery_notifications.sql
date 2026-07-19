-- SPDX-License-Identifier: MIT-0
-- Replace nullable notification decisions with explicit disabled state.

ALTER TABLE job_deliveries
ADD COLUMN notification_schema_version TEXT NOT NULL DEFAULT '1.0'
    CHECK(notification_schema_version = '1.0');

ALTER TABLE job_deliveries
ADD COLUMN notification_mode TEXT NOT NULL DEFAULT 'disabled'
    CHECK(notification_mode = 'disabled');

ALTER TABLE job_deliveries
ADD COLUMN notification_status TEXT NOT NULL DEFAULT 'not_applicable'
    CHECK(notification_status = 'not_applicable');

-- SQLite applies the defaults to released rows when each column is added.
-- Keep an explicit backfill statement so the migration's recovery intent is
-- reviewable and remains correct if a compatible legacy database supplied
-- nullable values through an external migration tool.
UPDATE job_deliveries
SET notification_schema_version = '1.0',
    notification_mode = 'disabled',
    notification_status = 'not_applicable';
