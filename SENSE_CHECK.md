# Sense Check — how solid is each learning, really?

Written 2026-08-13. Every major claim traced to its evidence; the retraction log
examined for patterns; the plan stress-tested against both.

---

## 1. The claims, tiered by what actually supports them

### TIER A — bet-the-article on these (document-proven, independently reproducible)

| claim | evidence |
|---|---|
| `from_issue_date`/`to_issue_date` reaches full history; ~6mo is a **max span per query**, not a recency cap | verified live repeatedly; server-echoed queries; clamping reproduced |
| Per-ADA retrieval works for arbitrarily old records | Nov-2024 ADA fetched live |
| **16 ×100 amount errors at Rhodes** (€47.05M phantom) | 49 outliers PDF-checked; amounts stated *in words* on signed warrants; 2 apparent errors proven genuine (SIEMENS) — the detector was tested in both directions |
| **2 ΑΦΜ-in-amount errors** (€895M phantom) | digit-for-digit identity with supplier tax IDs; GE record re-fetched live |
| Empty-payee records DO name the payee in the source PDF | every parseable doc in a 14-record stratified sample |
| The Β.2.1 layer contains ≥1 ×100 error (€2,559,126 → €25,521.96) | PDF-proven (WALLS/overtime) |
| Extraction pipeline reproduces hand-classification | Aug/Sep 2025: match **to the cent** on both months |
| Monthly run-rate stable across independent collections | €1,219,993 vs €1,217,609/mo — 0.2% apart |

Note what Tier A is: **mechanics and documents.** Nothing here has ever reversed.

### TIER B — solid with one named caveat each

| claim | caveat |
|---|---|
| Corrected Rhodes 5yr total **€82.0M** | a *floor*: understatement is undetectable by design; whole-euro errors <€50k unscreened (€4.6M habitat) |
| **Lamia is clean** | statistical signature only, **zero PDF checks**; screens detect overstatement only |
| Field-completion gap **by count**: 2,503 empty-payee records (Rhodes) vs 8 (Lamia) | counts are trustworthy; *values* are not (see Tier C) |
| KAE exists in PDF when JSON field empty (~73%) | n=22, sample biased toward large payments; 2 parse-fails in a third layout |
| Operational similarity Rhodes↔Lamia (same categories, same suppliers, ~30% growth) | computed on KAE-coded subsets; Rhodes 21% uncoded |
| Threshold clustering identical in aggregate (1.21 vs 1.25) | payments ≠ awards |

### TIER C — indicative only; DO NOT publish without upgrade

| claim | why it's soft | upgrade path |
|---|---|---|
| Anonymity **value** (€35.6M / 28.8% / 25.0%) | numerator contains ≥1 proven ×100 error and was never amount-screened | B21 whole-euro screen + glossAPI cross-check |
| All-value per-bed "**within 1%**" (73,719 vs 74,520) | false precision — includes the contaminated B21 amounts; removing just the one proven phantom moves it to ~3% | say "within a few percent" until B21 is screened *(patched in docs today)* |
| Per-destination structuring (3 suppliers, 45–71% near-ceiling) | VAT-permissive test; MY SERVICES flag likely dissolves at its real 24% rate; only ΤΕΧΝΙΚΗ is clean | award PDFs (~50 docs) |
| Single-bid direct awards "3 of 5" | n=5 | full Β.2.1 pass |
| **2026 KAE collapse (99% uncoded)** | coincides with a new record format — **this could be OUR parser missing a relocated field**, the exact class of bug we've already made twice | hand-check 3 × 2026 records JSON-vs-PDF before ever citing |
| DDQI as a *national* ranking | validated on exactly the 2 hospitals it was built from — circular until tested on fresh ones | spot-validate 2–3 mid-rank hospitals from the batch |
| Security/per-bed/per-category comparisons | name-matching + external bed counts of different vintages | publish totals primarily |
| Pharma share collapse 47%→14% | unexplained; three hypotheses untested | targeted look |

## 2. The retraction log — 12 corrections, 4 patterns

We reversed ourselves on: the "6-month hard wall" (twice), "OCR corpus needed for
history", ATRON at 11.3% (→3.5%), "×100 stopped after 2023", the 2–6× anonymity ratio,
"€35.6M is hidden money", "Lamia hides payees differently", supplier count 895 (→729),
"no structuring signal", the 400MB storage plan (→30MB), "errors likely portal-wide",
plus three near-miss parser bugs (E7 truncation, mojibake nulls, grep truncation).

Every one of the twelve falls into four failure modes:

1. **Small-window extrapolation** (ATRON, "stopped after 2023", single-bid n=5)
2. **Parser null read as world null** (mojibake "no supplier", empty organizations.json)
3. **Aggregation masking** (no-structuring-in-aggregate, supplier name/ΑΦΜ key)
4. **Unverified assumption about the platform** (6-month wall, storage projection, "portal-wide")

**The reassuring pattern:** Tier A never churned. Every retraction was an
*interpretation*; every survival was a *document*. Our epistemic ratchet works —
claims only ever moved toward the PDFs, never away. The churn isn't a sign the
learnings are weak; it's the mechanism that made them strong. But it also means:
**anything not yet document-anchored should be presumed wrong in some detail.**

## 3. Plan stress-test against those four failure modes

| plan element | verdict |
|---|---|
| Gate 4 random-sample audit as critical path | ✅ **exactly the antidote** to modes 1 & 4 — the plan's core is sound |
| DDQI national ranking (output A) | ⚠️ mode 1 risk: index validated only on its own 2 training hospitals. **Add: validate on 2–3 fresh mid-rank hospitals before publication** |
| "Ευαγγελισμός cross-check" | ✅ right instinct — catches discovery gaps (mode 4) |
| glossAPI as verification shortcut | ⚠️ mode 2 risk (RapidOCR nulls) — script already treats parse-fail ≠ absence; also run `--coverage` before relying on it |
| Naming decision deferred | ⚠️ still open; must close at Gate 4 |
| Tiered depth (12mo national / 5yr top-20) | ✅ sound; current top-50 run is harmless surplus |
| Fix-ask (2 validation rules) | ✅ rests entirely on Tier A — the strongest possible footing |

**Net verdict: the plan survives its own history.** The destination and gates are
right; the critical path (random audit) is precisely the correction mechanism our own
errors prove necessary. Three amendments needed, none structural:

1. **Before Gate 3 outputs:** screen the Β.2.1 layer for amount errors (it feeds the
   anonymity value, the all-value-per-bed figure, and the DDQI payee component — three
   published numbers currently inherit one unscreened layer).
2. **Add to Gate 3:** hand-verify the 2026 format change (3 records, JSON vs PDF)
   before citing the "99% uncoded" regression.
3. **Add to Gate 3:** DDQI out-of-sample validation on hospitals it wasn't built on.

## 4. The one-sentence versions

- **What we know:** Diavgeia's machine-readable layer materially contradicts its own
  signed documents at ΓΝ Ρόδου — 18 proven records, ~€942M phantom value, error classes
  ongoing into 2025 — while a peer hospital on the same platform shows none of it, and
  the full history needed to prove all this is retrievable despite the documented
  "6-month limit".
- **What we believe but haven't proven:** the value-weighted anonymity figures, the
  structuring interpretation, the 2026 regression, and every per-bed number.
- **What we've learned about ourselves:** we make the same four mistakes repeatedly;
  the plan's audit gate exists because of that, and must not be traded away for speed.
