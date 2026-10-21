
from pathlib import Path
import pandas as pd


def main():
    # Define project paths
    project_dir = Path(__file__).resolve().parent
    input_file = project_dir / "data" / "orders.csv"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read data
    orders = pd.read_csv(input_file)
    input_count = len(orders)

    print("\n--- RAW DATA ---")
    print(orders.to_string(index=False))

    # 2. Remove duplicate order IDs
    orders = orders.drop_duplicates(
        subset=["order_id"], keep="first"
    )
    deduplicated_count = len(orders)

    # 3. Clean text columns
    for column in ["customer_name", "product", "category"]:
        orders[column] = orders[column].astype("string").str.strip()

    # 4. Convert numeric columns safely
    orders["quantity"] = pd.to_numeric(
        orders["quantity"], errors="coerce"
    )
    orders["price"] = pd.to_numeric(
        orders["price"], errors="coerce"
    )

    # 5. Validate records
    valid_mask = (
        orders["order_id"].notna()
        & orders["customer_name"].notna()
        & orders["customer_name"].ne("")
        & orders["product"].notna()
        & orders["product"].ne("")
        & orders["category"].notna()
        & orders["category"].ne("")
        & orders["quantity"].notna()
        & orders["quantity"].gt(0)
        & orders["price"].notna()
        & orders["price"].gt(0)
    )

    cleaned = orders.loc[valid_mask].copy()
    rejected_count = deduplicated_count - len(cleaned)

    # 6. Transform data
    cleaned["total_amount"] = (
        cleaned["quantity"] * cleaned["price"]
    ).round(2)

    print("\n--- CLEANED DATA ---")
    print(cleaned.to_string(index=False))

    # 7. Generate category-wise report
    category_report = (
        cleaned.groupby("category", as_index=False)
        .agg(
            total_items=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 8. Generate product-wise report
    product_report = (
        cleaned.groupby("product", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 9. Save CSV outputs
    cleaned.to_csv(output_dir / "cleaned_orders.csv", index=False)
    category_report.to_csv(
        output_dir / "category_report.csv", index=False
    )
    product_report.to_csv(
        output_dir / "product_report.csv", index=False
    )

    # 10. Save Parquet output
    cleaned.to_parquet(
        output_dir / "cleaned_orders.parquet", index=False
    )

    # 11. Display processing summary
    print("\n--- PROCESSING SUMMARY ---")
    print(f"Input records: {input_count}")
    print(f"Records after deduplication: {deduplicated_count}")
    print(f"Valid records: {len(cleaned)}")
    print(f"Rejected records: {rejected_count}")
    print(f"Output folder: {output_dir}")
    print("\nProcessing completed successfully!")


if __name__ == "__main__":
    main()
