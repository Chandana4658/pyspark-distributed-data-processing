
from pathlib import Path
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def validate_orders(orders, seen_order_ids=None):
    """Clean, validate, and separate valid and rejected orders."""
    orders = orders.copy()

    # Keep duplicate tracking across chunks when a set is provided.
    if seen_order_ids is None:
        seen_order_ids = set()

    # 1. Clean text fields
    for column in ["customer_name", "product", "category"]:
        orders[column] = (
            orders[column].astype("string").str.strip()
        )

    # 2. Convert numeric columns
    orders["quantity"] = pd.to_numeric(
        orders["quantity"], errors="coerce"
    )
    orders["price"] = pd.to_numeric(
        orders["price"], errors="coerce"
    )

    # 3. Validate records and record rejection reasons
    rejection_reasons = []

    for _, row in orders.iterrows():
        reasons = []
        order_id = row["order_id"]

        if pd.isna(order_id):
            reasons.append("Missing order ID")
        elif order_id in seen_order_ids:
            reasons.append("Duplicate order ID")
        else:
            seen_order_ids.add(order_id)

        for column in ["customer_name", "product", "category"]:
            if pd.isna(row[column]) or row[column] == "":
                reasons.append(
                    f"Missing {column.replace('_', ' ')}"
                )

        if pd.isna(row["quantity"]):
            reasons.append("Missing or invalid quantity")
        elif row["quantity"] <= 0:
            reasons.append("Quantity must be greater than zero")

        if pd.isna(row["price"]):
            reasons.append("Missing or invalid price")
        elif row["price"] <= 0:
            reasons.append("Price must be greater than zero")

        rejection_reasons.append("; ".join(reasons))

    orders["rejection_reason"] = rejection_reasons

    # 4. Separate valid and rejected records
    rejected = orders.loc[
        orders["rejection_reason"] != ""
    ].copy()

    cleaned = orders.loc[
        orders["rejection_reason"] == ""
    ].drop(columns=["rejection_reason"]).copy()

    # 5. Calculate order amount
    cleaned["total_amount"] = (
        cleaned["quantity"] * cleaned["price"]
    ).round(2)

    return cleaned, rejected


def main():
    project_dir = Path(__file__).resolve().parent
    input_file = project_dir / "data" / "orders.csv"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_size = 1000
    start_time = time.perf_counter()

    cleaned_csv = output_dir / "cleaned_orders.csv"
    rejected_csv = output_dir / "rejected_records.csv"
    parquet_file = output_dir / "cleaned_orders.parquet"
    category_file = output_dir / "category_report.csv"
    product_file = output_dir / "product_report.csv"

    # Remove old outputs to prevent stale data.
    for file in [
        cleaned_csv,
        rejected_csv,
        parquet_file,
        category_file,
        product_file,
    ]:
        if file.exists():
            file.unlink()

    # Processing state
    seen_order_ids = set()
    category_parts = []
    product_parts = []

    input_count = 0
    valid_count = 0
    rejected_count = 0
    first_chunk = True
    parquet_writer = None

    try:
        # 1. Read and process the CSV in chunks.
        for chunk_number, orders in enumerate(
            pd.read_csv(input_file, chunksize=chunk_size),
            start=1,
        ):
            input_count += len(orders)

            cleaned, rejected = validate_orders(
                orders,
                seen_order_ids=seen_order_ids,
            )

            valid_count += len(cleaned)
            rejected_count += len(rejected)

            # 2. Append valid and rejected records to CSV files.
            cleaned.to_csv(
                cleaned_csv,
                mode="w" if first_chunk else "a",
                header=first_chunk,
                index=False,
            )

            rejected.to_csv(
                rejected_csv,
                mode="w" if first_chunk else "a",
                header=first_chunk,
                index=False,
            )

            # 3. Write valid records to one Parquet file.
            if not cleaned.empty:
                table = pa.Table.from_pandas(
                    cleaned,
                    preserve_index=False,
                )

                if parquet_writer is None:
                    parquet_writer = pq.ParquetWriter(
                        parquet_file,
                        table.schema,
                    )

                parquet_writer.write_table(table)

                # 4. Aggregate report data for this chunk.
                category_parts.append(
                    cleaned.groupby("category", as_index=False)
                    .agg(
                        total_items=("quantity", "sum"),
                        total_revenue=("total_amount", "sum"),
                        total_orders=("order_id", "nunique"),
                    )
                )

                product_parts.append(
                    cleaned.groupby("product", as_index=False)
                    .agg(
                        total_quantity=("quantity", "sum"),
                        total_revenue=("total_amount", "sum"),
                    )
                )

            first_chunk = False

            print(
                f"Processed chunk {chunk_number}: "
                f"{len(orders)} input rows"
            )

        # 5. Handle an empty CSV containing headers only.
        if first_chunk:
            empty_orders = pd.read_csv(input_file, nrows=0)
            cleaned, rejected = validate_orders(empty_orders)

            cleaned.to_csv(cleaned_csv, index=False)
            rejected.to_csv(rejected_csv, index=False)

        # 6. Combine category reports across all chunks.
        if category_parts:
            category_report = (
                pd.concat(category_parts, ignore_index=True)
                .groupby("category", as_index=False)
                .agg(
                    total_items=("total_items", "sum"),
                    total_revenue=("total_revenue", "sum"),
                    total_orders=("total_orders", "sum"),
                )
                .sort_values(
                    "total_revenue", ascending=False
                )
            )
        else:
            category_report = pd.DataFrame(
                columns=[
                    "category",
                    "total_items",
                    "total_revenue",
                    "total_orders",
                ]
            )

        # 7. Combine product reports across all chunks.
        if product_parts:
            product_report = (
                pd.concat(product_parts, ignore_index=True)
                .groupby("product", as_index=False)
                .agg(
                    total_quantity=("total_quantity", "sum"),
                    total_revenue=("total_revenue", "sum"),
                )
                .sort_values(
                    "total_revenue", ascending=False
                )
            )
        else:
            product_report = pd.DataFrame(
                columns=[
                    "product",
                    "total_quantity",
                    "total_revenue",
                ]
            )

        # 8. Save final reports.
        category_report.to_csv(category_file, index=False)
        product_report.to_csv(product_file, index=False)

    finally:
        if parquet_writer is not None:
            parquet_writer.close()

    # 9. Print processing summary.
    elapsed_time = time.perf_counter() - start_time

    print("\n--- DATA QUALITY SUMMARY ---")
    print(f"Input records: {input_count}")
    print(f"Valid records: {valid_count}")
    print(f"Rejected records: {rejected_count}")

    if input_count > 0:
        valid_percentage = valid_count / input_count * 100
        print(f"Valid data percentage: {valid_percentage:.2f}%")

    print(f"Chunk size: {chunk_size}")
    print(f"Execution time: {elapsed_time:.4f} seconds")
    print(f"Output directory: {output_dir}")
    print("\nProcessing completed successfully!")


if __name__ == "__main__":
    main()
