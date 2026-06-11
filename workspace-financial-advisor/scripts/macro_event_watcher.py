#!/usr/bin/env python3
"""
macro_event_watcher.py

Seed and monitor the daily macro events selected by the morning brief.

When events become due (check mode), generates a rich formatted alert with:
  - Event name and scheduled time
  - Consensus cross-reference link (if available)
  - "So what" directional interpretation
  - Live market snapshot (SPY, QQQ, DXY, VIX, 2Y, 10Y)
  - Source URL (BLS/BEA/Fed)

Usage:
  python3 scripts/macro_event_watcher.py seed < events.json
  python3 scripts/macro_event_watcher.py check        # read-only; reports due events + ack_cmd
  python3 scripts/macro_event_watcher.py ack <idx>... # mark events delivered (call AFTER sending)

Seed input JSON format:
{
  "date": "2026-05-19",
  "source": "Daily Portfolio Morning Brief",
  "events": [
    {
      "title": "US Existing Home Sales",
      "time_utc": "2026-05-19T14:00:00Z",
      "priority": "medium",
      "impact": "Housing/consumer read; modest rate sensitivity",
      "why_it_matters": "Could move yields and broad risk sentiment",
      "watch_for": "Bond yields, SPY, QQQ, gold, bitcoin",
      "actual": null,
      "consensus": null,
      "previous": null
    }
  ]
}
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Paths are env-overridable for testing; default to the live portfolio files.
WATCH_PATH = os.environ.get(
    "MACRO_WATCH_PATH", os.path.join(BASE_DIR, "portfolio", "daily_macro_watch.json"))
ALERT_STATE_PATH = os.environ.get(
    "MACRO_WATCH_ALERT_STATE_PATH",
    os.path.join(BASE_DIR, "portfolio", ".macro_watch_alert_state.json"))

VALID_PRIORITIES = {"high", "medium", "low"}


@dataclass
class DueEvent:
    index: int
    event: dict[str, Any]


def utc_now() -> datetime:
    override = os.environ.get("MACRO_WATCHER_NOW")
    if override:
        return parse_iso_z(override)
    return datetime.now(timezone.utc)


def parse_iso_z(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def read_json(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def write_json(path: str, payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate a single event dict."""
    if "title" not in raw or not str(raw["title"]).strip():
        raise ValueError("Each event requires a non-empty 'title'.")
    if "time_utc" not in raw or not str(raw["time_utc"]).strip():
        raise ValueError(f"Event '{raw['title']}' is missing 'time_utc'.")

    time_utc = parse_iso_z(str(raw["time_utc"]))
    priority = str(raw.get("priority", "medium")).lower()
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Event '{raw['title']}' has invalid priority '{priority}'.")

    return {
        "title": str(raw["title"]).strip(),
        "time_utc": time_utc.isoformat().replace("+00:00", "Z"),
        "priority": priority,
        "impact": str(raw.get("impact", "")).strip(),
        "why_it_matters": str(raw.get("why_it_matters", "")).strip(),
        "watch_for": str(raw.get("watch_for", "")).strip(),
        "actual": raw.get("actual"),
        "consensus": raw.get("consensus"),
        "previous": raw.get("previous"),
        "status": str(raw.get("status", "scheduled")).strip() or "scheduled",
        "alert_sent_at": None,
    }


def _stale_already_alerted(today: str) -> bool:
    try:
        with open(ALERT_STATE_PATH) as f:
            return json.load(f).get("stale_alert_date") == today
    except (FileNotFoundError, ValueError, OSError):
        return False


def _mark_stale_alerted(today: str) -> None:
    try:
        write_json(ALERT_STATE_PATH, {"stale_alert_date": today})
    except OSError:
        pass


