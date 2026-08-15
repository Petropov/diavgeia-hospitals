#!/usr/bin/env python3
"""Download source PDFs for any worklist CSV that has 'ada' (+optional 'org') columns.
Usage:
  python3 scripts/download_docs.py data/_registry/verify_quarantine.csv data/_registry/quarantine_pdfs
  python3 scripts/download_docs.py data/_registry/audit_sample.csv     data/_registry/audit_pdfs
Resumable: existing non-empty files are skipped.
"""
import csv, os, sys, time, urllib.parse, urllib.request

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
rows = list(csv.DictReader(open(src)))
ok = fail = skip = 0
for i, r in enumerate(rows, 1):
    ada = r["ada"]
    tag = r.get("org", "")
    dest = os.path.join(outdir, f"{tag}__{ada}.pdf" if tag else f"{ada}.pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        skip += 1
        continue
    try:
        req = urllib.request.Request(
            "https://diavgeia.gov.gr/doc/" + urllib.parse.quote(ada),
            headers={"User-Agent": "research/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        ok += 1
        print(f"  {i}/{len(rows)} ok {os.path.getsize(dest):>8,}b  {ada}")
    except Exception as e:
        fail += 1
        print(f"  {i}/{len(rows)} FAIL {ada}: {e}")
    time.sleep(0.3)
print(f"\ndone: {ok} downloaded, {skip} skipped, {fail} failed -> {outdir}/")
