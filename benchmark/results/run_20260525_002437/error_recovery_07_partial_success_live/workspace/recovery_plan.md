```json
{
  "root_cause": "db_connection_pool_exhaustion",
  "successful_files": 700,
  "failed_files": 281,
  "partial_files": 18,
  "retry_files_total": 299,
  "cleanup_files_total": 18,
  "cleanup_examples": ["file_0701.dat", "file_0702.dat", "file_0703.dat"],
  "retry_examples": ["file_0719.dat", "file_0720.dat", "file_0721.dat", "file_0722.dat", "file_0723.dat"],
  "batch_size": 50,
  "max_retries": 3,
  "backoff_seconds": [10, 30, 60]
}
```

## Evidence Summary

### Root Cause Analysis
- Database connection pool exhaustion at 14:58:18Z (line 703 in process.log)
- Active connections reached limit (32/32) causing `db_connection_timeout`
- Error propagated from file_0701.dat onward

### File Status Cross-check
1. **Successfully processed (700 files)**: file_0001.dat through file_0700.dat
   - Log entries: `SUCCESS rows=100`
   - Database state: `committed` with `commit_complete`
   - No retry needed

2. **Partially written (18 files)**: file_0701.dat through file_0718.dat
   - Log entries: `PARTIAL rows_written=37-83` (partial counts vary)
   - Database state: `partial` with `timed_out_after_insert`
   - Must be cleaned up before retry

3. **Failed before commit (281 files)**: file_0719.dat through file_0999.dat
   - Log entries: `FAILED before_commit error=db_connection_timeout`
   - Not present in processed_files.csv
   - Can be retried directly

## Recovery Strategy

### Phase 1: Cleanup (18 files)
1. **Target**: All partially written files (file_0701.dat to file_0718.dat)
2. **Action**: Delete partial records from database
   ```sql
   DELETE FROM target_table WHERE source_file IN ('file_0701.dat', ...);
   ```
3. **Verification**: Confirm zero rows remain for these files

### Phase 2: Retry (299 files)
1. **Direct retry (281 files)**: file_0719.dat to file_0999.dat
2. **Post-cleanup retry (18 files)**: file_0701.dat to file_0718.dat
3. **Execution order**: Process cleaned files first, then failed files

### Conservative Retry Configuration
- **Batch size**: 50 files (reduced from original to prevent pool exhaustion)
- **Max retries**: 3 attempts per file
- **Exponential backoff**: 10s, 30s, 60s between retries
- **Pool monitoring**: Alert if active connections > 24/32 (75% threshold)

## Verification Steps

1. **Pre-retry validation**:
   - Confirm database connection pool healthy (active < 25)
   - Validate cleanup completed (no partial rows)
   - Check file availability for all 299 files

2. **During retry monitoring**:
   - Monitor `pool_in_use` metric in logs
   - Alert on consecutive timeouts
   - Track progress vs. expected completion time

3. **Post-retry verification**:
   - Compare row counts: expected 100 rows per file
   - Verify all files marked `committed` in database
   - Validate no duplicate or missing records
   - Generate completion report with success/failure counts

## Risk Mitigation

1. **Connection pool management**:
   - Implement circuit breaker pattern
   - Add connection timeout fallback (fall to queue)
   - Monitor and alert on pool saturation

2. **Idempotent processing**:
   - Ensure retry logic handles partial writes
   - Use transactional boundaries per file
   - Maintain audit trail of retry attempts

3. **Rollback readiness**:
   - Backup checkpoint before retry batch
   - Document rollback SQL for each file group
   - Test rollback procedure on sample data
```