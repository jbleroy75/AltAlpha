# AltAlpha Quant Terminal

AltAlpha is a personal **quantitative-research platform for alternative data**. It collects public market-adjacent datasets, normalizes them point-in-time, combines them into signals, backtests portfolios, measures risk and validates strategies out-of-sample through a responsive FastAPI web terminal.

> **Status:** research framework / portfolio project. AltAlpha is not a broker-connected execution system or a commercial market-data/risk-model replacement.

## One-click setup

```bash
git clone https://github.com/jbleroy75/AltAlpha.git
cd AltAlpha
./start.sh
```

On **Windows**, use `start.bat`. On **macOS**, `start.command` can also be launched from Finder.

The launcher automatically creates `.venv`, installs the required Python packages, creates `.env`, initializes the database, starts FastAPI and opens the terminal. On the first launch AltAlpha can also start its initial data synchronization automatically.

## Screenshots

### Research overview
![AltAlpha research overview](docs/screenshots/01-overview.svg)

### Signal screener
![AltAlpha signal screener](docs/screenshots/02-signals.svg)

### Portfolio backtest
![AltAlpha portfolio backtest](docs/screenshots/03-backtest.svg)

### Risk & statistical validation
![AltAlpha risk and statistical validation](docs/screenshots/04-risk-validation.svg)

### Alpha Discovery Lab
![AltAlpha Alpha Discovery Lab](docs/screenshots/05-alpha-discovery.svg)

### Open-data sources
![AltAlpha data sources](docs/screenshots/06-data-sources.svg)

## Why point-in-time matters

Alternative datasets are delayed, heterogeneous and easy to backtest incorrectly. Every normalized AltAlpha event distinguishes:

- `event_at` — when the underlying economic event occurred;
- `published_at` — when the information became publicly observable.

The signal engine acts on `published_at`, not blindly on the economic event date, to reduce look-ahead bias.

```text
Alternative data
      ↓
Entity / security resolution
      ↓
Point-in-time normalization
      ↓
Signal construction
      ↓
Multi-signal scoring
      ↓
Risk model & optimizer
      ↓
Execution-cost model
      ↓
Portfolio backtest
      ↓
Walk-forward / statistical validation
```

## Open-data-first synchronization

AltAlpha aims for a **clone → start → data arrives automatically** workflow wherever public or openly accessible sources make that possible.

| Dataset | Default source | Status |
|---|---|---|
| Insider transactions | SEC EDGAR / Form 4 | automatic |
| Institutional holdings | SEC 13F | automatic |
| Earnings facts | SEC Company Facts | automatic |
| Lobbying | Senate LDA API | automatic |
| Government contracts | USAspending | automatic |
| Congress House / Senate | public gateway sourced from STOCK Act filings | automatic, recent window |
| Short interest | FINRA Consolidated Short Interest | automatic |
| Social mentions | Bluesky public API | automatic |
| Historical prices | Stooq development adapter | automatic |
| Patents | USPTO Open Data Portal | public data; account/API key required |
| Google Trends | official API adapter | limited-access API |
| Options flow | normalized import adapter | professional history generally licensed |
| Corporate flights | normalized import adapter | historical feeds may be licence constrained |
| Earnings transcripts | normalized import adapter | no single uniform official API |

The **SYNC ALL DATA** control reports each source as `synced`, `skipped`, `missing_import` or `error`. Gated/licensed data is never silently replaced with fabricated observations.

The keyless Congress connector intentionally synchronizes a **recent window** and does not claim to provide a complete historical Congress database.

## Quant research engine

### Multi-signal scoring

Signals can be combined using configurable weights, lookbacks, thresholds and holding periods.

```yaml
weights:
  sec_form4: 1.5
  congress_house: 1.2
  congress_senate: 1.2
  usaspending: 1.0
  options_flow: 1.0
  finra_short_interest: -0.8
  sec_companyfacts: 0.8
```

### Portfolio backtesting

