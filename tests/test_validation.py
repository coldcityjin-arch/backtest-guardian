import unittest
from datetime import datetime, timedelta

from backtest_guardian import validate_prices


class ValidationTests(unittest.TestCase):
    def test_clean_data(self):
        start = datetime(2025, 1, 1)
        self.assertEqual(validate_prices([start, start + timedelta(days=1)], [100, 101]), [])

    def test_flags_duplicates_order_and_bad_prices(self):
        now = datetime(2025, 1, 1)
        issues = validate_prices([now, now], [100, float("nan")])
        codes = {issue.code for issue in issues}
        self.assertTrue({"duplicate_timestamp", "non_monotonic_time", "non_finite_price"} <= codes)


if __name__ == "__main__":
    unittest.main()

