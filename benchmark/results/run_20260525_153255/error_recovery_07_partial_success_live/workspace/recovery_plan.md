```json
{
  "root_cause": "db_connection_pool_exhaustion",
  "successful_files": 700,
  "failed_files": 282,
  "partial_files": 18,
  "retry_files_total": 300,
  "cleanup_files_total": 18,
  "cleanup_examples": ["file_0701.dat", "file_0702.dat", "file_0703.dat"],
  "retry_examples": ["file_0719.dat", "file_0720.dat", "file_0721.dat", "file_0722.dat", "file_0723.dat"],
  "batch_size": 20,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 30]
}
```

## Evidence Analysis

**Root Cause Identification:**
- Log shows `db_connection_timeout` with `active=32 limit=32` (connection pool exhausted)
- Error pattern: After processing 700 files successfully, pool saturation led to timeouts
- Partial writes occurred during the initial pool exhaustion phase (files 0701-0718)

**Cross-Reference Findings:**
1. `process.log` vs `processed_files.csv` alignment:
   - 700 files marked SUCCESS in log ↔ `committed` in CSV
   - 18 files marked PARTIAL in log ↔ `partial` in CSV with rows_written 19-83
   - 282 files marked FAILED in log ↔ **not present** in CSV
2. `file_list.txt` contains all 1000 candidate files
3. Database state indicates partial writes for files 0701-0718 require cleanup

## Cleanup Requirements

**Files Needing Cleanup Before Retry (18 files):**
- These files have partial database writes (19-83 rows each)
- Must delete existing partial records before re-processing
- Cleanup SQL example: `DELETE FROM target_table WHERE source_file = 'file_0701.dat'`
- Verify deletion by counting rows before/after cleanup

## Retry Strategy

**Conservative Approach:**
1. **Cleanup Phase:** Process 18 partial files individually with verification
2. **Retry Phase:** Process remaining 300 files (18 cleanup + 282 failed) in small batches
3. **Batch Size:** 20 files per batch to avoid connection pool exhaustion
4. **Retry Logic:** Exponential backoff with max 3 attempts
5. **Backoff Sequence:** 5s → 15s → 30s (strictly increasing)

**Execution Order:**
1. Cleanup all 18 partial files (alphabetical order)
2. Retry batches: Start with partial files, then failed files
3. Monitor connection pool usage (`pool_in_use` metric)

## Verification Steps

1. **Pre-retry Verification:**
   - Confirm 700 successful files exist in database with 100 rows each
   - Validate no duplicate entries for files 0701-0718 after cleanup

2. **Post-cleanup Verification:**
   - For each partial file: `SELECT COUNT(*) WHERE source_file = '...'` must return 0

3. **Post-retry Verification:**
   - All 1000 files should have exactly 100 rows in database
   - Check `processed_files` table for `committed` status
   - Verify no `partial` or missing entries remain

4. **Monitoring During Retry:**
   - Track connection pool utilization (< 80% capacity)
   - Alert if `pool_in_use` exceeds 25/32 connections
   - Pause processing if waiters queue forms

## Risk Mitigation

- Process during low-traffic periods
- Maintain database connection health checks
- Implement circuit breaker pattern for database connectivity
- Keep detailed audit log of all cleanup and retry operations
- Prepare rollback plan for each batch

**Note:** This plan assumes database connectivity issues are resolved and connection pool limits are appropriately configured for the workload.
