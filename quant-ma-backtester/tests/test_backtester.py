from datetime import date, timedelta
import unittest

from src.backtester import BacktestConfig, PriceBar, calculate_metrics, load_prices, run_backtest


class BacktesterTests(unittest.TestCase):
    def test_config_rejects_invalid_windows(self) -> None:
        with self.assertRaises(ValueError):
            BacktestConfig(short_window=50, long_window=20).validate()

    def test_load_prices_sorts_dates(self) -> None:
        prices = load_prices("data/sample_prices.csv")

        self.assertGreater(len(prices), 0)
        self.assertTrue(all(prices[index].trading_date <= prices[index + 1].trading_date for index in range(len(prices) - 1)))

    def test_backtest_outputs_expected_values(self) -> None:
        prices = [
            PriceBar(trading_date=date(2024, 1, 1) + timedelta(days=index), close=100 + index)
            for index in range(80)
        ]
        config = BacktestConfig(short_window=5, long_window=20, initial_capital=1000)
        rows = run_backtest(prices, config)
        metrics = calculate_metrics(rows, config.initial_capital)

        self.assertIn("strategy_value", rows[-1])
        self.assertIn("buy_hold_value", rows[-1])
        self.assertGreater(float(rows[-1]["strategy_value"]), 1000)
        self.assertAlmostEqual(metrics["strategy_final_value"], float(rows[-1]["strategy_value"]))


if __name__ == "__main__":
    unittest.main()

