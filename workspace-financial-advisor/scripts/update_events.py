#!/usr/bin/env python3
"""
update_events.py — Fetch upcoming events for portfolio holdings and write
to portfolio/upcoming_events.json.

Data sources:
  - yfinance: earnings dates, ex-dividend dates, dividend pay dates
  - Skips ETFs/bonds/crypto where calendar data is rarely available

Run weekly (Sunday 9 AM PT) via cron. Safe to run manually at any time.
"""

import json
import os
import sys
from datetime import date, datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip3 install yfinance --break-system-packages")
    sys.exit(1)

PORTFOLIO_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio", "manik_portfolio.json")
EVENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio", "upcoming_events.json")

# Skip these types — ETFs/bonds/crypto rarely have meaningful calendar events
SKIP_TYPES = {"etf", "bond", "crypto"}

# How far ahead to look (days)
LOOKAHEAD_DAYS = 90


def load_portfolio():
    with open(PORTFOLIO_PATH) as f:
        return json.load(f)


def fetch_events_for_symbol(symbol: str) -> list[dict]:
    """Return list of upcoming event dicts for a symbol."""
    events = []
    today = date.today()
    cutoff = today + timedelta(days=LOOKAHEAD_DAYS)

    try:
        ticker = yf.Ticker(symbol)
        cal = ticker.calendar  # dict or empty dict
    except Exception as e:
        print(f"  [{symbol}] yfinance error: {e}")
        return []

    if not cal:
        return []

    # Earnings date
    earnings_dates = cal.get("Earnings Date", [])
    if isinstance(earnings_dates, list):
        for ed in earnings_dates:
            if isinstance(ed, date) and today <= ed <= cutoff:
                events.append({
                    "symbol": symbol,
                    "event": "Earnings",
                    "date": ed.isoformat(),
                    "source": "yfinance",
                })
    elif isinstance(earnings_dates, date):
        if today <= earnings_dates <= cutoff:
            events.append({
                "symbol": symbol,
                "event": "Earnings",
                "date": earnings_dates.isoformat(),
                "source": "yfinance",
            })

    # Ex-dividend date
    exdiv = cal.get("Ex-Dividend Date")
    if isinstance(exdiv, date) and today <= exdiv <= cutoff:
        events.append({
            "symbol": symbol,
            "event": "Ex-Dividend",
            "date": exdiv.isoformat(),
            "source": "yfinance",
        })

    # Dividend pay date
    div_date = cal.get("Dividend Date")
    if isinstance(div_date, date) and today <= div_date <= cutoff:
        events.append({
            "symbol": symbol,
            "event": "Dividend Pay Date",
            "date": div_date.isoformat(),
            "source": "yfinance",
        })

    return events


def dedupe_holdings(portfolio: dict) -> list[dict]:
    """Return unique holdings by symbol (skip duplicates, skip unsupported types)."""
    seen = set()
    result = []
    for h in portfolio.get("holdings", []):
        sym = h["symbol"]
        htype = h.get("type", "")
        if sym in seen:
            continue
        seen.add(sym)
        if htype in SKIP_TYPES:
            print(f"  [{sym}] skipping ({htype})")
            continue
        result.append(h)
    return result


def main():
    print(f"update_events.py — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Portfolio: {PORTFOLIO_PATH}")
    print(f"Output:    {EVENTS_PATH}")
    print()

    portfolio = load_portfolio()
    holdings = dedupe_holdings(portfolio)

    all_events = []
    for h in holdings:
        sym = h["symbol"]
        print(f"Fetching {sym}...")
        events = fetch_events_for_symbol(sym)
        if events:
            for ev in events:
                print(f"  -> {ev['event']} on {ev['date']}")
        else:
            print(f"  -> no upcoming events in next {LOOKAHEAD_DAYS} days")
        all_events.extend(events)

    # Sort by date
    all_events.sort(key=lambda e: e["date"])

    output = {
        "generated": date.today().isoformat(),
        "lookahead_days": LOOKAHEAD_DAYS,
        "source": "yfinance",
        "note": "Auto-updated weekly. Agent-supplemented events may also be appended during daily reports.",
        "events": all_events,
    }

    with open(EVENTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote {len(all_events)} events to {EVENTS_PATH}")
    for ev in all_events:
        print(f"  {ev['date']}  {ev['symbol']:8s}  {ev['event']}")


if __name__ == "__main__":
    main()