def stale_alarm(status: str, watch_date: Any, today: str, now: datetime) -> dict[str, Any]:
    """
    Build the check() response for a stale or missing watch file.

    On a trading weekday a stale file is a real monitoring failure — today's
    events were never seeded, so releases (CPI, NFP, FOMC, rate decisions) will
    be missed. Escalate with alert=true + ready-to-send alert_text, but only
    ONCE per day (deduped via ALERT_STATE_PATH). On weekends there are no
    scheduled US/CA releases, so stay quiet.
    """
    result: dict[str, Any] = {
        "ok": True,
        "status": status,
        "path": WATCH_PATH,
        "watch_date": watch_date,
        "today": today,
        "alert": False,
    }
    if now.weekday() >= 5:  # Saturday/Sunday
        result["note"] = "stale on weekend; no scheduled releases"
        return result
    if _stale_already_alerted(today):
        result["note"] = "stale on weekday; already alerted today"
        return result
    _mark_stale_alerted(today)
    result["alert"] = True
    result["alert_text"] = (
        "🚨 MACRO WATCH FILE STALE — intraday macro monitoring is DOWN.\n"
        f"The watch file is dated {watch_date or 'MISSING'}, but today is {today}. "
        "Today's economic events were never seeded, so any releases today "
        "(CPI, NFP, FOMC, rate decisions, etc.) will be MISSED by the hourly watcher.\n"
        "Action: re-seed daily_macro_watch.json for today — re-run the Economic "
        "Calendar Seed Check, or run `macro_event_watcher.py seed` with today's events."
    )
    return result


def seed() -> int:
    """Seed today's macro events from stdin JSON."""
    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: seed expects JSON on stdin", file=sys.stderr)
        return 1

    payload = json.loads(raw)
    date_str = str(payload.get("date") or utc_now().date().isoformat())
    source = str(payload.get("source") or "Daily Portfolio Morning Brief")
    events = [normalize_event(ev) for ev in payload.get("events", [])]
    events.sort(key=lambda ev: ev["time_utc"])

    output = {
        "date": date_str,
        "source": source,
        "seeded_at": utc_now().isoformat().replace("+00:00", "Z"),
        "watch_window": "hourly",
        "events": events,
    }
    write_json(WATCH_PATH, output)
    result = {
        "ok": True,
        "path": WATCH_PATH,
        "events_seeded": len(events),
        "events": [
            {
                "title": ev["title"],
                "time_utc": ev["time_utc"],
                "priority": ev["priority"],
            }
            for ev in events
        ],
    }
    print(json.dumps(result, indent=2))
    return 0


def find_due_events(payload: dict[str, Any], now: datetime) -> list[DueEvent]:
    """Find events that are scheduled <= now and haven't been alerted yet."""
    due: list[DueEvent] = []
    for idx, event in enumerate(payload.get("events", [])):
        if event.get("alert_sent_at"):
            continue
        event_time = parse_iso_z(event["time_utc"])
        if event_time <= now:
            due.append(DueEvent(index=idx, event=event))
    return due


