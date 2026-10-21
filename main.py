
from pathlib import Path
import pandas as pd


def validate_orders(orders):
    """Clean, validate, and separate valid and rejected orders."""
    orders = orders.copy()

    # 1. Clean text fields
    for column in ["customer_name", "product", "category"]:
        orders[column] = orders[column].astype("string").str.strip()

    # 2. Convert numeric columns
    orders["quantity"] = pd.to_numeric(
        orders["quantity"], errors="coerce"
    )
    orders["price"] = pd.to_numeric(
        orders["price"], errors="coerce"
    )

    # 3. Validate records and record rejection reasons
    rejection_reasons = []
    seen_order_ids = set()

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

    # 1. Read raw data
    orders = pd.read_csv(input_file)
    input_count = len(orders)

    print("\n--- RAW DATA ---")
    print(orders.to_string(index=False))

    # 2. Validate, clean, and transform
    cleaned, rejected = validate_orders(orders)

    print("\n--- REJECTED RECORDS ---")
    if rejected.empty:
        print("No rejected records.")
    else:
        print(rejected.to_string(index=False))

    print("\n--- CLEANED DATA ---")
    print(cleaned.to_string(index=False))

    # 3. Generate category-wise sales report
    category_report = (
        cleaned.groupby("category", as_index=False)
        .agg(
            total_items=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 4. Generate product-wise sales report
    product_report = (
        cleaned.groupby("product", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    # 5. Save output files
    cleaned.to_csv(
        output_dir / "cleaned_orders.csv", index=False
    )

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

    # 6. Print processing summary
    print("\n--- DATA QUALITY SUMMARY ---")
    print(f"Input records: {input_count}")
    print(f"Valid records: {len(cleaned)}")
    print(f"Rejected records: {len(rejected)}")

    if input_count:
        valid_percentage = len(cleaned) / input_count * 100
        print(f"Valid data percentage: {valid_percentage:.2f}%")

    print(f"Output directory: {output_dir}")
    print("\nProcessing completed successfully!")


if __name__ == "__main__":
    main()
