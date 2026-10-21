# Pandas-Based Data Processing Pipeline

A Python data-processing project that processes large CSV datasets in chunks, validates order records, separates invalid records, and generates business reports.

## Project Overview

This project processes 100,000 order records using Pandas. It uses chunk-based processing to reduce memory usage and produces cleaned datasets, rejected records, and business reports.

## Features

- Read large CSV files in configurable chunks.
- Validate order records and reject invalid data.
- Track duplicate order IDs across chunks.
- Calculate order totals and revenue.
- Export cleaned data to CSV and Parquet formats.
- Generate category and product revenue reports.
- Log pipeline progress and errors.
- Measure processing time and data quality.
- Benchmark different chunk sizes.
- Test data validation and revenue calculations using pytest.

## Technologies Used

- Python
- Pandas
- PyArrow
- pytest
- Git and GitHub

## Project Structure

```text
pyspark-distributed-data-processing/
├── data/
│   └── orders_large.csv
├── output/
│   ├── cleaned_orders.csv
│   ├── cleaned_orders.parquet
│   ├── rejected_records.csv
│   ├── category_report.csv
│   ├── product_report.csv
│   └── benchmark_results.csv
├── tests/
│   └── test_pipeline.py
├── main.py
├── generate_large_data.py
├── benchmark.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```powershell
git clone https://github.com/Chandana4658/pyspark-distributed-data-processing.git
cd pyspark-distributed-data-processing
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Generate the Dataset

Generate the large CSV dataset:

```powershell
python generate_large_data.py
```

## Run the Pipeline

```powershell
python main.py
```

The pipeline validates order records, separates invalid records, calculates order totals, and generates reports.

## Run Tests

```powershell
pytest -v
```

The project has five tests covering pipeline functionality and data processing.

## Benchmark Results

The pipeline was benchmarked using 100,000 input records and three chunk sizes.

| Chunk Size | Execution Time (seconds) | Cleaned Records | Rejected Records |
|---:|---:|---:|---:|
| 500 | 10.7582 | 99,867 | 133 |
| 1,000 | 8.5821 | 99,867 | 133 |
| 5,000 | 7.2042 | 99,867 | 133 |

In this benchmark run, a chunk size of 5,000 was the fastest. All three configurations produced the same cleaned and rejected record counts.

Execution times may vary depending on system resources and workload.

### Run the Benchmark

```powershell
python benchmark.py
```

Benchmark results are saved to `output/benchmark_results.csv`.

## Latest Pipeline Results

- Input records: 100,000
- Valid records: 99,867
- Rejected records: 133
- Data quality rate: 99.87%
- Last recorded processing time: approximately 6.36 seconds with a chunk size of 5,000

These pipeline timings are from a separate run and may differ from benchmark timings.

## Learning Outcomes

- Processing large CSV datasets in chunks with Pandas.
- Data validation and duplicate detection.
- Handling invalid records.
- Exporting data to CSV and Parquet.
- Generating business reports.
- Logging and exception handling.
- Writing automated tests with pytest.
- Measuring pipeline performance.

## Author

**Venkata Chandana Netturi**

GitHub: https://github.com/Chandana4658



## PostgreSQL Integration

Loaded the cleaned order data from `output/cleaned_orders.csv` into a PostgreSQL database named `orders_db`.

### Features
- Python-to-PostgreSQL integration using `psycopg2`
- Bulk insertion of cleaned CSV records
- Duplicate order prevention using `ON CONFLICT`
- SQL sales reports by category and product
- Overall sales summary

### Database
Table: `orders`

Columns:
- `order_id`
- `customer_name`
- `product`
- `category`
- `quantity`
- `price`
- `total_amount`

### Run the Loader

Set your PostgreSQL password in PowerShell:

```powershell
$env:PGPASSWORD = Read-Host "Enter PostgreSQL password"
```

Then run:

```powershell
python .\load_to_postgres.py
```

### SQL Reports

See `sql/01_sales_summary.sql` for queries covering:
- Overall sales summary
- Category-wise sales
- Top 10 products by sales

