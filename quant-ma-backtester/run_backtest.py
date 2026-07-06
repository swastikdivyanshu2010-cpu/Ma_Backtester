from __future__ import annotations

import argparse
from pathlib import Path

from src.backtester import BacktestConfig, calculate_metrics, load_prices, run_backtest, save_plot, save_results_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a moving-average crossover backtest.")
    parser.add_argument("--data", default="data/sample_prices.csv", help="CSV file with Date and Close columns.")
    parser.add_argument("--short-window", type=int, default=20, help="Short moving average window.")
    parser.add_argument("--long-window", type=int, default=50, help="Long moving average window.")
    parser.add_argument("--capital", type=float, default=10_000.0, help="Starting portfolio value.")
    parser.add_argument("--plot", default="results/backtest.png", help="Path for the output chart.")
    parser.add_argument("--results", default="results/backtest_results.csv", help="Path for detailed CSV results.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = BacktestConfig(
        short_window=args.short_window,
        long_window=args.long_window,
        initial_capital=args.capital,
    )
    prices = load_prices(args.data)
    rows = run_backtest(prices, config)
    metrics = calculate_metrics(rows, config.initial_capital)
    save_results_csv(rows, args.results)
    plot_created = save_plot(rows, args.plot)

    print("\nMoving Average Crossover Backtest")
    print("=" * 38)
    print(f"Rows tested: {len(rows)}")
    print(f"Date range: {rows[0]['date']} to {rows[-1]['date']}")
    print(f"Short / long windows: {config.short_window} / {config.long_window}")
    print(f"Detailed results saved to: {Path(args.results).resolve()}")
    if plot_created:
        print(f"Chart saved to: {Path(args.plot).resolve()}")
    else:
        print("Chart skipped: install matplotlib to generate PNG charts.")
    print("\nPerformance")
    print("-" * 38)
    for name, value in metrics.items():
        pretty_name = name.replace("_", " ").title()
        if name.endswith("_pct"):
            print(f"{pretty_name}: {value:.2f}%")
        elif "value" in name:
            print(f"{pretty_name}: ${value:,.2f}")
        else:
            print(f"{pretty_name}: {value:.2f}")


if __name__ == "__main__":
    main()
