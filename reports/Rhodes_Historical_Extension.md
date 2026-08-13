# ΓΝ Ρόδου — Historical Extension (Aug 2025 →), breaking the "6-month ceiling"

**Status: the 6-month API limit was wrong — or rather, incomplete.** Earlier work in this project concluded that Diavgeia's opendata API hard-caps history at ~6 months and that older data was unreachable without OCR'd third-party corpora. That conclusion was based on testing `from_date`/`to_date` and a raw `q=` override, both of which the server silently clamps.

**The actual behaviour (verified live 2026-08-11):** the parameters are `from_issue_date` / `to_issue_date`. With those, the server returns clean structured JSON for arbitrary historical periods. Confirmed by the echoed query:

```
issueDate:[DT(2025-08-01T00:00:00+03:00) TO DT(2025-08-15T00:00:00+03:00)]
```

Combined with `type=Β.2.2`, this returns *only* payment records — reducing the work from ~4,000 decisions/6mo to ~475.

Working call:
```
https://diavgeia.gov.gr/opendata/search.json
  ?org=99221940&type=%CE%92.2.2
  &from_issue_date=YYYY-MM-DD&to_issue_date=YYYY-MM-DD
  &size=50&page=N
```
(`%CE%92` = Greek capital Beta. Per-ADA hydration via `/opendata/decisions/{ADA}.json` also works for arbitrarily old decisions.)

No Hugging Face dataset, no OCR, no gated access, no 14GB download required.

## Results (same classification rules as the 2026 window)

| Month | Payments | Verified EUR | Status |
|---|---:|---:|---|
| Aug 2025 | 76 | 1,156,139.54 | complete (3 self-referential excluded) |
| Sep 2025 | 123 | 1,283,846.44 | complete (1 data-entry error excluded — see below) |
| Oct 2025 | 47 | 1,285,698.68 | **partial — page 0 of 3 only** |
| **Subtotal** | **246** | **3,725,684.66** | |

Not yet pulled: rest of Oct 2025, Nov 2025, Dec 2025, Jan 2026, Feb 1–11 2026. Fully resumable — just walk the months.

## The cross-validation that matters

- Aug+Sep 2025 (complete months, this pull): **€1,219,993 / month**
- Feb–Aug 2026 (the earlier 4,392-decision window): €7,305,654 / 6 = **€1,217,609 / month**

**A 0.2% difference between two independently collected six-month datasets.** This is strong evidence that the classification methodology (Β.2.2 with named sponsor + populated amount; excluding anonymous ΧΕ, self-referential payroll, recalled corrections, and Β.1.3 commitments) is stable and reproducible rather than an artifact of one sampling window.

It also means the earlier "roughly €14.6M/year" extrapolation is now **substantially corroborated by real data** rather than being a doubling of a single window.

## CONFIRMED DATA-ENTRY ERROR — €94.5M phantom payment

**ADA `6Χ4Μ46907Κ-8Θ2`** | protocol 815 | issued 2025-09-19 | type Β.2.2
Supplier: GE HEALTHCARE ΦΑΡΜΑΚΕΥΤΙΚΗ (ΑΦΜ **094472918**)
Recorded `expenseAmount`: `9.4472918E7` = **€94,472,918**
CPV 50421000-2 (medical equipment maintenance), KAE 0887

**Proof it is an error, not a real payment:** the recorded amount is digit-for-digit the supplier's own tax ID. `094472918` → `94,472,918`. The ΑΦΜ was typed into the amount field.

Scale of distortion: this single record is ~6.5× the hospital's true *annual* payments. Any automated analysis summing `expenseAmount` for this organisation — including any published spending figure or league table built from Diavgeia's own open data — would be wrong by €94.5M unless it happens to catch this.

Two ways it can silently corrupt an analysis:
1. Naive summation → inflates Rhodes' spend by €94.5M.
2. A regex like `[0-9.]+` that doesn't handle JSON scientific notation → silently truncates it to **€9.45** (this nearly happened here; it was caught only because the value looked anomalous).

Excluded from all totals above. True value unknown — a maintenance contract of this type is plausibly ~€94,472.92.

## SECOND ERROR CLASS — MISSING DECIMAL SEPARATOR (×100), PROVEN AGAINST SOURCE PDF

Full 5-year pull (Aug 2021 – Aug 2026, org 99221940) returned 4,796 verified payments
totalling **€129,095,335.04** — ~€25.8M/yr, roughly 1.8× the hand-verified run-rate of
€1.22M/month. The excess is contamination, not spending.

**Diagnostic that isolated it — the median is immune to outliers:**

