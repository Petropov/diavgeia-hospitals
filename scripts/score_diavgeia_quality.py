#!/usr/bin/env python3
"""
Diavgeia Data Quality Index (DDQI) — stack-rank organisations by how well they
populate the transparency portal's machine-readable payment fields.

Scores what an org WRITES, not what it SPENDS. Every metric was validated on
ΓΝ Ρόδου (poor) vs ΓΝ Λαμίας (clean), where each failure mode was confirmed
against source PDFs first. See Fraud_Risk_Assessment.md / Rhodes_5Year_Insights.md.

THE INDEX (0-100, higher = better data)
---------------------------------------
  35  Payee completion      share of Β.2.1+Β.2.2 payment VALUE carrying a real
                            sponsor ΑΦΜ (self-referential = named for this purpose;
                            payroll legitimately lacks a supplier)
  25  Budget-code (KAE)     share of Β.2.2 value with a non-empty kae field
  20  Amount integrity      starts at 20, minus:
                              8 per ΑΦΜ-in-amount record (amount == supplier tax id)
                              2 per whole-euro amount >= €200k (x100-error signature;
                                unverified proxy — PDF check can clear individual hits)
                              4 if any year's mean/median ratio > 15 (contamination)
  10  Name consistency      share of ΑΦΜs with a single name variant, weighted by
                            payment count (fragmentation defeats name-based audit)
  10  No recency regression latest full year's KAE completion vs the org's own
                            prior 3-year average (catches e.g. Rhodes' 2026 collapse
                            from 86% coded to 1%)

Usage:
  python3 scripts/score_diavgeia_quality.py --orgs 99221940 99221923 99221913 --start 2022-01-01
  python3 scripts/score_diavgeia_quality.py --local data/99221940  # score an existing pull

Network runs fetch Β.2.2 and Β.2.1 via from_issue_date windows (~2-4 min/org).
Only stdlib. Windows must stay <6 months (server clamps longer spans silently).
"""

import argparse, collections, csv, json, statistics, sys, time
import urllib.parse, urllib.request
from datetime import date, timedelta

API="https://diavgeia.gov.gr/opendata/search.json"

def fetch(params, retries=4):
    url=API+"?"+urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"ddqi/1.0"})
            with urllib.request.urlopen(req,timeout=60) as r:
                raw=r.read().decode()
            if raw.strip(): return json.loads(raw)
        except Exception:
            time.sleep(1.5*(i+1))
    return None

def pull(org,start,end,dtype):
    out=[]
    cur=start
    while cur<end:
        nxt=min(cur+timedelta(days=150),end)
        page=0
        while True:
            d=fetch({"org":org,"type":dtype,"from_issue_date":cur.isoformat(),
                     "to_issue_date":nxt.isoformat(),"size":200,"page":page})
            if not d or not d.get("decisions"): break
            out+=d["decisions"]
            if len(d["decisions"])<200: break
            page+=1; time.sleep(0.3)
        cur=nxt; time.sleep(0.3)
    return out

def digits(s): return "".join(c for c in str(s) if c.isdigit()).lstrip("0")

def rows_from_api(decisions):
    """Flatten API decisions to the same shape as our CSVs."""
    rows=[]
    for dec in decisions:
        efv=dec.get("extraFieldValues") or {}
        org_afm=((efv.get("org") or {}).get("afm")) or ""
        iso=""
        if dec.get("issueDate"):
            from datetime import datetime
            iso=datetime.utcfromtimestamp(dec["issueDate"]/1000).date().isoformat()
        for sp in (efv.get("sponsor") or [{}]):
            nb=sp.get("sponsorAFMName") or {}
            amt=(sp.get("expenseAmount") or {}).get("amount")
            try: amt=float(amt)
            except (TypeError,ValueError): amt=0.0
            rows.append({"ada":dec.get("ada"),"issue_date":iso,
                         "supplier_afm":(nb.get("afm") or "").strip(),
                         "supplier_name":(nb.get("name") or "").strip(),
                         "amount_eur":amt,"kae":sp.get("kae") or "",
                         "org_afm":org_afm,"type":dec.get("decisionTypeId")})
    return rows