The daily simulator supports long-only / long-short portfolios, holding periods, max-position sizing, gross/net exposure, transaction costs, slippage, turnover and benchmark comparison.

Research analytics include **CAGR, volatility, Sharpe, Sortino, Calmar, maximum drawdown, alpha, beta, Information Ratio and monthly/annual returns**.

### Risk model & optimizer

AltAlpha includes a statistical **PCA factor-risk model** with component-risk attribution and a constrained **SLSQP portfolio optimizer** supporting max-position, gross/net exposure, turnover penalties, long/short bounds and sector-constraint hooks.

### Anti-overfitting controls

- walk-forward out-of-sample testing;
- Purged K-Fold primitives and embargo;
- Probabilistic Sharpe Ratio;
- Deflated Sharpe Ratio approximation;
- bootstrap Sharpe confidence intervals;
- winner-stability and negative-OOS-fold diagnostics.

The **Alpha Discovery Lab** ranks signal combinations using out-of-sample performance rather than full-sample fit alone.

## Security master

The security-master layer supports ticker, CIK, CUSIP, FIGI, company name, sector, exchange, validity dates and active/delisted state. Corporate-action storage is included for splits and distributions.

Institutional-grade survivorship-bias control would still require a licensed point-in-time universe and delisted-security price history.

## Responsive web terminal

The terminal includes **Overview, Signals, Company View, Backtest, Risk & Validation, Alpha Discovery and Data Sources**. Navigation wraps on narrow screens, cards and forms collapse to one column, charts remain fluid and dense tables use local horizontal scrolling.

## Architecture

```text
app/
├── collectors/          # Alternative-data ingestion
├── static/              # Responsive terminal
├── main.py              # FastAPI API / web app
├── models.py            # SQLAlchemy data model
├── sync_manager.py      # One-click source orchestration
├── strategy.py          # Signal engine
├── portfolio.py         # Daily portfolio simulator
├── risk_model.py        # PCA factor/risk model
├── optimizer.py         # Constrained optimizer
├── validation.py        # PSR, DSR, bootstrap, purged CV
├── discovery.py         # Walk-forward alpha discovery
├── security_master.py   # Security identifiers / validity
└── prices.py            # Development pricing adapter
```

## Tech stack

Python · FastAPI · SQLAlchemy · SQLite / PostgreSQL · NumPy · pandas · SciPy · scikit-learn · statsmodels · APScheduler · HTML/CSS/JavaScript

## Configuration

```env
WATCHLIST=AAPL,MSFT,NVDA,AMZN,META,GOOGL,TSLA,PLTR,JPM,GS
BOOTSTRAP_PRICE_YEARS=5
AUTO_SYNC_ON_FIRST_RUN=true
```

PostgreSQL can be enabled with:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/altalpha
```

Swagger is available at `http://127.0.0.1:8000/docs`.

## Tests

```bash
PYTHONPATH=. python -m pytest -q
```

Latest local V0.8 validation: **6 tests passed**.

## Research limitations

AltAlpha deliberately does **not** claim institutional production infrastructure. Serious deployment would additionally require institutional point-in-time pricing/universe data, stronger corporate-action history, calibrated market-impact and borrow models, richer factor data, capacity analysis, OMS/broker connectivity, production monitoring and broader test coverage.

## Interview summary

> Built a Python-based quantitative research platform aggregating alternative datasets including insider transactions, congressional disclosures, institutional holdings, government contracts and short-interest data. Implemented point-in-time event normalization, multi-signal strategy construction, constrained portfolio backtesting, factor-risk analytics and walk-forward / multiple-testing-aware validation, with a responsive FastAPI research terminal and one-click local data synchronization.

## License & third-party data

AltAlpha source code is licensed under the **MIT License**. External datasets and APIs remain subject to their providers' terms and redistribution rules. AltAlpha fetches data into the user's local database rather than bundling third-party raw datasets in the repository. See `NOTICE`.

## Disclaimer

Research and educational use only. This repository does not constitute investment advice and is not a production trading or execution system.
