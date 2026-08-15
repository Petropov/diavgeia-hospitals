#!/usr/bin/env python3
"""Find απολογισμός / budget-execution / financial-statement decisions for an org
by subject keywords (they hide under generic decision types).

Usage: python3 scripts/find_reconciliation_docs.py [org] [years]
Defaults: org 99221940 (Rhodes), 3 years back.
Output: data/{org}/reconciliation_worklist.csv
"""
import csv, datetime as dt, json, sys, time, urllib.parse, urllib.request

ORG = sys.argv[1] if len(sys.argv) > 1 else "99221940"
YEARS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
TOKENS = ["ΑΠΟΛΟΓΙΣΜ", "ΕΚΤΕΛΕΣΗ ΠΡΟΫΠΟΛΟΓΙΣΜΟΥ", "ΕΚΤΕΛΕΣΗΣ ΠΡΟΫΠΟΛΟΓΙΣΜΟΥ",
          "ΕΚΤΕΛΕΣΗ ΠΡΟΥΠΟΛΟΓΙΣΜΟΥ", "ΕΚΤΕΛΕΣΗΣ ΠΡΟΥΠΟΛΟΓΙΣΜΟΥ",
          "ΟΙΚΟΝΟΜΙΚΕΣ ΚΑΤΑΣΤΑΣΕΙΣ", "ΙΣΟΛΟΓΙΣΜ"]
UA = {"User-Agent": "research/1.0"}

def fetch(params):
    url = "https://diavgeia.gov.gr/opendata/search.json?" + urllib.parse.urlencode(params)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"    retry {a+1}: {e}"); time.sleep(5 * (a + 1))
    raise SystemExit("giving up")

hits, seen = [], set()
end = dt.date.today(); cur = end - dt.timedelta(days=YEARS * 365)
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
            subj = (d.get("subject") or "").upper()
            if ada in seen: continue
            seen.add(ada)
            if any(t in subj for t in TOKENS):
                ts = d.get("issueDate", 0)
                hits.append({"org": ORG, "ada": ada, "type": d.get("decisionTypeId", ""),
                             "issue_date": dt.date.fromtimestamp(ts / 1000).isoformat() if ts else "",
                             "subject": (d.get("subject") or "")[:160],
                             "doc_url": f"https://diavgeia.gov.gr/doc/{ada}"})
        if len(decs) < 500: break
        page += 1
    print(f"  {cur} -> {nxt}: {len(hits)} hits")
    cur = nxt; time.sleep(0.5)

out = f"data/{ORG}/reconciliation_worklist.csv"
if hits:
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hits[0].keys()))
        w.writeheader(); w.writerows(hits)
print(f"\ndone: {len(hits)} -> {out}")
print(f"next: python3 scripts/download_docs.py {out} data/{ORG}/reconciliation_pdfs")
