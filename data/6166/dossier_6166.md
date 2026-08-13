# Municipality Intelligence Dossier — Org UID 6166

_Generated 2026-05-14 10:47 · 8 decisions loaded · 2 hydrated · 3 pending hydration_


## Dataset Health

| Metric | Value |
|:---|---:|
| Total decisions loaded | **8** |
| Procurement rows (normalized) | **8** |
| High-value candidates (score ≥ 5) | **5** |
| Already hydrated | **2** |
| Needs hydration | **3** |


### Monthly Activity

| Year | Month | Decisions | Enriched | Suppliers |
|-----:|------:|----------:|---------:|----------:|
| 2026 | 1 | 4 | 0 | 0 |
| 2026 | 2 | 4 | 0 | 0 |


## Decision Type Distribution

| Decision Type | Count | % |
|:---|---:|---:|
| ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | 3 | 37.5% |
| ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣΙΩΝ / ΜΕΛΕΤΩΝ | 2 | 25.0% |
| ΑΝΑΛΗΨΗ ΥΠΟΧΡΕΩΣΗΣ | 2 | 25.0% |
| ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ | 1 | 12.5% |


## High-Value Candidate ADAs

_Top 5 decisions ranked by intelligence value (score ≥ 5). Full list in `candidates.json`._

| Score | ADA | Yr | Type (abbrev.) | Subject | Amount | Hydrated |
|------:|:----|---:|:---------------|:--------|-------:|:---------|
| 12 | `Ψ8ΣΝΩΛΚ-1ΤΜ` | 2026 | ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣ… | ΠΑΡΟΧΗ ΑΝΕΞΑΡΤΗΤΩΝ ΥΠΗΡΕΣΙΩΝ ΕΣΩΤΕΡΙΚΟΥ ΕΛΕΓΧΟΥ | — | ✓ |
| 10 | `901ΓΩΛΚ-ΓΙΣ` | 2026 | ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣ… | Εντολή και πληρεξουσιότητα σε δικηγόρο για σύνταξη γνωμοδοτικού σ… | — | ✓ |
| 7 | `94ΨΚΩΛΚ-Χ95` | 2026 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Έγκριση 1α Πρακτικού ηλεκτρονικού ανοικτού διαγωνισμού ΠΡΟΜΗΘΕΙΑ … | — | ⚠ |
| 6 | `ΡΕ5ΨΩΛΚ-Ξ77` | 2026 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Μετάθεση καταληκτικής ημερομηνίας ηλεκτρονικού ανοικτού διεθνούς … | — | ⚠ |
| 5 | `9ΞΕ6ΩΛΚ-Κ9Φ` | 2026 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Έγκριση 2ου Πρακτικού ηλεκτρονικού ανοικτού διεθνούς διαγωνισμού … | — | ⚠ |


## ADAs Pending Hydration

Run to fetch next batch:
```bash
python scripts/hydrate_candidate_details.py --org 6166 --limit 100
```

| Pri | ADA | Score | Type | Subject |
|----:|:----|------:|:----|:--------|
| 1 | `94ΨΚΩΛΚ-Χ95` | 7 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Έγκριση 1α Πρακτικού ηλεκτρονικού ανοικτού διαγωνισμού ΠΡΟΜΗΘΕΙΑ ΕΞΟΠΛΙΣΜΟΥ ΠΟΛΙ… |
| 2 | `ΡΕ5ΨΩΛΚ-Ξ77` | 6 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Μετάθεση καταληκτικής ημερομηνίας ηλεκτρονικού ανοικτού διεθνούς διαγωνισμού Ανά… |
| 3 | `9ΞΕ6ΩΛΚ-Κ9Φ` | 5 | ΚΑΝΟΝΙΣΤΙΚΗ ΠΡΑΞΗ | Έγκριση 2ου Πρακτικού ηλεκτρονικού ανοικτού διεθνούς διαγωνισμού Προμήθεια ηλεκτ… |


