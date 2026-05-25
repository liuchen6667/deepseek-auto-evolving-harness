```json
{
  "root_cause": "db_connection_pool_exhaustion",
  "successful_files": 700,
  "failed_files": 282,
  "partial_files": 18,
  "retry_files_total": 282,
  "cleanup_files_total": 18,
  "cleanup_examples": ["file_0701.dat", "file_0702.dat", "file_0703.dat"],
  "retry_examples": ["file_0719.dat", "file_0720.dat", "file_0721.dat", "file_0722.dat", "file_0723.dat"],
  "batch_size": 10,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 30]
}
```

## Evidence Analysis

**Root Cause**: Database connection pool exhaustion (active=32/32) starting at 14:58:18, causing `db_connection_timeout` with 30s wait time. The pool remained saturated through the failure window.

**Cross-check Results**:
- **Successful (700 files)**: `file_0001.dat` to `file_0700.dat` – logged as SUCCESS with 100 rows each, confirmed `committed` in database.
- **Partial writes (18 files)**: `file_0701.dat` to `file_0718.dat` – logged as PARTIAL with varying rows_written (19‑83 rows), database shows `partial` state for 0701‑0717; 0718 is missing from DB but logged as PARTIAL.
- **Failed before commit (281 files)**: `file_0719.dat` to `file_0999.dat` – logged as FAILED before_commit, no DB entry.
- **Never started (1 file)**: `file_1000.dat` – in file list but no log entry.

## Cleanup Required

**18 partial files** must have their partially inserted rows deleted before retry:
1. Query database for rows inserted by each partial file (use `file_name` as source identifier).
2. Delete those rows in a single transaction per file.
3. Verify deletion by counting rows before/after.
4. Update `processed_files` table to mark as `cleaned` (or delete the record).

**Cleanup order**: Process files alphabetically, one at a time, with verification after each.

## Retry Strategy

**Conservative approach**:
- **Batch size**: 10 files per batch to avoid pool exhaustion.
- **Max retries**: 3 attempts per file with exponential backoff.
- **Backoff sequence**: 5s, 15s, 30s between retries.
- **Isolation**: Process cleanup files first, then failed files.
- **Pacing**: 2-second gap between files within a batch.

**Execution order**:
1. Cleanup all 18 partial files (sequential, verified).
2. Retry failed files in batches of 10, alphabetical order.
3. Include `file_1000.dat` in the retry queue.

## Verification Steps

1. **Pre-retry check**: Confirm DB connection pool is healthy (<50% utilization).
2. **Cleanup verification**: For each partial file, assert row count = 0 after cleanup.
3. **Batch verification**: After each batch of 10 retries:
   - Check `processed_files` table for `committed` status.
   - Verify log shows SUCCESS for each file.
   - Confirm no ERROR or PARTIAL entries.
4. **Final audit**: Compare total committed files (should be 1000) against `file_list.txt`.
5. **Integrity check**: Sum of `rows_written` should equal 100,000 (100 rows × 1000 files).

**Rollback plan**: If any batch fails >50%, pause and investigate before proceeding.