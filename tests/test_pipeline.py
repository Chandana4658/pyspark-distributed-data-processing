
import unittest
import pandas as pd
import pytest

from main import validate_orders, check_data_quality


class TestOrderPipeline(unittest.TestCase):

    def setUp(self):
        self.orders = pd.DataFrame({
            "order_id": [1, 2, 3],
            "customer_name": ["Ravi", "", "Sita"],
            "product": ["Laptop", "Mouse", "Chair"],
            "category": [
                "Electronics", "Electronics", "Furniture"
            ],
            "quantity": [1, 2, -1],
            "price": [50000, 500, 2000],
        })

    def test_valid_order_is_kept(self):
        cleaned, rejected = validate_orders(self.orders)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["order_id"], 1)

    def test_missing_customer_is_rejected(self):
        cleaned, rejected = validate_orders(self.orders)
        self.assertIn(2, rejected["order_id"].tolist())

    def test_negative_quantity_is_rejected(self):
        cleaned, rejected = validate_orders(self.orders)
        self.assertIn(3, rejected["order_id"].tolist())

    def test_revenue_calculation(self):
        cleaned, rejected = validate_orders(self.orders)
        self.assertEqual(cleaned.iloc[0]["total_amount"], 50000)

    def test_rejection_reason_is_recorded(self):
        cleaned, rejected = validate_orders(self.orders)
        row = rejected.loc[
            rejected["order_id"] == 2
        ].iloc[0]

        self.assertIn(
            "Missing customer name",
            row["rejection_reason"],
        )


def test_data_quality_valid_summary():
    assert check_data_quality(
        input_count=100000,
        valid_count=99867,
        rejected_count=133,
        valid_percentage=99.867,
        rejected_percentage=0.133,
    )


def test_data_quality_rejects_inconsistent_counts():
    with pytest.raises(ValueError, match="Input count"):
        check_data_quality(
            input_count=100,
            valid_count=80,
            rejected_count=10,
            valid_percentage=80.0,
            rejected_percentage=10.0,
        )


def test_data_quality_rejects_negative_counts():
    with pytest.raises(ValueError, match="cannot be negative"):
        check_data_quality(
            input_count=100,
            valid_count=-10,
            rejected_count=110,
            valid_percentage=0.0,
            rejected_percentage=100.0,
        )


def test_data_quality_rejects_incorrect_percentages():
    with pytest.raises(ValueError, match="Valid percentage"):
        check_data_quality(
            input_count=100,
            valid_count=80,
            rejected_count=20,
            valid_percentage=70.0,
            rejected_percentage=30.0,
        )


def test_missing_required_column_is_rejected():
    orders = pd.DataFrame({
        "order_id": ["ORD001"],
        "customer_name": ["Alice"],
        "product": ["Laptop"],
        "category": ["Electronics"],
        "quantity": [1],
        # The required price column is missing.
    })

    with pytest.raises(ValueError, match="missing required columns"):
        validate_orders(orders)


def test_duplicate_order_id_across_chunks_is_rejected():
    first_chunk = pd.DataFrame({
        "order_id": ["ORD001"],
        "customer_name": ["Alice"],
        "product": ["Laptop"],
        "category": ["Electronics"],
        "quantity": [1],
        "price": [50000],
    })

    second_chunk = pd.DataFrame({
        "order_id": ["ORD001"],
        "customer_name": ["Bob"],
        "product": ["Phone"],
        "category": ["Electronics"],
        "quantity": [2],
        "price": [20000],
    })

    seen_order_ids = set()

    cleaned_first, rejected_first = validate_orders(
        first_chunk,
        seen_order_ids=seen_order_ids,
    )

    cleaned_second, rejected_second = validate_orders(
        second_chunk,
        seen_order_ids=seen_order_ids,
    )

    assert len(cleaned_first) == 1
    assert len(rejected_first) == 0

    assert len(cleaned_second) == 0
    assert len(rejected_second) == 1

    assert (
        "Duplicate order ID"
        in rejected_second.iloc[0]["rejection_reason"]
    )



def test_empty_orders_dataframe():
    columns = [
        "order_id",
        "customer_name",
        "product",
        "category",
        "quantity",
        "price",
    ]

    empty_orders = pd.DataFrame(columns=columns)

    cleaned, rejected = validate_orders(empty_orders)

    assert cleaned.empty
    assert rejected.empty
    assert "total_amount" in cleaned.columns
    assert "rejection_reason" in rejected.columns

if __name__ == "__main__":
    unittest.main()
