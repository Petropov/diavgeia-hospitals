# Diavgeia Hospital Payments — verified open data

Five-year (Aug 2021 – Aug 2026) payment datasets for two Greek public hospitals, extracted
from the [Diavgeia](https://diavgeia.gov.gr) transparency portal, **verified against source
PDFs, corrected, and fully reproducible**.

| org | hospital | dataset |
|---|---|---|
| `99221940` | ΓΝ Ρόδου «Ανδρέας Παπανδρέου» | `data/99221940/` |
| `99221923` | ΓΝ Λαμίας | `data/99221923/` |

**Headline:** naive summation of Diavgeia's machine-readable `expenseAmount` overstates
Rhodes' five-year spend by **57%** (€129.1M → corrected **€82.0M**). Eighteen records carry
~€942M of phantom value (tax IDs typed into amount fields; missing decimal separators —
each proven against the signed source document). Lamia's data shows none of these
signatures. Full analysis in `reports/`.

## Repository layout

```
scripts/
  fetch_payments_history.py    pull any org's Β.2.2/Β.2.1 history (bypasses the "6-month
                               limit" — it's a max span per query, not a recency cap)
  score_diavgeia_quality.py    DDQI: 0-100 data-quality index to stack-rank organisations
data/<org>/
  payments/payments.csv            raw extraction
  payments/payments_corrected.csv  with correction + original_amount audit columns (Rhodes)
  payments/excluded.csv            every excluded record + reason + amount
  payments/pdf_verified_corrections.csv  the 49 outlier verdicts (Rhodes)
  payments/anomalies.csv           AFM-in-amount detections
  payments_B21/...                 Β.2.1 (ΧΕ) layer, same shapes
  *_pdfs/                          source PDFs backing every correction (evidence)
reports/                           analysis & methodology (see esp. Known_Unknowns.md
                                   before quoting any number)
```

## Reproducing / updating

```bash
# refresh a hospital (new data appears continuously; totals drift — always record the date)
python3 scripts/fetch_payments_history.py --org 99221940 --start 2021-08-01

# rank data quality across organisations
python3 scripts/score_diavgeia_quality.py --orgs 99221940 99221923 --start 2022-01-01
```

Convention for updates: re-run, then commit with the extraction date in the message
(`data refresh 2026-09-01`). Diavgeia is live — two runs minutes apart differed by €5,549 —
so **every figure must carry its extraction date**.

## Read before using

- `reports/Known_Unknowns.md` — what these datasets **cannot** show. All verification was
  outlier-targeted; there is no measured base error rate. Detection is asymmetric
  (overstatement only). "Lamia clean" = "no signature our screens detect".
- Amounts are gross EUR as published; negatives (credit notes) are excluded, not netted.
- Β.2.2/Β.2.1 = supplies & services payments; **payroll is not in scope**.
- DDQI scores the machine-readable layer only — information present only in PDFs
  (payees, budget codes) correctly earns no credit.

## Sources & licence

Data: Diavgeia opendata API (`diavgeia.gov.gr/opendata`), public records under Greek
transparency law (Ν.3861/2010). Analysis and code: CC-BY-4.0 / MIT. Extraction: 2026-08-11.
