# Hospital Procurement Transparency: ΓΝ Ρόδου vs ΓΝ Λαμίας

Comparison of Diavgeia transparency-portal data for two Greek public hospitals, built on the corrected classification logic validated this session (see `diavgeia-pipeline-lessons.md`: budget-ceiling phrases in subject lines are never used as transaction amounts; only structured JSON fields are trusted).

## Scope mismatch — read this before the numbers

The two datasets are still **not the same depth**, though the Rhodes side is now far stronger than the original draft of this report:

- **ΓΝ Λαμίας (org 99221923):** the repository's full corrected historical dataset (multi-year, tens of thousands of decisions), rebuilt this session after fixing the budget-phrase contamination bug.
- **ΓΝ Ρόδου (org 99221940):** **the complete sampled window** — 4,392 decisions across pages 1–186, confirmed exhausted (page 186 returned zero results). This is not a partial slice anymore; it is every decision Diavgeia's opendata API exposes for this org, which is itself capped at roughly the last 6 months by a hard limit in Diavgeia's own API — a platform ceiling, not a choice made here.

Any "X vs Y in euros" comparison below is still a comparison of a full multi-year history (Lamia) against one complete recent ~6-month window (Rhodes) — a smaller hospital sampled over a shorter period could look smaller than a larger hospital sampled over years, independent of actual scale. The Rhodes figure is no longer an extrapolation or a small-sample estimate, but it does cover less calendar time than Lamia's.

## What's reliably comparable

| | ΓΝ Λαμίας (full history) | ΓΝ Ρόδου (complete ~6-month window, 4,392 decisions) |
|---|---|---|
| Supplier-anonymous payment records | ~64% of awards publish no supplier identity (prior finding, `diavgeia-pipeline-lessons.md`) | Same structural gap confirmed at full scale: `Β.2.1` payment-warrant (`ΧΕ`) records carry a real amount but a structurally empty `sponsorAFMName: {}` throughout the entire window — recurring in nearly every round sampled, from the first pages through the last |
| Known suppliers in clean data | 277 distinct AFMs identified after the fix | Well over 100 distinct named suppliers identified with genuine Β.2.2 payments across the full window (not yet deduplicated into a single master list, but the growth log in `Rhodes_Hospital_Sample_Note.md` has every one logged page-by-page) |
| Genuine large single-item purchases exist | Yes — verified: €1.49M osteosynthesis (ADA 9ΗΘΩ4690ΒΜ-Π7Ω), €841k neurosurgical supplies (ADA 9ΠΒΦ4690ΒΜ-ΔΟΟ) | Largest verified single Β.2.2 payments found: €300,036.05 (ΜΠΑΞΤΕΡ ΕΛΛΑΣ / BAXTER, pharmaceuticals), €265,113.56 and €165,348.75 (two separate ATRON HEALTH ΑE orders), €171,764.81 (fuel, ΕΛΛΗΝΙΚΑ ΚΑΥΣΙΜΑ). No single Rhodes payment reaches Lamia's seven-figure outliers, but Rhodes also has no equivalent multi-year window to search for one |
| Budget-reallocation / recall entries that must be excluded from spend totals | Confirmed pattern (source of the original inflation bug) | Same pattern, confirmed at full scale and much larger in the later window: `recalledExpenseDecision: true` rows including a very large multi-KAE prior-year-debt reconciliation series in pages 162–186 (individual entries up to €4.78M) — all correctly excluded from the verified-payments total for the same reason as Lamia |
| Supplier concentration | 277 distinct AFMs, no single-supplier concentration finding published | **ATRON HEALTH ΑE (AFM 800519113)** alone accounts for ≈11.3% of the entire Rhodes verified-payments total (€827,365.78 of €7,305,654, across 5 distinct payments) — see the dedicated deep-dive in `Rhodes_Hospital_Sample_Note.md` |
| Granular procurement pipeline structure | Committee/evaluation stage often precedes award; `Δ.2.2`-type records frequently show empty `person: []` / null `awardAmount` mid-process | Same structure confirmed throughout: the large majority of `Δ.2.1`/`Δ.2.2` records across the full window are procurement-request/administrative steps with no supplier or amount yet — this is the hospital's normal requisition workflow, not a data gap |

## The Rhodes verified-payments total

**≈ €7,305,654** in genuine Β.2.2 payments (real named supplier + populated expense amount, all exclusion rules applied consistently: anonymous `ΧΕ` records, self-referential payroll/ΕΦΚΑ/ΦΜΥ remittances, recalled corrections, and Β.1.3 budget commitments all excluded) across the **complete** 4,392-decision sampled window (pages 1–186 of Diavgeia's ~6-month opendata cap for org 99221940).

Plus a separate, smaller list of completed Δ.2.2 awards tracked outside this total because they weren't confirmed as paid within the window: ΑΛΚΟΝ ΛΑΜΠΟΡΑΤΟΡΙΣ ΕΛΛΑΣ (€235,600.00), TRANE ΕΛΛΑΣ ΑΕ (€199,553.20), ΛΙΒΑΣ ΧΡΗΣΤΟΣ ΙΩΑΝΝΗΣ (€26,600.00), Κ.ΤΕΛΙΔΗΣ ΑΕ (€1,600.00) — ≈€463,353.20 combined.

## What this does NOT support

- A ranking of "which hospital spends more" or "which hospital is more opaque" — Lamia's figure covers years, Rhodes covers one ~6-month window; a full-year or multi-year Rhodes figure isn't available because Diavgeia's own API doesn't expose it.
- Any fraud/anomaly-detector scoring for Rhodes (the kind used in the Lamia assessment) — that would require running the same structured pipeline/heuristics used on Lamia against this now-complete Rhodes dataset, which hasn't happened yet (this report was built from a manual decision-by-decision classification log, not the automated pipeline).

## Honest bottom line

Both hospitals show the same two structural transparency gaps on Greece's Diavgeia platform: a meaningful share of real payments publish amounts without supplier identity, and multi-stage procurement workflows mean early-stage decisions legitimately lack award data until a later decision fills it in. Both patterns hold up at full scale on the Rhodes side now, not just in a small sample — reinforcing that this is a platform-level or ministry-level transparency design gap, not a single hospital's collection failure. Rhodes additionally shows a concrete, quantified supplier-concentration finding (ATRON HEALTH ΑE at ~11.3% of total verified spend) that Lamia's dataset hasn't been checked for yet. A true euro-for-euro comparison between the two hospitals would still require either extending Rhodes's window backward (not possible via the live API) or narrowing Lamia's history down to a matching 6-month slice.
