#!/usr/bin/env python3
"""
Regression tests for macro_event_watcher.py staleness handling.

Bug being guarded against (2026-06-10): a stale/missing watch file on a trading
weekday was reported as benign ("stale-watch-file" -> watcher stays silent),
silently missing CPI/BoC alerts. The watcher must now ESCALATE a stale file on a
weekday into an actionable alarm (alert=true + alert_text), deduped to once/day,
while staying quiet on weekends and when the file is current.

Run: python3 scripts/test_macro_watcher.py
Uses env overrides (MACRO_WATCH_PATH, MACRO_WATCH_ALERT_STATE_PATH,
MACRO_WATCHER_NOW) so it never touches the real watch file.
"""
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(__file__), "macro_event_watcher.py")


def _env(watch_file, state_file, now_iso):
    env = dict(os.environ)
    env["MACRO_WATCH_PATH"] = watch_file
    env["MACRO_WATCH_ALERT_STATE_PATH"] = state_file
    env["MACRO_WATCHER_NOW"] = now_iso
    env["MACRO_SKIP_SNAPSHOT"] = "1"  # avoid network in tests
    return env


def run_check(watch_file, state_file, now_iso, watch_contents=None):
    if watch_contents is None:
        if os.path.exists(watch_file):
            os.remove(watch_file)
    else:
        with open(watch_file, "w") as f:
            json.dump(watch_contents, f)
    out = subprocess.run([sys.executable, SCRIPT, "check"], capture_output=True, text=True,
                         env=_env(watch_file, state_file, now_iso))
    assert out.returncode == 0, f"check exited {out.returncode}: {out.stderr}"
    return json.loads(out.stdout)


def run_ack(watch_file, state_file, now_iso, indices):
    out = subprocess.run([sys.executable, SCRIPT, "ack", *[str(i) for i in indices]],
                         capture_output=True, text=True, env=_env(watch_file, state_file, now_iso))
    return out.returncode, (json.loads(out.stdout) if out.stdout.strip() else {})


def read_file(watch_file):
    with open(watch_file) as f:
        return json.load(f)


def main():
    failures = []

    def expect(name, cond, detail=""):
        if cond:
            print(f"  PASS  {name}")
        else:
            print(f"  FAIL  {name}  {detail}")
            failures.append(name)

    with tempfile.TemporaryDirectory() as d:
        watch = os.path.join(d, "daily_macro_watch.json")
        state = os.path.join(d, ".alert_state.json")
        STALE = {"date": "2026-06-05", "source": "x", "events": []}
        WED = "2026-06-10T14:05:00Z"   # Wednesday, first watcher run
        SAT = "2026-06-13T14:05:00Z"   # Saturday

        # A) stale file on a weekday -> escalate
        r = run_check(watch, state, WED, STALE)
        expect("A stale+weekday escalates", r.get("alert") is True and "alert_text" in r, r)
        expect("A alert_text mentions stale/monitoring",
               "STALE" in r.get("alert_text", "").upper(), r.get("alert_text"))

        # B) second run same day -> deduped (no repeat alarm)
        r = run_check(watch, state, "2026-06-10T15:05:00Z", STALE)
        expect("B stale repeat is deduped same day", r.get("alert") is False, r)

        # C) missing file on a weekday -> escalate
        os.remove(state) if os.path.exists(state) else None
        r = run_check(watch, state, WED, None)
        expect("C missing+weekday escalates", r.get("alert") is True and r.get("status") == "no-watch-file", r)

        # D) current dated file, nothing due -> silent (no false alarm)
        os.remove(state) if os.path.exists(state) else None
        cur = {"date": "2026-06-10", "source": "x",
               "events": [{"title": "T", "time_utc": "2026-06-10T20:30:00Z", "priority": "medium"}]}
        r = run_check(watch, state, WED, cur)
        expect("D current file nothing-due stays silent",
               r.get("status") == "nothing-due" and not r.get("alert"), r)

        # E) stale file on a weekend -> no alarm (events don't release)
        os.remove(state) if os.path.exists(state) else None
        r = run_check(watch, state, SAT, STALE)
        expect("E stale+weekend no alarm", not r.get("alert"), r)

        # --- decoupling: check() is read-only; ack() marks ---
        DUE = {"date": "2026-06-10", "source": "x",
               "events": [{"title": "US CPI", "time_utc": "2026-06-10T12:30:00Z", "priority": "high"}]}

        # F) check reports the due event but does NOT mark it
        os.remove(state) if os.path.exists(state) else None
        r = run_check(watch, state, WED, DUE)
        expect("F check reports due-events", r.get("status") == "due-events" and r.get("due_count") == 1, r)
        expect("F alert carries index + ack_cmd", r["alerts"][0].get("index") == 0 and "ack 0" in r.get("ack_cmd", ""), r)
        expect("F check is READ-ONLY (event unmarked)", not read_file(watch)["events"][0].get("alert_sent_at"),
               read_file(watch)["events"][0])

        # G) ack marks the delivered event
        rc, ar = run_ack(watch, state, WED, [0])
        expect("G ack marks the event", rc == 0 and bool(read_file(watch)["events"][0].get("alert_sent_at")), ar)

        # H) after ack, the event is no longer due (won't re-alert)
        out = subprocess.run([sys.executable, SCRIPT, "check"], capture_output=True, text=True,
                             env=_env(watch, state, WED))
        r = json.loads(out.stdout)
        expect("H acked event no longer due", r.get("status") == "nothing-due", r)

    print()
    if failures:
        print(f"{len(failures)} FAILED: {failures}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
