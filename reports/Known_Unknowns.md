# Known Unknowns — errors we cannot see, and the risk of not reporting them

Companion to `Fraud_Risk_Assessment.md`. That document lists what we found. This one lists
what our methods **cannot find**, sized where possible. It exists because every PDF
verification in this project was **targeted at statistical outliers** — we have *never*
verified a random sample of ordinary-looking records, and therefore **we have no measured
base error rate**. Any implication that "the rest of the data is fine" is unsupported.

## 1. The detection asymmetry (most important)

Every screen we built detects **overstatement**: whole-euro outliers, mean/median blowouts,
amounts ≥ thresholds. None detects **understatement**:

- A ÷100 error (€18,590 typed as €185.90) produces a small, cents-bearing, perfectly
  ordinary-looking payment. **Invisible to every test we ran.**
- ×10 errors: any amount with cents ×10 still has a cents-like ending (1,234.56 → 12,345.60).
  **Invisible** — our signature only catches ×100 (which forces .00 endings).
- Plausible-but-wrong amounts (12,500 vs 12,900): statistically undetectable in principle.

Consequence: our "corrected" totals are corrected **downward only**. If under-entry errors
exist at anything like the rate of the 16 proven over-entry errors, true spend is *higher*
than reported — and we would systematically not report it.

## 2. Sized blind spots (measurable, unverified)

| blind spot | Rhodes | Lamia | why unverified |
|---|---|---|---|
| Whole-euro payments €1k–50k — the habitat of ×100 errors whose true value is <€500 | 567 pmts, €4.57M (5.6%) | 1,341 pmts, €7.42M (6.4%) | below our €50k screen; PDF-checking 1,900 docs wasn't done |
| Same supplier + same amount + same day, different ADA | 38 groups, €691k at stake | 109 groups, €602k | we ruled "different ADA = genuine" from ONE verified pair; monthly instalments and true duplicates look identical |
| Rhodes Β.2.1 layer (€35.6M) | never amount-screened; contains ≥1 proven ×100 error (€2.56M→€25.5k) and 6 more whole-euro ≥€50k (€3.1M) | n/a | discovered late; only 14 of 2,503 PDFs read |
| Negative amounts silently excluded | −€44k…−€57k (various) | **−€1.35M** | credit notes/reversals never netted; totals overstate by up to this much |
| `correctedVersionId` ignored | unknown | unknown | our pipeline keeps the version the search returned; superseded amounts may be counted |
| `privateData:true` records | present, uncounted impact | present | content restrictions may hide amounts/payees |

## 3. Structurally invisible (cannot be sized from Diavgeia at all)

1. **Omission** — payments never posted to Diavgeia. We measure the published subset; the
   unpublished remainder is *definitionally* invisible here. Only reconciliation against the
   hospitals' financial statements (απολογισμοί, Court of Audit filings) bounds it. Our
   five-year totals (€123.5M / €118.5M) are plausible for ~320-bed hospitals, but 10–15%
   missing would not be distinguishable.
2. **Wrong supplier attribution** — a valid-but-incorrect ΑΦΜ passes every check we have.
   Concentration figures, supplier rankings and the structuring screen all inherit this risk.
3. **Net-vs-gross inconsistency** — if some records post net-of-VAT amounts, category and
   hospital comparisons are silently distorted; nothing in the JSON marks which convention
   a record used.
4. **Lamia's clean bill of health** — rests on statistical signatures plus **zero** PDF
   verifications. Its 39 whole-euro ≥€50k flags are unverified; error classes without a
   whole-euro signature (÷100, ×10, wrong-amount) were never tested for at all. "Lamia is
   clean" should be read as "Lamia shows no signature our screens detect."

## 4. Errors in *our* pipeline that nearly shipped (and what they imply)

These are documented because each was caught late or by luck — implying siblings weren't:

- The regex that truncated `9.4472918E7` to €9.45 (caught only because the value looked odd).
- "No supplier found" on mojibake PDFs — a parser null read as a real-world null; it briefly
  *supported* the concealment narrative before being disproven.
- The 2–6× anonymity ratio (misattributed console output between two runs).
- ATRON at 11.3% (short-window artifact), supplier count 895 vs 729 (aggregation key bug).

Four self-corrections in one project is a good catch-rate only if the detection was
systematic. It wasn't — two were luck. Assume at least one comparable error remains.

## 5. What honest reporting requires

1. **State the asymmetry**: totals are corrected for overstatement only; understatement is
   untested. Never present €82.0M / €116.3M without this caveat.
2. **Run the missing experiment — a random-sample audit**: ~60 randomly selected records
   per hospital, PDF-checked. With 0 errors found that yields a ~95% upper bound of ~5% on
   the record-level error rate; any errors found give an actual rate to publish. This is
   the single cheapest way to convert "we found 18 errors we went looking for" into "the
   data is X% reliable," and it directly tests Lamia's clean verdict.
3. **Net the negatives** (−€1.35M at Lamia) or state their exclusion.
4. **Reconcile one year against the απολογισμός** of each hospital to bound omission.
5. **Report the blind-spot table (§2) alongside the findings table** — the reader must see
   both what was found and where nobody looked.

The deeper point for the Public Tech thesis: our own experience reproduces, in miniature,
exactly the institutional failure we documented at Rhodes. Errors were found only where
someone thought to look; everywhere else, absence of evidence quietly became evidence of
absence. The only structural fix — for us and for the ministry — is *randomized*
verification against source documents, not outlier-chasing.

## 6. The Crete gap — structural payment-layer silence (probed 2026-08-15)

The national dataset's largest known omission is not an error but a publishing choice.
Both Heraklion hospitals — ΠΑΓΝΗ (99222010, Crete's largest) and Βενιζέλειο (99221997),
which operate under a joint administration — publish **zero payment-execution records**
(Β.2.2 and Β.2.1 both = 0), while remaining otherwise highly active on Diavgeia. ΠΑΓΝΗ in
5 recent months: 3,732 decisions, of which 1,450 award decisions (Δ.2.2) and 439 budget
commitments (Β.1.3, including single entries of €11.8M) — procurement fully visible, money
out completely dark. Other Cretan hospitals (e.g. Χανιά) do publish Β.2.2, so this is an
institutional practice of the two linked Heraklion hospitals, not a regional or platform
rule.

Consequences: (a) our €7.80B national Β.2.2 total structurally understates Greece — likely
by hundreds of millions over 5yr given ΠΑΓΝΗ's size; (b) DDQI cannot even be computed for
them — silence outranks bad data in evading measurement, the extreme case of the §2
detection asymmetry; (c) partial recovery is possible: Βενιζέλειο's Β.1.3 subjects embed
supplier name, ΑΦΜ and contract amount, so a commitment-layer reconstruction is feasible
if ever needed. For any national publication, ΠΑΓΝΗ/Βενιζέλειο must be listed as
"non-reporting at the payment layer", not silently absent.
