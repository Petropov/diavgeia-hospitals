# Fraud & Integrity Risk Assessment — ΓΝ Ρόδου vs ΓΝ Λαμίας
**Basis:** matched 5-year Diavgeia payment datasets (Aug 2021–Aug 2026), Rhodes corrected
against source PDFs, Lamia verified clean. Extraction 2026-08-11.

> **Framing.** Nothing here is a finding of fraud. It is a risk assessment: confirmed
> data-integrity failures, plus unverified indicators ranked by how much they warrant
> document-level follow-up. Payment data alone cannot prove impropriety — but it can say
> precisely where to look.

---

## 1. Risk matrix

| # | Signal | Hospital | Status | Risk reading | Resolves via |
|---|---|---|---|---|---|
| 1 | ×100 amount errors (16 rec., €47.0M phantom) | Rhodes | **CONFIRMED** vs PDFs | Integrity failure, error not fraud — but shows nobody reconciles published data | fixed in our dataset; institutional fix pending |
| 2 | ΑΦΜ typed into amount (2 rec., €895M phantom) | Rhodes | **CONFIRMED** | same | same |
| 3 | Payee field empty on 2,503 records | Rhodes | **CONFIRMED** (payee *is* in PDFs) | Machine-readability failure; defeats automated oversight, whether or not intended | bulk PDF extraction |
| 4 | Per-destination near-ceiling structuring: 3 suppliers, 45–71% of their revenue in band 10% under €30k net; ~€2.3M | Rhodes | **RESOLVED — award docs read 2026-08-15 (§5)** | Structuring hypothesis **rejected** for all 3: near-ceiling payments are monthly instalments of tendered contracts. Residual risk relocated: MYSERVICES sole-bidder pattern | — |
| 5 | Eponymous supplier ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣ. ΡΟΔΟΥ: €2.15M, 28× at €28,200 net, rising yearly, 46% of its payments uncoded | Rhodes | **RESOLVED (§5)** | Eponymy dissolved: ERP vendor label (code 2184) for the ΚΑΡΑΝΤΩΝΗΣ–ΠΑΠΑΔΟΥΛΗΣ consortium; electromechanical maintenance under tender 31/2024, contract 1042/2024 (8/2024–7/2026) | optional: verify tender 31/2024 bid count in ΚΗΜΔΗΣ |
| 6 | Single-bid direct awards on high-cost drugs (3 of 5 sampled) | Rhodes | **INDICATOR** (n=5) | Plausibly structural (sole distributors); unmeasured baseline | full Β.2.1 PDF pass; compare Lamia |
| 7 | Supplier name fragmentation (MYSERVICES under 5 names) | Rhodes | CONFIRMED pattern | Defeats name-based monitoring; ΑΦΜ-level dedup required (done here) | — |
| 8 | 2026 regression: 99% of spend uncoded (was 14%) | Rhodes | **CONFIRMED, ONGOING** | Whatever workflow changed this year, category oversight is now blind | ask the hospital; monitor |
| 9 | Guarding spend halved after 2022 (€923k→€370k) | Rhodes | Unexplained | Could be good news (renegotiation) or displaced spend | contract history |
| 10 | Supplier concentration | both | measured | **Low risk** — HHI 202/329, no capture | — |
| 11 | Aggregate threshold clustering | both | measured | **Low risk** — identical 1.2–1.4 ratios | — |
| 12 | All of the above at Lamia | Lamia | screened | **Low across the board**: 0 amount errors, 0.8% payee-empty, near-ceiling payments incidental (11–13% of flagged suppliers' revenue) | — |

**Overall:** Lamia — low. Rhodes — no confirmed impropriety, but **three overlapping
medium-strength indicators (#4, #5, #6) concentrated in the same corner: recurring
service/supply relationships transacted just under the direct-award ceiling**, inside a
record-keeping environment (#1–#3, #8) that materially weakens after-the-fact oversight.
That *combination* — weak records + threshold-adjacent recurring spend — is the classic
setting in which procurement abuse persists undetected, and equally the classic setting in
which honest sloppiness looks suspicious. Only the award documents distinguish the two.

## 2. Why the data-integrity failures matter for fraud risk (even as innocent errors)

The ×100 and ΑΦΜ errors are almost certainly typos. Their significance is what they prove:
**no one — not the portal, not the ministry, not the hospital — reconciles the published
figures against source documents.** A €94M phantom payment stood uncorrected for years. An
environment that cannot detect a €94M accident cannot detect a €50k deliberate one. Lamia
shows the same platform run with discipline; the control weakness is institutional, not
systemic.

## 3. Comparable figures — €/bed/year (full years 2022–2025)

Rhodes 335 beds, Lamia 318 (external, imperfect counts). "adj" scales Rhodes for its 21%
uncoded spend (assumes uncoded distributes like coded — upper bound).

| category | Rhodes | Rhodes adj | Lamia | Rhodes/Lamia (adj) |
|---|---:|---:|---:|---:|
| Pharmaceuticals | 16,859 | 21,337 | 22,680 | **0.94** |
| Medical supplies | 5,709 | 7,225 | 9,533 | 0.76 |
| Special med. materials | 3,067 | 3,881 | 2,744 | **1.41** |
| Lab reagents | 2,228 | 2,820 | 5,068 | 0.56 |
| Cleaning/facilities | 1,985 | 2,513 | 4,619 | 0.54 |
| Equipment maintenance | 890 | 1,126 | 2,019 | 0.56 |
| External services | 1,068 | 1,352 | 4,225 | **0.32** |
| Security (CPV/name-matched) | 1,608 | — | 1,227 | **1.31** |
| Fuel/energy | 1,445 | 1,829 | 199 | 9.2* |
| **All Β.2.2** | **49,389** | — | **74,600** | 0.66 |
| **All payment value (Β.2.2+Β.2.1, 5yr)** | **~73,700*** | — | **74,520** | **~0.97–0.99** |

\* Rhodes' Β.2.1 amounts are unscreened for ×100 errors (≥1 proven: €2.56M → €25.5k), so
this figure carries more uncertainty than the corrected Β.2.2 numbers. "Near-parity"
holds; the second decimal does not. See `SENSE_CHECK.md`.

\* fuel ratio overstated by coding differences — Lamia's natural gas and medical gases sit
in other codes; the direction (island fuel premium) is real, the magnitude isn't clean.

**Readings:**
- **Medical core is comparable.** Pharma per bed is within 6% once Rhodes' uncoded share is
  allowed for. The clinical operation costs what it costs, in both places.
- **Rhodes runs 1.4× on special medical materials** (implants/orthopedics family) — worth a
  clinical read (trauma/tourism case-mix?) before any procurement read.
- **Lamia buys far more outsourced services per bed** (external services 3×, cleaning 2×,
  equipment maintenance 2×) — *visible in coded data*. Some of Rhodes' service spend hides
  in its uncoded/Β.2.1 layers, so this gap is partly real, partly recording.
- **Rhodes pays ~31% more per bed for security** — the one service category where it
  out-spends Lamia, purchased from the supplier with the weakest paper trail (#4, #7).
- **Total payment value per bed is within 1%.** The institutions cost the same; they
  *account* differently. Category-level per-bed comparisons between Greek hospitals are
  only meaningful after correcting for field-population differences — which is itself a
  finding for anyone attempting national benchmarking.

## 5. Award-document verification (2026-08-15) — flags #4/#5 resolved

22,199 Δ-category decisions pulled (5yr); 296 matched; 54 priority PDFs read
(`data/99221940/award_pdfs/`, worklist `award_pdfs_priority.csv`). Verdict per supplier:

**ΑΦΟΙ ΚΟΜΠΑΤΣΙΑΡΗ (catering, €1.46M) — CLOSED.** Open electronic tender *above* EU
thresholds, lowest-price criterion, signed contract 65/2024; the €527k option year was
exercised by formal board decision (631Ω46907Κ-ΦΔ2), and the decision records that the
tender file and contract passed external audit. Near-ceiling payments = monthly instalments.

**ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣ. ΡΟΔΟΥ (€2.15M) — CLOSED as eponymy/structuring; reframed.**
Not a company: the hospital ERP's vendor label for the ΚΑΡΑΝΤΩΝΗΣ–ΠΑΠΑΔΟΥΛΗΣ consortium
(Αγίων Αναργύρων 76, Ρόδος), providing electromechanical maintenance. Warrants reference
tender file 31/2024 and contract 1042/2024 (1/8/2024–31/7/2026), preceded by contracts
ΧΕ 1263/21 and ΧΕ 1557/2023 with option-year extensions — a procurement chain, not serial
direct awards. Residual note: same incumbent continuously since ≥2021; competitiveness of
the underlying tenders (bid counts) not yet verified.

**MYSERVICES (3 ΑΦΜs, €1.9M) — flag TRANSFORMED, not closed.** Procedures exist but
competition repeatedly fails: the 27/2020 international open tender (ΕΣΗΔΗΣ 90095)
was derailed by pre-judicial appeals (ISS et al.) and cancelled; the fallback simplified
tender 91/2021 drew **exactly one bid — MY SERVICES — which won**; the 2026 laundry
tender 784/2026 again shows a **sole bidder — MYSERVICES — which won** (Ψ2Ω846907Κ-ΗΕ9).
The 67/2024 cleaning tender had multiple bidders but all offers were rejected at a stage;
91/2025 re-ran. So the correct finding is not threshold structuring but **persistent
single-bidder outcomes on an island market while above-threshold tenders stall** —
combined with the supplier's 3-ΑΦΜ fragmentation, this stays a monitoring item: compare
its unit prices against Λαμία's UNISON contract and check ΕΣΗΔΗΣ bid histories.

**Net effect on the overall assessment:** the "weak records + threshold-adjacent recurring
spend" combination flagged in §1 is downgraded — the recurring spend is contracted and
tendered. What remains is a *market-thinness* risk (one credible bidder for services on
Rhodes), which is a procurement-policy problem, not an integrity indicator against the
hospital.

## 4. Priority actions (cheapest decisive evidence first)

1. **Pull ~50 award decisions** behind the three near-ceiling suppliers (#4/#5): one
   tendered contract each → close the flag; serial direct awards → escalate.
2. **ΓΕΜΗ ownership lookup** on ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ (ΑΦΜ 997563888) —
   an afternoon's work, resolves the eponymy question.
3. **Bulk Β.2.1 PDF pass** (2,503 docs): corrected anonymity figure, single-bid rate,
   ×100 screen on the layer never checked.
4. **Ask about 2026**: what changed in the payment workflow that stopped budget-code
   publication (#8).
5. Extend the same pipeline to the other 2η ΥΠΕ island hospitals (99221913/20/42/46) — turns
   Rhodes-vs-Lamia contrasts into a distribution, the difference between anecdote and
   benchmark.
