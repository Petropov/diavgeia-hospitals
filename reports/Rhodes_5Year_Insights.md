# ΓΝ Ρόδου «Ανδρέας Παπανδρέου» — Five-Year Payment Analysis (Aug 2021 – Aug 2026)

**Org:** 99221940 · **Source:** Diavgeia opendata API, decision type Β.2.2 (ΕΝΤΑΛΜΑ ΠΛΗΡΩΜΗΣ)
**Dataset:** 4,796 verified payments · 729 distinct suppliers · **€82,042,987** corrected

Every figure below is on the **corrected** dataset. 16 records were corrected and 2 excluded
after individual verification against their source PDFs. Raw uncorrected data overstates
five-year spend by **€47.05M (+57%)** — see *Data Integrity* below before reusing any of this.

> **Recurring theme across this report.** Three separate "missing data" findings —
> missing payee (§5), missing budget code (§3), and the ×100 amount errors (§4) — all turn
> out to be **failures to populate structured fields correctly, not absent information.**
> In each case the authoritative scanned document holds the right value. Diavgeia's
> machine-readable layer is an unreliable transcription of its own PDFs. That is the single
> most important conclusion here, and it applies to anyone building analysis on this API.

---

## 1. Spend over time

| year | payments | total € | mean | median |
|---|---:|---:|---:|---:|
| 2021 (partial, from Aug) | 585 | 8,054,500 | 13,768 | 2,000 |
| 2022 | 689 | 12,489,878 | 18,128 | 2,408 |
| 2023 | 1,283 | 17,512,686 | 13,650 | 2,768 |
| 2024 | 918 | 19,504,514 | 21,247 | 3,940 |
| 2025 | 1,022 | 16,674,630 | 16,316 | 3,448 |
| 2026 (partial, to Aug) | 299 | 7,806,779 | 26,110 | 7,734 |

**Full-year average (2022–2025): €16.5M/yr ≈ €1.38M/month.**

Cross-check: independent hand-classification of Aug–Sep 2025 gave €1.22M/month, and the
Feb–Aug 2026 window gave €1.22M/month. The corrected dataset is consistent with both.

Spend grew from €12.5M (2022) to €19.5M (2024), then eased to €16.7M (2025) — a ~56% rise
2022→2024. The **median payment more than doubled** (€2,408 → €3,940) while payment counts
stayed broadly flat, so this is larger individual invoices rather than more transactions.

## 2. Supplier concentration — low

| | |
|---|---|
| Distinct suppliers (by ΑΦΜ) | **729** |
| Top-10 share | **36.6%** |
| Top-20 share | **51.7%** |
| **HHI** | **202** |

*(Corrected 2026-08-11: an earlier version of this table reported 895 suppliers / 30.5% /
HHI 152. That aggregated by ΑΦΜ **and** name, which split single suppliers across name
variants and understated concentration. Aggregating by ΑΦΜ alone is correct. The
conclusion is unchanged.)*

An HHI of 202 is *very* low (US DOJ treats <1,500 as unconcentrated). No supplier captures
this hospital's procurement; the base is fragmented and competitive. That is a meaningful
negative finding — supplier capture is a common concern in health procurement and the data
does not support it here.

### Top 15 suppliers (5 years, corrected)

| # | supplier | n | total € | share |
|---|---|---:|---:|---:|
| 1 | ΕΛΛΗΝΙΚΑ ΚΑΥΣΙΜΑ ΟΡΥΚΤΕΛΑΙΑ (fuel) | 31 | 4,781,522 | 5.8% |
| 2 | ROCHE ΕΛΛΑΣ | 20 | 3,101,403 | 3.8% |
| 3 | SARP FACILITY MANAGEMENT | 34 | 2,947,592 | 3.6% |
| 4 | ATRON HEALTH | 18 | 2,889,590 | 3.5% |
| 5 | MERCK SHARP & DOHME | 4 | 2,117,181 | 2.6% |
| 6 | SIEMENS HEALTHCARE | 5 | 2,030,453 | 2.5% |
| 7 | ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ | 48 | 1,924,381 | 2.3% |
| 8 | SANOFI AVENTIS | 14 | 1,764,421 | 2.2% |
| 9 | ΑΥΤΟΜΑΤΟΙ ΑΝΑΛΥΤΕΣ / ΔΙΑΓΝΩΣΤΙΚΑ | 26 | 1,760,660 | 2.1% |
| 10 | ΑΡΗΤΗ (pharma/medical) | 63 | 1,693,005 | 2.1% |
| 11 | TAKEDA ΕΛΛΑΣ | 17 | 1,576,903 | 1.9% |
| 12 | ΥΠΟΥΡΓΕΙΟ ΟΙΚΟΝΟΜΙΚΩΝ | 23 | 1,518,619 | 1.9% |
| 13 | HEALTH AND IASIS | 26 | 1,202,919 | 1.5% |
| 14 | ΑΦΟΙ ΚΟΜΠΑΤΣΙΑΡΗ | 27 | 1,162,925 | 1.4% |
| 15 | ΜΠΡΙΣΤΟΛ ΜΑΓΙΕΡΣ ΣΚΟΥΙΜΠ | 15 | 1,100,838 | 1.3% |

