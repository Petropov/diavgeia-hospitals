#!/usr/bin/env python3
"""
build_intelligence_dossier.py
─────────────────────────────
Builds a Markdown intelligence dossier from Diavgeia normalized data.

Philosophy: "search-wide, hydrate-narrow."
  - Reads ALL available search-level rows for breadth.
  - Reads hydrated raw JSONs only for ADAs already on disk.
  - Ranks every ADA by intelligence value and marks the top-N as
    candidates for hydration on the next pass.

Inputs (read from data/{org}/):
  normalized/decisions.csv          — flat table from build_normalized_tables.py
  normalized/procurements.csv       — procurement-filtered subset
  normalized/monthly_summary.csv    — per-month stats
  search_exports/*.json             — raw Diavgeia search API pages (fallback)
  decisions/{ada}.json              — hydrated raw JSONs (where available)

Outputs (written to data/{org}/):
  dossier_{org}.md                  — the intelligence dossier
  candidates.json                   — ranked ADAs with hydration status

Usage:
  python scripts/build_intelligence_dossier.py --org 6166
  python scripts/build_intelligence_dossier.py --org 6166 --top-n 300 --data-dir ./data
  python scripts/build_intelligence_dossier.py --org 6166 --output ./reports/lamia.md

MVP loop:
  python scripts/build_intelligence_dossier.py  --org 6166
  python scripts/hydrate_candidate_details.py   --org 6166 --limit 100
  python scripts/build_normalized_tables.py     --org 6166
  python scripts/build_intelligence_dossier.py  --org 6166   ← repeat with new data
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Scoring configuration
# ─────────────────────────────────────────────────────────────────────────────

# Base intelligence score per Diavgeia decision type.
# Higher = more likely to contain actionable procurement/legal intelligence.
DECISION_TYPE_SCORES: dict[str, int] = {
    "ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣΙΩΝ / ΜΕΛΕΤΩΝ": 10,
    "ΣΥΜΒΑΣΗ": 9,
    "ΚΑΤΑΚΥΡΩΣΗ": 9,
    "ΠΕΡΙΛΗΨΗ ΔΙΑΚΗΡΥΞΗΣ": 7,
    "ΠΕΡΙΛΗΨΗ ΔΙΑΚΗΡΥΞΗΣ / ΔΙΑΚΗΡΥΞΗ (ΑΠΟ 1.10.2025)": 7,
    "ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ": 4,
    "ΠΑΡΑΧΩΡΗΣΗ ΧΡΗΣΗΣ ΠΕΡΙΟΥΣΙΑΚΩΝ ΣΤΟΙΧΕΙΩΝ": 4,
    "ΑΛΛΗ ΠΡΑΞΗ ΑΝΑΠΤΥΞΙΑΚΟΥ ΝΟΜΟΥ": 4,
    "ΠΡΑΞΕΙΣ ΧΩΡΟΤΑΞΙΚΟΥ - ΠΟΛΕΟΔΟΜΙΚΟΥ ΠΕΡΙΕΧΟΜΕΝΟΥ": 3,
    "ΕΠΙΤΡΟΠΙΚΟ ΕΝΤΑΛΜΑ": 3,
    "ΠΡΑΞΗ ΠΟΥ ΑΦΟΡΑ ΣΕ ΣΥΛΛΟΓΙΚΟ ΟΡΓΑΝΟ - ΕΠΙΤΡΟΠΗ - ΟΜΑΔΑ ΕΡΓΑΣΙΑΣ - ΟΜΑΔΑ ΕΡΓΟΥ - ΜΕΛΗ ΣΥΛΛΟΓΙΚΟΥ ΟΡΓΑΝΟΥ": 3,
    "ΕΓΚΡΙΣΗ ΔΑΠΑΝΗΣ": 2,
    "ΕΓΚΡΙΣΗ ΠΡΟΥΠΟΛΟΓΙΣΜΟΥ": 2,
    "ΙΣΟΛΟΓΙΣΜΟΣ – ΑΠΟΛΟΓΙΣΜΟΣ": 2,
    "ΛΟΙΠΕΣ ΑΤΟΜΙΚΕΣ ΔΙΟΙΚΗΤΙΚΕΣ ΠΡΑΞΕΙΣ": 2,
    "ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ": 1,   # high volume, low per-row value
    "ΑΝΑΛΗΨΗ ΥΠΟΧΡΕΩΣΗΣ": 1,        # ditto
    "ΠΙΝΑΚΕΣ ΕΠΙΤΥΧΟΝΤΩΝ, ΔΙΟΡΙΣΤΕΩΝ & ΕΠΙΛΑΧΟΝΤΩΝ": 0,
    "ΠΡΟΚΗΡΥΞΗ ΠΛΗΡΩΣΗΣ ΘΕΣΕΩΝ": 0,
}

# Subject keywords that boost score (procurement / legal relevance)
HIGH_VALUE_KEYWORDS: list[str] = [
    "διαγωνισμ",   # tender
    "συμβαση",     # contract
    "συμβατ",      # contractual
    "κατακυρ",     # tender award
    "διακηρυξ",    # tender notice
    "μελετ",       # study / design
    "εργο",        # works / project
    "κατασκευ",    # construction
    "ανακαιν",     # renovation
    "συντηρησ",    # maintenance
    "δικηγορ",     # lawyer
    "νομικ",       # legal
    "συμβουλ",     # consulting / advisory
    "ελεγχ",       # audit / control
    "ψηφιακ",      # digital
    "πληροφορ",    # IT / information systems
    "ασφαλ",       # insurance
    "οχηματ",      # vehicles
    "εξοπλισμ",    # equipment
    "υπηρεσι",     # services (broad, lower weight)
    "προμηθει",    # procurement / supply
    "εκτελεσ",     # execution
]

# Subject keywords that reduce score (payroll / HR noise)
LOW_VALUE_KEYWORDS: list[str] = [
    "μισθοδοσ",     # payroll
    "αποδοχ",       # salary payment
    "αποζημ",       # compensation / severance
    "υπερωρ",       # overtime
    "επιδομ",       # allowance
    "διορισμ",      # staff appointment
    "μετατ",        # staff transfer
    "αποσπ",        # secondment
    "αναρρωτ",      # sick leave
    "κανονικ αδει", # annual leave
    "πινακ",        # score tables (hiring lists)
    "αξιολογ προσ", # staff evaluation
    "πρωτοχρονιατ", # new year's celebration (low intel value)
]

# Municipality self-referencing AFMs — appear as "supplier" in payment records
# but are actually the issuing entity, not a commercial vendor.
MUNICIPALITY_SELF_AFMS: set[str] = {
    "997947640",  # ΔΗΜΟΣ ΛΑΜΙΕΩΝ (known)
    "997948000",  # variant
    "99794764",   # truncation artifact
}

# Minimum score to include an ADA in the candidates list
MIN_CANDIDATE_SCORE = 5


# ─────────────────────────────────────────────────────────────────────────────
# Scoring logic
# ─────────────────────────────────────────────────────────────────────────────

def score_decision(decision_type: str, subject: str, amount) -> int:
    """
    Score a decision by expected intelligence value.
    Returns an integer ≥ 0.  Higher = more worth hydrating.
    """
    subject_lower = (subject or "").lower()
    dtype = decision_type or ""

    # Base score from decision type
    base = 0
    for key, val in DECISION_TYPE_SCORES.items():
        if key in dtype:
            base = val
            break

    # Subject keyword bonuses
    bonus = sum(1 for kw in HIGH_VALUE_KEYWORDS if kw in subject_lower)

    # Payroll / admin penalty
    penalty = sum(4 for kw in LOW_VALUE_KEYWORDS if kw in subject_lower)

    # Amount bonus
    amount_bonus = 0
    try:
        amt = float(amount)
        if not math.isnan(amt) and amt > 0:
            if amt >= 1_000_000:
                amount_bonus = 7
            elif amt >= 200_000:
                amount_bonus = 5
            elif amt >= 50_000:
                amount_bonus = 3
            elif amt >= 10_000:
                amount_bonus = 2
            elif amt >= 1_000:
                amount_bonus = 1
    except (TypeError, ValueError):
        pass

    return max(0, base + bonus + amount_bonus - penalty)


# ─────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def safe_ada_filename(ada: str) -> str:
    """Convert ADA string to a safe filename (preserves Greek chars, replaces specials)."""
    return re.sub(r'[\\/*?:"<>|]', "_", ada) + ".json"


def load_csv(path: Path) -> list[dict]:
    """Load a CSV into a list of dicts. Returns [] if file missing."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_json_safe(path: Path):
    """Load JSON file. Returns None on missing or parse error."""
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_search_exports(org_dir: Path) -> list[dict]:
    """
    Load all *.json files from {org_dir}/search_exports/.
    Handles three formats:
      - list of decision dicts
      - {"decisions": [...]}
      - {"rows": [...]}
    """
    rows: list[dict] = []
    exports_dir = org_dir / "search_exports"
    if not exports_dir.exists():
        return rows
    for json_file in sorted(exports_dir.glob("*.json")):
        data = load_json_safe(json_file)
        if data is None:
            continue
        if isinstance(data, list):
            rows.extend(data)
        elif isinstance(data, dict):
            for key in ("decisions", "rows", "results"):
                if key in data and isinstance(data[key], list):
                    rows.extend(data[key])
                    break
    return rows


