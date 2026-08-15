#!/usr/bin/env python3
"""Pull ALL Δ-category (procurement/award) decisions for an org over 5 years and
flag those naming the target suppliers (by ΑΦΜ or name token, anywhere in the JSON).

Resolves Fraud_Risk_Assessment #4/#5: one tendered contract per supplier -> close the
flag; serial direct awards -> escalate.

Usage (on the Mac, network required):
  python3 scripts/fetch_awards.py                # defaults: Rhodes + the 3 flagged suppliers
Then download the flagged award PDFs:
  python3 scripts/download_docs.py data/99221940/awards_worklist.csv data/99221940/award_pdfs
"""
import csv, datetime as dt, gzip, json, os, re, time, urllib.parse, urllib.request

ORG = "99221940"
YEARS = 5
OUT = f"data/{ORG}"
# ΑΦΜ -> label (MYSERVICES intentionally under 3 ΑΦΜs — fragmentation is itself a finding)
TARGETS = {
    "997563888": "ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣ. ΡΟΔΟΥ",
    "094180805": "ΑΦΟΙ ΚΟΜΠΑΤΣΙΑΡΗ",
    "997516863": "MYSERVICES (SECURITY AND FACILITY)",
    "996589476": "MYSERVICES (ΛΕΙΤΟΥΡΓ. ΥΠΟΣΤ.)",
    "801114586": "MYSERVICES (HUMAN RESOURCES)",
}
NAME_TOKENS = ["ΚΟΜΠΑΤΣΙΑΡ", "MYSERVICES", "MY SERVICES", "ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣ"]
# Most Δ.2.2 records have person:[] (anonymous in JSON) — catch the flagged suppliers'
# service categories by subject so their awards land in the worklist anyway.
CATEGORY_TOKENS = ["ΦΥΛΑΞΗ", "ΑΣΦΑΛΕΙΑ", "SECURITY", "ΣΙΤΙΣΗ", "ΕΣΤΙΑΣ", "ΚΑΘΑΡΙΟΤΗΤ",
                   "ΚΑΘΑΡΙΣΜ", "ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ", "ΑΝΘΡΩΠΙΝΟ ΔΥΝΑΜΙΚ"]

BASE = "https://diavgeia.gov.gr/opendata/search.json"
UA = {"User-Agent": "research/1.0"}

def fetch(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"    retry {attempt+1}: {e}"); time.sleep(5 * (attempt + 1))
    raise SystemExit("giving up")

def main():
    os.makedirs(OUT, exist_ok=True)
    end = dt.date.today(); start = end - dt.timedelta(days=YEARS * 365)
    awards, hits, seen = [], [], set()
    cur = start
    while cur < end:
        nxt = min(cur + dt.timedelta(days=150), end)
        page = 0
        while True:
            j = fetch({"org": ORG, "from_issue_date": cur.isoformat(),
                       "to_issue_date": nxt.isoformat(), "size": 500, "page": page})
            decs = j.get("decisions", [])
            if not decs: break
            for d in decs:
                ada = d.get("ada", "")
                tid = str(d.get("decisionTypeId", ""))
                if ada in seen or not tid.startswith("Δ"): continue
                seen.add(ada)
                blob = json.dumps(d, ensure_ascii=False)
                row = {"ada": ada, "org": ORG, "type": tid,
                       "issue_date": str(d.get("issueDate", ""))[:10],
                       "subject": (d.get("subject") or "")[:160],
                       "award_amount": (d.get("extraFieldValues") or {}).get("awardAmount", ""),
                       "doc_url": f"https://diavgeia.gov.gr/doc/{ada}"}
                awards.append(row)
                up = blob.upper()
                m_afm = [a for a in TARGETS if a in blob]
                m_tok = [t for t in NAME_TOKENS if t in up]
                m_cat = [t for t in CATEGORY_TOKENS if t in (row["subject"] or "").upper()]
                if m_afm or m_tok or m_cat:
                    hits.append({**row,
                                 "match_kind": "afm" if m_afm else ("name" if m_tok else "category"),
                                 "matched_afm": ";".join(m_afm),
                                 "matched_supplier": ";".join(TARGETS[a] for a in m_afm)
                                                     or ";".join(m_tok) or ";".join(m_cat)})
            if len(decs) < 500: break
            page += 1
            if page * 500 >= 9500: print("  WARNING: near 10k cap — shrink window"); break
        print(f"  {cur} -> {nxt}: {len(awards)} Δ-decisions so far, {len(hits)} target hits")
        cur = nxt
        time.sleep(0.5)

    for name, rows in [("awards_all.csv", awards), ("awards_worklist.csv", hits)]:
        if rows:
            with open(f"{OUT}/{name}", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)
    print(f"\ndone: {len(awards)} Δ-decisions -> {OUT}/awards_all.csv")
    print(f"      {len(hits)} naming target suppliers -> {OUT}/awards_worklist.csv")
    print(f"next: python3 scripts/download_docs.py {OUT}/awards_worklist.csv {OUT}/award_pdfs")

if __name__ == "__main__":
    main()
