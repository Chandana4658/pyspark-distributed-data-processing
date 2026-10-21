
import csv
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "data" / "orders_large.csv"

CHUNK_SIZES = [500, 1000, 5000]


def count_csv_records(file_path):
    """Count CSV data records without loading the full file into memory."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        return max(sum(1 for _ in csv.reader(file)) - 1, 0)


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        print("Run python generate_large_data.py first.")
        return

    results = []

    for chunk_size in CHUNK_SIZES:
        env = os.environ.copy()
        env["CHUNK_SIZE"] = str(chunk_size)

        print(f"\nBenchmarking chunk size: {chunk_size}")

        start = time.perf_counter()
        process = subprocess.run(
            [sys.executable, str(PROJECT_DIR / "main.py")],
            cwd=PROJECT_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
        elapsed = time.perf_counter() - start

        if process.returncode != 0:
            print("Pipeline failed:")
            print(process.stderr)
            continue

        output_dir = PROJECT_DIR / "output"
        cleaned_file = output_dir / "cleaned_orders.csv"
        rejected_file = output_dir / "rejected_records.csv"

        cleaned_count = count_csv_records(cleaned_file)
        rejected_count = count_csv_records(rejected_file)

        results.append(
            {
                "chunk_size": chunk_size,
                "execution_seconds": round(elapsed, 4),
                "cleaned_records": cleaned_count,
                "rejected_records": rejected_count,
            }
        )

        print(f"Execution time: {elapsed:.4f} seconds")
        print(f"Cleaned records: {cleaned_count}")
        print(f"Rejected records: {rejected_count}")

    if results:
        report_file = PROJECT_DIR / "output" / "benchmark_results.csv"

        with report_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "chunk_size",
                    "execution_seconds",
                    "cleaned_records",
                    "rejected_records",
                ],
            )
            writer.writeheader()
            writer.writerows(results)

        print("\n--- BENCHMARK SUMMARY ---")
        for result in results:
            print(result)

        print(f"\nResults saved to: {report_file}")


if __name__ == "__main__":
    main()
