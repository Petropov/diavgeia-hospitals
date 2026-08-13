#!/usr/bin/env python3
"""
build_normalized_tables.py
───────────────────────────
Converts raw Diavgeia search export JSON files into normalised CSV tables
consumed by build_intelligence_dossier.py.

This is the "ingest" step — run it whenever you add new search_exports.

Inputs (from data/{org}/search_exports/*.json):
  Each file is a raw Diavgeia search API response page, supporting formats:
    - {"decisions": [...], "info": {...}}
    - list of decision dicts
    - {"rows": [...]}

Outputs (written to data/{org}/normalized/):
  decisions.csv         — one row per unique ADA (all types)
  procurements.csv      — filtered to procurement-relevant decision types
  monthly_summary.csv   — per (year, month) aggregate stats

Usage:
  python scripts/build_normalized_tables.py --org 6166
  python scripts/build_normalized_tables.py --org 6166 --data-dir /path/to/data
  python scripts/build_normalized_tables.py --org 6166 --verbose

The Diavgeia search API can be queried like:
  GET https://diavgeia.gov.gr/luminapi/api/search
      ?q=*
      &fq=organizationUid:6166
      &size=500
      &page=0
      &sort=issueDate+DESC

Save each response page as data/6166/search_exports/{year}_{month:02d}_p{page}.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Decision types that are considered procurement-relevant
# ─────────────────────────────────────────────────────────────────────────────
PROCUREMENT_TYPES = {
    "ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣΙΩΝ / ΜΕΛΕΤΩΝ",
    "ΣΥΜΒΑΣΗ",
    "ΚΑΤΑΚΥΡΩΣΗ",
    "ΠΕΡΙΛΗΨΗ ΔΙΑΚΗΡΥΞΗΣ",
    "ΠΕΡΙΛΗΨΗ ΔΙΑΚΗΡΥΞΗΣ / ΔΙΑΚΗΡΥΞΗ (ΑΠΟ 1.10.2025)",
    "ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ",          # often contains tender procedural acts
    "ΕΠΙΤΡΟΠΙΚΟ ΕΝΤΑΛΜΑ",
    "ΠΑΡΑΧΩΡΗΣΗ ΧΡΗΣΗΣ ΠΕΡΙΟΥΣΙΑΚΩΝ ΣΤΟΙΧΕΙΩΝ",
    "ΕΓΚΡΙΣΗ ΔΑΠΑΝΗΣ",
    "ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ",    # included for supplier tracking
    "ΑΝΑΛΗΨΗ ΥΠΟΧΡΕΩΣΗΣ",         # budget commitments
}

# Known municipality self-referencing AFMs (not real suppliers)
SELF_AFMS: set[str] = {"997947640", "997948000", "99794764"}

# CSV column order for decisions.csv
DECISIONS_COLUMNS = [
    "ada", "year", "month", "decision_type", "subject",
    "supplier_tax_id", "amount", "issue_date", "protocol_number",
    "signer_ids", "unit_ids", "private_data", "status",
    "cpv", "assignment_type", "award_currency",
]

# CSV column order for procurements.csv
PROCUREMENTS_COLUMNS = DECISIONS_COLUMNS  # same schema, filtered rows

# CSV column order for monthly_summary.csv
MONTHLY_COLUMNS = [
    "year", "month", "decision_count",
    "detail_enriched_decision_count", "supplier_count",
    "procurement_count", "total_amount",
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def ms_to_date(ts) -> str:
    try:
        return datetime.utcfromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return ""


def ms_to_ym(ts) -> tuple[str, str]:
    d = ms_to_date(ts)
    if d:
        parts = d.split("-")
        return parts[0], str(int(parts[1]))
    return "", ""


def normalize_afm(raw) -> str:
    """Normalize an AFM from any format to a clean integer string."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if s in ("nan", "None", "0", ""):
        return ""
    # Handle scientific notation: "1.29993e+08" → "129993000"
    try:
        return str(int(float(s)))
    except (ValueError, OverflowError):
        return s


def extract_amount(efv: dict) -> tuple[float | None, str]:
    """Extract award amount and currency from extraFieldValues."""
    aw = efv.get("awardAmount") or {}
    if isinstance(aw, dict):
        amt = aw.get("amount")
        cur = aw.get("currency", "EUR")
        if amt is not None:
            try:
                return float(amt), cur
            except (TypeError, ValueError):
                pass
    return None, "EUR"