def check() -> int:
    """
    Check for due events. If found, generates rich formatted alerts
    via macro_alert_formatter.py and prints them as a JSON payload
    with the alert_text included.

    Output JSON format on due:
    {
      "ok": true,
      "status": "due-events",
      "due_count": 1,
      "alerts": [
        {
          "event": { ... },
          "alert_text": "Rich formatted markdown alert...",
          "market_snapshot": { ... }
        }
      ],
      "remaining": 0
    }
    """
    now = utc_now()
    today = now.date().isoformat()

    if not os.path.exists(WATCH_PATH):
        print(json.dumps(stale_alarm("no-watch-file", None, today, now), indent=2))
        return 0

    payload = read_json(WATCH_PATH)
    if payload.get("date") != today:
        print(json.dumps(stale_alarm("stale-watch-file", payload.get("date"), today, now), indent=2))
        return 0

    due = find_due_events(payload, now)

    if not due:
        remaining = sum(1 for ev in payload.get("events", []) if not ev.get("alert_sent_at"))
        print(json.dumps({
            "ok": True,
            "status": "nothing-due",
            "path": WATCH_PATH,
            "remaining": remaining,
        }, indent=2))
        return 0

    # Import the formatter
    sys.path.insert(0, BASE_DIR)
    try:
        from scripts.macro_alert_formatter import format_macro_alert, fetch_market_snapshot
    except ImportError:
        print(json.dumps({
            "ok": False,
            "status": "error",
            "error": "macro_alert_formatter.py not found or import failed",
        }, indent=2))
        return 1

    # Fetch one market snapshot for all due events (same time).
    # NOTE: check() is READ-ONLY — it does NOT mark events as alerted. Marking
    # happens via `ack <indices>` AFTER the agent confirms delivery, so a
    # delivery/model failure leaves the event unmarked for the next run to
    # retry (avoids the silent "marked-but-not-delivered" loss). MACRO_SKIP_SNAPSHOT
    # skips the (network) market fetch — used by tests.
    snapshot = {} if os.environ.get("MACRO_SKIP_SNAPSHOT") else fetch_market_snapshot()

    alerts = []
    due_indices = []
    for item in due:
        ev = item.event
        due_indices.append(item.index)

        # Build data strings from seed data (if provided)
        actual_str = None
        actual = ev.get("actual")
        consensus = ev.get("consensus")
        previous = ev.get("previous")
        if actual is not None or consensus is not None:
            parts = []
            if actual is not None:
                parts.append(f"Actual: {actual}")
            if consensus is not None:
                parts.append(f"Consensus: {consensus}")
            actual_str = " | ".join(parts)
        previous_str = f"Previous: {previous}" if previous is not None else None

        # Generate rich alert
        alert_text = format_macro_alert(
            ev,
            snapshot=snapshot,
            actual_vs_estimate=actual_str,
            previous_value=previous_str,
        )

        alerts.append({
            "index": item.index,
            "event": ev,
            "alert_text": alert_text,
        })

    # READ-ONLY: do not write the file here. `remaining` counts unalerted events
    # NOT in the current due set (i.e. still-upcoming events).
    remaining = sum(1 for ev in payload.get("events", []) if not ev.get("alert_sent_at")) - len(due)
    ack_cmd = f"python3 {os.path.abspath(__file__)} ack " + " ".join(str(i) for i in due_indices)
    output = {
        "ok": True,
        "status": "due-events",
        "path": WATCH_PATH,
        "due_count": len(alerts),
        "alerts": alerts,
        "remaining": remaining,
        "ack_required": True,
        "ack_cmd": ack_cmd,
    }

    # Also format snapshot for top-level convenience
    order = ["SPY", "QQQ", "DXY", "VIX", "2Y Yield", "10Y Yield"]
    mkt_rows = []
    for label in order:
        if label in snapshot:
            d = snapshot[label]
            last = d.get("last")
            chg = d.get("change")
            chg_pct = d.get("change_pct")
            if last is not None:
                mkt_rows.append(f"{label}: {last} ({chg:+.2f}" + (f", {chg_pct:+.2f}%)" if chg_pct is not None else ")"))
    if mkt_rows:
        output["market_snapshot_summary"] = " | ".join(mkt_rows)

    print(json.dumps(output, indent=2, default=str))
    return 0


def ack() -> int:
    """
    Mark the given event indices as alerted (delivered). The watcher calls this
    AFTER it has actually sent the alert(s) — so a failed delivery leaves events
    unmarked and the next run retries them.

    Usage: macro_event_watcher.py ack <idx> [idx ...]
    """
    idx_args = sys.argv[2:]
    if not idx_args:
        print(json.dumps({"ok": False, "status": "error", "error": "ack requires event indices"}, indent=2))
        return 1
    try:
        indices = sorted({int(a) for a in idx_args})
    except ValueError:
        print(json.dumps({"ok": False, "status": "error", "error": f"invalid indices: {idx_args}"}, indent=2))
        return 1

    if not os.path.exists(WATCH_PATH):
        print(json.dumps({"ok": False, "status": "no-watch-file", "path": WATCH_PATH}, indent=2))
        return 1

    payload = read_json(WATCH_PATH)
    events = payload.get("events", [])
    now_iso = utc_now().isoformat().replace("+00:00", "Z")
    acked, skipped = [], []
    for i in indices:
        if 0 <= i < len(events):
            if not events[i].get("alert_sent_at"):
                events[i]["alert_sent_at"] = now_iso
                events[i]["status"] = "released"
                acked.append(events[i].get("title", f"#{i}"))
            else:
                skipped.append(events[i].get("title", f"#{i}"))  # already acked
        else:
            skipped.append(f"index {i} out of range")
    write_json(WATCH_PATH, payload)
    remaining = sum(1 for ev in events if not ev.get("alert_sent_at"))
    print(json.dumps({"ok": True, "status": "acked", "acked": acked, "skipped": skipped, "remaining": remaining}, indent=2))
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in {"seed", "check", "ack"}:
        print(__doc__.strip())
        return 1
    if sys.argv[1] == "seed":
        return seed()
    if sys.argv[1] == "ack":
        return ack()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
