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
  "batch_size": 20,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 30]
}
```

## Evidence Analysis

### Root Cause
The failure was caused by **database connection pool exhaustion**. Log entries show `active=32 limit=32` with `db_connection_timeout` errors starting at `2026-03-21T14:58:18Z`. The connection pool (size 32) became fully occupied, causing subsequent operations to timeout after 30 seconds (`wait_ms=30000`).

### File Classification
Cross-referencing three sources (`process.log`, `processed_files.csv`, `file_list.txt`) reveals:
1. **Successfully processed (700 files)**: `file_0001.dat` through `file_0700.dat` - marked `SUCCESS` in logs and `committed` in database.
2. **Partially written (18 files)**: `file_0701.dat` through `file_0718.dat` - marked `PARTIAL` in logs with `rows_written` (19-83 rows) and `partial` state in database. These files have incomplete data that must be cleaned up before retry.
3. **Failed before commit (282 files)**: `file_0719.dat` through `file_0999.dat` - marked `FAILED before_commit` in logs, no database entry. These can be retried directly.
4. **Remaining file**: `file_1000.dat` was not processed (not in logs or database).

All three sources are consistent with no discrepancies.

## Recovery Strategy

### Phase 1: Cleanup (18 files)
**Files requiring cleanup before retry**: The 18 partially written files (`file_0701.dat` to `file_0718.dat`) have incomplete data in the database (`timed_out_after_insert`).

**Cleanup procedure**:
1. For each file in the cleanup list, delete the partially inserted rows from the database using the `rows_written` count from `processed_files.csv`.
2. Verify deletion by checking row counts match expected removal.
3. Update database state from `partial` to `cleaned`.

### Phase 2: Retry (282 files)
**Files ready for immediate retry**: The 282 failed files (`file_0719.dat` to `file_0999.dat`) had no database writes and can be reprocessed.

**Retry configuration**:
- **Batch size**: 20 files per batch (reduced from original to prevent connection pool exhaustion)
- **Max retries**: 3 attempts per file
- **Exponential backoff**: 5, 15, 30 seconds between retries
- **Connection pool monitoring**: Ensure active connections stay below 80% of limit (25/32)

**Execution order**:
1. Process cleanup files first (after cleanup)
2. Process failed files in alphabetical order
3. Process remaining file `file_1000.dat`

## Verification Steps

1. **Pre-recovery verification**:
   - Confirm database connection pool is healthy (active < 25 connections)
   - Validate cleanup SQL correctly targets partial rows

2. **Post-cleanup verification**:
   - Check `processed_files` table shows `cleaned` state for all 18 files
   - Verify row counts match expected deletions

3. **During retry verification**:
   - Monitor connection pool usage (`pool_in_use` in logs)
   - Log each file success/failure with detailed error codes
   - Implement circuit breaker if connection pool exceeds 28 connections

4. **Post-recovery verification**:
   - All 1000 files should be in `processed_files` table with `committed` state
   - Row counts should be 100 for each file (except any legitimate failures)
   - Compare total rows inserted with expected 100,000 rows (1000 files × 100 rows)

## Risk Mitigation

- **Connection pool exhaustion**: Reduced batch size (20), backoff strategy, and real-time monitoring
- **Partial data corruption**: Cleanup phase ensures database consistency before retry
- **Duplicate processing**: Database state tracking prevents reprocessing successful files
- **Cascading failures**: Circuit breaker halts processing if error rate exceeds 10%

## Rollback Plan

If recovery fails:
1. Stop all processing immediately
2. Document current state (files processed, database rows)
3. Restore from pre-recovery database snapshot
4. Investigate root cause before attempting alternative recovery strategy