def extract_supplier_afm(efv: dict) -> str:
    """
    Extract primary supplier AFM from extraFieldValues.
    For payment finalizations (ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ), the real
    supplier is in sponsor[], not in person[] or org.
    """
    # Try person[] first (ΑΝΑΘΕΣΗ decisions)
    persons = efv.get("person") or []
    if persons and isinstance(persons, list):
        for p in persons:
            afm = normalize_afm(p.get("afm"))
            if afm and afm not in SELF_AFMS:
                return afm

    # Try sponsor[] (payment finalization decisions)
    sponsors = efv.get("sponsor") or []
    if sponsors and isinstance(sponsors, list):
        for s in sponsors:
            afm_obj = s.get("sponsorAFMName") or {}
            afm = normalize_afm(afm_obj.get("afm"))
            if afm and afm not in SELF_AFMS:
                return afm

    # Fallback: org field (but this is usually the municipality itself)
    org_obj = efv.get("org") or {}
    if isinstance(org_obj, dict):
        afm = normalize_afm(org_obj.get("afm"))
        if afm and afm not in SELF_AFMS:
            return afm

    return ""


def load_json_safe(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"    ⚠  Could not load {path.name}: {e}", file=sys.stderr)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Row parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_decision_row(raw: dict) -> dict:
    """
    Parse a single raw Diavgeia decision object (from search API or hydrated JSON)
    into a normalised flat dict matching DECISIONS_COLUMNS.
    """
    ada      = (raw.get("ada") or raw.get("ADA") or "").strip()
    subject  = (raw.get("subject") or "").strip()
    dtype    = (raw.get("decisionType") or raw.get("decision_type") or "").strip()
    status   = (raw.get("status") or "").strip()
    private  = raw.get("privateData", False)
    proto    = (raw.get("protocolNumber") or "").strip()
    signer_ids = ",".join(raw.get("signerIds") or [])
    unit_ids   = ",".join(str(u) for u in (raw.get("unitIds") or []))

    issue_ts   = raw.get("issueDate")
    issue_date = ms_to_date(issue_ts)
    year, month = ms_to_ym(issue_ts)

    # If year/month already set as flat fields (from CSV input), prefer those
    year  = str(raw.get("year") or year).strip()
    month = str(raw.get("month") or month).strip()

    efv = raw.get("extraFieldValues") or {}
    if not isinstance(efv, dict):
        efv = {}

    amount, currency = extract_amount(efv)
    supplier_afm     = extract_supplier_afm(efv)

    # CPV codes
    cpv_raw = efv.get("cpv") or []
    cpv = ",".join(cpv_raw) if isinstance(cpv_raw, list) else str(cpv_raw)

    assignment_type = (efv.get("assignmentType") or "").strip()

    return {
        "ada":             ada,
        "year":            year,
        "month":           month,
        "decision_type":   dtype,
        "subject":         subject,
        "supplier_tax_id": supplier_afm,
        "amount":          "" if amount is None else str(amount),
        "issue_date":      issue_date,
        "protocol_number": proto,
        "signer_ids":      signer_ids,
        "unit_ids":        unit_ids,
        "private_data":    "true" if private else "false",
        "status":          status,
        "cpv":             cpv,
        "assignment_type": assignment_type,
        "award_currency":  currency,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def build_tables(
    org: str,
    data_dir: Path,
    verbose: bool = False,
) -> dict:

    org_dir        = data_dir / org
    exports_dir    = org_dir / "search_exports"
    normalized_dir = org_dir / "normalized"

    normalized_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Collect all raw rows from search exports ────────────────────────
    print(f"\n[1/4] Scanning search_exports for org {org} ...")

    if not exports_dir.exists():
        print(f"      ⚠  Directory not found: {exports_dir}")
        print(f"      Place Diavgeia search API pages as JSON files in that directory.")
        print(f"      Example filename: 2026_01_p0.json")
        # Still create empty output files so the pipeline doesn't break
        _write_empty_csvs(normalized_dir)
        return {"decisions": 0, "procurements": 0}

    export_files = sorted(exports_dir.glob("*.json"))
    print(f"      Found {len(export_files)} export file(s)")

    raw_decisions: list[dict] = []
    for fpath in export_files:
        data = load_json_safe(fpath)
        if data is None:
            continue

        items: list[dict] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("decisions", "rows", "results"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            # Also support a single decision object
            if not items and "ada" in data:
                items = [data]

        if verbose:
            print(f"      {fpath.name}: {len(items)} rows")
        raw_decisions.extend(items)

    print(f"      Total raw rows collected: {len(raw_decisions):,}")

    # ── 2. Deduplicate and parse ───────────────────────────────────────────
    print("[2/4] Deduplicating and parsing ...")

    seen_adas: set[str] = set()
    parsed: list[dict] = []

    for raw in raw_decisions:
        row = parse_decision_row(raw)
        ada = row["ada"]
        if not ada or ada in seen_adas:
            continue
        seen_adas.add(ada)
        parsed.append(row)

    parsed.sort(key=lambda r: (r.get("year",""), r.get("month",""), r.get("ada","")))
    print(f"      Unique decisions: {len(parsed):,}")

    # ── 3. Split into decisions vs procurements ────────────────────────────
    print("[3/4] Splitting decisions / procurements ...")

    procurements = [
        r for r in parsed
        if any(pt in r["decision_type"] for pt in PROCUREMENT_TYPES)
    ]
    print(f"      All decisions: {len(parsed):,}")
    print(f"      Procurement-relevant: {len(procurements):,}")

    # ── 4. Build monthly summary ───────────────────────────────────────────
    print("[4/4] Building monthly summary ...")

    month_map: dict[tuple, dict] = defaultdict(lambda: {
        "decision_count": 0,
        "detail_enriched_decision_count": 0,
        "supplier_count": 0,
        "procurement_count": 0,
        "total_amount": 0.0,
        "suppliers": set(),
    })

    for r in parsed:
        key = (r["year"], r["month"])
        month_map[key]["decision_count"] += 1

        # Count as "detail enriched" if it has a CPV or amount
        if r["cpv"] or r["amount"]:
            month_map[key]["detail_enriched_decision_count"] += 1

        # Track unique suppliers
        if r["supplier_tax_id"] and r["supplier_tax_id"] not in SELF_AFMS:
            month_map[key]["suppliers"].add(r["supplier_tax_id"])

        # Count procurement rows
        if any(pt in r["decision_type"] for pt in PROCUREMENT_TYPES):
            month_map[key]["procurement_count"] += 1

        # Accumulate amounts
        try:
            amt = float(r["amount"])
            if not math.isnan(amt):
                month_map[key]["total_amount"] += amt
        except (TypeError, ValueError):
            pass

    monthly_rows: list[dict] = []
    for key in sorted(month_map.keys()):
        v = month_map[key]
        monthly_rows.append({
            "year":   key[0],
            "month":  key[1],
            "decision_count": v["decision_count"],
            "detail_enriched_decision_count": v["detail_enriched_decision_count"],
            "supplier_count": len(v["suppliers"]),
            "procurement_count": v["procurement_count"],
            "total_amount": f"{v['total_amount']:.2f}" if v["total_amount"] else "",
        })

    # ── Write CSVs ────────────────────────────────────────────────────────
    out_decisions    = normalized_dir / "decisions.csv"
    out_procurements = normalized_dir / "procurements.csv"
    out_monthly      = normalized_dir / "monthly_summary.csv"

    _write_csv(out_decisions,    DECISIONS_COLUMNS,  parsed)
    _write_csv(out_procurements, PROCUREMENTS_COLUMNS, procurements)
    _write_csv(out_monthly,      MONTHLY_COLUMNS,    monthly_rows)

    print(f"\n✓  decisions.csv      → {out_decisions}  ({len(parsed):,} rows)")
    print(f"✓  procurements.csv   → {out_procurements}  ({len(procurements):,} rows)")
    print(f"✓  monthly_summary.csv→ {out_monthly}  ({len(monthly_rows)} months)")

    return {
        "decisions": len(parsed),
        "procurements": len(procurements),
        "months": len(monthly_rows),
    }


def _write_csv(path: Path, columns: list[str], rows: list[dict]):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_empty_csvs(normalized_dir: Path):
    for fname, cols in [
        ("decisions.csv",      DECISIONS_COLUMNS),
        ("procurements.csv",   PROCUREMENTS_COLUMNS),
        ("monthly_summary.csv", MONTHLY_COLUMNS),
    ]:
        path = normalized_dir / fname
        if not path.exists():
            _write_csv(path, cols, [])
            print(f"      Created empty {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build normalised CSV tables from Diavgeia search export JSONs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--org", required=True,
                        help="Organisation UID (e.g. 6166)")
    parser.add_argument("--data-dir", default="./data",
                        help="Root data directory (default: ./data)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print row counts per export file")

    args = parser.parse_args()

    result = build_tables(
        org=args.org,
        data_dir=Path(args.data_dir),
        verbose=args.verbose,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
