import unittest

from backtest_guardian import CostModel, walk_forward


class WalkForwardTests(unittest.TestCase):
    def test_folds_are_strictly_forward_and_cover_tail(self):
        prices = [100 + i + (i % 3) for i in range(30)]
        folds = walk_forward(prices, [2, 3, 5], initial_train=12, test_size=7, costs=CostModel(1, 1))
        self.assertEqual([(f.train_end, f.test_end) for f in folds], [(12, 19), (19, 26), (26, 30)])
        self.assertTrue(all(f.selected_window in {2, 3, 5} for f in folds))


if __name__ == "__main__":
    unittest.main()

