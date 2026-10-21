## Benchmark Results

The pipeline was benchmarked using 100,000 input records and three chunk sizes.

| Chunk Size | Execution Time (seconds) | Cleaned Records | Rejected Records |
|---:|---:|---:|---:|
| 500 | 10.7582 | 99,867 | 133 |
| 1,000 | 8.5821 | 99,867 | 133 |
| 5,000 | 7.2042 | 99,867 | 133 |

The chunk size of 5,000 was the fastest in this benchmark run. All three configurations produced the same cleaned and rejected record counts.

Execution times may vary depending on system resources and workload.

Run the benchmark again with:

```powershell
python benchmark.py




## Benchmark Results

The data-processing pipeline was tested with 100,000 input records using different chunk sizes.

| Chunk Size | Execution Time (seconds) | Cleaned Records | Rejected Records |
|---:|---:|---:|---:|
| 500 | 10.7582 | 99,867 | 133 |
| 1,000 | 8.5821 | 99,867 | 133 |
| 5,000 | 7.2042 | 99,867 | 133 |

In this benchmark run, a chunk size of 5,000 produced the fastest result. All three runs produced the same number of cleaned and rejected records.

Execution times may vary depending on system resources and workload.

### Run the Benchmark

```powershell
python benchmark.py
```

The benchmark results are saved to `output/benchmark_results.csv`.
