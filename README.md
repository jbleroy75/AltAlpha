# AltAlpha Quant Terminal

AltAlpha is a personal quantitative-research platform for testing whether **alternative data contains persistent predictive information in public equities**.

It combines alternative-data ingestion, point-in-time normalization, multi-signal research, portfolio backtesting, risk modelling, statistical validation and a responsive FastAPI web terminal.

> **Status:** research framework / portfolio project. AltAlpha is not a broker-connected execution system and is not a commercial market-data or risk-model replacement.

## One-click local setup

The default workflow is intentionally simple:

```bash
git clone https://github.com/jbleroy75/AltAlpha.git
cd AltAlpha
./start.sh
```

On **Windows**, double-click `start.bat`. On **macOS**, `start.command` can be launched from Finder.

On the first run AltAlpha automatically:

1. checks for Python 3.11+;
2. creates an isolated `.venv`;
3. installs **all Python dependencies** from `pyproject.toml`;
4. creates `.env` from `.env.example`;
5. initializes the database and import directories;
6. starts the FastAPI terminal;
7. opens `http://127.0.0.1:8000`;
8. starts the first data synchronization in the background;
9. bootstraps SEC ticker/CIK mappings for the configured watchlist;
10. downloads five years of development price history for the watchlist plus SPY.

The terminal also exposes **SYNC ALL DATA** for subsequent refreshes.

To install without starting the server, run `./install.sh` on macOS/Linux or `install.bat` on Windows.

## Why AltAlpha

Alternative datasets are delayed, heterogeneous and easy to backtest incorrectly. AltAlpha is built around one core rule: **a strategy may only act on information that was actually public at that moment**.

Every normalized event distinguishes:

- `event_at` — when the underlying economic event occurred;
- `published_at` — when the information became publicly observable.

The signal engine uses `published_at` to reduce look-ahead bias.

```text
Alternative data
      ↓
Entity / security resolution
      ↓
Point-in-time event normalization
      ↓
Signal construction
      ↓
Multi-signal scoring
      ↓
Risk model & portfolio optimizer
      ↓
Execution-cost model
      ↓
Portfolio backtest
      ↓
Walk-forward / statistical validation
```

## Data coverage

AltAlpha contains live collectors or normalized ingestion adapters for:

- SEC Form 4 insider transactions;
- US House and Senate congressional trading disclosures;
- SEC 13F institutional holdings;
- US federal lobbying disclosures;
- USAspending government-contract transactions;
- patents / USPTO exports;
- Google Trends adapter;
- Bluesky / social sentiment;
- options-flow imports;
- FINRA short-interest data;
- corporate-flight events;
- SEC Company Facts / earnings data;
- earnings-transcript imports;
- historical market prices for the configured watchlist and benchmark.

### Sync status

Each source explicitly reports one of:

- `synced` — the live collector or import completed;
- `skipped` — optional API access or configuration is missing;
- `missing_import` — a licensed/document-oriented source needs an export in `data/imports/`;
- `error` — the source failed and the UI displays the error.

AltAlpha does not silently replace gated or licensed datasets with fabricated data. Legally obtained exports placed in `data/imports/` are ingested automatically on the next sync.

## Quant research engine

### Multi-signal scoring

Signals can be combined into weighted composite scores with configurable lookbacks, thresholds and holding periods.

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

The daily portfolio simulator supports:

- long-only or long/short portfolios;
- configurable holding periods;
- max-position sizing;
- gross and net exposure tracking;
- transaction costs and slippage;
- turnover;
- benchmark comparison.

Analytics include CAGR, annualized volatility, Sharpe, Sortino, Calmar, maximum drawdown, alpha, beta, Information Ratio and monthly/annual returns.

### Risk model

AltAlpha includes a **statistical PCA factor model** estimated from historical return windows plus sector-exposure hooks from the security master. It calculates portfolio volatility, factor exposures and component-risk attribution.

### Constrained portfolio optimizer

The SLSQP optimizer supports expected returns, covariance-based risk penalization, max-position limits, gross exposure, target net exposure, long-only/long-short bounds, turnover penalties, sector-constraint hooks and configurable risk aversion.