The largest single supplier is **fuel, not medicine** — notable for an island hospital
where energy and logistics carry a structural premium.

**⚠️ Correction to earlier project finding.** A previous note in this project reported
ATRON HEALTH at **~11.3%** of verified spend, flagged as an outlier concentration. That was
computed from a single six-month window. Across the full five years ATRON is **3.5%
(rank 4)** — normal for a recurring medical supplier. **The 11.3% figure should not be
used.** It is a textbook short-window artifact: a supplier billing in a tight cluster looks
dominant until you widen the frame.

## 3. What the money buys (by budget code)

| KAE | € | share | meaning |
|---|---:|---:|---|
| — none recorded | 24,963,360 | 30.4% | **no budget code published** |
| 1312 | 24,341,675 | 29.7% | pharmaceuticals |
| 1311 | 8,884,403 | 10.8% | medical/surgical supplies |
| 1313 | 4,798,516 | 5.8% | specialised medical materials |
| 1359 | 3,414,970 | 4.2% | lab reagents/diagnostics |
| 0845 | 2,731,624 | 3.3% | maintenance/services |
| 1611 | 2,173,470 | 2.6% | fuel/energy |
| 0419 | 1,403,321 | 1.7% | external professional fees |

Clinical consumables (1311+1312+1313+1359) are **50.5%** of spend.

**⚠️ The "none recorded" row is a field-population gap, not a missing budget code.** An
earlier version of this report described this as €25M "unattributable to a spending
category." That overstates it. Of 22 downloaded PDFs whose JSON `kae` field is empty,
**16 (73%) do carry a budget code in the document** — e.g. `41311Β` (→ KAE 1311, medical
supplies), `41511Α`, `40879Α`, `0419Β` (staff fees), each printed with a full description.

This is the **same failure mode as the missing payee** (§5): the information is present in
the authoritative document and simply not written to the structured field. So the correct
statement is:

> 30.4% of spend has **no budget code in the machine-readable data**, though the code exists
> in the source PDF in roughly three-quarters of sampled cases.

The practical consequence is unchanged for any data consumer — €25M cannot be categorised
from the open data without opening thousands of scanned documents — but the cause is
metadata discipline, not absent accounting.

Two caveats on the 73%: the sample is 22 records (those already downloaded for the ×100
verification, so skewed toward large whole-euro payments), and the 6 misses include at least
two public-investment-programme documents in a third layout that the parser may simply have
failed to read. Treat 73% as indicative, not measured.

**Note on which code to read:** these documents also print deduction codes (`35291`, `35299`
— ΚΡΑΤΗΣΕΙΣ for stamp duty, ΕΑΑΔΗΣΥ, income tax). Those are not the expense KAE. The expense
code is the `4XXXXΑ/Β` form, which maps to the KAE by dropping the leading 4 and the trailing
letter (`41311Β` → 1311). A naive extraction that grabs the first numeric code will
systematically mis-categorise spend as deductions.

## 4. Data integrity — two proven error classes

All 49 whole-euro payments ≥€50,000 were downloaded and checked against their source PDFs.
**49/49 resolved: 16 errors, 33 genuine.**

### (a) Missing decimal separator — ×100 overstatement, 16 records

| year | errors | overstatement € |
|---|---:|---:|
| 2021 | 4 | 11,748,087 |
| 2022 | 6 | 31,927,500 |
| 2023 | 3 | 2,277,840 |
| 2024 | 1 | 488,313 |
| 2025 | 2 | 610,608 |
| **total** | **16** | **47,052,348** |

Proof example — ADA `ΨΤ6Τ46907Κ-8ΕΘ` (TAKEDA, 2022-09-28). The scanned warrant states the
sum **in words**: *«# 185,904.21 # εκατόν ογδόντα πέντε χιλιάδες εννιακόσια τέσσερα ευρώ και
είκοσι ένα λεπτά»*. The portal's JSON records `1.8590421E7` = **€18,590,421**. Exactly ×100.
The same document certifies the annual credit for that budget code as €6.06M — so the
recorded figure exceeds the whole year's budget line threefold and is impossible on its face.

**This error class is ongoing, not historical.** It occurs in every year including 2025. It
only appears to stop after 2023 if you screen at ≥€500k, because later errors sit on smaller
base amounts (€4,883 × 100 = €488k).

### (b) ΑΦΜ typed into the amount field — 2 records, €895M phantom

