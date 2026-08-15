# ΓΝ Ρόδου vs ΓΝ Λαμίας — Matched Five-Year Comparison (Aug 2021 – Aug 2026)

Both hospitals pulled with the **same script, same window, same decision type (Β.2.2), same
classification rules**. This supersedes `Rhodes_vs_Lamia_Comparison.md`, which compared a
full Lamia history against a six-month Rhodes slice and correctly warned it couldn't support
euro-for-euro conclusions. That caveat no longer applies.

| | **ΓΝ Ρόδου** (99221940) | **ΓΝ Λαμίας** (99221923) |
|---|---:|---:|
| Payments | 4,796 | **13,608** |
| Total € (5yr) | 82,042,987 | **116,323,760** |
| Distinct suppliers (ΑΦΜ) | 729 | 861 |
| Mean payment | **17,107** | 8,548 |
| Median payment | ~3,000 | ~1,200 |
| Top-10 share | 36.6% | 42.3% |
| Top-20 share | 51.7% | 56.1% |
| HHI | **202** | 329 |
| ×100 decimal errors | **16** | **0** |
| ΑΦΜ-in-amount errors | **2** | **0** |
| **Anonymity rate (value)** | **28.8%** | **0.8%** |

Rhodes figures are **corrected**; Lamia's are raw but verified clean (below).
Extracted 2026-08-11; Diavgeia is live and totals drift slightly between runs.

## 1. Two different operating patterns

Lamia processes **2.8× more payments** for **1.4× the value** — so its typical payment is
half the size (mean €8,548 vs €17,107; median ~€1,200 vs ~€3,000). Rhodes batches into
fewer, larger warrants; Lamia settles in a higher volume of smaller ones.

Neither is better on its face, but it matters for interpretation: any metric expressed
*per payment* will differ ~2× purely from administrative practice, not from spending
behaviour. Compare totals and shares, not per-payment averages.

## 2. Both have low supplier concentration

HHI 202 (Rhodes) and 329 (Lamia) are both far under the 1,500 "unconcentrated" line. Lamia
is somewhat more concentrated, driven by its top supplier.

**Lamia's #1 is not a supplier at all.** ΜΤΠΥ ΚΛΠ ΤΑΜΕΙΑ at €14.75M (12.7%, 647 payments)
is a public-servants' pension/insurance fund — statutory contributions, not procurement.
Excluding it, Lamia's procurement concentration falls close to Rhodes'. Comparable
statutory items appear in Rhodes' list too (ΥΠΟΥΡΓΕΙΟ ΟΙΚΟΝΟΜΙΚΩΝ, €1.5M, 1.9%).

**Genuine top procurement suppliers:**

| | Rhodes | Lamia |
|---|---|---|
| 1 | ΕΛΛΗΝΙΚΑ ΚΑΥΣΙΜΑ (fuel) 5.8% | UNISON FACILITY SERVICES 6.3% |
| 2 | ROCHE 3.8% | MERCK SHARP & DOHME 3.7%+3.3% |
| 3 | SARP FACILITY MGMT 3.6% | ΙΝΤΕΡΚΑΤ 3.2% |
| 4 | ATRON HEALTH 3.5% | ABBOTT 2.8% |

Both show the same shape: one large **facilities/cleaning** contractor, then pharma
multinationals. The visible difference is Rhodes' **fuel** at #1 — an island-logistics cost
that simply doesn't rank at mainland Lamia.

## 3. Data quality — the key divergence

This is where the two diverge sharply.

| signature | Rhodes | Lamia |
|---|---|---|
| whole-euro amounts ≥€500k | 12 (across 2021-23) | **0 in every year** |
| mean/median ratio, worst year | **26×** (2022) | 6–9× (stable) |
| ×100 decimal errors (PDF-verified) | **16**, worth €47.05M | **0** |
| ΑΦΜ typed into amount | **2**, worth €895M | **0** |

Lamia's top payments all carry realistic cents (€2,178,322.44; €1,049,820.24; €565,252.58)
and its mean/median ratio is stable across all six years. There is no contamination
signature. Rhodes' raw data overstated spend by **57%**; Lamia's appears sound as published.

