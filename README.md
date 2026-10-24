# APEX Trader: multi-method market analysis platform

A self-hostable web platform that scans forex charts with 51 analysis methods in 16 independent families, grades each setup with an auditable
checklist, tells users **what** to look at (opportunity radar) and **when** conditions are sensible (session/liquidity/news timing), and
sells access in tiers through Paystack. Admin console, trade journal, alerts, calendar and headline feeds, email flows and an optional
admin-only trading panel are included. Python standard library only (plus `tzdata`).

> It is analysis software. It does not predict markets, does not trade for subscribers, and cannot promise profit. Validate any method on
> your own data (walk-forward is built in) and keep position sizes small.

## What is real and what you supply
Nothing in the product is fabricated: no bundled prices, no sample users, no placeholder dates. Production mode refuses to start on test data.

| You supply | How |
|---|---|
| Market data | OANDA (a free practice account serves real prices), optionally Twelve Data as automatic failover, or MetaTrader 5 |
| Payments | Your Paystack keys (added later; the app runs and shows billing as "not enabled" until then) |
| Email | Any SMTP provider |
| Legal identity | Company name, jurisdiction, support email, review date, and your confirmation that a lawyer reviewed the legal text |
| Prices | Your plan prices (explicit; there are no silent defaults for money in production) |

## Quick start (development with your own CSV files)
```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
mkdir -p dev/market_data           # put YOUR OWN OHLCV history here: EURUSD_M15.csv with columns time,open,high,low,close,volume
cp config/web.development.example.json dev/web.json
python -m apex.cli --config dev/web.json web-create-admin --email you@example.com
python -m apex.cli --config dev/web.json web-serve        # http://127.0.0.1:8080  (a TEST DATA banner is always shown in this mode)
```

## Production
Follow **`deploy/DEPLOY.md`** (VPS + systemd + Caddy). In short: `web-init` -> set secrets in `/etc/apex/env` -> `web-create-admin` -> `news-check` and
`web-check` -> `paystack-check` once keys arrive. The admin page shows a live **go-live checklist** (HTTPS, data provider, backup provider, Paystack key
validity and mode, SMTP connection, feeds, calendar, 2FA admin, audit integrity, backup freshness, legal, timezone data).

## Commands
| Command | Purpose |
|---|---|
| `web-init` | Generate a production config with safe defaults |
| `web-serve` / `web-create-admin` / `web-reset-admin-2fa` | Run the service; admin bootstrap (CLI only, 2FA mandatory) |
| `web-check [--strict]` | Live go-live readiness; exit 1 on failures |
| `paystack-check` | Validate the Paystack key and show what to register |
| `news-check` | Test that the calendar/news feeds are readable from this server |
| `web-backup --out FILE` | Online-safe SQLite backup (mode 600); `deploy/backup.sh` adds integrity check, retention, off-site hook |
| `scan`, `analyze`, `backtest`, `edge`, `walkforward --csv FILE` | Research tools on your own history |
| `verify-journal`, `reset-kill` | Admin trading panel audit/safety tools |

## Features
* **Analysis**: 51 methods / 16 families, regime-aware consensus, A/B/C checklist, three selectivity profiles, evidence weighting, walk-forward validation with confidence intervals, risk throttle after losses.
* **Opportunity radar** (Pro), **timing verdicts** GO/WAIT/AVOID with DST-correct sessions, news blackout, next good window, signal expiry; calendar and headline pages with beat/miss and currency tone (keyword heuristic, labelled low reliability).
* **Tiers**: Free / Pro / Elite via Paystack (30-day passes, pro-rata upgrades, idempotent amount-checked settlement, signed webhooks, optional IP allow-list); email alerts; watchlists; trade journal with CSV export.
* **Accounts**: scrypt passwords, 2FA admin, email verification, emailed resets, session management, data export, account deletion, terms acceptance.
* **Operations**: schema migrations, backups, health endpoints, graceful shutdown, structured audit log (hash-chained), robots/security.txt.

## Security summary
Hashed sessions (HttpOnly, SameSite, `__Host-`), CSRF token + Origin checks, strict CSP with no inline script or style, HSTS, parameterised SQL, lockouts without account enumeration,
rate limits, Host-header validation, size caps, SSRF-guarded feed fetching, XML entity refusal, CSV-injection-safe exports, secrets only from the environment, admin 2FA with replay
protection, mode-600 database and backups. No system is unhackable: keep the OS patched, restrict SSH, and monitor.

## Known limits
Single process on SQLite (hundreds of concurrent users). In-memory rate-limit counters reset on restart. Provider and payment integrations follow public documentation but could only
be exercised against local look-alike servers during development: prove them with `web-check`, `news-check` and `paystack-check` on your server. Container files are templates.

## Tests
`python -m unittest tests.test_apex tests.test_web tests.test_v4 tests.test_v5 tests.test_v6 tests.test_v7` plus the jsdom browser smoke test in `tests/ui_smoke`.
Test price data is generated on the fly by `tests/synth.py` and never ships with the product.
