#!/usr/bin/env python3
"""
analyze_awards.py — risk analytics over normalized Diavgeia award data.

Reads either normalized/decisions.csv (from build_normalized_tables.py)
or any CSV with columns: ada,date,signer,afm,supplier,amount,cat,private,subject

Computes:
  1. Disclosure gaps      — awards missing supplier AFM and/or amount
  2. Supplier concentration (top-N, HHI, top-3 share) on disclosed spend
  3. Threshold proximity  — amounts within 2% below round thresholds
                            (30k legal direct-award limit; 20k/15k/12k internal)
  4. Identical-amount repetition — same € across nominally different awards
  5. Signer concentration — who signs what share of awards
  6. Same-subject clustering — repeated identical subjects (fragmentation)

Usage:
  python scripts/analyze_awards.py --csv data/6166/real/awards_2026_feb_mar.csv
  python scripts/analyze_awards.py --csv data/6166/normalized/procurements.csv --top 20
"""

from __future__ import annotations
import argparse, csv, sys
from collections import defaultdict

THRESHOLDS = (30000, 20000, 15000, 12000, 10000)
PROXIMITY = 0.98  # flag amounts in [t*0.98, t)


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    if not rows:
        sys.exit("empty csv")

    # normalise column names across formats
    def col(r, *names):
        for n in names:
            if n in r and r[n]:
                return r[n]
        return ""

    recs = [{
        "ada": col(r, "ada"),
        "afm": col(r, "afm", "supplier_tax_id"),
        "supplier": col(r, "supplier"),
        "amount": f(col(r, "amount")),
        "signer": col(r, "signer", "signer_ids"),
        "subject": col(r, "subject"),
    } for r in rows]

    total = len(recs)
    disclosed = [r for r in recs if r["amount"]]
    spend = sum(r["amount"] for r in disclosed)

    print(f"=== Disclosure ===")
    print(f"awards: {total} | with amount: {len(disclosed)} "
          f"| missing amount: {total-len(disclosed)} ({100*(total-len(disclosed))/total:.0f}%)")
    no_afm = sum(1 for r in recs if not r["afm"])
    print(f"missing supplier AFM: {no_afm} ({100*no_afm/total:.0f}%)")
    print(f"disclosed spend: €{spend:,.2f}")

    sup = defaultdict(lambda: [0, 0.0, ""])
    for r in disclosed:
        k = r["afm"] or "NONE"
        sup[k][0] += 1
        sup[k][1] += r["amount"]
        sup[k][2] = r["supplier"]
    print(f"\n=== Supplier concentration (top {a.top}) ===")
    for k, (n, amt, name) in sorted(sup.items(), key=lambda x: -x[1][1])[:a.top]:
        print(f"  €{amt:>11,.2f}  x{n:<2} {k:<12} {name[:40]}")
    if spend:
        shares = [v[1] / spend for v in sup.values()]
        hhi = sum(s * s for s in shares) * 10000
        top3 = sum(sorted((v[1] for v in sup.values()), reverse=True)[:3])
        print(f"  HHI: {hhi:,.0f} | top-3 share: {100*top3/spend:.1f}%")

    print(f"\n=== Threshold proximity (within 2% below) ===")
    hits = 0
    for r in disclosed:
        for t in THRESHOLDS:
            if t * PROXIMITY <= r["amount"] < t:
                print(f"  €{r['amount']:>10,.2f} (<{t:,})  {r['ada']}  {r['subject'][:60]}")
                hits += 1
                break
    if not hits:
        print("  none")

    print(f"\n=== Identical amounts across awards ===")
    amts = defaultdict(list)
    for r in disclosed:
        amts[round(r["amount"], 2)].append(r)
    found = False
    for amt, rs in sorted(amts.items(), key=lambda x: -x[0]):
        if len(rs) > 1 and amt >= 500:
            found = True
            print(f"  €{amt:,.2f} x{len(rs)}")
            for r in rs:
                print(f"    {r['ada']}  [{r['afm']}] {r['supplier'][:28]}  {r['subject'][:48]}")
    if not found:
        print("  none")

    print(f"\n=== Signer concentration ===")
    sig = defaultdict(int)
    for r in recs:
        sig[r["signer"] or "?"] += 1
    for s, n in sorted(sig.items(), key=lambda x: -x[1]):
        print(f"  {s}: {n} ({100*n/total:.0f}%)")

    print(f"\n=== Same-subject clusters (fragmentation) ===")
    subj = defaultdict(list)
    for r in recs:
        key = " ".join(r["subject"].split())[:70].upper()
        subj[key].append(r)
    for s, rs in sorted(subj.items(), key=lambda x: -len(x[1])):
        if len(rs) >= 3:
            undisclosed = sum(1 for r in rs if not r["amount"])
            print(f"  x{len(rs)} ({undisclosed} without amount): {s[:70]}")


if __name__ == "__main__":
    main()
