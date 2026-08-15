#!/usr/bin/env python3
"""
Batch 5-year extraction for many hospitals. Resumable, rate-limited, logged.

Wraps fetch_payments_history.py over a ranked hospital list, pulling BOTH
Β.2.2 (named payments) and Β.2.1 (the anonymous/ΧΕ layer) for each org, then
scoring data quality via score_diavgeia_quality.py.

Designed to be interrupted. Already-completed orgs are skipped on re-run
(detected by a non-empty payments.csv), so a dropped connection costs one org,
not the batch.

USAGE
  python3 scripts/batch_pull_hospitals.py --from-ranking data/_registry/hospitals_ranked.csv --top 50
  python3 scripts/batch_pull_hospitals.py --orgs 99221940 99221923 --start 2021-08-01
  python3 scripts/batch_pull_hospitals.py --from-ranking ... --top 50 --resume   # skip done

RUNTIME: roughly 3-6 min per hospital for both types over 5 years, so ~4h for
50 hospitals. Run it in a terminal you can leave open; progress is appended to
data/_registry/batch_log.csv after every org.
"""

import argparse, csv, os, subprocess, sys, time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FETCH = os.path.join(HERE, "fetch_payments_history.py")


def already_done(outdir):
    p = os.path.join(outdir, "payments.csv")
    return os.path.exists(p) and os.path.getsize(p) > 200


def run(org, dtype, outdir, start, end):
    cmd = [sys.executable, FETCH, "--org", org, "--start", start, "--end", end,
           "--type", dtype, "--outdir", outdir]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = (r.stdout or "").strip().splitlines()
    summary = next((l for l in reversed(tail) if "VERIFIED TOTAL" in l), "")
    return r.returncode, summary, time.time() - t0, (r.stderr or "")[-400:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-ranking")
    ap.add_argument("--orgs", nargs="*", default=[])
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--start", default="2021-08-01")
    ap.add_argument("--end", default=datetime.today().date().isoformat())
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    targets = []
    if a.from_ranking:
        with open(a.from_ranking, encoding="utf-8") as f:
            for r in list(csv.DictReader(f))[:a.top]:
                targets.append((r["uid"], r.get("label", "")))
    targets += [(o, "") for o in a.orgs]
    if not targets:
        sys.exit("no targets: pass --from-ranking or --orgs")

    os.makedirs("data/_registry", exist_ok=True)
    logp = "data/_registry/batch_log.csv"
    new = not os.path.exists(logp)
    log = open(logp, "a", newline="", encoding="utf-8")
    lw = csv.writer(log)
    if new:
        lw.writerow(["ts", "org", "label", "type", "rc", "secs", "summary", "stderr_tail"])

    print(f"batch: {len(targets)} hospitals x 2 record types, {a.start} -> {a.end}\n")
    for i, (org, label) in enumerate(targets, 1):
        for dtype, sub in [("Β.2.2", "payments"), ("Β.2.1", "payments_B21")]:
            outdir = f"data/{org}/{sub}"
            if not a.force and a.resume and already_done(outdir):
                print(f"[{i}/{len(targets)}] {org} {dtype:<6} SKIP (done)")
                continue
            print(f"[{i}/{len(targets)}] {org} {dtype:<6} {label[:40]:<42} pulling…",
                  end="", flush=True)
            rc, summary, secs, err = run(org, dtype, outdir, a.start, a.end)
            print(f" {secs:>5.0f}s  {'OK' if rc == 0 else 'FAIL'}  {summary}")
            lw.writerow([datetime.now().isoformat(timespec="seconds"), org, label,
                         dtype, rc, round(secs), summary, err.replace("\n", " ")])
            log.flush()
    log.close()
    print(f"\ndone. log: {logp}")
    print("next:  python3 scripts/score_diavgeia_quality.py --local " +
          " ".join(f"data/{o}" for o, _ in targets[:8]) + " ...")


if __name__ == "__main__":
    main()
