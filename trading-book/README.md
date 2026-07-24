# Trading Book — 300 Real-Data Chart Plates

A library of 300 annotated trading-education chart plates (2560×1440 lossless
PNG), each built from **genuine historical market data** and rendered with a
consistent publication design system. Every plate carries its ticker, market,
timeframe, focal bar timestamp, timezone, price scale, volume, a professional
annotation layer (zones, structure, arrows, entry/SL/TP with computed
risk-reward), a short lesson, and a provenance footer.

## Data provenance — no simulated prices, anywhere

This project was produced in a sandboxed environment whose network policy
blocks market-data hosts (TradingView, Binance, Yahoo Finance, Stooq, FRED were
all tested and denied). Rather than fabricate charts, the pipeline uses the
real historical datasets that ship inside published Python packages:

| Series | Coverage | Source package | Authenticity checks performed |
|---|---|---|---|
| GOOG (NASDAQ) daily | 2004-08-19 → 2013-03-01 | `backtesting` (backtesting.py) | Reproduces the documented +19.1% earnings gap (2008-04-18), −10.1% miss gap (2006-02-01), and the 2012-10-18 intraday early-release selloff |
| EURUSD 1H (+4H resample) | 2017-04 → 2018-02 | `backtesting` | Hourly volume peaks exactly at London (07:00 UTC) and New York (12:30–15:00 UTC) opens; FOMC/ECB/NFP reactions land on their documented dates & hours |
| ASML.AS daily | 2010 → 2013 | `stockstats` test data | Yahoo Finance export, cross-checked ranges |
| 002032.SZ (Supor) daily | 2004 → 2015 | `stockstats` test data | Shenzhen SE daily OHLCV |
| US GDP / CPI / rates / unemployment (quarterly) | 1959 → 2009 | `statsmodels` `macrodata` (FRED) | Official Federal Reserve data compilation |

Weekly/monthly/4-hour plates are standard OHLCV aggregations of those real
bars. Every annotation marks an event **algorithmically detected in the data**
(gaps, sweeps, structure breaks, pattern geometry, indicator crosses) — nothing
is drawn that did not happen.

**Honest limitation:** the original brief requested 27 markets (BTC, Gold,
indices, …) via TradingView screenshots. Neither browser automation nor any
market-data API is reachable from this environment, so the 300 plates cover the
five real datasets above. `pipeline/net_fetch.py` contains ready fetchers for
Binance / Yahoo / Stooq: allow those hosts in the environment's network policy
(or run locally) and re-run the build to regenerate the full multi-market
version with no other changes.

## Outputs

```
Trading Book Images/
  SMC/  ICT/  Price Action/  Technical Analysis/  Indicators/
  Wyckoff/  Elliott/  Fibonacci/  Fundamental Analysis/
  index.csv          # Image Name, Topic, Ticker, Date, Timeframe, Concept, Market, Data Source
Trading_Book_300_Charts.zip
```

Plates are numbered 001–300 globally, grouped by category. No two plates share
a focal date on the same instrument (enforced by the catalog's global dedupe).

## Reproduce

```bash
pip install backtesting mplfinance stockstats statsmodels scipy pandas
cd trading-book
python3 -m pipeline.build
```

## Pipeline

- `pipeline/data_sources.py` — real-data loaders, resampling, provenance metadata
- `pipeline/indicators.py` — textbook indicator implementations (RSI, MACD, BB, ATR, ADX, Ichimoku, VWAP, volume profile, …)
- `pipeline/detectors.py` — setup detection on real series (FVG, order blocks, BOS/CHoCH, sweeps, equal levels, H&S, double tops, triangles, wedges, flags, springs, divergences, …)
- `pipeline/annotate.py` — the publication renderer (2560×1440, consistent palette & typography, CVD-safe candle colors, annotation toolkit)
- `pipeline/cases_*.py` — the 300-case catalog builders per category, with lesson text
- `pipeline/build.py` — orchestration, index.csv, ZIP