| ADA | supplier | recorded € | supplier ΑΦΜ |
|---|---|---:|---|
| `ΨΚ1Τ46907Κ-Α8Ω` | VIMATRONIX | 800,495,854 | 800495854 |
| `6Χ4Μ46907Κ-8Θ2` | GE HEALTHCARE | 94,472,918 | 094472918 |

Digit-for-digit identical to the supplier's tax ID. Excluded entirely (true values unknown).

### Combined

| class | records | phantom € |
|---|---:|---:|
| ΑΦΜ-in-amount | 2 | 894,968,772 |
| ×100 decimal | 16 | 47,052,348 |
| **total** | **18** | **~942.0M** |

Eighteen records carry ~€942M that was never spent, against real five-year spend of €82M.
**A naive sum of Diavgeia's `expenseAmount` for this one hospital overstates by 57%** — and
that is *after* the AFM cases are removed; including them the raw field sums to over €1bn.

### Caveats on the correction
- Verification covered whole-euro amounts **≥€50,000** (49 records). Errors on smaller
  amounts (recorded <€50k, i.e. true value <€500) are not excluded and remain unquantified.
- Amounts *with* cents were not checked; a ×100 error there would be unusual but is not
  logically impossible.
- 285 self-referential payroll/ΕΦΚΑ records and 21 with no sponsor block were excluded by
  rule, consistent with prior methodology.

## 5. Supplier anonymity — now measured

The Β.2.1 (`ΧΕ`) pull is complete. Those records publish an amount but frequently leave
`sponsorAFMName` structurally empty.

| Rhodes, 5 years | records | € |
|---|---:|---:|
| Β.2.2 named (corrected) | 4,796 | 82,042,987 |
| Β.2.1 named | 435 | 5,830,830 |
| **Β.2.1 anonymous** | **2,503** | **35,605,727** |
| Β.2.1 self-referential | 3 | 25,361 |
| **all payment value** | **7,737** | **123,504,905** |

**€35.6M — 28.8% of total payment value — is published with an amount but no payee
identity.** By count, 2,503 of 7,737 payment records (32.4%) name no supplier.

### ⚠️ MAJOR REVISION — the "anonymous" money is NOT secret

A 14-record stratified sample of these anonymous records was downloaded and read against
source PDFs. **The payee is identified in the PDF in every case we could parse.** The
`sponsorAFMName` field is empty, but the document behind it names the recipient.

| ADA | what the JSON shows | what the PDF shows |
|---|---|---|
| `9ΕΙΘ46907Κ-3ΩΝ` | no supplier | **SPECIFAR A.B.E.E.**, 1 offer received |
| `6ΔΖ946907Κ-ΞΛΔ` | no supplier | **GILEAD SCIENCES ΕΛΛΑΣ**, 1 offer |
| `6Ε9Λ46907Κ-ΔΓΧ` | no supplier | **ΒΙΑΝΕΞ Α.Ε.**, 1 offer |
| `6Ι4Α46907Κ-ΟΦΔ` | no supplier, €2,559,126 | **WALLS JERALDΙΝ ΚΤΛ** (staff overtime), **€25,521.96** |
| `ΨΤ4Ψ46907Κ-ΓΟ4` | no supplier | ΕΦΗΜΕΡΙΕΣ ΕΣΥ (on-call duties) |
| `619Ω46907Κ-9ΘΡ` | no supplier | VACARCIOUC ALEXANDRA ΚΛΠ (staff) |

**So this is a machine-readability failure, not concealment.** The legal disclosure
obligation is met — the information is public in the PDF. What is missing is the structured
field, which is what every automated analysis, dashboard and league table actually reads.
The money is traceable, but only by a human opening several thousand scanned documents
one at a time.

That is a materially *less severe* finding than "€35.6M with no identifiable recipient",
and this report previously implied the stronger version. It is corrected here.

It is also a far **cheaper** problem to fix: the data exists at the point of entry; it simply
isn't being written to the structured field.

### Two further consequences of the same check

**1. Much of the "anonymous" total is payroll, not procurement.** The parseable records
resolve to staff overtime, on-call duty compensation (ΕΦΗΜΕΡΙΕΣ ΕΣΥ) and named individuals.
A subject-line filter attributed only €6.3M (17.7%) to payroll, but that filter only catches
records whose *subject* says so — many read simply "ΧΕ 1189". The true payroll share is
materially higher, so the genuine *supplier*-anonymity figure is well below €29.3M.

**2. The Β.2.1 records contain ×100 errors too — and were never checked.** The largest
"anonymous payment" in the entire dataset, `6Ι4Α46907Κ-ΟΦΔ` at **€2,559,126**, is in fact
**€25,521.96** of September 2021 staff overtime. All ×100 verification in this project was
performed on Β.2.2 only. **The €35.6M Β.2.1 total is therefore itself unverified and
probably inflated.** It should not be quoted until the same PDF screen is run against it.

