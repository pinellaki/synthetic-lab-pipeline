-- Add minimal issue-resolution tracking to rejected records.
--
-- Existing rejected records receive the default status "open".
-- The migration is repeat-safe because every column uses IF NOT EXISTS.

ALTER TABLE rejected_record
    ADD COLUMN IF NOT EXISTS resolution_status TEXT NOT NULL DEFAULT 'open';

ALTER TABLE rejected_record
    ADD COLUMN IF NOT EXISTS corrected_value TEXT;

ALTER TABLE rejected_record
    ADD COLUMN IF NOT EXISTS resolution_note TEXT;

ALTER TABLE rejected_record
    ADD COLUMN IF NOT EXISTS resolved_by TEXT;

ALTER TABLE rejected_record
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;

COMMENT ON COLUMN rejected_record.resolution_status IS
    'Current issue status: open, corrected, resolved, or dismissed.';

COMMENT ON COLUMN rejected_record.corrected_value IS
    'Corrected value associated with the rejected record, when applicable.';

COMMENT ON COLUMN rejected_record.resolution_note IS
    'Explanation of how the issue was corrected, resolved, or dismissed.';

COMMENT ON COLUMN rejected_record.resolved_by IS
    'Person or process that handled the issue.';

COMMENT ON COLUMN rejected_record.resolved_at IS
    'Date and time when the issue was corrected, resolved, or dismissed.';