def normalize_tax_id(raw: str) -> str:
    """Normalize a tax ID from float notation (e.g. '1.29993e+08') to integer string."""
    if not raw or raw in ("nan", "None", ""):
        return ""
    try:
        return str(int(float(raw)))
    except (ValueError, OverflowError):
        return raw.strip()


def fmt_amount(val) -> str:
    """Format an amount for display, or return '—' if missing."""
    try:
        f = float(val)
        if math.isnan(f):
            return "—"
        return f"€{f:,.2f}"
    except (TypeError, ValueError):
        return "—"


def ms_to_date(ts) -> str:
    """Convert a millisecond epoch timestamp to YYYY-MM-DD."""
    try:
        return datetime.utcfromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Row normalization (handles both CSV and API field names)
# ─────────────────────────────────────────────────────────────────────────────

def normalize_row(row: dict) -> dict:
    """Extract canonical fields from a decision row (CSV or API format)."""
    ada = (
        row.get("ada") or row.get("ADA") or
        row.get("decisionId") or row.get("id") or ""
    ).strip()

    dtype = (
        row.get("decision_type") or row.get("decisionType") or
        row.get("decisionTypeId") or ""
    ).strip()

    subject = (row.get("subject") or row.get("Subject") or "").strip()
    amount  = row.get("amount") or row.get("awardAmount") or ""
    year    = str(row.get("year") or "").strip()
    month   = str(row.get("month") or "").strip()
    supplier_tax_id = normalize_tax_id(
        str(row.get("supplier_tax_id") or row.get("supplierTaxId") or "")
    )

    # Try to extract year/month from issueDate if not present
    if (not year or not month) and row.get("issueDate"):
        d = ms_to_date(row["issueDate"])
        if d:
            parts = d.split("-")
            year = year or parts[0]
            month = month or parts[1].lstrip("0")

    return {
        "ada": ada,
        "decision_type": dtype,
        "subject": subject,
        "amount": amount,
        "year": year,
        "month": month,
        "supplier_tax_id": supplier_tax_id,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────

def build_dossier(
    org: str,
    data_dir: Path,
    top_n: int = 200,
    output_path: Path | None = None,
) -> dict:

    org_dir       = data_dir / org
    decisions_dir = org_dir / "decisions"
    normalized_dir= org_dir / "normalized"
    candidates_path = org_dir / "candidates.json"

    org_dir.mkdir(parents=True, exist_ok=True)
    decisions_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Load all available decision rows ───────────────────────────────
    print(f"\n[1/6] Loading decisions for org {org} ...")

    all_rows_raw: list[dict] = []

    csv_rows = load_csv(normalized_dir / "decisions.csv")
    if csv_rows:
        print(f"      {len(csv_rows):,} rows from normalized/decisions.csv")
        all_rows_raw.extend(csv_rows)

    search_rows = load_search_exports(org_dir)
    if search_rows:
        print(f"      {len(search_rows):,} rows from search_exports/")
        # Merge: add search rows whose ADA is not yet in all_rows_raw
        existing_adas = {normalize_row(r)["ada"] for r in all_rows_raw}
        added = 0
        for r in search_rows:
            ada = normalize_row(r)["ada"]
            if ada and ada not in existing_adas:
                all_rows_raw.append(r)
                existing_adas.add(ada)
                added += 1
        if added:
            print(f"      +{added:,} unique ADAs merged from search exports")

    if not all_rows_raw:
        print("      ⚠  No decision data found. Expected one of:")
        print(f"         {normalized_dir}/decisions.csv")
        print(f"         {org_dir}/search_exports/*.json")
        print("      Continuing with empty dataset — dossier will be skeletal.")

    # Normalize all rows
    all_rows = [normalize_row(r) for r in all_rows_raw]
    all_rows = [r for r in all_rows if r["ada"]]  # drop empty ADAs
    print(f"      Total unique decisions: {len(all_rows):,}")

    # ── 2. Load supplementary tables ──────────────────────────────────────
    print("[2/6] Loading supplementary tables ...")
    procurement_rows = load_csv(normalized_dir / "procurements.csv")
    monthly_rows     = load_csv(normalized_dir / "monthly_summary.csv")
    print(f"      procurement rows: {len(procurement_rows):,}")
    print(f"      monthly summary rows: {len(monthly_rows):,}")

    # ── 3. Score and rank ─────────────────────────────────────────────────
    print("[3/6] Scoring decisions ...")

    scored: list[dict] = []
    for row in all_rows:
        s = score_decision(row["decision_type"], row["subject"], row["amount"])
        scored.append({**row, "score": s})

    scored.sort(key=lambda x: x["score"], reverse=True)

    # Candidates = everything above threshold, up to top_n
    candidates_raw = [r for r in scored if r["score"] >= MIN_CANDIDATE_SCORE][:top_n]
    print(f"      Scored {len(scored):,} decisions → {len(candidates_raw)} candidates (score ≥ {MIN_CANDIDATE_SCORE})")

    # ── 4. Check hydration status ─────────────────────────────────────────
    print("[4/6] Checking hydration status ...")

    candidates: list[dict] = []
    for row in candidates_raw:
        ada = row["ada"]
        json_path = decisions_dir / safe_ada_filename(ada)
        hydrated = json_path.exists()
        candidates.append({
            **row,
            "hydrated": hydrated,
            "needs_hydration": not hydrated,
            "json_path": str(json_path),
        })

    hydrated_count = sum(1 for c in candidates if c["hydrated"])
    needs_hydration = [c for c in candidates if c["needs_hydration"]]

    print(f"      Hydrated:       {hydrated_count}")
    print(f"      Needs hydration:{len(needs_hydration)}")

    # Save candidates.json (strip internal json_path, keep it clean)
    candidates_export = [
        {
            "ada": c["ada"],
            "score": c["score"],
            "decision_type": c["decision_type"],
            "subject": c["subject"][:300],
            "amount": str(c["amount"]),
            "year": c["year"],
            "month": c["month"],
            "supplier_tax_id": c["supplier_tax_id"],
            "hydrated": c["hydrated"],
            "needs_hydration": c["needs_hydration"],
        }
        for c in candidates
    ]
    with open(candidates_path, "w", encoding="utf-8") as f:
        json.dump(candidates_export, f, ensure_ascii=False, indent=2)
    print(f"      Saved → {candidates_path}")

    # ── 5. Load hydrated decision details ─────────────────────────────────
    print("[5/6] Loading hydrated JSON details ...")

    hydrated_details: list[dict] = []
    for c in candidates:
        if not c["hydrated"]:
            continue
        raw = load_json_safe(Path(c["json_path"]))
        if not raw:
            continue

        efv = raw.get("extraFieldValues") or {}

        # Award amount
        award_amount = None
        award_currency = "EUR"
        aw = efv.get("awardAmount") or {}
        if isinstance(aw, dict) and aw.get("amount") is not None:
            award_amount = aw["amount"]
            award_currency = aw.get("currency", "EUR")

        # Suppliers (person field)
        suppliers = [
            {"afm": p.get("afm", ""), "name": p.get("name", "")}
            for p in (efv.get("person") or [])
            if isinstance(p, dict)
        ]

        # Payees (sponsor field — used in payment finalizations)
        sponsors = []
        for s in (efv.get("sponsor") or []):
            afm_obj = s.get("sponsorAFMName") or {}
            exp_obj = s.get("expenseAmount") or {}
            sponsors.append({
                "afm": afm_obj.get("afm", ""),
                "name": afm_obj.get("name", ""),
                "amount": exp_obj.get("amount"),
                "kae": s.get("kae", ""),
            })

        # Related ADAs
        related = [
            rd["relatedDecisionsADA"]
            for rd in (efv.get("relatedDecisions") or [])
            if isinstance(rd, dict) and rd.get("relatedDecisionsADA")
        ]

        hydrated_details.append({
            "ada": c["ada"],
            "score": c["score"],
            "decision_type": c["decision_type"],
            "subject": raw.get("subject", c["subject"]),
            "protocol_number": raw.get("protocolNumber", ""),
            "issue_date": ms_to_date(raw.get("issueDate")),
            "signer_ids": raw.get("signerIds", []),
            "unit_ids": raw.get("unitIds", []),
            "private_data": raw.get("privateData", False),
            "status": raw.get("status", ""),
            "url": raw.get("documentUrl") or f"https://diavgeia.gov.gr/doc/{c['ada']}",
            "award_amount": award_amount,
            "award_currency": award_currency,
            "assignment_type": efv.get("assignmentType", ""),
            "cpv": efv.get("cpv") or [],
            "suppliers": suppliers,
            "sponsors": sponsors,
            "related_decisions": related,
        })

    print(f"      Loaded {len(hydrated_details)} hydrated records")

    # ── 6. Build aggregates ───────────────────────────────────────────────

    # Decision type distribution
    type_counter: Counter = Counter()
    for r in all_rows:
        type_counter[r["decision_type"] or "UNKNOWN"] += 1

    # Supplier frequency (excluding self-referencing AFMs)
    supplier_counter: Counter = Counter()
    for r in all_rows:
        tid = r["supplier_tax_id"]
        if tid and tid not in MUNICIPALITY_SELF_AFMS:
            supplier_counter[tid] += 1

    # Monthly summary fallback
    if not monthly_rows:
        month_map: dict[tuple, dict] = defaultdict(lambda: {"count": 0})
        for r in all_rows:
            key = (r["year"], r["month"])
            month_map[key]["count"] += 1
        monthly_rows = [
            {"year": k[0], "month": k[1], "decision_count": v["count"]}
            for k, v in sorted(month_map.items())
        ]

    # ── 7. Write dossier ──────────────────────────────────────────────────
    print("[6/6] Writing dossier ...")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if output_path is None:
        output_path = org_dir / f"dossier_{org}.md"

    lines: list[str] = []

    def h(level: int, text: str):
        lines.append(f"\n{'#' * level} {text}\n")

    def p(*parts: str):
        lines.append(" ".join(parts))

    def blank():
        lines.append("")

    # ── Header ──
    lines.append(f"# Municipality Intelligence Dossier — Org UID {org}")
    lines.append(f"\n_Generated {now} · {len(all_rows):,} decisions loaded · "
                 f"{hydrated_count} hydrated · {len(needs_hydration)} pending hydration_\n")

    # ── Dataset Health ──
    h(2, "Dataset Health")
    lines.append(f"| Metric | Value |")
    lines.append(f"|:---|---:|")
    lines.append(f"| Total decisions loaded | **{len(all_rows):,}** |")
    lines.append(f"| Procurement rows (normalized) | **{len(procurement_rows):,}** |")
    lines.append(f"| High-value candidates (score ≥ {MIN_CANDIDATE_SCORE}) | **{len(candidates):,}** |")
    lines.append(f"| Already hydrated | **{hydrated_count}** |")
    lines.append(f"| Needs hydration | **{len(needs_hydration)}** |")
    blank()

    if monthly_rows:
        h(3, "Monthly Activity")
        lines.append("| Year | Month | Decisions | Enriched | Suppliers |")
        lines.append("|-----:|------:|----------:|---------:|----------:|")
        for r in monthly_rows[:30]:
            lines.append(
                f"| {r.get('year','')} | {r.get('month','')} "
                f"| {r.get('decision_count', r.get('decisions',''))} "
                f"| {r.get('detail_enriched_decision_count', r.get('enriched','—'))} "
                f"| {r.get('supplier_count', r.get('suppliers','—'))} |"
            )
        blank()

    # ── Decision Type Distribution ──
    h(2, "Decision Type Distribution")
    lines.append("| Decision Type | Count | % |")
    lines.append("|:---|---:|---:|")
    total_typed = sum(type_counter.values())
    for dtype, count in type_counter.most_common(20):
        pct = f"{100*count/total_typed:.1f}%" if total_typed else "—"
        lines.append(f"| {dtype} | {count:,} | {pct} |")
    blank()

    # ── Repeated Supplier Tax IDs ──
    top_suppliers = [(tid, cnt) for tid, cnt in supplier_counter.most_common(30) if cnt > 1]
    if top_suppliers:
        h(2, "Repeated Supplier Tax IDs")
        lines.append("_Excludes municipality's own AFM. Frequency = appearances as supplier in loaded decisions._\n")
        lines.append("| Tax ID | Appearances |")
        lines.append("|:---|---:|")
        for tid, cnt in top_suppliers:
            lines.append(f"| `{tid}` | {cnt} |")
        blank()

    # ── Top Candidates Table ──
    h(2, "High-Value Candidate ADAs")
    lines.append(f"_Top {min(len(candidates), top_n)} decisions ranked by intelligence value "
                 f"(score ≥ {MIN_CANDIDATE_SCORE}). Full list in `candidates.json`._\n")
    lines.append("| Score | ADA | Yr | Type (abbrev.) | Subject | Amount | Hydrated |")
    lines.append("|------:|:----|---:|:---------------|:--------|-------:|:---------|")
    for c in candidates[:60]:
        dtype_short = c["decision_type"][:35] + ("…" if len(c["decision_type"]) > 35 else "")
        subj_short  = c["subject"][:65] + ("…" if len(c["subject"]) > 65 else "")
        flag = "✓" if c["hydrated"] else "⚠"
        amt  = fmt_amount(c["amount"])
        lines.append(f"| {c['score']} | `{c['ada']}` | {c['year']} | {dtype_short} | {subj_short} | {amt} | {flag} |")
    if len(candidates) > 60:
        lines.append(f"| … | _{len(candidates)-60} more in candidates.json_ | | | | | |")
    blank()

    # ── Needs Hydration ──
    h(2, "ADAs Pending Hydration")
    lines.append(f"Run to fetch next batch:\n"
                 f"```bash\npython scripts/hydrate_candidate_details.py --org {org} --limit 100\n```\n")
    if needs_hydration:
        lines.append("| Pri | ADA | Score | Type | Subject |")
        lines.append("|----:|:----|------:|:----|:--------|")
        for i, c in enumerate(needs_hydration[:150], 1):
            dtype_s = c["decision_type"][:40] + ("…" if len(c["decision_type"]) > 40 else "")
            subj_s  = c["subject"][:80] + ("…" if len(c["subject"]) > 80 else "")
            lines.append(f"| {i} | `{c['ada']}` | {c['score']} | {dtype_s} | {subj_s} |")
    else:
        lines.append("_All top candidates are already hydrated. 🎉_")
    blank()

    # ── Hydrated Decision Details ──
    if hydrated_details:
        h(2, "Hydrated Decision Details")
        lines.append(f"_{len(hydrated_details)} high-value decisions with full raw JSON data, "
                     f"sorted by intelligence score._\n")

        for det in sorted(hydrated_details, key=lambda x: x["score"], reverse=True):
            ada  = det["ada"]
            url  = det["url"]
            priv = " ⚠ privateData" if det["private_data"] else ""

            lines.append(f"### [`{ada}`]({url}) — Score {det['score']}{priv}\n")
            lines.append(f"**Type:** {det['decision_type']}  ")
            lines.append(f"**Date:** {det['issue_date']}  ")
            if det.get("protocol_number"):
                lines.append(f"**Protocol:** {det['protocol_number']}  ")
            lines.append(f"**Subject:** {det['subject']}  ")

            if det["award_amount"] is not None:
                lines.append(f"**Award:** {fmt_amount(det['award_amount'])} {det['award_currency']}  ")
            if det["assignment_type"]:
                lines.append(f"**Assignment type:** {det['assignment_type']}  ")
            if det["cpv"]:
                lines.append(f"**CPV:** {', '.join(det['cpv'])}  ")
            if det["signer_ids"]:
                lines.append(f"**Signer IDs:** {', '.join(det['signer_ids'])}  ")

            if det["suppliers"]:
                lines.append("\n**Suppliers:**")
                for s in det["suppliers"]:
                    afm_str = f"`{s['afm']}`" if s["afm"] else "—"
                    lines.append(f"  - AFM {afm_str} — {s['name']}")

            if det["sponsors"]:
                lines.append("\n**Payees (payment record):**")
                for s in det["sponsors"]:
                    amt_s = fmt_amount(s["amount"])
                    lines.append(f"  - {s['name']} (AFM `{s['afm']}`) — {amt_s} · KAE `{s['kae']}`")

            if det["related_decisions"]:
                links = ", ".join(
                    f"[`{r}`](https://diavgeia.gov.gr/doc/{r})"
                    for r in det["related_decisions"]
                )
                lines.append(f"\n**Related ADAs:** {links}  ")

            blank()

    # ── Caveats ──
    h(2, "Known Data Caveats")
    caveats = [
        "**AFM 997947640 (ΔΗΜΟΣ ΛΑΜΙΕΩΝ)** appears as 'supplier' in ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ records — "
        "it is the municipality's own AFM captured from the `org` field, not the actual payee. "
        "True payees live in `extraFieldValues.sponsor[].sponsorAFMName`.",

        "**Amount extraction is sparse.** Most amounts are only in raw JSON "
        "`extraFieldValues.awardAmount` and are not surfaced in search-level exports.",

        "**Historical years are search-only.** Hydration coverage is thin outside the hydrated months; "
        "trend analysis across years has low reliability.",

        "**Payroll / admin decisions contaminate procurement rows.** "
        "Apply the score filter to reduce noise before analysis.",

        "**`privateData: true` decisions** involve natural persons; supplier identity is "
        "legally protected and full names are redacted in Diavgeia.",

        "**Supplier names missing** for most rows. Resolve via ΓΕΜΗ business registry "
        "or ΑΑΔΕ cross-reference using the AFM.",

        "**AFMs in scientific notation** (e.g., `1.29993e+08`) are normalised to integers "
        "by this script, but source data should be re-extracted as integers at collection time.",
    ]
    for cav in caveats:
        lines.append(f"- {cav}")
    blank()

    # ── Next Steps ──
    h(2, "Next Steps — MVP Loop")
    lines.append("```bash")
    lines.append(f"# 1. Hydrate the next batch of high-value ADAs")
    lines.append(f"python scripts/hydrate_candidate_details.py --org {org} --limit 100")
    lines.append(f"")
    lines.append(f"# 2. Rebuild normalized tables from latest search exports")
    lines.append(f"python scripts/build_normalized_tables.py --org {org}")
    lines.append(f"")
    lines.append(f"# 3. Rebuild dossier with newly hydrated data")
    lines.append(f"python scripts/build_intelligence_dossier.py --org {org}")
    lines.append("```")
    blank()

    # Write file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n✓  Dossier  → {output_path}")
    print(f"✓  Candidates → {candidates_path}")
    print(f"\n   decisions:      {len(all_rows):,}")
    print(f"   candidates:     {len(candidates)}")
    print(f"   hydrated:       {hydrated_count}")
    print(f"   needs hydration:{len(needs_hydration)}")

    return {
        "total_decisions": len(all_rows),
        "candidates": len(candidates),
        "hydrated": hydrated_count,
        "needs_hydration": len(needs_hydration),
        "output_path": str(output_path),
        "candidates_path": str(candidates_path),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build Diavgeia intelligence dossier (search-wide, hydrate-narrow).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--org", required=True, help="Organisation UID, e.g. 6166")
    parser.add_argument(
        "--data-dir", default="./data",
        help="Root data directory (default: ./data)",
    )
    parser.add_argument(
        "--top-n", type=int, default=200,
        help="Maximum candidates to rank (default: 200)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Override dossier output path (default: data/{org}/dossier_{org}.md)",
    )
    args = parser.parse_args()

    result = build_dossier(
        org=args.org,
        data_dir=Path(args.data_dir),
        top_n=args.top_n,
        output_path=Path(args.output) if args.output else None,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
