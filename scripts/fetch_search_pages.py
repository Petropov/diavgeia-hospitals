#!/usr/bin/env python3
"""
fetch_search_pages.py
─────────────────────
Bulk collector for Diavgeia decisions using the **opendata** API.

WHY THIS EXISTS — the fix that unblocked the project:
  1. The previous pipeline used the `luminapi` endpoint, which is not
     reliably reachable and required one HTTP call per ADA ("hydration").
  2. The opendata search endpoint returns FULL decision objects
     (supplier AFM + name, award amount, CPV, signer, unit) inline —
     up to 500 per call. Per-ADA hydration is unnecessary for Δ.1 data.
     One month of direct awards = ONE api call.

Endpoints:
  search:   https://diavgeia.gov.gr/opendata/search.json
            params: org, type, from_date, to_date, size (max 500), page
  decision: https://diavgeia.gov.gr/opendata/decisions/{ada}.json

Note: from_date/to_date filter on SUBMISSION timestamp, and the API applies
a default issueDate window (~last 6 months) unless overridden. For older
periods pass explicit q= issue-date ranges or iterate month windows.

Usage:
  # All direct awards (Δ.1) for 2026 so far:
  python scripts/fetch_search_pages.py --org 6166 --type Δ.1 \
      --from 2026-01-01 --to 2026-07-01

  # Contracts + awards + tender notices for a window:
  python scripts/fetch_search_pages.py --org 6166 --type Δ.1,Δ.2,Α.2 \
      --from 2026-01-01 --to 2026-04-01

  # Everything (all types) in monthly windows:
  python scripts/fetch_search_pages.py --org 6166 --from 2025-01-01 --to 2026-01-01

Output:
  data/{org}/search_exports/{type}_{from}_{to}_p{page}.json
  (format identical to the raw API response; consumed by
   build_normalized_tables.py without changes)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

OPENDATA = "https://diavgeia.gov.gr/opendata"
PAGE_SIZE = 500
DELAY = 0.8


def fetch_json(url: str, timeout: int = 30):
    req = Request(url, headers={"Accept": "application/json",
                                "User-Agent": "DiavgeiaIntel/2.0 (public transparency research)"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_page(org: str, dtype: str | None, d_from: str, d_to: str, page: int) -> dict:
    params = {"org": org, "from_date": d_from, "to_date": d_to,
              "size": PAGE_SIZE, "page": page}
    if dtype:
        params["type"] = dtype
    url = f"{OPENDATA}/search.json?{urlencode(params, quote_via=quote)}"
    return fetch_json(url)


def month_windows(d_from: str, d_to: str):
    """Yield (from, to) date-string pairs, one calendar month each."""
    cur = date.fromisoformat(d_from)
    end = date.fromisoformat(d_to)
    while cur < end:
        if cur.month == 12:
            nxt = date(cur.year + 1, 1, 1)
        else:
            nxt = date(cur.year, cur.month + 1, 1)
        yield cur.isoformat(), min(nxt, end).isoformat()
        cur = nxt


def main():
    ap = argparse.ArgumentParser(description="Bulk-fetch Diavgeia search pages (opendata API).")
    ap.add_argument("--org", required=True)
    ap.add_argument("--type", default=None,
                    help="Decision type UID(s), comma-separated (e.g. Δ.1,Δ.2). Omit for all types.")
    ap.add_argument("--from", dest="d_from", required=True, help="YYYY-MM-DD")
    ap.add_argument("--to", dest="d_to", required=True, help="YYYY-MM-DD")
    ap.add_argument("--data-dir", default="./data")
    ap.add_argument("--delay", type=float, default=DELAY)
    args = ap.parse_args()

    out_dir = Path(args.data_dir) / args.org / "search_exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    types = [t.strip() for t in args.type.split(",")] if args.type else [None]
    grand = 0

    for dtype in types:
        label = dtype or "ALL"
        for w_from, w_to in month_windows(args.d_from, args.d_to):
            page = 0
            while True:
                try:
                    data = search_page(args.org, dtype, w_from, w_to, page)
                except Exception as e:  # noqa: BLE001
                    print(f"  FAIL {label} {w_from}..{w_to} p{page}: {e}", file=sys.stderr)
                    break

                info = data.get("info", {})
                n, total = info.get("actualSize", 0), info.get("total", 0)
                if n == 0:
                    break

                fname = f"{label}_{w_from}_{w_to}_p{page}.json".replace("/", "-")
                with open(out_dir / fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                grand += n
                print(f"  OK   {label} {w_from}..{w_to} p{page}: {n}/{total} → {fname}")

                if (page + 1) * PAGE_SIZE >= total:
                    break
                page += 1
                time.sleep(args.delay)
            time.sleep(args.delay)

    print(f"\nDone. {grand} decisions saved to {out_dir}")
    print("Next: python scripts/build_normalized_tables.py --org", args.org)


if __name__ == "__main__":
    main()
