#!/usr/bin/env python3
"""
Cross-check our Diavgeia extractions against the glossAPI corpus of OCR'd PDF text.

WHY THIS MATTERS
----------------
Our expensive step was never fetching records — it was verifying them against the
signed source document. We have done that 63 times, by hand, one PDF at a time.

glossAPI/diavgeia (HuggingFace, gated, CC-BY-4.0) already contains the extracted
PDF text for ~2.8M Diavgeia documents, keyed by ΑΔΑ:
    id             = ΑΔΑ
    markdown_text  = the document body (what we were calling pdftotext for)
    metadata_json  = the same Diavgeia metadata we pull from the API

So for every record of ours inside its coverage window we can do, for free and at
scale, the three things we have been doing by hand on samples:

  1. AMOUNT VERIFICATION      does the document text agree with the API's
                              expenseAmount? (this is how the 16 ×100 errors were
                              proven — on 49 records; here it can run on thousands)
  2. SUPPLIER RECOVERY        the Β.2.1 "anonymous" records DO name the payee in the
                              document. We proved that on 14 records. This recovers
                              names in bulk, which is the biggest open finding in the
                              project (€35.6M unattributed at Rhodes).
  3. RANDOM-SAMPLE AUDIT      Gate 4's blocker. Instead of 60 hand-read PDFs per
                              hospital, sample hundreds at zero marginal cost.

HARD LIMIT — COVERAGE
---------------------
The corpus was collected via the same API window trap we hit: it is concentrated in
roughly **Jul 2025 – Feb 2026**, NOT the full 2010→ archive and NOT our full 5 years.
Expect it to cover ~6 months of a 5-year pull. Records outside the window must still
be verified the slow way. Verify actual coverage with --coverage before relying on it.

OCR CAVEAT
----------
glossAPI used RapidOCR. Our own pdftotext extractions hit documents with broken font
encodings (mojibake) where naive parsing silently returned nothing — and a null parse
was briefly misread as "no supplier disclosed". Treat a failed extraction here as
UNKNOWN, never as absence. That distinction is the whole lesson of this project.

SETUP
-----
    pip install datasets pandas
    huggingface-cli login          # dataset is gated; access already granted
    python3 scripts/glossapi_crosscheck.py --coverage
    python3 scripts/glossapi_crosscheck.py --org 99221940 --mode amounts
    python3 scripts/glossapi_crosscheck.py --org 99221940 --mode suppliers
"""

import argparse, csv, json, os, re, sys

# ---------- text extraction (same patterns proven against real documents) ----------

def _num(s):
    s = s.strip()
    # European 1.234.567,89  vs  US 1,234,567.89
    if re.search(r",\d{2}$", s):
        return float(s.replace(".", "").replace(",", "."))
    return float(s.replace(",", ""))

AMOUNT_PATTERNS = [
    r"ποσ[όο]\s*των\s*ευρ[ώω]\s*:?\s*#?\s*([\d.,]+)\s*#",      # old ΕΝΤΑΛΜΑ layout
    r"ΣΥΝΟΛΙΚΟ\s+ΠΟΣΟ\s*:.*?([\d][\d.,]*\d)\s*$",               # newer layout
    r"ΣΥΝΟΛΟ\s*\(ολογράφω[ςσ]\)\s*:.*?([\d][\d.,]*\d)\s*$",
    r"ΓΕΝΙΚΟ ΣΥΝΟΛΟ[^:]*:\s*([\d.,]+)",
    r"συνολικο[ύυ]\s+ποσο[ύυ]\s+([\d.,]+)\s*ευρ",               # ΠΔΕ layout
]

PAYEE_PATTERNS = [
    r"Στον\s+[∆Δ]ικαιούχο\s*:?\s*(.{3,70})",
    r"[∆Δ]ΙΚΑΙΟΥΧΟΣ\s*:?\s*(.{3,70})",
    r"ΠΡΟΜΗΘΕΥΤΗΣ\s*:?\s*(.{3,70})",
    # direct-award acts name the winning bidder inline; mojibake-tolerant variant
    r"(?:εταιρεία[ςσ]|εηαιπεία[ρς])\s+([A-ZΑ-Ω][A-ZΑ-Ω0-9 .&\-]{3,45})",
]

def extract_amount(text):
    for p in AMOUNT_PATTERNS:
        m = re.search(p, text, re.M | re.I)
        if m:
            try:
                return _num(m.group(1))
            except ValueError:
                continue
    return None

def extract_payee(text):
    for p in PAYEE_PATTERNS:
        m = re.search(p, text)
        if m and m.group(1).strip():
            return " ".join(m.group(1).split())[:70]
    return None

def extract_offers(text):
    """Number of bids in a direct-award act — feeds the single-bid-rate question."""
    m = re.search(r"(?:κατατέθηκ|θαηαηέζεθ)\w*\s+(\d+)\s*\(", text)
    return int(m.group(1)) if m else None

# ---------- corpus access ----------

def iter_corpus(streaming=True, limit=None):
    try:
        from datasets import load_dataset
    except ImportError:
        sys.exit("pip install datasets   (and: huggingface-cli login)")
    ds = load_dataset("glossAPI/diavgeia", split="train", streaming=streaming)
    for i, row in enumerate(ds):
        if limit and i >= limit:
            break
        yield row

