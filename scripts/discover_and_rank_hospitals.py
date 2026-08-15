#!/usr/bin/env python3
"""
Discover every active Greek public hospital on Diavgeia and stack-rank them by
actual payment volume — so the 5-year extraction can start with the biggest.

WHY NOT AN EXTERNAL BUDGET TABLE
--------------------------------
No public per-hospital budget ranking exists in machine-readable form. The
Ministry's BI-health figures reach the press only as partial highlights (e.g.
Ευαγγελισμός €97.9M medical supplies 2025; ΠΓΝ Πατρών €61.2M; Αττικόν €41.9M —
ygeiamou.gr 2026-08-11), covering single categories, not totals.

Diavgeia itself is the better ranking source: it is the same corpus we analyse,
it is complete for published payments, and ranking on it means the ranking and
the analysis cannot disagree about what a hospital spent.

METHOD
------
Phase 1 DISCOVER — page recent Β.2.2 (payment) decisions nationally. Every
  payment record carries extraFieldValues.org.{name,afm} plus organizationId.
  Any org whose name matches the hospital pattern is collected. Hospitals post
  payments most working days, so a few weeks of national traffic surfaces
  essentially all active ones. Verified against /opendata/organizations/{uid}.json.

Phase 2 RANK — for each hospital, pull the last N months of Β.2.2 and sum
  expenseAmount, applying the same exclusions as fetch_payments_history.py
  (anonymous sponsor, self-referential payroll, AFM-in-amount). Ranking is
  therefore on *verified named-supplier payment value*, consistent with the rest
  of the project.

CAVEATS BAKED IN
----------------
* Payment volume != budget. Payroll largely does not pass through Β.2.2, and
  hospitals differ in how much they route via Β.2.1 (Rhodes ~29% of value,
  Lamia ~1%). A hospital that under-publishes will under-rank. The output
  therefore also reports Β.2.1 value and a `b21_share` column so you can see
  who is hiding volume in the anonymous layer.
* Discovery misses hospitals that published no Β.2.2 in the scan window.
  Widen --discover-days if a known hospital is absent.

USAGE
-----
  python3 scripts/discover_and_rank_hospitals.py --discover-days 30 --rank-months 12
  # -> data/_registry/hospitals_ranked.csv   (+ hospitals_discovered.csv)

Then feed the top N into the 5-year extraction:
  python3 scripts/batch_pull_hospitals.py --from-ranking data/_registry/hospitals_ranked.csv --top 50
"""

import argparse, csv, json, os, re, sys, time
import urllib.parse, urllib.request
from datetime import date, timedelta

API = "https://diavgeia.gov.gr/opendata/search.json"
ORG = "https://diavgeia.gov.gr/opendata/organizations/{}.json"
PAYMENT_TYPE = "Β.2.2"
ANON_TYPE = "Β.2.1"

# Greek hospital naming. Deliberately broad; false positives are filtered by the
# org-registry check in phase 1b.
NAMELESS_OIDS = set()   # publishers whose payment records omit the org block entirely

HOSPITAL_RX = re.compile(
    r"ΝΟΣΟΚΟΜΕΙΟ|ΝΟΣΟΚΟΜΕΙΩΝ|ΝΟΣΗΛΕΥΤΙΚΟ ΙΔΡΥΜΑ|ΑΝΤΙΚΑΡΚΙΝΙΚΟ|"
    r"ΜΑΙΕΥΤΗΡΙΟ|ΨΥΧΙΑΤΡΕΙΟ|ΣΑΝΑΤΟΡΙΟ|ΘΕΡΑΠΕΥΤΗΡΙΟ|"
    # Abbreviated forms. ΓΝ Λαμίας publishes as "Γ.Ν. ΛΑΜΙΑΣ" — no full word
    # ΝΟΣΟΚΟΜΕΙΟ anywhere — and was invisible to THREE national scans because
    # of it. Match Γ.Ν. / ΓΝ / Π.Γ.Ν. / ΠΓΝ / Ψ.Ν. as standalone tokens.
    r"(?:^|[\s(«\"])(?:Π\.?\s?Γ\.?\s?Ν|Γ\.?\s?Ν|Ψ\.?\s?Ν)\.?(?:[\s.)»\"]|$)", re.I)
