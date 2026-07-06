# Moving Average Crossover Backtester

A beginner-friendly quant development project that tests a simple trading rule:

> Buy when the short moving average is above the long moving average, otherwise stay in cash.

This project is intentionally small, but it shows the core workflow used in quantitative research:

- load market price data
- create trading signals
- avoid look-ahead bias by shifting positions
- compare the strategy against buy-and-hold
- calculate performance and risk metrics
- save daily backtest results to CSV
- optionally generate a chart for analysis

## Project Structure

```text
quant-ma-backtester/
|-- data/
|   `-- sample_prices.csv
|-- src/
|   `-- backtester.py
|-- tests/
|   `-- test_backtester.py
|-- run_backtest.py
|-- requirements.txt
`-- README.md
```

## Setup

The backtest itself uses only the Python standard library, so it can run immediately.

```bash
python run_backtest.py
```

For optional chart generation, install `matplotlib`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Run The Backtest

```bash
python run_backtest.py
```

You can also change the moving-average windows:

```bash
python run_backtest.py --short-window 10 --long-window 30
```

Detailed daily results are saved to:

```text
results/backtest_results.csv
```

If `matplotlib` is installed, the chart is saved to:

```text
results/backtest.png
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## Example Output

The script prints metrics like:

- strategy total return
- buy-and-hold total return
- final portfolio value
- annualized volatility
- maximum drawdown
- Sharpe ratio
- time in market

## Data Format

Use any CSV with these columns:

```csv
Date,Close
2024-01-01,100.0
2024-01-02,101.2
```

Then run:

```bash
python run_backtest.py --data path/to/your_prices.csv
```

## Ideas To Improve It

- Add transaction costs
- Add short selling
- Test many ticker symbols
- Replace the sample CSV with real market data
- Download data from Yahoo Finance
- Add more strategies like RSI or mean reversion
- Build a small Streamlit dashboard

## Why This Is Useful For Quant Dev

This project teaches the basic loop behind many quant projects: take historical data, define a strategy, simulate it carefully, then judge the result using metrics instead of gut feeling.