## Hydrated Decision Details

_2 high-value decisions with full raw JSON data, sorted by intelligence score._

### [`Ψ8ΣΝΩΛΚ-1ΤΜ`](https://diavgeia.gov.gr/doc/Ψ8ΣΝΩΛΚ-1ΤΜ) — Score 12

**Type:** ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣΙΩΝ / ΜΕΛΕΤΩΝ  
**Date:** 2026-01-22  
**Protocol:** 54823  
**Subject:** ΠΑΡΟΧΗ ΑΝΕΞΑΡΤΗΤΩΝ ΥΠΗΡΕΣΙΩΝ ΕΣΩΤΕΡΙΚΟΥ ΕΛΕΓΧΟΥ  
**Award:** €18,600.00 EUR  
**Assignment type:** Υπηρεσίες  
**Signer IDs:** 100084274  

**Suppliers:**
  - AFM `801382949` — ΕΣΩΤΕΡΙΚΟΣ ΕΛΕΓΧΟΣ ΜΟΝΟΠΡΟΣΩΠΗ Ι Κ Ε

### [`901ΓΩΛΚ-ΓΙΣ`](https://diavgeia.gov.gr/doc/901ΓΩΛΚ-ΓΙΣ) — Score 10

**Type:** ΑΝΑΘΕΣΗ ΕΡΓΩΝ / ΠΡΟΜΗΘΕΙΩΝ / ΥΠΗΡΕΣΙΩΝ / ΜΕΛΕΤΩΝ  
**Date:** 2026-01-15  
**Protocol:** 2/1/2026 Α.Δ.Ε.  
**Subject:** Εντολή και πληρεξουσιότητα σε δικηγόρο για σύνταξη γνωμοδοτικού σημειώματος ΓΑΚ 4191/2025 & ΕΑΚ 2188/2025  
**Assignment type:** Υπηρεσίες  
**CPV:** 79100000-5  
**Signer IDs:** 100085865  

**Suppliers:**
  - AFM `129992517` — ΛΙΑΝΟΥΛΟΠΟΥΛΟΣ,,ΓΕΩΡΓΙΟΣ,ΑΛΕΞΙΟΣ
  - AFM `997947640` — ΔΗΜΟΣ ΛΑΜΙΕΩΝ


## Known Data Caveats

- **AFM 997947640 (ΔΗΜΟΣ ΛΑΜΙΕΩΝ)** appears as 'supplier' in ΟΡΙΣΤΙΚΟΠΟΙΗΣΗ ΠΛΗΡΩΜΗΣ records — it is the municipality's own AFM captured from the `org` field, not the actual payee. True payees live in `extraFieldValues.sponsor[].sponsorAFMName`.
- **Amount extraction is sparse.** Most amounts are only in raw JSON `extraFieldValues.awardAmount` and are not surfaced in search-level exports.
- **Historical years are search-only.** Hydration coverage is thin outside the hydrated months; trend analysis across years has low reliability.
- **Payroll / admin decisions contaminate procurement rows.** Apply the score filter to reduce noise before analysis.
- **`privateData: true` decisions** involve natural persons; supplier identity is legally protected and full names are redacted in Diavgeia.
- **Supplier names missing** for most rows. Resolve via ΓΕΜΗ business registry or ΑΑΔΕ cross-reference using the AFM.
- **AFMs in scientific notation** (e.g., `1.29993e+08`) are normalised to integers by this script, but source data should be re-extracted as integers at collection time.


## Next Steps — MVP Loop

```bash
# 1. Hydrate the next batch of high-value ADAs
python scripts/hydrate_candidate_details.py --org 6166 --limit 100

# 2. Rebuild normalized tables from latest search exports
python scripts/build_normalized_tables.py --org 6166

# 3. Rebuild dossier with newly hydrated data
python scripts/build_intelligence_dossier.py --org 6166
```