EXCLUDE_RX = re.compile(r"ΥΓΕΙΟΝΟΜΙΚΗ ΠΕΡΙΦΕΡΕΙΑ|^ΥΠΕ\b|ΕΚΑΠΥ|ΕΟΠΥΥ", re.I)


def fetch(params, retries=4):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hospital-registry/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read().decode()
            if raw.strip():
                return json.loads(raw)
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def org_info(uid):
    try:
        req = urllib.request.Request(ORG.format(uid), headers={"User-Agent": "hospital-registry/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def digits(s):
    return "".join(c for c in str(s) if c.isdigit()).lstrip("0")


def discover(days, page_size=200, sleep=0.3):
    """Page national Β.2.2 traffic, collect hospital orgs.

    WINDOW SIZE MATTERS: search backends commonly cap deep paging at ~10,000
    results (page*size). National Β.2.2 volume is ~5-6k/day, so even 3-day
    windows overflow (measured live: cap hit at page 49). ONE-day windows stay
    under it. If a single day ever caps, that day's tail is lost — the warning
    fires and regular publishers still surface on other days.

    Also scans Β.2.1: hospitals routing payments mainly through ΧΕ records
    (as Rhodes partly does) would otherwise be invisible to discovery.
    """
    end = date.today()
    start = end - timedelta(days=days)
    found = {}
    NAMELESS_OIDS.clear()
    scan_types = [PAYMENT_TYPE, ANON_TYPE]
    cur = start
    while cur < end:
      nxt = min(cur + timedelta(days=1), end)
      for stype in scan_types:
        page = 0
        while True:
            d = fetch({"type": stype, "from_issue_date": cur.isoformat(),
                       "to_issue_date": nxt.isoformat(), "size": page_size, "page": page})
            if not d or not d.get("decisions"):
                break
            for dec in d["decisions"]:
                oid = dec.get("organizationId")
                if not oid:
                    continue
                org = ((dec.get("extraFieldValues") or {}).get("org")) or {}
                nm = (org.get("name") or "").strip()
                if nm:
                    if HOSPITAL_RX.search(nm) and not EXCLUDE_RX.search(nm):
                        found.setdefault(oid, {"uid": oid, "name": nm,
                                               "afm": org.get("afm") or ""})
                else:
                    # Records with NO org block at all — ΓΝ Λαμίας posts ~50
                    # payments/day yet was invisible to two national scans for
                    # exactly this reason. Collect the oid; resolve its name
                    # against the org registry after the scan.
                    NAMELESS_OIDS.add(oid)
            print(f"  [{cur}..{nxt}] page {page}: {len(found)} hospitals so far", file=sys.stderr)
            if (page + 1) * page_size >= 10_000:
                print(f"  !! hit ~10k deep-paging cap in window [{cur}..{nxt}] — "
                      f"records beyond this are INVISIBLE; shrink the window",
                      file=sys.stderr)
                break
            if len(d["decisions"]) < page_size:
                break
            page += 1
            time.sleep(sleep)
      cur = nxt
      time.sleep(sleep)

    # Resolve org-block-less publishers against the registry. This is where
    # Λαμία-style hospitals surface. Also note WHICH hospitals publish without
    # an org block — that is itself a data-quality observation worth keeping.
    if NAMELESS_OIDS:
        unresolved = [o for o in NAMELESS_OIDS if o not in found]
        print(f"  resolving {len(unresolved)} org-block-less publishers via registry…",
              file=sys.stderr)
        for oid in unresolved:
            info = org_info(oid)
            time.sleep(0.15)
            if not info:
                continue
            label = (info.get("label") or "").strip()
            if label and HOSPITAL_RX.search(label) and not EXCLUDE_RX.search(label):
                found[oid] = {"uid": oid, "name": label,
                              "afm": info.get("vatNumber") or "",
                              "no_org_block": "yes"}
                print(f"    + {label[:60]}  (publishes WITHOUT org block)",
                      file=sys.stderr)
    return found


# No single hospital payment plausibly exceeds this (largest PDF-verified genuine
# payment in this project: ~€1.0M SIEMENS equipment; Lamia's max: €2.18M MSD).
# Anything above is quarantined with its ADA for verification, NOT summed —
# the first national run ranked Τρίπολη #1 with €129 TRILLION because three
# hospitals carry absurd-magnitude records (error class #3) and the ranker
# naively added them.

CURRENCY_RX = re.compile(r"^\d{1,3}(?:\.\d{3})*,\d{2}$")

def swapped_amount(kae):
    """Field-swap detector: when amount holds the KAE code, the TRUE amount often
    survives currency-formatted in the kae field (proven live: ADA 6ΑΙΦ46907Ρ-ΒΒ5,
    amount=2.42e13, kae="6.261,99" -> real payment EUR 6,261.99)."""
    k = str(kae or "").strip()
    if CURRENCY_RX.match(k):
        return float(k.replace(".", "").replace(",", "."))
    return None

SANITY_CAP = 5_000_000
SUSPECTS = []   # (uid, ada, amount, supplier_afm, dtype)


def value_scan(uid, months, dtype, page_size=200, sleep=0.25):
    """Sum verified payment value for one org over the last `months`."""
    end = date.today()
    start = end - timedelta(days=int(months * 30.44))
    total = 0.0
    anon = 0.0
    n = 0
    suspect_v = 0.0
    org_afm = None
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=150), end)
        page = 0
        while True:
            d = fetch({"org": uid, "type": dtype, "from_issue_date": cur.isoformat(),
                       "to_issue_date": nxt.isoformat(), "size": page_size, "page": page})
            if not d or not d.get("decisions"):
                break
            for dec in d["decisions"]:
                efv = dec.get("extraFieldValues") or {}
                if org_afm is None:
                    org_afm = ((efv.get("org") or {}).get("afm")) or ""
                for sp in (efv.get("sponsor") or []):
                    nb = sp.get("sponsorAFMName") or {}
                    afm = (nb.get("afm") or "").strip()
                    amt = (sp.get("expenseAmount") or {}).get("amount")
                    try:
                        amt = float(amt)
                    except (TypeError, ValueError):
                        continue
                    if amt <= 0:
                        continue
                    if amt >= SANITY_CAP:             # error class #3: absurd magnitude
                        rec = swapped_amount(sp.get("kae"))
                        SUSPECTS.append((uid, dec.get("ada"), amt, afm, dtype,
                                         rec if rec is not None else ""))
                        suspect_v += amt
                        if rec is not None:           # swap proven: count TRUE value
                            total += rec
                            n += 1
                        continue
                    if not afm:
                        anon += amt
                        continue
                    if org_afm and digits(afm) == digits(org_afm):
                        continue                      # self-referential payroll
                    if amt == int(amt) and digits(int(amt)) == digits(afm):
                        continue                      # AFM-in-amount error
                    total += amt
                    n += 1
            if len(d["decisions"]) < page_size:
                break
            page += 1
            time.sleep(sleep)
        cur = nxt
        time.sleep(sleep)
    return total, anon, n, suspect_v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover-days", type=int, default=30)
    ap.add_argument("--rank-months", type=int, default=12)
    ap.add_argument("--outdir", default="data/_registry")
    ap.add_argument("--skip-discovery", action="store_true",
                    help="reuse hospitals_discovered.csv")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    disc_path = os.path.join(a.outdir, "hospitals_discovered.csv")

    if a.skip_discovery and os.path.exists(disc_path):
        hosp = {r["uid"]: r for r in csv.DictReader(open(disc_path))}
        print(f"reusing {len(hosp)} discovered hospitals", file=sys.stderr)
    else:
        print(f"PHASE 1: discovering hospitals from {a.discover_days} days of national payments…",
              file=sys.stderr)
        hosp = discover(a.discover_days)
        print(f"  verifying {len(hosp)} orgs against the registry…", file=sys.stderr)
        for uid, h in list(hosp.items()):
            info = org_info(uid)
            if info:
                h["label"] = info.get("label") or h["name"]
                h["status"] = info.get("status") or ""
                h["vat"] = info.get("vatNumber") or h.get("afm", "")
                h["supervisor"] = info.get("supervisorLabel") or ""
            time.sleep(0.15)
        with open(disc_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["uid", "name", "label", "afm", "vat",
                                              "status", "supervisor", "no_org_block"], extrasaction="ignore")
            w.writeheader()
            for h in hosp.values():
                w.writerow(h)
        print(f"  wrote {disc_path} ({len(hosp)} hospitals)", file=sys.stderr)

    print(f"\nPHASE 2: ranking {len(hosp)} hospitals on last {a.rank_months} months…",
          file=sys.stderr)
    rows = []
    for i, (uid, h) in enumerate(sorted(hosp.items()), 1):
        v22, anon22, n22, s22 = value_scan(uid, a.rank_months, PAYMENT_TYPE)
        v21, anon21, n21, s21 = value_scan(uid, a.rank_months, ANON_TYPE)
        named = v22 + v21
        anon = anon22 + anon21
        allv = named + anon
        suspect = s22 + s21
        rows.append({"uid": uid, "label": h.get("label") or h.get("name"),
                     "vat": h.get("vat", ""),
                     "named_value": round(named, 2), "anon_value": round(anon, 2),
                     "all_value": round(allv, 2),
                     "suspect_value": round(suspect, 2),
                     "b21_share_pct": round(v21 / named * 100, 1) if named else 0,
                     "anon_share_pct": round(anon / allv * 100, 1) if allv else 0,
                     "payments": n22 + n21})
        flag = f"  !! SUSPECT {suspect:,.0f}" if suspect else ""
        print(f"  {i}/{len(hosp)} {h.get('label','')[:44]:<46} "
              f"{named:>14,.0f}  (anon {anon:>12,.0f}){flag}", file=sys.stderr)

    rows.sort(key=lambda r: -r["all_value"])
    for rank, r in enumerate(rows, 1):
        r["rank"] = rank
    out = os.path.join(a.outdir, "hospitals_ranked.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "uid", "label", "vat", "all_value",
                                          "named_value", "anon_value", "suspect_value",
                                          "b21_share_pct", "anon_share_pct", "payments"])
        w.writeheader()
        w.writerows(rows)
    if SUSPECTS:
        sp = os.path.join(a.outdir, "suspect_payments.csv")
        with open(sp, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["uid", "ada", "amount", "supplier_afm", "type", "recovered_true_amount"])
            w.writerows(SUSPECTS)
        print(f"\n!! {len(SUSPECTS)} payments >= {SANITY_CAP:,.0f} EUR quarantined "
              f"(excluded from ranking) -> {sp}")
        print("   Verify each at https://diavgeia.gov.gr/doc/{ADA} before any use.")
    print(f"\nwrote {out}")
    print(f"\n{'#':<4}{'hospital':<48}{'all value €':>16}{'anon%':>7}{'suspect €':>14}")
    for r in rows[:25]:
        print(f"{r['rank']:<4}{r['label'][:46]:<48}{r['all_value']:>16,.0f}"
              f"{r['anon_share_pct']:>7.1f}{r['suspect_value']:>14,.0f}")


if __name__ == "__main__":
    main()
