# Retrieve / Verify / Store — what's actually optimal

Written in response to justified scepticism about the architecture I proposed. Where I
measured, the numbers are here. Where I couldn't, I say so.

---

## 1. STORE — measured. This was a non-problem and I over-engineered it.

| format | ΓΝ Λαμίας payments (13,609 rows) |
|---|---:|
| CSV | 2.71 MB |
| SQLite | 2.90 MB ← *bigger* |
| SQLite gzipped | 0.69 MB |
| **CSV gzipped** | **0.52 MB** ← winner |

**Plain gzipped CSV beats SQLite and needs no dependency.** Extrapolated to 50
hospitals with both record types: **~30 MB**, not the ~400 MB I projected.

**Therefore:**
- ❌ Drop the Zenodo/Git-LFS split as a *storage* necessity — GitHub handles 30–60 MB
  trivially. (Zenodo still has one real use: a **DOI + immutable snapshot** at
  publication. That's citability, not capacity. Do it once, at Gate 5.)
- ✅ Store CSVs uncompressed in git (they diff well, which is the point) and gzip only
  the raw-response archive.
- ❌ Don't bother with SQLite/Parquet. At this scale it's dependency cost for nothing.
  Revisit only past ~1 GB or if we need cross-hospital SQL joins.

**Verdict: storage is solved and cheap. Stop thinking about it.**

## 2. RETRIEVE — no bulk source exists; the lever is page size and *depth discipline*

Checked, per Ground Rule #2 (endpoints tested, results recorded):

| candidate | result |
|---|---|
| `/opendata/organizations.json`, `/opendata/organizations` | empty |
| `opendata.diavgeia.gov.gr` | same JS app, no dump |
| `data.gov.gr` | catalogue advertises bulk download; **no Diavgeia decisions dataset found** |
| glossAPI HF corpus (3.1 M docs) | OCR text + metadata, ~6-month window, gated. Weaker than the API for our fields |
| `from_issue_date` windowing | ✅ what we use |

**No bulk dump exists.** Per-org paging is the correct method. Two levers remain:

**(a) Page size.** Scripts use 200. A prior project in this repo used **500**
successfully → **2.5× fewer requests** for free. I could not verify 500 vs 1000 from
here: `web_fetch` truncates at ~60 KB, so what I measured was my own transport, not the
server. **Test it once from your side** (`--size 500`, confirm `actualSize` in the
response) and if fine, raise the default.

**(b) Depth discipline — the bigger win.** Do not pull 5 years for everyone. Tier it:

| tier | scope | depth | cost | buys |
|---|---|---|---|---|
| **T1** | ~130 hospitals (all) | **12 months** | ~1 h | **national DDQI ranking** — output A |
| **T2** | top ~20 by value | 5 years | ~1.5 h | trend + benchmark — output B |
| **T3** | flagged outliers only | PDFs | human hours | proof — the integrity findings |

**T1 alone produces the headline national result.** Five-year depth only matters where
we make *trend* claims, which is a handful of hospitals — not 50. This roughly halves
total fetch time *and* front-loads the most publishable output.

*(Your running job is T1-then-T2-at-50. That's fine and not wasted — but if it's slow,
cutting T2 to the top 20 loses almost nothing.)*

## 3. VERIFY — spend the effort where accuracy is actually bought

Verification cost is dominated by **human PDF reading**, not storage or fetching. Rank
by accuracy-per-hour:

| method | cost | what it buys | worth it? |
|---|---|---|---|
| **ΑΔΑ in every row** | free | anyone re-checks any record against the government's server | ✅ **essential** |
| **Automated screens** (ΑΦΜ-in-amount, whole-euro, mean/median) | free, already built | finds candidates | ✅ but **only finds overstatement** |
| **Random-sample audit** (60 records × 5 hospitals) | ~5 human-hours | **the measured error rate** — converts caveats into a number, and is the *only* method that detects understatement | ✅ **highest value remaining** |
| **Raw response archive** (gzipped) | ~3 MB/hospital, free | proves what the server said on our date; makes parsing auditable; detects later government edits | ✅ cheap insurance |
| **Full manifest + pinned totals** | seconds | tamper-evidence, binds headline figures to files | ✅ done |
| **PDF-verifying every outlier nationally** | 200–600 docs | proof for specific claims | ⚠️ only for records we actually cite |
| **PDF-verifying everything** | ~850k docs | completeness | ❌ absurd |

**The honest hierarchy:** ΑΔΑ (free, strongest) → screens (free, one-directional) →
random audit (cheap, the only thing that yields a *rate*) → targeted PDFs (proof for
named claims). Everything else is optional.

**What I'd cut if pressed:** nothing above, but I'd stop at *targeted* PDF verification
and never attempt exhaustive verification. And I'd treat the raw archive as insurance
rather than doctrine — if it ever gets expensive, per-record hashes give 80% of the
benefit at 5% of the size.

---

## Revised bottom line

1. **Storage: solved, ~30 MB, gzipped CSV, GitHub.** Zenodo only for a DOI at publication.
2. **Retrieval: no bulk source. Raise page size to 500 after one test; tier the depth
   (12 months everywhere, 5 years only for the top ~20).**
3. **Verification: ΑΔΑ + automated screens + a 300-record random audit.** That is the
   whole programme. The audit is the only item that turns "we found errors we looked
   for" into a defensible reliability figure — and it remains the critical path.

**Where I was wrong:** I projected 400 MB and designed a two-tier storage architecture
around it without measuring. Actual figure is ~30 MB. The scepticism was correct.
