#!/usr/bin/env python3
"""
macro_alert_formatter.py

Generates rich, formatted macro event alert text with:
  - Event name and scheduled time
  - Actual result vs consensus estimate
  - Previous value for context
  - 2-3 line "so what" interpretation with directional bias
  - Current market snapshot (SPY, QQQ, DXY, VIX, 2Y yield, 10Y yield)
  - Source URL (BLS/BEA/Fed websites)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FETCH_QUOTES = os.path.join(BASE_DIR, "scripts", "fetch_quotes.py")

# Source URL mapping for well-known government data releases
# Falls in order: direct match, partial match, then generic fallback
SOURCE_URL_MAP: dict[str, str] = {
    # Bureau of Labor Statistics
    "cpi": "https://www.bls.gov/news.release/cpi.nr0.htm",
    "consumer price index": "https://www.bls.gov/news.release/cpi.nr0.htm",
    "core cpi": "https://www.bls.gov/news.release/cpi.nr0.htm",
    "ppi": "https://www.bls.gov/news.release/ppi.nr0.htm",
    "producer price index": "https://www.bls.gov/news.release/ppi.nr0.htm",
    "core ppi": "https://www.bls.gov/news.release/ppi.nr0.htm",
    "employment situation": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "nonfarm payrolls": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "unemployment rate": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "average hourly earnings": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "labor force participation": "https://www.bls.gov/news.release/empsit.nr0.htm",
    "jolts": "https://www.bls.gov/news.release/jolts.nr0.htm",
    "job openings": "https://www.bls.gov/news.release/jolts.nr0.htm",
    "job openings and labor turnover": "https://www.bls.gov/news.release/jolts.nr0.htm",

    # Bureau of Economic Analysis
    "gdp": "https://www.bea.gov/news/glance",
    "gdp advance": "https://www.bea.gov/news/glance",
    "gdp second": "https://www.bea.gov/news/glance",
    "gdp third": "https://www.bea.gov/news/glance",
    "personal income": "https://www.bea.gov/news/glance",
    "personal spending": "https://www.bea.gov/news/glance",
    "pce": "https://www.bea.gov/news/glance",
    "core pce": "https://www.bea.gov/news/glance",
    "personal consumption expenditures": "https://www.bea.gov/news/glance",
    "trade balance": "https://www.bea.gov/news/glance",
    "international trade": "https://www.bea.gov/news/glance",
    "retail inventories": "https://www.census.gov/retail/",
    "wholesale inventories": "https://www.census.gov/wholesale/",
    "durable goods": "https://www.census.gov/manufacturing/m3/",
    "durable goods orders": "https://www.census.gov/manufacturing/m3/",
    "new home sales": "https://www.census.gov/newhomesales/",
    "existing home sales": "https://www.nar.realtor/research-and-statistics/housing-statistics/existing-home-sales",
    "housing starts": "https://www.census.gov/construction/nrc/",
    "building permits": "https://www.census.gov/construction/nrc/",
    "industrial production": "https://www.federalreserve.gov/releases/g17/current/",
    "capacity utilization": "https://www.federalreserve.gov/releases/g17/current/",
    "consumer confidence": "https://www.conference-board.org/data/consumerconfidence.cfm",
    "consumer sentiment": "https://www.sca.isr.umich.edu/",
    "michigan sentiment": "https://www.sca.isr.umich.edu/",
    "ism manufacturing": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/",
    "ism services": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/",
    "ism non-manufacturing": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/",
    "fed": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "fomc": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "federal reserve": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "interest rate decision": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "fed funds rate": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "beige book": "https://www.federalreserve.gov/monetarypolicy/beigebook/default.htm",
    "initial jobless claims": "https://www.dol.gov/ui/data.pdf",
    "jobless claims": "https://www.dol.gov/ui/data.pdf",
    "continuing claims": "https://www.dol.gov/ui/data.pdf",
    "philadelphia fed": "https://www.philadelphiafed.org/surveys-and-data/regional-data-releases/manufacturing-outlook-survey",
    "empire state": "https://www.newyorkfed.org/survey/empire/empiresurvey_overview.html",
    "richmond fed": "https://www.richmondfed.org/research/data_analysis/survey_of_manufacturers",
    "dallas fed": "https://www.dallasfed.org/research/surveys/tmos",
    "kansas city fed": "https://www.kansascityfed.org/surveys/manufacturing-survey/",
    "chicago pmi": "https://www.pmimonthly.org/",
    "factory orders": "https://www.census.gov/manufacturing/m3/",
    "business inventories": "https://www.census.gov/mtis/",
    "light vehicle sales": "https://www.bea.gov/data/gdp-private-investment-fixed-assets",
    "construction spending": "https://www.census.gov/construction/c30/",
    "treasury": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
    "treasury auction": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
    "supply of treasuries": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
    "quarterly refunding": "https://home.treasury.gov/resource-center/data-chart-center/quarterly-refunding",
    "cfpb": "https://www.consumerfinance.gov/data-research/",
    "sba": "https://www.sba.gov/data",
    "hhs": "https://www.hhs.gov/data/",
    "census": "https://www.census.gov/economic-indicators/",
}


def resolve_source_url(event_title: str) -> str | None:
    """Best-effort source URL lookup from event title."""
    title_lower = event_title.lower().strip()
    # Direct match
    if title_lower in SOURCE_URL_MAP:
        return SOURCE_URL_MAP[title_lower]
    # Partial match — find the longest prefix match
    matched = None
    this_match_len = 0
    for key, url in SOURCE_URL_MAP.items():
        if key in title_lower and len(key) > this_match_len:
            this_match_len = len(key)
            matched = url
    return matched


def fetch_market_snapshot() -> dict[str, Any]:
    """Fetch current market data for SPY, QQQ, DXY, VIX, 2Y yield, 10Y yield."""
    targets = ["SPY", "QQQ", "^VIX", "DX-Y.NYB", "^TNX", "2YY=F"]
    # Map yfinance symbols to readable labels
    label_map = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "^VIX": "VIX",
        "DX-Y.NYB": "DXY",
        "^TNX": "10Y Yield",
        "2YY=F": "2Y Yield",
    }

    # DXY and 2Y yield can be tricky with yfinance; use a direct approach
    result = {}
    try:
        import contextlib, io
        silenced = io.StringIO()
        with contextlib.redirect_stderr(silenced), contextlib.redirect_stdout(silenced):
            import yfinance as yf
            for sym in targets:
                label = label_map.get(sym, sym)
                try:
                    t = yf.Ticker(sym)
                    fi = t.fast_info
                    last = fi.last_price
                    prev = fi.previous_close
                    if last is not None and prev is not None:
                        change = round(float(last) - float(prev), 2)
                        change_pct = round((float(last) - float(prev)) / float(prev) * 100, 2)
                        result[label] = {
                            "last": round(float(last), 2),
                            "change": change,
                            "change_pct": change_pct,
                        }
                    else:
                        # fallback to history
                        hist = t.history(period="5d")
                        if not hist.empty and len(hist) >= 2:
                            last = float(hist["Close"].iloc[-1])
                            prev = float(hist["Close"].iloc[-2])
                            change = round(last - prev, 2)
                            change_pct = round((last - prev) / prev * 100, 2)
                            result[label] = {
                                "last": round(last, 2),
                                "change": change,
                                "change_pct": change_pct,
                            }
                        else:
                            result[label] = {"last": None, "change": None, "change_pct": None}
                except Exception as e:
                    result[label] = {"last": None, "change": None, "change_pct": None, "error": str(e)[:60]}
    except ImportError:
        # Fallback if yfinance unavailable — try fetching via subprocess
        for label in label_map.values():
            result[label] = {"last": None, "change": None, "change_pct": None}

    return result


def format_market_row(label: str, data: dict[str, Any]) -> str:
    """Format a single market line."""
    last = data.get("last")
    chg = data.get("change")
    chg_pct = data.get("change_pct")
    if last is None:
        return f"  • {label}: N/A"
    emoji = "📈" if chg is not None and chg >= 0 else "📉"
    if chg is not None and chg_pct is not None:
        return f"  • {label}: ${last} {emoji} {chg:+.2f} ({chg_pct:+.2f}%)"
    return f"  • {label}: ${last}"


def format_market_snapshot(snapshot: dict[str, Any]) -> str:
    """Format the full market snapshot block."""
    lines = ["```", "📊 Market Snapshot", "─" * 36]
    # Order: SPY, QQQ, DXY, VIX, 2Y Yield, 10Y Yield
    order = ["SPY", "QQQ", "DXY", "VIX", "2Y Yield", "10Y Yield"]
    for label in order:
        if label in snapshot:
            data = snapshot[label]
            last = data.get("last")
            chg = data.get("change")
            chg_pct = data.get("change_pct")
            if last is None:
                lines.append(f"  {label:12s}  N/A")
            else:
                emoji = "▲" if (chg is not None and chg >= 0) else "▼"
                if chg is not None and chg_pct is not None:
                    last_str = f"{last:.2f}"
                    lines.append(f"  {label:12s}  ${last_str:<8s}  {emoji} {chg:+.2f} ({chg_pct:+.2f}%)")
                else:
                    last_str = f"{last:.2f}"
                    lines.append(f"  {label:12s}  ${last_str:<8s}")
    lines.append("```")
    return "\n".join(lines)


def interpret_event(event_title: str, priority: str) -> str:
    """
    Generate a 2-3 line "so what" interpretation with directional bias for common macro events.
    This is invoked when actual data isn't yet available (just a time-based alert).
    The morning-brief seed provides the richer context; this is the template.
    """
    title_lower = event_title.lower().strip()
    lines = []

    if "cpi" in title_lower or "consumer price" in title_lower:
        lines.append("📊 **So What:** Inflation data sets the Fed's rate path.")
        lines.append("   🔴 Above consensus = hawkish (rates up, equities down, USD up)")
        lines.append("   🟢 Below consensus = dovish (rates down, equities up, USD down)")
    elif "ppi" in title_lower or "producer price" in title_lower:
        lines.append("🏭 **So What:** PPI is a leading indicator for CPI — pipeline inflation pressure.")
        lines.append("   🔴 Hot PPI → higher input costs → potential margin compression → equities may sell off")
        lines.append("   🟢 Cool PPI → easing cost pressures → bullish for equities and bonds")
    elif "payroll" in title_lower or "employment" in title_lower or "jobs" in title_lower or "unemployment" in title_lower:
        lines.append("💼 **So What:** Labor market data drives Fed policy expectations.")
        lines.append("   🔴 Too hot (>250K) → rates stay high, risk assets under pressure")
        lines.append("   🟢 Moderate (150-200K) → soft landing path intact, risk-on environment")
    elif "gdp" in title_lower:
        lines.append("📈 **So What:** GDP is the broadest measure of economic health.")
        lines.append("   🔴 Above trend → overheating concerns, taper fears")
        lines.append("   🟢 Below trend → recession fears, rate-cut hopes")
    elif "pce" in title_lower or "personal consumption" in title_lower:
        lines.append("🛒 **So What:** PCE is the Fed's preferred inflation gauge.")
        lines.append("   🔴 Core PCE >2.5% → Fed remains hawkish, rates stay higher for longer")
        lines.append("   🟢 Core PCE <2.0% → rate cuts on the table, bullish for equities and bonds")
    elif "fomc" in title_lower or "fed" in title_lower or "interest rate" in title_lower:
        lines.append("🏛️ **So What:** The single most important event for all markets.")
        lines.append("   🔴 Hawkish (hold/hike) → USD up, equities down, yields up")
        lines.append("   🟢 Dovish (cut/signal cuts) → risk-on, USD down, bonds rally")
    elif "housing" in title_lower or "home sales" in title_lower:
        lines.append("🏠 **So What:** Housing is rate-sensitive and leads consumer confidence.")
        lines.append("   📉 Weak housing → rates impacting economy → rate cuts more likely")
        lines.append("   📈 Strong housing → consumer resilient, but could delay rate cuts")
    elif "consumer confidence" in title_lower or "consumer sentiment" in title_lower or "michigan" in title_lower:
        lines.append("😊 **So What:** Consumer confidence predicts spending — 70% of US economy.")
        lines.append("   📉 Falling confidence → spending slowdown → recession risk up, equities down")
        lines.append("   📈 Rising confidence → resilient consumer → risk-on, but may delay cuts")
    elif "ism" in title_lower:
        if "services" in title_lower or "non-manufacturing" in title_lower:
            lines.append("🏢 **So What:** ISM Services drives 80%+ of US economic activity.")
            lines.append("   🔴 >55 → expansion, but may push yields higher")
            lines.append("   🟢 <50 → contraction, recession risk increases")
        else:
            lines.append("🏭 **So What:** ISM Manufacturing is a leading economic indicator.")
            lines.append("   🔴 >50 → expansion, good for cyclicals and commodities")
            lines.append("   🟢 <50 → contraction, defensive rotation")
    elif "claims" in title_lower or "jobless" in title_lower:
        lines.append("📋 **So What:** Weekly claims are the most timely labor market indicator.")
        lines.append("   🔴 Spiking claims (>260K) → labor market weakening, risk-off")
        lines.append("   🟢 Stable/low claims (<220K) → labor market tight, Fed can hold")
    elif "existing home sales" in title_lower:
        lines.append("🏡 **So What:** Existing home sales = 90% of housing market.")
        lines.append("   📉 Weak sales → high rates still biting, signals economic slowdown")
        lines.append("   📈 Recovering sales → housing bottom forming, bullish for consumer")
    elif "inventories" in title_lower:
        lines.append("📦 **So What:** Inventory data feeds GDP calculation.")
        lines.append("   📈 Rising inventories → possible demand weakening ahead")
        lines.append("   📉 Falling inventories → restocking needed, supports production")
    elif "durable goods" in title_lower:
        lines.append("🛠️ **So What:** Durable goods orders = capex proxy — business confidence.")
        lines.append("   📈 Rising orders → business investment expanding, bullish for industrials")
        lines.append("   📉 Falling orders → business caution, defensive rotation")
    elif "wholesale" in title_lower:
        lines.append("📦 **So What:** Wholesale trade signals supply chain and demand health.")
        lines.append("   📈 Rising sales → demand intact, inventory rebuild needed")
        lines.append("   📉 Falling sales → demand weakening, recession watch")
    elif "retail" in title_lower or "sales" in title_lower:
        lines.append("🛍️ **So What:** Retail sales = 1/3 of consumer spending.")
        lines.append("   🔴 Hot retail → consumer strong, rates may stay high")
        lines.append("   🟢 Weak retail → consumer under pressure, rate cuts likely")
    elif "dividend" in title_lower:
        lines.append("💰 **So What:** This is a portfolio income event, not a macro catalyst.")
        lines.append("   Track collection and reinvestment; no systemic market impact.")
    elif "earnings" in title_lower and "season" not in title_lower and "expiration" not in title_lower:
        lines.append("📊 **So What:** Company-level earnings drive individual positioning decisions.")
        lines.append("   Track guidance, margins, and forward outlook more than headline beats/misses.")
    else:
        lines.append("📊 **So What:** Check how actuals compare to consensus.")
        lines.append("   Markets react to deviations from expectations — the surprise, not the number itself.")

    return "\n".join(lines)


def format_macro_alert(
    event: dict[str, Any],
    snapshot: dict[str, Any] | None = None,
    actual_vs_estimate: str | None = None,
    previous_value: str | None = None,
    interpretation: str | None = None,
) -> str:
    """
    Generate a rich formatted macro event alert ready for Telegram delivery.

    Args:
        event: The event dict from daily_macro_watch.json
        snapshot: Optional pre-fetched market snapshot dict
        actual_vs_estimate: e.g. "Actual: 2.9% vs Consensus: 3.1%"
        previous_value: e.g. "Previous: 3.0%"
        interpretation: Custom interpretation override; if None, auto-generates
    """
    title = event.get("title", "Unknown Event")
    time_utc = event.get("time_utc", "")
    priority = event.get("priority", "medium")
    impact = event.get("impact", "")
    why_it_matters = event.get("why_it_matters", "")

    # Priority emoji
    prio_emoji = {"high": "🚨", "medium": "📌", "low": "ℹ️"}.get(priority, "📌")

    # Parse time for a readable format
    time_readable = time_utc
    try:
        if time_utc:
            from datetime import datetime
            dt = datetime.fromisoformat(time_utc.replace("Z", "+00:00"))
            est = dt.astimezone()
            time_readable = f"{dt.strftime('%Y-%m-%d %H:%M')} UTC / {est.strftime('%H:%M')} ET"
    except Exception:
        pass

    # Resolve source URL
    source_url = resolve_source_url(title)

    # Build the alert body
    parts = [
        f"{prio_emoji} **Macro Event Alert**",
        "",
        f"**{title}**",
        f"⏱ Scheduled: {time_readable}",
    ]

    if actual_vs_estimate:
        parts.append(f"📊 {actual_vs_estimate}")
    if previous_value:
        parts.append(f"📜 {previous_value}")

    # Impact & context
    if impact:
        parts.append(f"💡 Impact: {impact}")
    if why_it_matters:
        parts.append(f"🔍 Why it matters: {why_it_matters}")

    # Interpretation
    interp = interpretation if interpretation else interpret_event(title, priority)
    parts.append("")
    parts.append(interp)

    # Market snapshot
    if snapshot is None:
        snapshot = fetch_market_snapshot()
    parts.append("")
    parts.append(format_market_snapshot(snapshot))

    # Source URL
    if source_url:
        parts.append(f"🔗 Source: {source_url}")
    else:
        parts.append("🔗 Source: N/A — check economic calendar")

    parts.append("")
    parts.append("_" * 40)
    parts.append(f"🤖 Generated by FinAdvisor Macro Watcher at {datetime.now(timezone.utc).strftime('%H:%M UTC')}")

    return "\n".join(parts)


def format_macro_alert_with_data(
    event: dict[str, Any],
    actual: str,
    consensus: str,
    previous: str,
    direction: str,  # "beat" | "miss" | "in-line"
    custom_interpretation: str | None = None,
) -> str:
    """
    Convenience wrapper when the issuer already knows the actual data.
    direction: 'beat' = actual > consensus (for most metrics this is positive for the economy)
              'miss' = actual < consensus
              'in-line' = roughly as expected
    """
    actual_vs_estimate = f"Actual: {actual} | Consensus: {consensus} | Direction: {'✅ Beat' if direction == 'beat' else '❌ Miss' if direction == 'miss' else '➡️ In Line'}"
    previous_value = f"Previous: {previous}"

    snapshot = fetch_market_snapshot()
    return format_macro_alert(
        event=event,
        snapshot=snapshot,
        actual_vs_estimate=actual_vs_estimate,
        previous_value=previous_value,
        interpretation=custom_interpretation,
    )


if __name__ == "__main__":
    # CLI usage: pipe in event JSON, get formatted alert
    raw = sys.stdin.read().strip()
    if raw:
        event = json.loads(raw)
        print(format_macro_alert(event))
    else:
        print("Usage: cat event.json | python3 macro_alert_formatter.py", file=sys.stderr)
        print("   Or: python3 macro_alert_formatter.py '{\"title\":\"CPI\",\"time_utc\":\"...\",\"priority\":\"high\",\"impact\":\"...\",\"why_it_matters\":\"...\"}'", file=sys.stderr)
        sys.exit(1)
