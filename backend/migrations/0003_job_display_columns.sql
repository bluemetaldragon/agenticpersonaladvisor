-- ============================================================================
-- Board-Prep Agent — migration 0003: job display columns
-- ----------------------------------------------------------------------------
-- The Home in-progress tracker (J7) and Processing screen render a job before a
-- pack exists (pack_id is null until parsing completes), so the job itself must
-- carry the display title and the uploaded filename.
-- ============================================================================

alter table job
    add column if not exists title text not null default 'Board pack';

alter table job
    add column if not exists source_filename text;