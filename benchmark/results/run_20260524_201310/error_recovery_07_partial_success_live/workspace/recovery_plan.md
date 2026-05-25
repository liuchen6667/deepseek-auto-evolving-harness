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
  "batch_size": 50,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 30]
}
```

## Evidence Analysis

### Root Cause
The database connection pool exhaustion (32/32 connections active) caused timeout errors (`db_connection_timeout`) during the commit phase. Logs show `active=32 limit=32` and `error=db_connection_timeout` starting from file_0701.dat.

### File Status Classification
1. **Successful files (700)**: file_0001.dat to file_0700.dat
   - Log entries: `SUCCESS rows=100 db_ms=18`
   - Database state: `committed,100,commit_complete` in processed_files.csv
   - **Action**: Do not retry - these files are already fully processed.

2. **Partial files (18)**: file_0701.dat to file_0718.dat
   - Log entries: `PARTIAL rows_written=XX` (varying from 19 to 83 rows)
   - Database state: `partial,XX,timed_out_after_insert` in processed_files.csv
   - **Action**: Cleanup required before retry - partial rows must be removed.

3. **Failed files (282)**: file_0719.dat to file_1000.dat
   - Log entries: `FAILED before_commit error=db_connection_timeout`
   - **Not present** in processed_files.csv (no database state)
   - **Action**: Safe to retry directly - no database writes occurred.

## Recovery Strategy

### Phase 1: Cleanup (Partial Files)
1. For each of the 18 partial files, execute DELETE statements to remove partially inserted rows.
2. Use the `rows_written` count from processed_files.csv to verify cleanup completeness.
3. Example cleanup SQL: `DELETE FROM target_table WHERE source_file = 'file_0701.dat';`

### Phase 2: Retry with Conservative Settings
1. **Batch size**: 50 files per batch (reduced from original to avoid pool exhaustion)
2. **Max retries**: 3 attempts per batch
3. **Exponential backoff**: 5, 15, 30 seconds between retries
4. **Connection pool monitoring**: Ensure pool usage stays below 80% (25/32 connections)

### Execution Order
1. Cleanup all 18 partial files first
2. Retry failed files in batches of 50:
   - Batch 1: file_0719.dat to file_0768.dat (50 files)
   - Batch 2: file_0769.dat to file_0818.dat (50 files)
   - Batch 3: file_0819.dat to file_0868.dat (50 files)
   - Batch 4: file_0869.dat to file_0918.dat (50 files)
   - Batch 5: file_0919.dat to file_0968.dat (50 files)
   - Batch 6: file_0969.dat to file_1000.dat (32 files)

## Verification Steps

1. **Pre-retry verification**:
   - Confirm 700 successful files exist in database with 100 rows each
   - Verify 18 partial files have 0 rows after cleanup
   - Check connection pool is healthy (< 80% utilization)

2. **Post-retry verification**:
   - All 1000 files should have `committed` state in database
   - Each file should have exactly 100 rows written
   - No duplicate rows for partial files (cleanup verification)
   - Compare with processed_files.csv for completeness

3. **Final reconciliation**:
   - Export final database state and compare with file_list.txt
   - Generate completion report with counts and timestamps
   - Log any discrepancies for manual review

## Risk Mitigation
- Monitor database connection pool metrics during retry
- Implement circuit breaker pattern to pause if pool exceeds 80%
- Maintain audit trail of all cleanup and retry operations
- Have rollback plan for each batch in case of failure
```