#!/usr/bin/env python3
"""
Daily portfolio P&L / allocation snapshot for Manik's portfolio.

Deterministic — does ALL the arithmetic here so downstream reports never have to
estimate. Reuses fetch_quotes.py's yfinance quote logic for live prices and the
CAD/USD FX rate, then writes one snapshot file per day:

    portfolio/snapshots/YYYY-MM-DD.json

This is the persisted week-over-week baseline the weekly "Week in Review" report
reads. Re-running on the same day overwrites that day's file (idempotent).

Usage:
    python3 snapshot_portfolio.py
    python3 snapshot_portfolio.py --date 2026-06-05      # backfill / override
    python3 snapshot_portfolio.py --portfolio /path/to/portfolio.json
"""

import argparse
import datetime
import json
import os
import sys

# Reuse the battle-tested quote fetcher in the same directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_quotes import fetch_one  # noqa: E402

DEFAULT_PORTFOLIO = "/home/claw/.openclaw/workspace-financial-advisor/portfolio/manik_portfolio.json"
SNAPSHOT_DIR = "/home/claw/.openclaw/workspace-financial-advisor/portfolio/snapshots"
FX_SYMBOL = "CADUSD=X"

# Holding `type` (in manik_portfolio.json) -> target_allocation bucket key.
TYPE_TO_BUCKET = {
    "speculative": "speculative",
    "crypto": "crypto",
    "dividend": "dividend",
    "etf": "core_equity",
    "bond": "bonds",
    "commodity": "commodities",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", default=DEFAULT_PORTFOLIO)
    ap.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: today, local)")
    ap.add_argument("--out-dir", default=SNAPSHOT_DIR)
    args = ap.parse_args()

    snap_date = args.date or datetime.date.today().isoformat()

    with open(args.portfolio) as f:
        portfolio = json.load(f)
    holdings = portfolio.get("holdings", [])
    targets = portfolio.get("target_allocation", {})

    # One quote per unique symbol, plus the FX pair.
    symbols = sorted({h["symbol"] for h in holdings})
    prices = {}
    for sym in symbols + [FX_SYMBOL]:
        q = fetch_one(sym)
        if "error" not in q and q.get("last") is not None:
            prices[sym] = q["last"]

    fx_cadusd = prices.get(FX_SYMBOL)
    if fx_cadusd is None:
        # Fall back to ~0.73 only if FX fetch failed, and flag it.
        fx_cadusd = 0.73
        fx_estimated = True
    else:
        fx_estimated = False

    def to_usd(amount, currency):
        return amount * fx_cadusd if currency == "CAD" else amount

    holding_rows = []
    missing = []
    total_value = 0.0
    total_cost = 0.0
    bucket_value = {}

    for h in holdings:
        sym = h["symbol"]
        qty = h.get("quantity", 0)
        buy = h.get("buy_price", 0)
        currency = h.get("currency", "USD")
        last = prices.get(sym)
        if last is None:
            missing.append(sym)
            continue
        value_usd = to_usd(qty * last, currency)
        cost_usd = to_usd(qty * buy, currency)
        pnl_usd = value_usd - cost_usd
        total_value += value_usd
        total_cost += cost_usd
        bucket = TYPE_TO_BUCKET.get(h.get("type", ""), "other")
        bucket_value[bucket] = bucket_value.get(bucket, 0.0) + value_usd
        holding_rows.append({
            "symbol": sym,
            "quantity": qty,
            "currency": currency,
            "last": round(float(last), 4),
            "value_usd": round(value_usd, 2),
            "cost_usd": round(cost_usd, 2),
            "pnl_usd": round(pnl_usd, 2),
            "pnl_pct": round(pnl_usd / cost_usd * 100, 2) if cost_usd else None,
        })

    if not holding_rows:
        print(json.dumps({"error": "no quotes obtained for any holding", "missing": missing}),
              file=sys.stderr)
        sys.exit(1)

    buckets = {}
    for bucket, val in sorted(bucket_value.items()):
        pct = (val / total_value * 100) if total_value else 0.0
        target_pct = targets.get(bucket)
        buckets[bucket] = {
            "value_usd": round(val, 2),
            "pct": round(pct, 2),
            "target_pct": target_pct,
            "drift_pct": round(pct - target_pct, 2) if target_pct is not None else None,
        }

    snapshot = {
        "date": snap_date,
        "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_value_usd": round(total_value, 2),
        "total_cost_usd": round(total_cost, 2),
        "pnl_usd": round(total_value - total_cost, 2),
        "pnl_pct": round((total_value - total_cost) / total_cost * 100, 2) if total_cost else None,
        "fx_cadusd": round(float(fx_cadusd), 4),
        "fx_estimated": fx_estimated,
        "missing_symbols": missing,
        "buckets": buckets,
        "holdings": sorted(holding_rows, key=lambda r: r["value_usd"], reverse=True),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"{snap_date}.json")
    with open(out_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Snapshot written: {out_path}")
    print(f"  total_value_usd={snapshot['total_value_usd']} pnl_usd={snapshot['pnl_usd']} "
          f"pnl_pct={snapshot['pnl_pct']} fx_cadusd={snapshot['fx_cadusd']}"
          + (" (FX ESTIMATED)" if fx_estimated else ""))
    if missing:
        print(f"  WARNING missing prices for: {', '.join(missing)}")


if __name__ == "__main__":
    main()
