#!/usr/bin/env python3
"""Fetch Δ.2.2 award decisions (item-level: subject + awardAmount + supplier) for many
hospitals, for cross-hospital unit-price comparison.

Usage: python3 scripts/fetch_awards_multi.py [months_back] [uid uid ...]
Defaults: 24 months, top-15 hospitals by 5yr value from docs/hospitals.json.
Output: data/_registry/awards_national.csv (append-safe: skips orgs already present).
"""
import csv, datetime as dt, json, os, sys, time, urllib.parse, urllib.request

MONTHS = int(sys.argv[1]) if len(sys.argv) > 1 else 24
if len(sys.argv) > 2:
    UIDS = sys.argv[2:]
else:
    hosp = json.load(open('docs/hospitals.json'))
    UIDS = [h['uid'] for h in sorted(hosp, key=lambda h: -h['total5'])[:15]]

OUT = 'data/_registry/awards_national.csv'
UA = {"User-Agent": "research/1.0"}

def fetch(params):
    url = "https://diavgeia.gov.gr/opendata/search.json?" + urllib.parse.urlencode(params)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"    retry {a+1}: {e}"); time.sleep(5 * (a + 1))
    return None

done = set()
if os.path.exists(OUT):
    done = {r['org'] for r in csv.DictReader(open(OUT))}
    f = open(OUT, 'a', newline='')
    w = csv.writer(f)
else:
    f = open(OUT, 'w', newline='')
    w = csv.writer(f)
    w.writerow(['org', 'ada', 'issue_date', 'subject', 'award_amount', 'supplier_afm', 'supplier_name'])

end = dt.date.today(); start = end - dt.timedelta(days=MONTHS * 30)
for org in UIDS:
    if org in done:
        print(f"{org}: already fetched, skipping"); continue
    n = 0; cur = start
    while cur < end:
        nxt = min(cur + dt.timedelta(days=150), end)
        page = 0
        while True:
            j = fetch({"org": org, "type": "Δ.2.2", "from_issue_date": cur.isoformat(),
                       "to_issue_date": nxt.isoformat(), "size": 500, "page": page})
            if not j: break
            decs = j.get("decisions", [])
            if not decs: break
            for d in decs:
                ev = d.get("extraFieldValues") or {}
                aa = (ev.get("awardAmount") or {})
                amt = aa.get("amount") if isinstance(aa, dict) else None
                pers = ev.get("person") or []
                afm = pers[0].get("afm", "") if pers else ""
                nm = pers[0].get("name", "") if pers else ""
                ts = d.get("issueDate", 0)
                w.writerow([org, d.get("ada", ""),
                            dt.date.fromtimestamp(ts / 1000).isoformat() if ts else "",
                            (d.get("subject") or "").replace("\n", " ")[:200],
                            amt if amt is not None else "", afm, nm[:60]])
                n += 1
            if len(decs) < 500: break
            page += 1
        cur = nxt; time.sleep(0.4)
    f.flush()
    print(f"{org}: {n} awards")
f.close()
print(f"\ndone -> {OUT}")
