# Backtest Guardian

Backtest Guardian is a small, auditable Python toolkit for detecting common sources of false confidence in time-series strategy research.

It provides:

- explicit next-bar execution so a signal computed at close `t` cannot earn return before `t+1`;
- anchored walk-forward parameter selection with untouched forward test blocks;
- commission and slippage modeling based on portfolio turnover;
- timestamp, duplicate, ordering, finite-value, and positive-price validation;
- a dependency-free Python core, command-line report, and automated tests.

> This project is research software, not investment advice. Results do not predict future performance.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run it against a CSV containing `timestamp` and `close` columns:

```bash
backtest-guardian prices.csv --window 20 --commission-bps 1 --slippage-bps 2 --walk-forward
```

The command validates input before calculating total return, maximum drawdown, annualized Sharpe ratio, turnover, modeled costs, and optional walk-forward fold results.

## Look-ahead policy

Indicators may use observations through bar `t`, but the position is applied only to the return from `t` to `t+1`. The engine implements this invariant directly: `signals[t-1]` controls the price move from `prices[t-1]` to `prices[t]`. Tests pin this behavior.

## Walk-forward policy

For each fold, candidate moving-average windows are evaluated only on the anchored training prefix. The best window is then frozen and evaluated on the next chronological block. Indicator history is carried into the boundary, while performance is measured only in the test block.

## Scope and limitations

The MVP models a single asset, long/cash exposure, close-to-close returns, and linear costs. It does not model taxes, borrow, market impact, partial fills, corporate actions, or survivorship bias. Data must already be adjusted appropriately for the intended study.

## Contributing

Bug reports and focused pull requests are welcome. Please include a regression test when changing execution timing, fold boundaries, cost calculations, or validation rules.

## License

MIT
