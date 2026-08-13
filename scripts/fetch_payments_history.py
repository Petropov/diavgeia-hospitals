#!/usr/bin/env python3
"""
Fetch and classify verified payment records (Β.2.2) from Diavgeia for any
Greek public organisation, over an arbitrary historical range.

WHY THIS EXISTS
---------------
Diavgeia's opendata search API appears to cap history at ~6 months. It does not.
The trap is parameter naming:

  * from_date / to_date        -> SILENTLY CLAMPED to a recent rolling window
  * q=issueDate:[...] override -> SILENTLY IGNORED
  * from_issue_date / to_issue_date -> WORKS, at any point in history

The ~6 months IS real, but as a MAXIMUM SPAN PER QUERY, not a recency limit.
You may position that 6-month window anywhere in the archive. So we walk the
timeline in sub-6-month steps. (Verified live 2026-08-11: a request for
2021-01-01..2022-01-01 came back clamped to 2021-01-01..2021-06-30.)

Always verify by reading info.query in the response - it echoes the range the
server ACTUALLY applied. This script does that for you and warns on clamping.

CLASSIFICATION RULES (validated on ΓΝ Ρόδου 99221940 and ΓΝ Λαμίας 99221923)
---------------------------------------------------------------------------
Counted as a verified real payment:
    decisionTypeId == "Β.2.2"  AND  a named sponsor with a populated amount.
Excluded:
    - sponsorAFMName == {}          -> structurally anonymous (the Β.2.1/ΧΕ gap)
    - sponsor AFM == the org's AFM  -> self-referential payroll/ΕΦΚΑ/ΦΜΥ remittance
    - missing/zero amount
    - AFM-IN-AMOUNT data-entry errors (see below)

THE AFM-IN-AMOUNT TRAP
----------------------
Real case: ADA 6Χ4Μ46907Κ-8Θ2, GE HEALTHCARE, Sept 2025.
  expenseAmount = 9.4472918E7  = 94,472,918
  supplier ΑΦΜ  = 094472918
The tax ID was typed into the amount field. That single record is ~6.5x the
hospital's true ANNUAL spend. Any naive sum of expenseAmount is wrong by 94.5M.
Note also the value is JSON *scientific notation* - a regex like [0-9.]+ silently
truncates it to 9.45. Parsing as JSON (as here) avoids that; the detector below
catches the error class generally, anywhere it occurs.

USAGE
-----
    python3 fetch_payments_history.py --org 99221940 --start 2021-08-01
    python3 fetch_payments_history.py --org 99221923 --start 2019-01-01 --end 2026-08-01

Outputs (into --outdir, default data/<org>/payments/):
    payments.csv        one row per verified payment
    excluded.csv        every excluded record + the reason
    monthly_summary.csv month, n_payments, total_eur
    anomalies.csv       suspected AFM-in-amount errors, for follow-up

Only stdlib. No API key. Be polite: default 0.4s between requests.
"""

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta

API = "https://diavgeia.gov.gr/opendata/search.json"
PAYMENT_TYPE = "Β.2.2"          # ΕΝΤΑΛΜΑ ΠΛΗΡΩΜΗΣ - actual payment orders
MAX_SPAN_DAYS = 150             # stay safely under the server's ~6-month cap
PAGE_SIZE = 200
SLEEP = 0.4


def fetch(params, retries=4):
    url = API + "?" + urllib.parse.urlencode(params, encoding="utf-8")
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "public-tech-research/1.0",
            })
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode("utf-8")
            if not raw.strip():
                raise ValueError("empty response body")
            return json.loads(raw)      # json handles 9.4472918E7 correctly
        except Exception as e:          # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    print(f"  !! giving up on {url}\n     {last}", file=sys.stderr)
    return None


def windows(start: date, end: date, span=MAX_SPAN_DAYS):
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=span), end)
        yield cur, nxt
        cur = nxt


def digits(s):
    return "".join(ch for ch in str(s) if ch.isdigit()).lstrip("0")


