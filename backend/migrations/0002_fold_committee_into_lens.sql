-- ============================================================================
-- Board-Prep Agent — migration 0002: fold committee into lens
-- ----------------------------------------------------------------------------
-- The committee enum is replaced by the lens concept. A director profile now
-- references a lens (the emphasis keyword map, FR-PR-4) rather than carrying a
-- 4-valued committee enum. This lets nodes.py drive emphasis from the lens.
--
-- Idempotent: safe to re-run. (The original cut lacked the IF [NOT] EXISTS
-- guards, which is why a partial re-run errored on "column already exists".)
-- ============================================================================

alter table director_profile
    add column if not exists lens_id text references lens(id) on delete set null;

-- Default new/existing profiles to the Full board lens (matches user_settings).
update director_profile set lens_id = 'lens_fullboard' where lens_id is null;

-- Drop the committee column (its CHECK constraint drops with it).
alter table director_profile
    drop column if exists committee;

comment on column director_profile.lens_id is
    'Replaces the former committee enum. Points at lens (§14.7). Emphasis is lens-driven (FR-PR-4).';