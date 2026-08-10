# AltAlpha Quant Terminal

AltAlpha is a personal quantitative research platform for testing whether **alternative data contains persistent predictive information in public equities**.

It combines alternative-data ingestion, point-in-time normalization, multi-signal research, portfolio backtesting, risk modelling, statistical validation and a lightweight web terminal in one Python/FastAPI codebase.

> **Status:** research framework / portfolio project. It is **not** a broker-connected execution system and should not be treated as an institutional market-data or risk-model replacement.

## Why AltAlpha

Alternative datasets are often delayed, heterogeneous and easy to backtest incorrectly. AltAlpha is built around a simple research principle: **a strategy may only act on information that was actually public at that moment**.

Every event therefore distinguishes:

- `event_at` — when the underlying economic event happened;
- `published_at` — when the market could observe it.

The signal engine and backtester use `published_at` to reduce look-ahead bias.

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

## Alternative-data coverage

AltAlpha contains collectors or normalized ingestion adapters for:

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
- earnings transcript imports.

Some feeds are live public APIs, while others intentionally use import adapters because historical or commercial-quality data may be gated, licensed or document-oriented. AltAlpha does not attempt to bypass source access controls.

## Quant research engine

### Point-in-time event model

Events are normalized into a common schema with source, issuer, actor, ticker, side, economic value, event timestamp and publication timestamp. This makes heterogeneous datasets comparable while preserving information availability.

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

The daily portfolio simulator supports long-only or long/short portfolios, configurable holding periods, max-position sizing, gross/net exposure tracking, transaction costs, slippage, turnover and benchmark comparison.

Analytics include CAGR, annualized volatility, Sharpe, Sortino, Calmar, maximum drawdown, alpha, beta, Information Ratio, monthly/annual returns and equity/drawdown curves.

### Risk model

AltAlpha includes a **statistical PCA factor model** estimated from historical return windows, plus sector-exposure hooks from the security master. The risk layer calculates portfolio volatility, factor exposures, component-risk attribution and covariance matrices.

This is intentionally a statistical research model rather than a commercial Barra-style factor model.

### Constrained portfolio optimizer

The SLSQP optimizer supports expected returns, covariance-based risk penalization, max-position constraints, gross-exposure limits, target net exposure, long-only / long-short bounds, turnover penalties, sector-constraint hooks and configurable risk aversion.

### Anti-overfitting controls

AltAlpha includes:

- walk-forward out-of-sample testing;
- Purged K-Fold split primitives;
- embargo around validation folds;
- Probabilistic Sharpe Ratio;
- Deflated Sharpe Ratio approximation;
- bootstrap Sharpe confidence intervals;
- cross-fold winner-stability diagnostics;
- out-of-sample negative-fold diagnostics.

The Alpha Discovery Lab compares combinations of alternative signals using out-of-sample results rather than only full-sample backtests.

## Security master

The security-master layer is designed to associate ticker, CIK, CUSIP, FIGI, company name, sector, exchange, validity dates and active/delisted status. Corporate-action storage is included for splits and cash distributions.

For institutional-grade survivorship-bias control, the framework still requires a legally obtained point-in-time historical universe and delisted-security price database.

## Web terminal

The FastAPI application serves a browser-based research terminal at `/` with:

- **Overview** — dataset status and research summary;
- **Signals** — alternative-data screener;
- **Company view** — signal history by ticker;
- **Backtest** — configurable portfolio simulations;
- **Risk & Validation** — research controls and statistical diagnostics;
- **Alpha Discovery** — walk-forward signal-combination research;
- **Data Sources** — source inventory and event tape.

## Architecture

```text
app/
├── collectors/          # Alternative-data ingestion
├── static/              # Web terminal
├── main.py              # FastAPI application / endpoints
├── models.py            # SQLAlchemy data model
├── strategy.py          # Event-level signal strategy engine
├── portfolio.py         # Daily portfolio simulator
├── risk_model.py        # PCA factor/risk model
├── optimizer.py         # Constrained portfolio optimizer
├── validation.py        # PSR, DSR, bootstrap, purged CV
├── discovery.py         # Walk-forward alpha discovery
├── security_master.py   # Security identifiers / validity
├── scheduler.py         # Collection scheduler foundation
└── prices.py            # Development price-data adapter
```

## Tech stack

Python · FastAPI · SQLAlchemy · PostgreSQL / SQLite · NumPy · pandas · SciPy · scikit-learn · statsmodels · APScheduler · HTML/CSS/JavaScript

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.cli init-db
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` or Swagger at `http://127.0.0.1:8000/docs`.

## Example collectors

```bash
python -m app.cli sec-form4 --count 100
python -m app.cli sec-13f 1067983
python -m app.cli lobbying --client "Palantir" --year 2026
python -m app.cli contracts "Palantir" --days 730
python -m app.cli bluesky "NVIDIA" --ticker NVDA
python -m app.cli earnings 1045810 NVDA
```

## Import adapters

```bash
python -m app.cli import-congress data/imports/house.csv house
python -m app.cli import-congress data/imports/senate.csv senate
python -m app.cli import-patents data/imports/patents.csv
python -m app.cli import-options data/imports/options.csv
python -m app.cli import-short-interest data/imports/finra.txt
python -m app.cli import-flights data/imports/flights.csv
python -m app.cli import-transcripts data/imports/transcripts.csv
```

See `IMPORT_SCHEMAS.md` for expected columns.

## PostgreSQL

SQLite is the default development configuration. PostgreSQL can be used with:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/altalpha
```

## Research limitations

AltAlpha deliberately does **not** claim institutional production infrastructure. Serious deployment would still require licensed point-in-time universe/pricing data including delisted securities, stronger corporate-action history, calibrated bid/ask and market-impact models, borrow costs, richer style/fundamental factors, capacity analysis, broker/OMS connectivity, operational monitoring and broader automated test coverage.

The current project is best viewed as a **quantitative research laboratory for alternative data**.

## Interview summary

> Built a Python-based quantitative research platform aggregating alternative datasets including insider transactions, congressional disclosures, institutional holdings, government contracts and options activity. Implemented point-in-time event normalization, multi-signal strategy construction, constrained portfolio backtesting, factor-risk analytics and walk-forward / multiple-testing-aware statistical validation, with a FastAPI research terminal for visualization.

## Disclaimer

Research and educational use only. This repository does not constitute investment advice and is not a production trading or execution system.
