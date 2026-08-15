#!/usr/bin/env python3
"""
Build a provenance manifest so every published figure is independently verifiable.

THE PROBLEM
-----------
Diavgeia is a LIVE system. Records are added, corrected (`correctedVersionId`) and
occasionally withdrawn. Two runs minutes apart differed by €5,549. So "we got €82M"
is meaningless without stating *what was on the server, when, and proof it hasn't
been edited since* — by them or by us.

THE FOUR-LEVEL VERIFICATION CHAIN
---------------------------------
L1  ADA          every row carries its ΑΔΑ -> anyone can re-fetch the record from
                 diavgeia.gov.gr/opendata/decisions/{ADA}.json, forever, from the
                 government's own server. Independent of us entirely.
L2  RAW SNAPSHOT gzipped raw API responses -> proves what the server returned to US
                 on the extraction date, so our PARSING can be audited, and so
                 later government edits are detectable by diff.
L3  SOURCE PDF   the signed ΕΝΤΑΛΜΑ ΠΛΗΡΩΜΗΣ behind every specific claim -> the
                 legally authoritative figure (this is how the ×100 errors were proven).
L4  MANIFEST     SHA-256 of every file + record counts + totals -> proves nothing was
                 altered after publication, including by us.

This script builds L4 and indexes L1-L3.

USAGE
  python3 scripts/make_manifest.py                    # whole data/ tree
  python3 scripts/make_manifest.py --path data/99221940
  python3 scripts/make_manifest.py --verify           # re-check against existing manifest
"""

import argparse, csv, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone

SKIP_DIRS = {".git", "__pycache__", ".ipynb_checkpoints"}


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(buf):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


def csv_stats(path):
    """Row count and summed amount_eur, so totals are pinned in the manifest."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f)
            n = 0
            total = 0.0
            has_amt = rd.fieldnames and "amount_eur" in rd.fieldnames
            for r in rd:
                n += 1
                if has_amt:
                    try:
                        total += float(r["amount_eur"] or 0)
                    except ValueError:
                        pass
        return {"rows": n, "sum_amount_eur": round(total, 2) if has_amt else None}
    except Exception:
        return {}


def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for name in sorted(fn):
            if name == "MANIFEST.json":
                continue
            yield os.path.join(dp, name)


def build(path):
    entries = []
    for p in sorted(walk(path)):
        rel = os.path.relpath(p)
        st = os.stat(p)
        e = {"path": rel, "bytes": st.st_size, "sha256": sha256(p)}
        if p.endswith(".csv"):
            e.update(csv_stats(p))
        entries.append(e)
    pdfs = [e for e in entries if e["path"].endswith(".pdf")]
    csvs = [e for e in entries if e["path"].endswith(".csv")]
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(),
        "source": {
            "portal": "https://diavgeia.gov.gr",
            "api": "https://diavgeia.gov.gr/opendata/search.json",
            "record_url_template": "https://diavgeia.gov.gr/opendata/decisions/{ADA}.json",
            "document_url_template": "https://diavgeia.gov.gr/doc/{ADA}",
            "legal_basis": "N.3861/2010 (Programme Diavgeia) — public records",
            "note": ("LIVE system: totals drift between extractions as records are "
                     "added or corrected. Every figure must be quoted with its "
                     "extraction date. Re-fetch any ADA to verify independently.")
        },
        "counts": {"files": len(entries), "csv_files": len(csvs), "pdf_files": len(pdfs),
                   "total_bytes": sum(e["bytes"] for e in entries)},
        "files": entries,
    }


def verify(path, manifest_path):
    man = json.load(open(manifest_path, encoding="utf-8"))
    idx = {e["path"]: e for e in man["files"]}
    ok = changed = missing = added = 0
    for p in sorted(walk(path)):
        rel = os.path.relpath(p)
        if rel not in idx:
            print(f"  ADDED    {rel}")
            added += 1
            continue
        if sha256(p) != idx[rel]["sha256"]:
            print(f"  CHANGED  {rel}")
            changed += 1
        else:
            ok += 1
    seen = {os.path.relpath(p) for p in walk(path)}
    for rel in idx:
        if rel not in seen:
            print(f"  MISSING  {rel}")
            missing += 1
    print(f"\nverified against {manifest_path} (generated {man['generated_utc']})")
    print(f"  unchanged {ok} | changed {changed} | missing {missing} | added {added}")
    return 0 if (changed == 0 and missing == 0) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="data")
    ap.add_argument("--out", default="MANIFEST.json")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.verify:
        sys.exit(verify(a.path, a.out))
    man = build(a.path)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    c = man["counts"]
    print(f"wrote {a.out}")
    print(f"  {c['files']} files ({c['csv_files']} csv, {c['pdf_files']} pdf), "
          f"{c['total_bytes']/1e6:.1f} MB")
    print(f"  git commit: {man['git_commit']}")
    tot = [(e['path'], e.get('sum_amount_eur'), e.get('rows'))
           for e in man['files'] if e.get('sum_amount_eur')]
    if tot:
        print("  pinned totals:")
        for p, s, n in sorted(tot, key=lambda x: -(x[1] or 0))[:8]:
            print(f"    {s:>16,.2f}  ({n:>6} rows)  {p}")


if __name__ == "__main__":
    main()