def classify(dec, org_afm):
    """Return (list_of_payments, list_of_exclusions, list_of_anomalies)."""
    pays, excl, anom = [], [], []
    ada = dec.get("ada")
    efv = dec.get("extraFieldValues") or {}
    issue = dec.get("issueDate")
    issue_iso = (datetime.utcfromtimestamp(issue / 1000).date().isoformat()
                 if issue else "")
    subject = (dec.get("subject") or "").replace("\n", " ").strip()

    if not org_afm:
        org_afm = ((efv.get("org") or {}).get("afm")) or ""

    # Who signed it and which unit issued it. Diavgeia returns these on every
    # decision; keeping them lets you ask whether anonymity / errors concentrate
    # in one department or one signer rather than being institution-wide.
    signers = "|".join(dec.get("signerIds") or [])
    units = "|".join(dec.get("unitIds") or [])

    sponsors = efv.get("sponsor") or []
    if not sponsors:
        excl.append((ada, issue_iso, subject, "", "", "", "no sponsor block"))
        return pays, excl, anom

    for sp in sponsors:
        name_blk = sp.get("sponsorAFMName") or {}
        afm = (name_blk.get("afm") or "").strip()
        name = (name_blk.get("name") or "").strip()
        amt_blk = sp.get("expenseAmount") or {}
        amount = amt_blk.get("amount")

        # Keep the numeric amount on EVERY exclusion too - otherwise you can
        # count anonymous records but not measure how many euros they hide,
        # which is the whole point when auditing the Β.2.1 anonymity gap.
        try:
            amt_s = f"{float(amount):.2f}"
        except (TypeError, ValueError):
            amt_s = ""

        if not name_blk or not afm:
            excl.append((ada, issue_iso, subject, afm, name, amt_s,
                         "anonymous sponsor (empty sponsorAFMName)"))
            continue
        if org_afm and digits(afm) == digits(org_afm):
            excl.append((ada, issue_iso, subject, afm, name, amt_s,
                         "self-referential (payroll/EFKA/FMY remittance)"))
            continue
        if amount in (None, "", 0):
            excl.append((ada, issue_iso, subject, afm, name, amt_s, "no amount"))
            continue

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            excl.append((ada, issue_iso, subject, afm, name, amt_s,
                         "unparseable amount"))
            continue

        # --- AFM-in-amount detector -------------------------------------
        # The tax ID typed into the amount field. Compare digit strings so
        # 094472918 == 94472918.0 is caught regardless of leading zero.
        if amount == int(amount) and digits(int(amount)) == digits(afm):
            anom.append((ada, issue_iso, subject, afm, name, f"{amount:.2f}",
                         "amount equals supplier AFM - data-entry error"))
            excl.append((ada, issue_iso, subject, afm, name, amt_s,
                         "ANOMALY: amount == supplier AFM"))
            continue
        if amount < 0:
            excl.append((ada, issue_iso, subject, afm, name, amt_s,
                         "negative amount"))
            continue

        pays.append((ada, issue_iso, subject, afm, name, round(amount, 2),
                     sp.get("cpv") or "", sp.get("kae") or ""))
    return pays, excl, anom


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", required=True, help="Diavgeia organisation UID, e.g. 99221940")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", default=date.today().isoformat(), help="YYYY-MM-DD")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--type", default=PAYMENT_TYPE,
                    help="decision type (default Β.2.2 payment orders)")
    ap.add_argument("--sleep", type=float, default=SLEEP)
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    outdir = args.outdir or f"data/{args.org}/payments"
    import os
    os.makedirs(outdir, exist_ok=True)

    all_pay, all_excl, all_anom = [], [], []
    org_afm = None
    total_seen = 0

    for w_start, w_end in windows(start, end):
        page = 0
        while True:
            params = {
                "org": args.org,
                "type": args.type,
                "from_issue_date": w_start.isoformat(),
                "to_issue_date": w_end.isoformat(),
                "size": PAGE_SIZE,
                "page": page,
            }
            data = fetch(params)
            if data is None:
                break
            info = data.get("info", {}) or {}
            decisions = data.get("decisions", []) or []

            if page == 0:
                # Verify the server honoured our range; warn if it clamped.
                q = info.get("query", "")
                if w_end.isoformat() not in q and str(w_end.year) not in q:
                    print(f"  ~ note: server may have adjusted the range. "
                          f"echoed: {q[:120]}", file=sys.stderr)
                print(f"[{w_start} .. {w_end}] total={info.get('total')}")

            if not decisions:
                break

            for dec in decisions:
                if org_afm is None:
                    org_afm = (((dec.get("extraFieldValues") or {}).get("org")) or {}).get("afm")
                p, e, a = classify(dec, org_afm)
                all_pay.extend(p); all_excl.extend(e); all_anom.extend(a)
            total_seen += len(decisions)

            if len(decisions) < PAGE_SIZE:
                break
            page += 1
            time.sleep(args.sleep)
        time.sleep(args.sleep)

    # ---- write outputs -------------------------------------------------
    def dump(name, header, rows):
        path = os.path.join(outdir, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)
        return path

    dump("payments.csv",
         ["ada", "issue_date", "subject", "supplier_afm", "supplier_name",
          "amount_eur", "cpv", "kae"], all_pay)
    dump("excluded.csv",
         ["ada", "issue_date", "subject", "supplier_afm", "supplier_name",
          "amount_eur", "reason"], all_excl)
    dump("anomalies.csv",
         ["ada", "issue_date", "subject", "supplier_afm", "supplier_name",
          "recorded_amount", "note"], all_anom)

    monthly = defaultdict(lambda: [0, 0.0])
    for r in all_pay:
        m = r[1][:7]
        monthly[m][0] += 1
        monthly[m][1] += r[5]
    dump("monthly_summary.csv", ["month", "n_payments", "total_eur"],
         [(m, v[0], round(v[1], 2)) for m, v in sorted(monthly.items())])

    total = sum(r[5] for r in all_pay)
    print("\n" + "=" * 62)
    print(f"decisions scanned      : {total_seen}")
    print(f"VERIFIED PAYMENTS      : {len(all_pay)}")
    print(f"VERIFIED TOTAL (EUR)   : {total:,.2f}")
    print(f"excluded records       : {len(all_excl)}")
    if all_excl:
        agg = defaultdict(lambda: [0, 0.0])
        for e in all_excl:
            try:
                v = float(e[5])
            except (TypeError, ValueError):
                v = 0.0
            agg[e[6]][0] += 1
            agg[e[6]][1] += v
        print("  excluded value by reason:")
        for reason, (n, v) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
            print(f"    {n:>6}  {v:>16,.2f}  {reason}")
    if all_anom:
        print(f"\n!! {len(all_anom)} SUSPECTED DATA-ENTRY ERROR(S) "
              f"(amount == supplier AFM) - see anomalies.csv")
        for a in all_anom[:10]:
            print(f"   {a[0]}  {a[1]}  {a[4][:44]:44s} EUR {float(a[5]):,.2f}")
    print(f"\nwritten to: {outdir}/")
    print("=" * 62)


if __name__ == "__main__":
    main()