**This narrows the earlier hypothesis.** A previous note in this project suggested these
errors were likely portal-wide. On this evidence they are **not**: two hospitals on the same
platform, same period, same record type — one contaminated, one clean. The portal *permits*
the error (no validation on `expenseAmount`, no check against the supplier's own ΑΦΜ), but
the error is introduced locally at Rhodes. It is a Rhodes data-entry practice operating
inside a portal that fails to catch it.

Both statements are needed to be accurate:
- **Rhodes-specific** — Lamia's staff did not make these errors.
- **Portal-enabled** — nothing in Diavgeia stopped 16 impossible values, including one
  exceeding its own certified annual budget line threefold, from being published for years.

## 4. Supplier anonymity — measured for both, and the gap is enormous

Both hospitals now have Β.2.2 **and** Β.2.1 pulled, with exclusion values captured.

| | **ΓΝ Ρόδου** | **ΓΝ Λαμίας** |
|---|---:|---:|
| Named payments | €87,873,817 (5,231) | €117,524,983 (13,625) |
| **Anonymous (amount, no payee)** | **€35,605,727 (2,503)** | **€961,818 (8)** |
| No-sponsor-block records | €0 (21) | €0 (2,415) |
| Total payment value | €123,479,544 | €118,486,801 |
| **ANONYMITY RATE** | **28.8%** | **0.8%** |

**Rhodes leaves the payee field empty on 28.8% of its payment value. Lamia on 0.8%.
A 36× difference between two hospitals on the same platform.**

> **⚠️ Revised interpretation (PDF-verified).** A 14-record sample of Rhodes' anonymous
> records was checked against source documents: **the payee is named in the PDF in every
> parseable case** (SPECIFAR, GILEAD, ΒΙΑΝΕΞ; staff names and on-call compensation for the
> payroll ones). This is a **machine-readability failure, not concealment** — the disclosure
> obligation is met, the structured field simply isn't populated. Two further consequences:
> much of the total is payroll rather than procurement, and the Β.2.1 records contain
> ×100 errors that were never screened (the largest, €2,559,126, is really €25,521.96).
> **The €35.6M figure is unverified and inflated; do not quote it.** See
> `Rhodes_5Year_Insights.md` §5. The 36× *field-completion* gap between the two hospitals
> stands regardless.

Two corrections to earlier drafts of this document, both now resolved by data:

1. **Lamia's 2,415 "no sponsor block" records are not hidden payments.** An earlier version
   of this report speculated Lamia's anonymity was "differently shaped" — hidden in missing
   sponsor blocks rather than empty name fields. Re-run with the fixed script, those 2,415
   records total **€0.00**: they carry no amount at all. They are empty or administrative
   records, not concealed money. The speculation was wrong.
2. **Lamia barely uses Β.2.1 at all** — 32 records in five years, versus Rhodes' 2,941.
   Rhodes routes a large share of its spending through the record type that permits an empty
   supplier field; Lamia essentially does not.

So the anonymity gap is not a reporting-format artefact. It is a real difference in what the
two hospitals disclose.

### Still not established

**Whether Lamia's 39 whole-euro payments ≥€50k are genuine.** The statistical signature says
yes, but Rhodes taught us only the PDFs settle it — and 2 of 12 apparent errors there turned
out to be real payments. Worth verifying before Lamia's total is quoted as final.

**Live-data drift.** Lamia's two runs, minutes apart, returned €116,323,759.86 and
€116,329,309.34 (+€5,549, +1 payment). Diavgeia is a live system; totals move as records are
added or corrected. Quote figures with the extraction date attached.

## 4c. The substantive gist — what the two hospitals actually do with money

Setting aside how each populates Diavgeia, the operational picture:

**They buy the same things in roughly the same proportions.** Where budget codes exist,
both are pharmacy-led: pharmaceuticals ~43% of Rhodes' coded spend and ~30% of Lamia's
(1312-family, €34.6M), followed in the same order by medical supplies (16% vs 11%), lab
reagents (6% vs 6%), and facilities/maintenance services. These are two instances of the
same operating model — a Greek regional general hospital — not different strategies.
Differences at the margin are geographic: fuel ranks high only at Rhodes (island energy
logistics); Lamia's coded spend includes ~€12M of 33xx-family remittance/pass-through codes
Rhodes records elsewhere.

**They buy from substantially the same market.** 307 suppliers serve both hospitals —
42% of Rhodes' supplier base, 36% of Lamia's — and those shared suppliers take **64% of
Rhodes' spend and 56% of Lamia's**. The majority of both hospitals' money flows to the same
national vendors (pharma multinationals, facilities groups, diagnostics firms). Genuinely
local procurement is the minority almost everywhere except Rhodes' fuel and eponymous
maintenance contractor.

**Value is concentrated in few payments at both.** ~156 payments ≥€100k carry 39% of
Rhodes' value; 191 carry 35% of Lamia's. Meanwhile 59% (Rhodes) and 77% (Lamia) of payment
*events* are under €5k. Oversight effort should follow the ~150–190 large payments per
hospital, not the thousands of small ones.

**Security/guarding, per bed (asked specifically):** Rhodes spends **~€538,823/yr
(€1,608/bed)** on guarding vs Lamia's **~€390,259/yr (€1,227/bed)** — Rhodes ~31% higher
per bed (full-year averages 2022–25; supplier-name + CPV 79713000-5 matching, name variants
deduped). Both markets are thin: 3–4 active security firms each, one dominant (MYSERVICES
group at Rhodes across five name variants; ΗΦΑΙΣΤΟΣ at Lamia — which also does a small job
at Rhodes). Rhodes' trajectory is odd: €923k in 2022, then halved to ~€370k by 2024–25 —
either a renegotiation/tender success or a shift of guarding spend into records this
extraction doesn't capture. Lamia's is lumpy (€58k in 2024 vs €719k in 2025), suggesting
invoice timing rather than staffing swings. Note MYSERVICES is also one of the three
suppliers flagged in the per-destination structuring screen
(`Integrity_Signals_Rhodes_vs_Lamia.md` §1b).

**Both grew ~30% in three years** (+34% vs +28%, 2022→2025) — the inflation story is
system-wide, not hospital-specific. And on *all* payment value per bed they are within a
few percent of each other (€368.6k vs €372.6k over five years — but note Rhodes' Β.2.1
amounts are unscreened for ×100 errors and contain at least one proven €2.5M phantom, so
"~1%" would be false precision; see `SENSE_CHECK.md`).

**Where they genuinely differ:**
1. **Payment administration.** Lamia: many small, steady, well-coded payments (median
   ~€1,200, smooth YoY). Rhodes: batchier and larger (median ~€3,000, swings of +40%/−15%).
2. **Single-bid exposure at Rhodes** on high-cost drugs via direct awards (3 of 5 sampled
   — small sample, plausibly structural for patented drugs, but unmeasured at Lamia).
3. **Record integrity** — the 57% inflation and empty-field issues are Rhodes-specific
   (documented above).

The honest headline: **operationally these are near-twins; administratively they are far
apart.** Almost everything that distinguishes Rhodes from Lamia in this dataset is about
how money is recorded and awarded, not what it is spent on.

## 5. Bottom line

- Lamia is the **larger operation**: 1.4× the spend, 2.8× the payment volume.
- Both are **structurally similar** in procurement: low concentration, facilities contractor
  plus pharma multinationals at the top. Rhodes' fuel dependence is the visible island effect.
- They differ decisively on **data quality**. Rhodes' published figures required a 57%
  correction; Lamia's did not.
- They differ even more decisively on **disclosure**. Rhodes publishes 28.8% of its payment
  value with no payee; Lamia 0.8%. **36×.**

The two findings compound. Rhodes' open data was simultaneously **inflated by 57%** and
**missing the payee on 28.8% of value**. Neither problem appears at a comparable hospital
operating the same platform in the same period — so neither can be explained away as "how
Diavgeia works." This is an institution-level data-governance failure at ΓΝ Ρόδου, sitting
inside a portal that validates nothing and therefore catches nothing.

The constructive reading: both are fixable, and cheaply. A single validation rule
(`amount != supplier ΑΦΜ`) would have caught 2 records worth €895M. A plausibility check
against the decision's own certified budget line would have caught all 16 ×100 errors. And
Lamia demonstrates that near-complete payee disclosure is achievable on this platform today —
it is a choice, not a technical limit.

**Methodological point worth carrying forward:** the mean/median ratio is a reliable
first-pass contamination detector. It flagged Rhodes (26×) and cleared Lamia (6–9×) before
any PDF was opened. But it only identifies *which dataset* to inspect — it cannot tell you
which individual records are wrong, and it produced two false positives at Rhodes that would
have destroyed €1.69M of genuine spending had they been "corrected" mechanically.
