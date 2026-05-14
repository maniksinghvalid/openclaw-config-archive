#!/usr/bin/env python3
"""
Batch quote fetcher for Manik's portfolio. Uses yfinance to grab live prices,
previous close, day change %, and currency for every holding plus benchmarks
(SPY, QQQ, ^VIX) and a CAD/USD FX rate in a single invocation.

Replaces the legacy approach of firing 18 separate Brave web_search calls per
portfolio cron run, which routinely hit Brave Free plan's 1-req/sec limit.

Output: JSON to stdout. Exit non-zero only if no quotes were obtained.

Usage:
    python3 fetch_quotes.py
    python3 fetch_quotes.py --portfolio /path/to/portfolio.json
    python3 fetch_quotes.py --symbols NIO,CLOV,SPY,QQQ,^VIX
"""

import argparse
import contextlib
import datetime
import io
import json
import logging
import os
import sys

try:
    import yfinance as yf
except ImportError:
    print(json.dumps({"error": "yfinance not installed. Run: pip install yfinance"}), file=sys.stderr)
    sys.exit(2)

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


DEFAULT_PORTFOLIO = "/home/claw/.openclaw/workspace-financial-advisor/portfolio/manik_portfolio.json"
DEFAULT_BENCHMARKS = ["SPY", "QQQ", "^VIX"]
DEFAULT_FX_PAIRS = ["CADUSD=X"]


def load_portfolio_symbols(path):
    with open(path) as f:
        data = json.load(f)
    symbols = sorted({h["symbol"] for h in data.get("holdings", [])})
    watchlist = data.get("watchlist", [])
    return symbols, watchlist


VIX_ALIASES = {"VIX": "^VIX"}


def fetch_one(symbol):
    resolved = VIX_ALIASES.get(symbol, symbol)
    silenced = io.StringIO()
    try:
        with contextlib.redirect_stderr(silenced), contextlib.redirect_stdout(silenced):
            t = yf.Ticker(resolved)
            last = prev = currency = None
            try:
                fi = t.fast_info
                last = fi.last_price
                prev = fi.previous_close
                currency = fi.currency
            except Exception:
                pass
            if last is None or prev is None:
                hist = t.history(period="5d", auto_adjust=False)
                if not hist.empty and len(hist) >= 2:
                    last = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
        if last is None or prev is None:
            return {"symbol": symbol, "error": "no price data"}
        change_pct = ((last - prev) / prev * 100) if prev else None
        return {
            "symbol": symbol,
            "resolved_symbol": resolved if resolved != symbol else None,
            "last": round(float(last), 4),
            "previous_close": round(float(prev), 4),
            "change_pct": round(float(change_pct), 3) if change_pct is not None else None,
            "currency": currency,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", default=DEFAULT_PORTFOLIO)
    ap.add_argument("--symbols", help="Comma-separated symbols; overrides --portfolio")
    ap.add_argument("--no-benchmarks", action="store_true")
    ap.add_argument("--no-fx", action="store_true")
    args = ap.parse_args()

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
        watchlist = []
    elif os.path.exists(args.portfolio):
        symbols, watchlist = load_portfolio_symbols(args.portfolio)
    else:
        print(json.dumps({"error": f"portfolio not found: {args.portfolio}"}), file=sys.stderr)
        sys.exit(2)

    fetch_list = list(symbols)
    if not args.no_benchmarks:
        for s in DEFAULT_BENCHMARKS + watchlist:
            if s and s not in fetch_list:
                fetch_list.append(s)
    if not args.no_fx:
        for s in DEFAULT_FX_PAIRS:
            if s not in fetch_list:
                fetch_list.append(s)

    quotes = [fetch_one(s) for s in fetch_list]
    ok = [q for q in quotes if "error" not in q]
    failed = [q for q in quotes if "error" in q]

    print(json.dumps({
        "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ok_count": len(ok),
        "failed_count": len(failed),
        "quotes": quotes,
    }, indent=2))

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
