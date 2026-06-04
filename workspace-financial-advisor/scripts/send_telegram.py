#!/usr/bin/env python3
"""Deterministic Telegram delivery with guaranteed chunking.

Splits a message into parts that each fit Telegram's 4096 UTF-16 code-unit
sendMessage limit (emojis count as 2 units), preferring paragraph/line
boundaries, and sends them in order. This removes any dependence on the
model correctly counting characters or splitting messages itself.

Usage:
    python3 send_telegram.py <chat_id> --file <path>
    python3 send_telegram.py <chat_id>            # reads message from stdin
    echo "report text" | python3 send_telegram.py <chat_id>

Exit code 0 on full success; non-zero on any failure, printing the literal
Telegram API error so callers can quote it verbatim.
"""
import sys
import json
import urllib.request
import urllib.error

CONFIG_PATH = "/home/claw/.openclaw/openclaw.json"
# Stay safely under Telegram's 4096 UTF-16 hard limit (headroom for safety).
MAX_UNITS = 3900


def utf16_len(s: str) -> int:
    """Length in UTF-16 code units — what Telegram actually counts."""
    return len(s.encode("utf-16-le")) // 2


def _split_oversized(piece: str) -> list:
    """Hard-split a single piece that exceeds MAX_UNITS, on a char boundary."""
    out, cur = [], ""
    for ch in piece:
        if utf16_len(cur) + utf16_len(ch) > MAX_UNITS:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def chunk(text: str) -> list:
    """Greedily pack paragraphs (then lines) into <=MAX_UNITS chunks."""
    text = text.strip()
    if not text:
        return []
    chunks, cur = [], ""

    def flush():
        nonlocal cur
        if cur.strip():
            chunks.append(cur.strip())
        cur = ""

    for para in text.split("\n\n"):
        block = para if not cur else "\n\n" + para
        if utf16_len(cur) + utf16_len(block) <= MAX_UNITS:
            cur += block
            continue
        # Paragraph won't fit appended; flush and place it on its own.
        flush()
        if utf16_len(para) <= MAX_UNITS:
            cur = para
            continue
        # Paragraph itself too big: break by lines, then hard-split.
        for line in para.split("\n"):
            lb = line if not cur else "\n" + line
            if utf16_len(cur) + utf16_len(lb) <= MAX_UNITS:
                cur += lb
            else:
                flush()
                if utf16_len(line) <= MAX_UNITS:
                    cur = line
                else:
                    for hp in _split_oversized(line):
                        flush()
                        cur = hp
    flush()
    return chunks


def get_token() -> str:
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    tok = cfg.get("channels", {}).get("telegram", {}).get("botToken")
    if not tok:
        raise RuntimeError("No channels.telegram.botToken in config")
    return tok


def send(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("ERROR: chat_id required", file=sys.stderr)
        return 2
    chat_id = args[0]
    text = None
    if "--file" in args:
        path = args[args.index("--file") + 1]
        with open(path, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    parts = chunk(text)
    if not parts:
        print("ERROR: empty message, nothing to send", file=sys.stderr)
        return 2

    token = get_token()
    for i, part in enumerate(parts, 1):
        try:
            send(token, chat_id, part)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            print(
                f"ERROR: Telegram sendMessage failed on part {i}/{len(parts)}: "
                f"{e.code} {body}",
                file=sys.stderr,
            )
            return 1
        except Exception as e:  # noqa: BLE001
            print(
                f"ERROR: send failed on part {i}/{len(parts)}: {e}",
                file=sys.stderr,
            )
            return 1
    print(f"Delivered in {len(parts)} part(s) to {chat_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
