
from pathlib import Path
import pandas as pd


def main():
    project_dir = Path(__file__).resolve().parent
    input_file = project_dir / "data" / "orders.csv"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read raw data
    orders = pd.read_csv(input_file)
    input_count = len(orders)

    print("\n--- RAW DATA ---")
    print(orders.to_string(index=False))

    # 2. Clean text fields and numeric values
    for column in ["customer_name", "product", "category"]:
        orders[column] = orders[column].astype("string").str.strip()

    orders["quantity"] = pd.to_numeric(
        orders["quantity"], errors="coerce"
    )
    orders["price"] = pd.to_numeric(
        orders["price"], errors="coerce"
    )

    # 3. Validate every record and capture rejection reasons
    rejection_reasons = []

    seen_order_ids = set()

    for _, row in orders.iterrows():
        reasons = []

        order_id = row["order_id"]

        if pd.isna(order_id):
            reasons.append("Missing order ID")
        else:
            # Treat repeated order IDs after the first as duplicates.
            if order_id in seen_order_ids:
                reasons.append("Duplicate order ID")
            else:
                seen_order_ids.add(order_id)

        if pd.isna(row["customer_name"]) or row["customer_name"] == "":
            reasons.append("Missing customer name")

        if pd.isna(row["product"]) or row["product"] == "":
            reasons.append("Missing product")

        if pd.isna(row["category"]) or row["category"] == "":
            reasons.append("Missing category")

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

    # 4. Split valid and rejected records
    rejected = orders.loc[
        orders["rejection_reason"] != ""
    ].copy()

    cleaned = orders.loc[
        orders["rejection_reason"] == ""
    ].drop(columns=["rejection_reason"]).copy()

    rejected_count = len(rejected)

    print("\n--- REJECTED RECORDS ---")
    if rejected.empty:
        print("No rejected records.")
    else:
        print(rejected.to_string(index=False))

    # 5. Transform valid records
    cleaned["total_amount"] = (
        cleaned["quantity"] * cleaned["price"]
    ).round(2)

    print("\n--- CLEANED DATA ---")
    print(cleaned.to_string(index=False))

    # 6. Generate category-wise report
    category_report = (
        cleaned.groupby("category", as_index=False)
        .agg(
            total_items=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 7. Generate product-wise report
    product_report = (
        cleaned.groupby("product", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 8. Save processed data and quality reports
    cleaned.to_csv(output_dir / "cleaned_orders.csv", index=False)

    category_report.to_csv(
        output_dir / "category_report.csv", index=False
    )

    product_report.to_csv(
        output_dir / "product_report.csv", index=False
    )

    rejected.to_csv(
        output_dir / "rejected_records.csv", index=False
    )

    cleaned.to_parquet(
        output_dir / "cleaned_orders.parquet", index=False
    )

    # 9. Print data quality summary
    print("\n--- DATA QUALITY SUMMARY ---")
    print(f"Input records: {input_count}")
    print(f"Valid records: {len(cleaned)}")
    print(f"Rejected records: {rejected_count}")

    if input_count:
        valid_percentage = len(cleaned) / input_count * 100
        print(f"Valid data percentage: {valid_percentage:.2f}%")

    print(f"Quality report: {output_dir / 'rejected_records.csv'}")
    print("\nProcessing completed successfully!")


if __name__ == "__main__":
    main()