def score(rows):
    """rows: dicts with amount_eur(float), supplier_afm, supplier_name, kae, issue_date, org_afm, type"""
    val=lambda r: r["amount_eur"] if r["amount_eur"]>0 else 0.0
    total=sum(val(r) for r in rows) or 1.0

    # 1. payee completion (35)
    named=sum(val(r) for r in rows if r["supplier_afm"])
    s_payee=35*named/total

    # 2. KAE completion on Β.2.2 (25)
    b22=[r for r in rows if r.get("type") in (None,"Β.2.2")]
    b22v=sum(val(r) for r in b22) or 1.0
    coded=sum(val(r) for r in b22 if str(r["kae"]).strip())
    kae_share=coded/b22v
    s_kae=25*kae_share

    # 3. amount integrity (20)
    s_amt=20.0; flags=[]
    afm_hits=[r for r in rows if r["amount_eur"]>=1000 and
              r["amount_eur"]==int(r["amount_eur"]) and r["supplier_afm"] and
              digits(int(r["amount_eur"]))==digits(r["supplier_afm"])]
    s_amt-=8*len(afm_hits)
    big_round=[r for r in rows if r["amount_eur"]>=200_000 and r["amount_eur"]==int(r["amount_eur"])]
    s_amt-=2*len(big_round)
    yr=collections.defaultdict(list)
    for r in rows:
        if val(r)>0: yr[r["issue_date"][:4]].append(val(r))
    bad_ratio=any(len(v)>30 and statistics.mean(v)/statistics.median(v)>15 for v in yr.values())
    if bad_ratio: s_amt-=4
    s_amt=max(0.0,s_amt)
    if afm_hits: flags.append(f"{len(afm_hits)} AFM-in-amount")
    if big_round: flags.append(f"{len(big_round)} whole-euro>=200k")
    if bad_ratio: flags.append("mean/median>15")

    # 4. name consistency (10)
    names=collections.defaultdict(set); cnt=collections.Counter()
    for r in rows:
        if r["supplier_afm"]:
            names[r["supplier_afm"]].add(r["supplier_name"]); cnt[r["supplier_afm"]]+=1
    if cnt:
        good=sum(c for a,c in cnt.items() if len(names[a])==1)
        s_name=10*good/sum(cnt.values())
    else: s_name=0.0

    # 5. recency regression (10)
    years=sorted(y for y in yr if y.isdigit())
    s_rec=10.0; rec_note=""
    if len(years)>=3:
        def kshare(y):
            v=[r for r in b22 if r["issue_date"][:4]==y]; tv=sum(val(r) for r in v) or 1
            return sum(val(r) for r in v if str(r["kae"]).strip())/tv
        latest=years[-1]; prior=years[-4:-1] if len(years)>=4 else years[:-1]
        p=statistics.mean(kshare(y) for y in prior); l=kshare(latest)
        if p>0.3 and l<p*0.5:
            s_rec=max(0.0,10*l/p); rec_note=f"KAE {p*100:.0f}%->{l*100:.0f}% in {latest}"
    parts=dict(payee=s_payee,kae=s_kae,amount=s_amt,names=s_name,recency=s_rec)
    return sum(parts.values()),parts,flags,rec_note,total,len(rows)

def load_local(d):
    rows=[]
    import os
    for sub,typ in [("payments","Β.2.2"),("payments_B21","Β.2.1")]:
        p=os.path.join(d,sub,"payments.csv")
        pc=os.path.join(d,sub,"payments_corrected.csv")
        f=pc if os.path.exists(pc) else p
        if not os.path.exists(f): continue
        for r in csv.DictReader(open(f)):
            rows.append({"ada":r["ada"],"issue_date":r["issue_date"],
                         "supplier_afm":r["supplier_afm"],"supplier_name":r["supplier_name"],
                         "amount_eur":float(r["amount_eur"] or 0),"kae":r.get("kae",""),
                         "org_afm":"","type":typ})
        x=os.path.join(d,sub,"excluded.csv")
        if os.path.exists(x):
            for r in csv.DictReader(open(x)):
                if 'anonymous' in (r.get('reason') or ''):
                    try: a=float(r.get('amount_eur') or 0)
                    except ValueError: a=0
                    rows.append({"ada":r["ada"],"issue_date":r["issue_date"],
                                 "supplier_afm":"","supplier_name":"",
                                 "amount_eur":a,"kae":"","org_afm":"","type":typ})
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--orgs",nargs="*",default=[])
    ap.add_argument("--local",nargs="*",default=[])
    ap.add_argument("--start",default="2022-01-01")
    ap.add_argument("--end",default=date.today().isoformat())
    a=ap.parse_args()
    results=[]
    for d in a.local:
        rows=load_local(d)
        if rows: results.append((d,)+score(rows))
    for org in a.orgs:
        print(f"pulling {org} ...",file=sys.stderr)
        decs=pull(org,date.fromisoformat(a.start),date.fromisoformat(a.end),"Β.2.2")
        decs+=pull(org,date.fromisoformat(a.start),date.fromisoformat(a.end),"Β.2.1")
        rows=rows_from_api(decs)
        if rows: results.append((org,)+score(rows))
    results.sort(key=lambda t:-t[1])
    print(f"\n{'org':<28}{'DDQI':>6}  {'payee':>6}{'kae':>6}{'amt':>5}{'name':>6}{'rec':>5}"
          f"  {'value €':>14}{'rows':>7}  flags")
    print("-"*118)
    for org,tot,parts,flags,rec,val,n in results:
        print(f"{str(org)[:28]:<28}{tot:>6.1f}  {parts['payee']:>6.1f}{parts['kae']:>6.1f}"
              f"{parts['amount']:>5.1f}{parts['names']:>6.1f}{parts['recency']:>5.1f}"
              f"  {val:>14,.0f}{n:>7}  {'; '.join(flags)}{('; '+rec) if rec else ''}")

if __name__=="__main__":
    main()
