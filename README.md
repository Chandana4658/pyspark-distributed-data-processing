# Pandas-Based Data Processing Pipeline

A Python data-processing project that processes large CSV datasets in chunks, validates order records, separates invalid records, and generates reports.

## Project Overview

This project processes 100,000 order records using Pandas. It uses chunk-based processing to reduce memory usage and produces cleaned datasets, rejected records, and business reports.

## Features

- Read large CSV files in configurable chunks.
- Validate order records and reject invalid data.
- Track duplicate order IDs across chunks.
- Calculate order totals and revenue.
- Export cleaned data to CSV and Parquet formats.
- Generate category and product revenue reports.
- Measure processing time and data quality.
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
│   ├── orders.csv
│   └── orders_large.csv
├── output/
│   ├── cleaned_orders.csv
│   ├── cleaned_orders.parquet
│   ├── rejected_records.csv
│   ├── category_report.csv
│   └── product_report.csv
├── tests/
│   └── test_pipeline.py
├── generate_large_data.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and Installation

Create and activate a virtual environment, then install the project dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Generate the Dataset

```powershell
python generate_large_data.py
```

## Run the Pipeline

```powershell
python main.py
```

The pipeline processes the input data and saves the generated files in the `output/` directory.

## Run Tests

```powershell
python -m pytest -v
```

The current test suite contains five tests covering valid records, missing customer information, negative quantities, rejection reasons, and revenue calculations.

## Performance and Data Quality

Latest successful run with 100,000 input records:

| Metric | Result |
|---|---:|
| Input records | 100,000 |
| Valid records | 99,867 |
| Rejected records | 133 |
| Valid data percentage | 99.87% |
| Chunk size | 5,000 |
| Execution time | 6.1983 seconds |

The cleaned and rejected CSV files were verified to contain 99,867 and 133 records respectively, accounting for all 100,000 input records.

*Performance may vary depending on hardware and system load.*

## Output Files

| File | Description |
|---|---|
| `cleaned_orders.csv` | Validated order records |
| `cleaned_orders.parquet` | Cleaned records in columnar Parquet format |
| `rejected_records.csv` | Rejected records and validation details |
| `category_report.csv` | Item counts, revenue, and order counts by category |
| `product_report.csv` | Total quantity and revenue by product |

## Key Learning Outcomes

- Processing large CSV files in chunks.
- Data validation and cleaning with Pandas.
- Working with CSV and Parquet formats.
- Generating business reports.
- Writing automated tests with pytest.
- Benchmarking a data-processing pipeline.

## Author

Venkata Chandana Netturi

GitHub: https://github.com/Chandana4658/pyspark-distributed-data-processing