### What this does not soften

The structured field is still empty on 2,503 records, and the portal still accepts that. Any
consumer of Diavgeia's open data — including the Ministry's own reporting — sees no payee.
Lamia demonstrates it is avoidable: 8 such records in five years versus Rhodes' 2,503.

**But it is not inevitable.** The matched five-year pull for ΓΝ Λαμίας (see
`Rhodes_vs_Lamia_5Year.md`) puts its anonymity rate at **0.8%** — €961,818 of €118.5M, from
just 8 records. Lamia barely uses the Β.2.1 record type at all (32 records in five years vs
Rhodes' 2,941). Same platform, same period, same rules: **28.8% vs 0.8%, a 36× gap.**
Near-complete payee disclosure is demonstrably achievable here.

*(An earlier draft of this analysis claimed anonymous records outnumbered named ones by
2–6×. That was based on misattributing Lamia's Β.2.2 window counts to Rhodes' Β.2.1 run and
is withdrawn. The table above is the measured result.)*

## 6. Per-bed spend and year-over-year trend

Bed counts (external, imperfect): Rhodes **~335 οργανικές κλίνες** (figure dates to the
hospital's founding; today's may differ), Lamia **~318 developed beds**. Different
definitions and vintages — per-bed *levels* are indicative only. The two hospitals being
nearly the same size is itself useful: the comparison is at least between peers.

**Β.2.2 spend per bed, full years (Rhodes corrected / Lamia as published):**

| year | Rhodes € | €/bed | YoY | Lamia € | €/bed | YoY |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 12,489,878 | 37,283 | — | 21,415,953 | 67,346 | — |
| 2023 | 17,512,686 | 52,277 | **+40%** | 21,372,779 | 67,210 | −0% |
| 2024 | 19,504,514 | 58,222 | +11% | 24,666,083 | 77,566 | +15% |
| 2025 | 16,674,630 | 49,775 | **−15%** | 27,436,772 | 86,279 | +11% |
| 2022→2025 | | | **+34%** | | | **+28%** |

**Trend (the robust part):** both hospitals grew ~30% over three years — consistent with
post-2022 medical/energy inflation. The difference is the *path*: Lamia climbs smoothly
(0/+15/+11); Rhodes swings (+40/+11/−15). Rhodes' volatility fits its record-keeping
profile — batchy payment practice and shifting field discipline — more than any plausible
swing in real hospital activity.

**Levels (the treacherous part):** at face value Rhodes runs at **58% of Lamia's spend per
bed** (€49.8k vs €86.3k in 2025). But this is mostly a *record-routing artifact*: Rhodes
pushes substantial payment value through Β.2.1 records (which this table excludes), Lamia
essentially doesn't. On **all payment value (Β.2.2+Β.2.1), five-year totals per bed are
almost identical: Rhodes €368.6k vs Lamia €372.6k** (€123.5M/335 vs €118.5M/318 — a 1%
difference). The apparent per-bed gap is where the money is *recorded*, not what the
hospital spends. (Caveat: Rhodes' Β.2.1 amounts are unverified for ×100 errors — §5 — so
treat the combined figure as approximate.)

Also remember scope: Β.2.2/Β.2.1 capture supplies and services, **not payroll**, which is
the majority of true hospital cost. This is "procurement-type spend per bed", not "cost
per bed".

**Two open questions surfaced by the YoY view:**

1. **Rhodes' pharma (KAE 1312) share collapses 47% → 41% → 37% → 14% (2022→2025).** It is
   *not* a KAE-recording artifact — the empty-KAE share falls over the same years
   (42%→14%). Real candidates: high-cost drugs migrating to Β.2.1 direct-award records
   (where KEYTRUDA/OPDIVO etc. dominate subjects), central/ΕΟΠΥΥ procurement taking over,
   or genuine substitution. Unresolved; worth a targeted look before quoting.
2. **2026 shows a fresh data-governance regression: 99% of Rhodes' 2026 Β.2.2 spend has an
   empty KAE field** (vs 14% in 2025) — coinciding with the appearance of a new document
   format/issuing unit in the records. Whatever changed in the workflow in 2026 effectively
   stopped budget-code publication.

## 7. Reproducing

```
python3 scripts/fetch_payments_history.py --org 99221940 --start 2021-08-01
```
Artefacts: `payments.csv` (raw), `payments_corrected.csv` (with `correction` and
`original_amount` audit columns), `pdf_verified_corrections.csv` (all 49 verdicts),
`verify_pdfs/` (source PDFs), `monthly_summary.csv`, `excluded.csv`, `anomalies.csv`.

**Status:** Lamia (99221923) comparison pending — requires the same pull + PDF verification
to be a matched comparison rather than the mismatched one the earlier report warned about.
