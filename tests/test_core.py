import unittest

from backtest_guardian import CostModel, backtest, moving_average_signal


class BacktestTests(unittest.TestCase):
    def test_signal_is_executed_next_bar(self):
        result = backtest([100, 200, 100], [1, 0, 0])
        self.assertEqual(result.positions, (0.0, 1.0, 0.0))
        self.assertAlmostEqual(result.total_return, 1.0)

    def test_future_price_cannot_change_prior_signal(self):
        a = moving_average_signal([10, 11, 12, 13], 2)
        b = moving_average_signal([10, 11, 12, 999], 2)
        self.assertEqual(a[:3], b[:3])

    def test_costs_reduce_returns_on_turnover(self):
        free = backtest([100, 101, 102], [1, 0, 0])
        costly = backtest([100, 101, 102], [1, 0, 0], CostModel(10, 10))
        self.assertLess(costly.total_return, free.total_return)
        self.assertAlmostEqual(costly.turnover, 2.0)


if __name__ == "__main__":
    unittest.main()

