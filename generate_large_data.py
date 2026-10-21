
import csv
from pathlib import Path

project_dir = Path(__file__).resolve().parent
output_file = project_dir / "data" / "orders_large.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)

products = [
    ("Laptop", "Electronics", 50000),
    ("Mouse", "Electronics", 800),
    ("Keyboard", "Electronics", 1500),
    ("Chair", "Furniture", 6000),
    ("Desk", "Furniture", 12000),
    ("Notebook", "Stationery", 100),
]

total_rows = 100_000

with output_file.open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "customer_name",
        "product",
        "category",
        "quantity",
        "price",
    ])

    for i in range(1, total_rows + 1):
        product, category, price = products[(i - 1) % len(products)]

        quantity = -1 if i % 1000 == 0 else (i % 5) + 1
        customer = (
            "" if i % 1500 == 0
            else f"Customer_{i % 500}"
        )

        writer.writerow([
            i,
            customer,
            product,
            category,
            quantity,
            price,
        ])

print(f"Generated {total_rows:,} records.")
print(f"File: {output_file}")
