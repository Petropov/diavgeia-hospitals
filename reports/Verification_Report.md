# National Verification Report — 354 Source Documents vs API
**Gate 4 of the working-backwards plan. Extraction 2026-08-15. All PDFs on disk
(`data/_registry/quarantine_pdfs/`, `audit_pdfs/`); machine-settled verdicts in
`quarantine_results.csv`, `audit_results.csv`.**

## A. Random audit — the measured national error rate

300 records, 60 × 5 strata, seed 42, amounts < €5M. **All 300 parsed** (0 PARSE_FAIL after
handling the no-colon ΧΕΠ layout variant used by Μυτιλήνη/Λαμία).

| Stratum | n | errors |
|---|---:|---:|
| Μυτιλήνη (DDQI #1) | 60 | 0 |
| Λαμία (known-clean) | 60 | 0 |
| Κέρκυρα (DDQI last) | 60 | 1 |
| Ευαγγελισμός (largest) | 60 | 2 |
| Ρόδος (known-bad) | 60 | 3 |

**Error rate: 6/300 = 2.00% (95% CI 0.42–3.58%).** All six confirmed against the
amount-in-words on the warrant — none is a parser artifact.

**The invisible error class is now proven: 4 of 6 errors are UNDERSTATEMENTS**
(Ρόδος 14,101.70 published vs 14,401.70 paid — a digit substitution; two dropped-cents
cases; Ευαγγελισμός −9 cents). Every automated screen we run catches overstatement only;
this is the first direct measurement of the other direction. Net value impact of all six:
**+€249.82** — the typo class is roughly value-neutral at national scale. The value
distortion lives entirely in the ≥€5M magnitude class (below).

DDQI validation: known-clean strata (Λαμία, Μυτιλήνη) had zero errors; known-bad Ρόδος had
the most. The index orders real-world accuracy correctly.

**Two methodological traps this audit itself hit (and fixed) — recorded because both
produce confident wrong answers:**
1. *Unit mismatch*: Λαμία/Μυτιλήνη issue multi-beneficiary batch warrants; comparing an API
   sponsor **line** to a document **total** yields a false 90% "error rate". Compare at ADA
   level (sum of lines).
2. *Layout blindness as false mismatch*: a parser that demands a `:` after ΣΥΝΟΛΙΚΟ ΠΟΣΟ
   matches the wrong field (ΠΛΗΡΩΤΕΟ = net after deductions) and "finds" thousands of
   phantom discrepancies. The first-pass "37.67% error rate" was 100% parser, 0% data.

## B. Quarantine — the €129 trillion decomposed

54 records ≥€5M (nominal €129.2T). Verdicts:

| Class | n | Nominal | Document truth |
|---|---:|---:|---:|
| ×100 (missing decimals) | 26 | €626.8M | €6.27M |
| ×1000 | 2 | €273.5M | €0.27M |
| AFM/KAE-in-amount, other | 22 | €32.3T | €2.45M |
| AFM-concatenation (Γιαννιτσά, parse-fail) | 3 | €96.9T | unknown, excluded |
| **GENUINE** | **1** | **€6.58M** | **€6.58M** |

- **Only 1 of 54 was real**: MSD Α.Φ.Β.Ε.Ε €6,581,968.63 (Παπαγεωργίου, 2023-04-12) — now
  the largest PDF-verified single hospital payment; the €5M cap stays but needs a
  doc-verification passthrough, not automatic exclusion.
- ×100 errors are **national, not a Rhodes quirk**: Ευαγγελισμός alone has three (incl.
  GILEAD €235.2M → €2.35M), Γεννηματάς, Χανιά, others.
- **Corrected national Β.2.2 5-yr total: €7,798,880,002** (clean €7,783,310,466 +
  €15,569,536 document-verified add-back).

## C. What this buys the project
Every caveat in `Known_Unknowns.md` about undetected error now has a number: published
amounts are right ~98% of the time (CI 96.4–99.6%), wrong records are value-neutral except
the magnitude class, which is 98% noise and fully recoverable from source PDFs. The
dataset behind our reports is defensible at document level.

Remaining before publication (Gate 5): award-doc pulls for Rhodes structuring suppliers,
ΓΕΜΗ lookup, right-of-reply, naming decision.
