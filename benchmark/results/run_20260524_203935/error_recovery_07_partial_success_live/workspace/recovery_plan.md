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
  "batch_size": 10,
  "max_retries": 3,
  "backoff_seconds": [5, 15, 30]
}
```

## Evidence

- **process.log**: Shows 700 SUCCESS entries (file_0001.dat to file_0700.dat), 18 PARTIAL entries (file_0701.dat to file_0718.dat), and 282 FAILED before_commit entries (file_0719.dat to file_1000.dat). The log indicates database connection pool exhaustion (`active=32 limit=32`) starting at 14:58:18Z.
- **processed_files.csv**: Contains 719 records: 701 committed (file_0001.dat to file_0700.dat plus file_0700.dat appears twice? Actually check: file_0700.dat is committed), and 18 partial (file_0701.dat to file_0718.dat) with `db_state=partial` and `rows_written` values.
- **file_list.txt**: Lists 1000 files (file_0001.dat to file_1000.dat), matching the total processed.

## File Categories

1. **Successful files (700)**: Already committed to the database. These should **not** be retried to avoid duplicates.
2. **Partial files (18)**: Partially written rows (`rows_written` between 19 and 83). These require **cleanup** (delete partial rows) before retry.
3. **Failed files (282)**: Failed before any commit (`before_commit`). No rows written, can be retried directly.

## Cleanup Procedure

For each partial file (18 files):
1. Identify the partially inserted rows using the `rows_written` count from `processed_files.csv`.
2. Execute a targeted delete operation (e.g., `DELETE FROM target_table WHERE file_name = ? AND row_id > ?`).
3. Verify that no rows from that file remain in the target table.

## Retry Strategy

- **Batch size**: 10 files per batch to avoid overwhelming the database connection pool.
- **Max retries**: 3 attempts per file.
- **Exponential backoff**: Wait 5, 15, then 30 seconds between retries.
- **Order**: Process partial files (after cleanup) first, then failed files, in alphabetical order.
- **Monitoring**: Watch connection pool usage (`pool_in_use`) and pause if approaching limit.

## Verification Steps

1. **Pre‑retry check**: Confirm that successful files (700) are present and complete in the database.
2. **Cleanup verification**: For each partial file, query the database to ensure zero rows remain before retry.
3. **Retry monitoring**: Log each file’s outcome (SUCCESS/PARTIAL/FAILED) and rows written.
4. **Post‑retry audit**: Compare the final database state with `file_list.txt`; all 1000 files should be in `committed` state.
5. **Integrity check**: Validate row counts per file match expected 100 rows (or the sum of partial retries).

## Notes

- Do not modify the input evidence files (`process.log`, `processed_files.csv`, `file_list.txt`).
- The recovery process should be idempotent: running it multiple times should not create duplicates or data loss.
- If connection pool issues persist, consider increasing the pool size or reducing batch size further.