def org_of(row):
    try:
        return json.loads(row["metadata_json"]).get("organizationId")
    except Exception:
        return None

# ---------- modes ----------

def coverage(orgs, scan_limit):
    """How much of our data does the corpus actually cover? Run this FIRST."""
    want = set(orgs)
    hits = {o: 0 for o in want}
    dates = {o: [] for o in want}
    seen = 0
    for row in iter_corpus(limit=scan_limit):
        seen += 1
        o = org_of(row)
        if o in want:
            hits[o] += 1
            try:
                d = json.loads(row["metadata_json"]).get("issueDate")
                if d:
                    from datetime import datetime
                    dates[o].append(datetime.utcfromtimestamp(d/1000).date().isoformat())
            except Exception:
                pass
        if seen % 100_000 == 0:
            print(f"  scanned {seen:,} rows… hits so far: {sum(hits.values())}", file=sys.stderr)
    print(f"\nscanned {seen:,} corpus rows")
    for o in orgs:
        ds_ = sorted(dates[o])
        span = f"{ds_[0]} → {ds_[-1]}" if ds_ else "—"
        print(f"  org {o}: {hits[o]:,} documents   {span}")
    print("\nNOTE: corpus is concentrated ~Jul 2025–Feb 2026. Records outside that "
          "window still need direct PDF verification.")

def load_ours(org):
    rows = {}
    for sub in ("payments", "payments_B21"):
        for name in ("payments_corrected.csv", "payments.csv"):
            p = f"data/{org}/{sub}/{name}"
            if os.path.exists(p):
                for r in csv.DictReader(open(p)):
                    rows[r["ada"]] = {"amount": float(r["amount_eur"] or 0),
                                      "supplier": r["supplier_name"], "layer": sub}
                break
        p = f"data/{org}/{sub}/excluded.csv"
        if os.path.exists(p):
            for r in csv.DictReader(open(p)):
                if "anonymous" in (r.get("reason") or ""):
                    try:
                        a = float(r.get("amount_eur") or 0)
                    except ValueError:
                        a = 0.0
                    rows[r["ada"]] = {"amount": a, "supplier": "", "layer": sub + ":ANON"}
    return rows

def run(org, mode, scan_limit, out):
    ours = load_ours(org)
    if not ours:
        sys.exit(f"no local data for org {org} — pull it first")
    print(f"local records for {org}: {len(ours):,}", file=sys.stderr)
    res = []
    seen = matched = 0
    for row in iter_corpus(limit=scan_limit):
        seen += 1
        ada = row.get("id")
        if ada not in ours:
            continue
        matched += 1
        txt = row.get("markdown_text") or ""
        mine = ours[ada]
        rec = {"ada": ada, "layer": mine["layer"], "api_amount": mine["amount"],
               "api_supplier": mine["supplier"]}
        if mode in ("amounts", "both"):
            doc = extract_amount(txt)
            rec["doc_amount"] = doc
            rec["ratio"] = round(mine["amount"]/doc, 4) if doc else None
            rec["verdict"] = ("PARSE_FAIL" if doc is None else
                              "match" if abs(mine["amount"]-doc) < 0.02 else
                              "x100" if doc and abs(mine["amount"]/doc - 100) < 0.5 else
                              "MISMATCH")
        if mode in ("suppliers", "both"):
            rec["doc_payee"] = extract_payee(txt)
            rec["offers"] = extract_offers(txt)
        res.append(rec)
        if matched % 500 == 0:
            print(f"  matched {matched}…", file=sys.stderr)
    if not res:
        sys.exit("no overlap found — check --scan-limit or coverage window")
    fields = sorted({k for r in res for k in r})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(res)
    print(f"\nscanned {seen:,} | matched {matched:,} -> {out}")
    if mode in ("amounts", "both"):
        from collections import Counter
        c = Counter(r["verdict"] for r in res)
        print("  amount verdicts:", dict(c))
        bad = [r for r in res if r["verdict"] in ("x100", "MISMATCH")]
        for r in sorted(bad, key=lambda r: -(r["api_amount"] or 0))[:10]:
            print(f"    {r['api_amount']:>14,.2f} vs doc {r['doc_amount']:>12,.2f} "
                  f"({r['verdict']})  {r['ada']}")
    if mode in ("suppliers", "both"):
        anon = [r for r in res if r["layer"].endswith("ANON")]
        named = [r for r in anon if r.get("doc_payee")]
        if anon:
            print(f"  anonymous records matched: {len(anon)}, "
                  f"payee recovered from document text: {len(named)} "
                  f"({len(named)/len(anon)*100:.0f}%)")
            recovered = sum(r["api_amount"] for r in named)
            print(f"  value re-attributable: {recovered:,.2f} EUR")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", default="99221940")
    ap.add_argument("--orgs", nargs="*", default=["99221940", "99221923"])
    ap.add_argument("--mode", choices=["amounts", "suppliers", "both", "coverage"],
                    default="both")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--scan-limit", type=int, default=None,
                    help="stop after N corpus rows (dev). Full pass is 7.79M rows.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.coverage or a.mode == "coverage":
        coverage(a.orgs, a.scan_limit)
    else:
        out = a.out or f"data/{a.org}/glossapi_crosscheck.csv"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        run(a.org, a.mode, a.scan_limit, out)

if __name__ == "__main__":
    main()