### Anti-overfitting controls

AltAlpha includes:

- walk-forward out-of-sample testing;
- Purged K-Fold primitives;
- embargo around validation folds;
- Probabilistic Sharpe Ratio;
- Deflated Sharpe Ratio approximation;
- bootstrap Sharpe confidence intervals;
- cross-fold winner-stability diagnostics;
- out-of-sample negative-fold diagnostics.

The **Alpha Discovery Lab** compares signal combinations using out-of-sample results instead of ranking only full-sample backtests.

## Security master

The security-master layer supports ticker, CIK, CUSIP, FIGI, company name, sector, exchange, validity dates and active/delisted status. Corporate-action storage is included for splits and cash distributions.

For institutional-grade survivorship-bias control, a licensed point-in-time universe and delisted-security price database would still be required.

## Responsive web terminal

The browser terminal includes:

- **Overview** — dataset health, sync state and research summary;
- **Signals** — cross-source alternative-data screener;
- **Company view** — signal history by ticker;
- **Backtest** — configurable portfolio simulation and equity curve;
- **Risk & Validation** — research controls and statistical diagnostics;
- **Alpha Discovery** — walk-forward signal-combination research;
- **Data Sources** — source inventory and event tape.

The UI is responsive across desktop, tablet and mobile: navigation wraps, cards/forms collapse to a single column, charts remain fluid and dense tables use local horizontal scrolling.

## Architecture

```text
app/
├── collectors/          # Alternative-data ingestion
├── static/              # Responsive web terminal
├── main.py              # FastAPI API / web app
├── models.py            # SQLAlchemy data model
├── sync_manager.py      # One-click source orchestration
├── strategy.py          # Event-level signal engine
├── portfolio.py         # Daily portfolio simulator
├── risk_model.py        # PCA factor/risk model
├── optimizer.py         # Constrained optimizer
├── validation.py        # PSR, DSR, bootstrap, purged CV
├── discovery.py         # Walk-forward alpha discovery
├── security_master.py   # Security identifiers / validity
├── scheduler.py         # Scheduled collection foundation
└── prices.py            # Development price-data adapter
```

## Tech stack

Python · FastAPI · SQLAlchemy · SQLite / PostgreSQL · NumPy · pandas · SciPy · scikit-learn · statsmodels · APScheduler · HTML/CSS/JavaScript

## Configuration

Default watchlist:

```env
WATCHLIST=AAPL,MSFT,NVDA,AMZN,META,GOOGL,TSLA,PLTR,JPM,GS
BOOTSTRAP_PRICE_YEARS=5
AUTO_SYNC_ON_FIRST_RUN=true
```

SQLite is the default local database. PostgreSQL is supported with:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/altalpha
```

Swagger is available at `http://127.0.0.1:8000/docs`.

## Tests

The V0.7 local test suite currently covers point-in-time entry behaviour, optimizer constraints, statistical-validation utilities and sync-status persistence.

```bash
PYTHONPATH=. python -m pytest -q
```

Latest local validation before publication: **4 tests passed**.

## Research limitations

AltAlpha deliberately does **not** claim institutional production infrastructure. Serious deployment would still require licensed point-in-time universe/pricing data including delisted securities, stronger corporate-action history, calibrated bid/ask and market-impact models, borrow costs, richer style/fundamental factors, capacity analysis, broker/OMS connectivity, operational monitoring and broader automated test coverage.

The project is best viewed as a **quantitative research laboratory for alternative data**.

## Interview summary

> Built a Python-based quantitative research platform aggregating alternative datasets including insider transactions, congressional disclosures, institutional holdings, government contracts and options activity. Implemented point-in-time event normalization, multi-signal strategy construction, constrained portfolio backtesting, factor-risk analytics and walk-forward / multiple-testing-aware statistical validation, with a responsive FastAPI research terminal and one-click local data synchronization.

## License & third-party data

AltAlpha source code is licensed under the **MIT License**. External datasets, APIs and imported files remain subject to the terms, licenses and redistribution rules of their respective providers. See `NOTICE` for details.

## Disclaimer

Research and educational use only. This repository does not constitute investment advice and is not a production trading or execution system.