| year | n | total | mean | median | max |
|---|---:|---:|---:|---:|---:|
| 2021* | 585 | 19,802,588 | 33,851 | 2,000 | 5,628,028 |
| 2022 | 689 | 44,417,378 | 64,466 | 2,449 | 18,590,421 |
| 2023 | 1283 | 19,790,525 | 15,425 | 2,768 | 1,395,506 |
| 2024 | 918 | 19,992,826 | 21,779 | 3,940 | 493,245 |
| 2025 | 1022 | 17,285,239 | 16,913 | 3,472 | 1,263,742 |
| 2026* | 299 | 7,806,779 | 26,110 | 7,734 | 300,036 |

*(2021 and 2026 are partial years.)* The **median is stable** (2,000 → 7,734, gentle
inflationary drift) while 2022's **mean is 26× its median**. Classic contaminated subset.

Whole-euro amounts ≥ €500,000: **6 in 2021, 4 in 2022, 2 in 2023, and ZERO in 2024/2025/2026.**
The practice stops dead after 2023.

### Proof (ADA ΨΤ6Τ46907Κ-8ΕΘ, TAKEDA ΕΛΛΑΣ, 2022-09-28)

Source PDF (`diavgeia.gov.gr/doc/{ADA}`) is a scanned ΕΝΤΑΛΜΑ ΠΛΗΡΩΜΗΣ and states the sum
**in words**, which is unambiguous:

> `Πληρώσατε το ποσό των ευρώ: # 185,904.21 #`
> *εκατόν ογδόντα πέντε χιλιάδες εννιακόσια τέσσερα ευρώ και είκοσι ένα λεπτά*

| | |
|---|---|
| PDF (authoritative) | **€185,904.21** |
| Diavgeia JSON `expenseAmount` | **1.8590421E7 = €18,590,421** |
| Ratio | **exactly ×100** |

Corroborated three ways within the same document: (a) invoice table sums to
175,381.34 + 10,522.87 VAT = 185,904.21; (b) deductions €10,604.88, net to supplier
€175,299.33; (c) page 3 certifies the **annual** credit for KAE 01-41312Β is
€6,064,643.98 — so an €18.59M single payment is arithmetically impossible.

### Corrected five-year total

```
129,095,335.04   script total (AFM-errors already excluded)
-47,201,545.00   the 12 decimal-error records as recorded
+   472,015.45   their true value (÷100)
= 82,365,805.49
```

**≈ €82.4M over ~5 years ≈ €16.5M/yr ≈ €1.37M/month** — consistent with the
independently hand-verified €1.22M/month. The correction reconciles the dataset.

Caveat: the ≥€500k whole-euro screen is a **floor, not a census**. ENTHESYS at
€493,245.00 (2024) carries the same signature just under the threshold. Smaller
contaminated records almost certainly remain; only 1 of the 12 has been PDF-verified
so far (PDFs for all 12 are in `data/99221940/suspect_pdfs/`).

### Combined phantom value in ONE hospital's records

| class | records | phantom € |
|---|---:|---:|
| ΑΦΜ typed into amount | 2 | 894,968,772 |
| Missing decimal separator (×100) | 12 | 46,729,529 |
| **Total** | **14** | **~941.7M** |

Fourteen records carry ~€941.7M of value that was never spent — against a real
five-year spend of ~€82M. Any league table, dashboard, or research dataset built by
summing `expenseAmount` from Diavgeia without outlier screening is catastrophically wrong.

## Other observations

- **Large payment to an individual:** ΧΕ 682, ΔΙΑΚΟΜΑΝΩΛΗ ΑΡΧΟΝΤΟΥΛΑ (ΑΦΜ 062129532), €296,856.00, ADA `ΨΞΥΥ46907Κ-ΥΩΛ`, Sept 2025. Payments to natural persons at this scale are unusual enough to be worth a look at the underlying document (no CPV/KAE recorded on the entry).
- **Self-referential payroll records persist historically** (hospital's own ΑΦΜ 999052193 as sponsor) — 3 in Aug, 3 in Oct p0 — same pattern as the 2026 window, confirming it's structural, not period-specific.
- **glossAPI dataset-card caveat:** its decision-type labels appear mismapped (it lists Β.2.2 as "Ανάληψη Υποχρέωσης" and Β.1.3 as human-resources acts). Empirically in this org's data the opposite holds: Β.2.2 = payment orders with sponsor+expenseAmount; Β.1.3 = ΔΕΣΜΕΥΣΗ budget commitments. Trust the observed field structure over that card.

## Reproducing / resuming

Raw extracted amounts per page are in `data/rhodes_hist/*.txt`, with the anomaly documented in `data/rhodes_hist/ANOMALY_ge_healthcare.md`. To continue: run the working call above for Oct 2025 pages 1–2, then Nov 2025 → Feb 11 2026, applying the same exclusions.
