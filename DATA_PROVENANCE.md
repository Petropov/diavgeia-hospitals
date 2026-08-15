# Data Provenance — how these figures stay verifiable

Diavgeia is a **live, mutable system**. Records are added, corrected
(`correctedVersionId`), and occasionally withdrawn. Two extractions minutes apart
differed by €5,549. So a number like "€82,042,987" is meaningless unless we can say
**what the server held, on what date, and prove nothing has been edited since — by the
government or by us.**

This document is the answer to "how is this verifiable and re-retrievable?"

---

## The four-level verification chain

| level | artefact | proves | who can check | independent of us? |
|---|---|---|---|---|
| **L1** | **ΑΔΑ** on every row | the record exists and is public | anyone, forever | ✅ fully |
| **L2** | gzipped **raw API responses** | what the server returned *to us*, so our parsing is auditable | anyone with the repo | ⚠️ our copy |
| **L3** | **source PDF** | the legally authoritative amount | anyone | ✅ re-downloadable |
| **L4** | **MANIFEST.json** (SHA-256) | nothing altered post-publication | anyone | ✅ cryptographic |

**L1 is the strongest link and costs nothing.** Every row carries its ΑΔΑ, so any
figure can be checked against the government's own server without trusting this repo
at all:

```
https://diavgeia.gov.gr/opendata/decisions/{ADA}.json   # structured record
https://diavgeia.gov.gr/doc/{ADA}                       # signed PDF
```

That is how the ×100 errors were proven: `ΨΤ6Τ46907Κ-8ΕΘ` says €185,904.21 in words
on the signed warrant, while the API field says €18,590,421.

**L2 was missing until now** — a real gap, and a violation of our own Ground Rule #1
("first artifact of any integration is one saved raw response, not code"). Every CSV
in this repo was processed output; a reader could verify our *arithmetic* but not our
*parsing*. Now fixed:

```bash
python3 scripts/fetch_payments_history.py --org 99221940 --start 2021-08-01 --save-raw
# -> data/99221940/payments/raw/Β.2.2_2021-08-01_2021-12-29_p0.json.gz
```

**Use `--save-raw` for anything that will be published.** It is optional only because
exploratory pulls don't need it.

**L4 pins the totals.** `MANIFEST.json` records SHA-256, row counts *and summed
amounts* per CSV — so the headline figures are bound to the files:

```
129,095,335.04  ( 4796 rows)  data/99221940/payments/payments.csv        (raw)
 82,042,987.28  ( 4796 rows)  data/99221940/payments/payments_corrected.csv
116,329,309.34  (13609 rows)  data/99221923/payments/payments.csv
```

```bash
python3 scripts/make_manifest.py            # build
python3 scripts/make_manifest.py --verify   # detect any change since
```

---

## Where the data lives

### Now — GitHub (primary, working)
**https://github.com/Petropov/diavgeia-hospitals** · currently 27 MB

Good for: CSVs, scripts, reports, manifests, evidence PDFs. Every commit is a
timestamped snapshot; `git diff` between refreshes shows exactly which records the
government added, changed or withdrew.

### At publication — Zenodo (archival, citable)
GitHub repos can be renamed, made private, or deleted; a published paper cannot
depend on that. At Gate 5 of the plan, cut a **Zenodo release** (CERN-backed,
permanent, versioned): gives a **DOI**, an immutable snapshot, and a home for the
bulk raw archive that doesn't belong in git history.

Zenodo takes GitHub releases automatically once linked — practically one click.

### Size projection at 50 hospitals

| component | estimate | where |
|---|---:|---|
| Processed CSVs (Β.2.2 + Β.2.1) | ~160 MB | GitHub |
| Evidence PDFs (national screens + random audit) | ~90 MB | GitHub |
| Raw responses, gzipped | ~160 MB | **Zenodo release** (or Git LFS) |
| **total** | **~400 MB** | |

GitHub's practical soft limit is ~1 GB per repo and a hard 100 MB per file, so this
fits — but raw snapshots are append-only bulk that gains nothing from git's
diffing. Ship them as release assets, keep working data in git.

**If it outgrows this**, the natural split is: git = analysis + evidence; Zenodo =
full raw corpus; both cross-referenced by the manifest.

---

## Re-retrieval: the drift workflow

Because the source mutates, **re-extraction is not a chore — it is an instrument.**

```bash
# 1. baseline (already committed, MANIFEST.json pins it)
# 2. later, re-pull the same window
python3 scripts/fetch_payments_history.py --org 99221940 --start 2021-08-01 --save-raw
# 3. what changed on the government's side?
git diff --stat data/99221940/
python3 scripts/make_manifest.py --verify
```

The diff answers questions no static dataset can:

- **Did the €94M GE Healthcare phantom (`6Χ4Μ46907Κ-8Θ2`) ever get corrected?** If it
  silently changes after we publish, that is itself the story.
- Are the 16 ×100 errors fixed, or still live?
- Did records disappear? Withdrawal of a record we cited would be highly significant.

**Convention:** commit refreshes as `data refresh YYYY-MM-DD`, never amend an earlier
extraction. Each extraction is a historical fact about what the portal said that day.

---

## Quoting rules (bind these to every published figure)

1. **Always attach the extraction date.** "€82.0M (extracted 2026-08-11)". Never bare.
2. **Cite the ΑΔΑ** for any specific record claim — it is the reader's independent path.
3. **State the correction status**: raw / corrected / which records changed and why.
4. **Link `Known_Unknowns.md`** — verification was outlier-targeted, detection is
   asymmetric (overstatement only), and there is still no measured base error rate
   until the random-sample audit at Gate 4.

---

## What this does *not* cover

- **Omission.** Payments never posted to Diavgeia are invisible to every level above.
  Only reconciliation against each hospital's απολογισμός bounds it (Gate 4).
- **Wrong-but-valid data.** A plausible amount attached to the wrong supplier ΑΦΜ
  passes L1–L4 intact. Provenance proves faithful transcription, not truth.
- **Our interpretation.** The chain guarantees the *data*; the reports' judgements
  (structuring indicators, risk ratings) remain arguments, and are labelled as such.
