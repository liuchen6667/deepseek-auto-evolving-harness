```json
{
  "root_cause": "db_connection_pool_exhaustion",
  "successful_files": 700,
  "failed_files": 282,
  "partial_files": 18,
  "retry_files_total": 300,
  "cleanup_files_total": 18,
  "cleanup_examples": ["file_0701.dat", "file_0702.dat", "file_0703.dat"],
  "retry_examples": ["file_0701.dat", "file_0702.dat", "file_0703.dat", "file_0704.dat", "file_0705.dat"],
  "batch_size": 50,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 45]
}
```

## Evidence Analysis

### Root Cause
Database connection pool exhaustion caused timeout failures. Log shows `active=32 limit=32` and `error=db_connection_timeout` for files 779-1000. The pool reached maximum capacity, preventing new connections.

### File Status Classification
1. **Successful (700 files)**: Files 0001-0700 show `SUCCESS` in log and `committed` in database export.
2. **Partial (18 files)**: Files 0701-0718 show `partial` state with varying `rows_written` (19-83 rows) and `timed_out_after_insert` stage.
3. **Failed (282 files)**: Files 0719-1000 show `FAILED before_commit` in log, no database entries.

### Data Consistency Check
- `file_list.txt`: 1000 total files
- `process.log`: 778 SUCCESS entries + 222 FAILED entries = 1000 total
- `processed_files.csv`: 700 committed + 18 partial = 718 entries
- Gap: Files 0719-1000 (282 files) failed before database write, not in CSV.

## Cleanup Requirements

**18 partial files** require cleanup before retry:
- Delete partially inserted rows for each file
- Use transaction rollback or targeted delete based on `file_name` foreign key
- Verify no orphaned records remain
- Cleanup examples: `file_0701.dat`, `file_0702.dat`, `file_0703.dat`

## Retry Strategy

**Conservative approach to prevent pool exhaustion:**

1. **Batch processing**: 50 files per batch
2. **Exponential backoff**: 5s, 15s, 45s between retries
3. **Max 3 retries** per file
4. **Monitor pool usage**: Keep below 80% capacity (≤25 connections)
5. **Sequential processing within batch** to control load

**Retry order**:
1. Clean partial files (701-718)
2. Retry failed files (719-1000)

## Verification Steps

1. **Pre-retry verification**:
   - Check database connection pool configuration
   - Validate cleanup completed for partial files
   - Confirm successful files (0001-0700) unchanged

2. **During retry monitoring**:
   - Track pool usage per batch
   - Log each file outcome (SUCCESS/FAILURE)
   - Stop if pool usage exceeds 80%

3. **Post-retry validation**:
   - Compare `processed_files.csv` count: should be 1000 committed
   - Verify all rows_written = 100 for each file
   - Check no duplicate entries exist
   - Run consistency check: total rows = 100,000 (1000 files × 100 rows)

## Risk Mitigation

- **Database backup** before cleanup
- **Transaction isolation** for each file
- **Circuit breaker** pattern: stop if >10% failures in a batch
- **Manual intervention point** after each batch completion

## Rollback Plan

If retry fails:
1. Preserve successful files (0001-0700)
2. Mark partial files for manual review
3. Document failure pattern for root cause analysis
4. Reset database to pre-retry state using backup
```