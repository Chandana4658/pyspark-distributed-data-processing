
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

CSV_PATH = "output/cleaned_orders.csv"

def load_orders():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}. Run main.py first.")

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "order_id", "customer_name", "product", "category",
        "quantity", "price", "total_amount"
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    df = df[required_columns].copy()
    df["order_id"] = df["order_id"].astype(str)

    password = os.getenv("PGPASSWORD")
    if not password:
        raise ValueError("Set PGPASSWORD in PowerShell before running this script.")

    connection = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "orders_db"),
        user=os.getenv("PGUSER", "postgres"),
        password=password,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                rows = [
                    tuple(None if pd.isna(v) else v for v in row)
                    for row in df.itertuples(index=False, name=None)
                ]

                if rows:
                    execute_values(
                        cursor,
                        """
                        INSERT INTO orders
                        (order_id, customer_name, product, category,
                         quantity, price, total_amount)
                        VALUES %s
                        ON CONFLICT (order_id) DO NOTHING
                        """,
                        rows,
                        page_size=1000,
                    )

                cursor.execute("SELECT COUNT(*) FROM orders")
                total = cursor.fetchone()[0]

        print(f"CSV rows read: {len(df)}")
        print(f"Rows in PostgreSQL orders table: {total}")

    finally:
        connection.close()


if __name__ == "__main__":
    load_orders()
