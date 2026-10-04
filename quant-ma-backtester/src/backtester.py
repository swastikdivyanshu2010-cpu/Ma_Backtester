from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev


TRADING_DAYS = 252


@dataclass(frozen=True)
class PriceBar:
    trading_date: date
    close: float


@dataclass(frozen=True)
class BacktestConfig:
    short_window: int = 20
    long_window: int = 50
    initial_capital: float = 10_000.0

    def validate(self) -> None:
        if self.short_window <= 0:
            raise ValueError("short_window must be positive")
        if self.long_window <= 0:
            raise ValueError("long_window must be positive")
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be smaller than long_window")
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be positive")


def load_prices(csv_path: str | Path) -> list[PriceBar]:
    with Path(csv_path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or {"Date", "Close"}.difference(reader.fieldnames):
            raise ValueError("CSV must contain Date and Close columns")

        prices = [
            PriceBar(
                trading_date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                close=float(row["Close"]),
            )
            for row in reader
            if row.get("Date") and row.get("Close")
        ]

    if not prices:
        raise ValueError("Price file does not contain usable rows")

    return sorted(prices, key=lambda bar: bar.trading_date)


def moving_average(values: list[float], window: int) -> list[float | None]:
    averages: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            averages.append(None)
            continue
        window_values = values[index + 1 - window : index + 1]
        averages.append(mean(window_values))
    return averages


def run_backtest(prices: list[PriceBar], config: BacktestConfig) -> list[dict[str, float | int | date | None]]:
    config.validate()
    closes = [bar.close for bar in prices]
    short_ma = moving_average(closes, config.short_window)
    long_ma = moving_average(closes, config.long_window)

    rows: list[dict[str, float | int | date | None]] = []
    strategy_value = config.initial_capital
    buy_hold_value = config.initial_capital
    previous_signal = 0

    start_index = config.long_window - 1

    for index, bar in enumerate(prices):
        if index < start_index:
            continue

        market_return = 0.0 if index == start_index else bar.close / prices[index - 1].close - 1
        position = previous_signal
        strategy_return = position * market_return
        strategy_value *= 1 + strategy_return
        buy_hold_value *= 1 + market_return

        current_signal = 1 if short_ma[index] is not None and long_ma[index] is not None and short_ma[index] > long_ma[index] else 0
        previous_signal = current_signal

        rows.append(
            {
                "date": bar.trading_date,
                "close": bar.close,
                "short_ma": short_ma[index],
                "long_ma": long_ma[index],
                "signal": current_signal,
                "position": position,
                "market_return": market_return,
                "strategy_return": strategy_return,
                "buy_hold_value": buy_hold_value,
                "strategy_value": strategy_value,
            }
        )

    return rows


def calculate_metrics(rows: list[dict[str, float | int | date | None]], initial_capital: float) -> dict[str, float]:
    # Exclude the first row (initialization day) for statistical metrics to avoid an artificial 0 return
    active_rows = rows[1:] if len(rows) > 1 else rows

    strategy_returns = [float(row["strategy_return"]) for row in active_rows]
    market_returns = [float(row["market_return"]) for row in active_rows]

    strategy_values = [float(row["strategy_value"]) for row in rows]
    buy_hold_values = [float(row["buy_hold_value"]) for row in rows]

    running_peak = strategy_values[0]
    drawdowns: list[float] = []

    for value in strategy_values:
        running_peak = max(running_peak, value)
        drawdowns.append(value / running_peak - 1)

    volatility = pstdev(strategy_returns) * sqrt(TRADING_DAYS)
    sharpe_ratio = 0.0 if pstdev(strategy_returns) == 0 else mean(strategy_returns) / pstdev(strategy_returns) * sqrt(TRADING_DAYS)

    return {
        "strategy_total_return_pct": (strategy_values[-1] / initial_capital - 1) * 100,
        "buy_hold_total_return_pct": (buy_hold_values[-1] / initial_capital - 1) * 100,
        "strategy_final_value": strategy_values[-1],
        "buy_hold_final_value": buy_hold_values[-1],
        "annualized_volatility_pct": volatility * 100,
        "max_drawdown_pct": min(drawdowns) * 100,
        "sharpe_ratio": sharpe_ratio,
        "time_in_market_pct": mean(float(row["position"]) for row in active_rows) * 100,
        "average_daily_buy_hold_return_pct": mean(market_returns) * 100,
    }


def save_results_csv(rows: list[dict[str, float | int | date | None]], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_plot(rows: list[dict[str, float | int | date | None]], output_path: str | Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(dates, [row["close"] for row in rows], label="Close", linewidth=1.6)
    axes[0].plot(dates, [row["short_ma"] for row in rows], label="Short MA", linewidth=1.2)
    axes[0].plot(dates, [row["long_ma"] for row in rows], label="Long MA", linewidth=1.2)
    axes[0].set_title("Moving Average Crossover")
    axes[0].set_ylabel("Price")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(dates, [row["strategy_value"] for row in rows], label="Strategy", linewidth=1.6)
    axes[1].plot(dates, [row["buy_hold_value"] for row in rows], label="Buy & Hold", linewidth=1.6)
    axes[1].set_title("Portfolio Value")
    axes[1].set_ylabel("Value")
    axes[1].legend()
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True

