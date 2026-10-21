
import unittest
import pandas as pd

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
            "Missing customer name", row["rejection_reason"]
        )


if __name__ == "__main__":
    unittest.main()




def test_data_quality_valid_summary():
    assert check_data_quality(
        input_count=100000,
        valid_count=99867,
        rejected_count=133,
        valid_percentage=99.867,
        rejected_percentage=0.133,
    )


def test_data_quality_rejects_inconsistent_counts():
    import pytest

    with pytest.raises(ValueError, match="Input count"):
        check_data_quality(
            input_count=100,
            valid_count=80,
            rejected_count=10,
            valid_percentage=80.0,
            rejected_percentage=10.0,
        )


def test_data_quality_rejects_negative_counts():
    import pytest

    with pytest.raises(ValueError, match="cannot be negative"):
        check_data_quality(
            input_count=100,
            valid_count=-10,
            rejected_count=110,
            valid_percentage=0.0,
            rejected_percentage=100.0,
        )


def test_data_quality_rejects_incorrect_percentages():
    import pytest

    with pytest.raises(ValueError, match="Valid percentage"):
        check_data_quality(
            input_count=100,
            valid_count=80,
            rejected_count=20,
            valid_percentage=70.0,
            rejected_percentage=30.0,
        )
