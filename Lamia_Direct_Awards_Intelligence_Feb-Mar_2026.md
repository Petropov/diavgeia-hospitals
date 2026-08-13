# Lamia Municipality — Direct Award Intelligence Report
**Δήμος Λαμιέων (Org UID 6166) · Direct awards (Δ.1), 13 Feb – 31 Mar 2026**
*Source: Diavgeia opendata API, complete Δ.1 record for the period (106 decisions). Every figure below is from live API data, not extrapolation. Generated 2 July 2026.*

---

## Why this report is different from the previous attempt

The earlier pipeline treated search results as thin metadata and tried to "hydrate" every decision individually — a per-ADA API call that made full coverage impractical. The correction: **Diavgeia's opendata search endpoint returns complete decision objects — supplier AFM, supplier name, award amount, CPV, signer — up to 500 per call.** One month of direct awards costs one API call. The dataset below is therefore *complete* for the period, with no sampling and no classification noise: every record is a genuine Δ.1 direct-award decision.

---

## Headline findings

**1. 59% of all direct awards in the period disclose neither supplier nor amount — all from one committee.**
Of 106 direct awards, 63 are decisions of the Vehicle Maintenance & Repair Committee (Επιτροπή Συντήρησης και Επισκευής Οχημάτων), every single one published with an *empty* supplier field and an *empty* award amount, under an identical boilerplate subject. All 63 are signed by the same signer (ID 100089180, unit 100015910). Confirmed ADAs include 9ΟΡ1ΩΛΚ-Ψ8Ο, Ψ27ΛΩΛΚ-ΓΩ2, 6Α2ΚΩΛΚ-ΖΥΣ, 92ΩΗΩΛΚ-ΖΜΣ, ΨΑΙΒΩΛΚ-1ΣΚ, 9ΕΞΒΩΛΚ-ΥΕΠ, ΨΖΜΘΩΛΚ-ΝΕΩ, 93Σ5ΩΛΚ-Ο55 (full list of 63 in `data/6166/real/awards_2026_feb_mar.csv`). They were issued in daily batches — e.g. eight consecutive protocol numbers (10353–10360) on 19 March alone.
*Why it matters:* Diavgeia submission rules require the counterparty and amount in award metadata. Whatever the aggregate fleet spend is, it is structurally invisible: not one euro of it can be totalled from the register. **Confidence: high (fact — complete enumeration, not sample).** *→ Revised by PDF verification: see Addendum — the PDFs contain the data; scale is small; issue reclassified as systematic metadata non-compliance.*

**2. Twin €19,964.00 tree-pruning awards to the same contractor, one week apart, split by district.**
ΚΑΝΔΗΛΑΡΗΣ ΑΘΑΝΑΣΙΟΣ (AFM 056254873) received *exactly* €19,964.00 on 17 March for "dangerous tree pruning, D.E. Lamias" (Ρ920ΩΛΚ-5ΓΙ) and *exactly* €19,964.00 again on 24 March for the identical service in D.E. Gorgopotamou (9Ν52ΩΛΚ-3ΩΝ) — €39,928 combined, exceeding the €30,000 direct-award ceiling that would have applied to a single combined contract, with each piece priced €36 under a round €20,000. A third, related award — "consulting services for large tree management" (ΡΛ77ΩΛΚ-ΚΘΞ, €15,996.00) — was published *without any supplier identified*, which is a metadata violation on its own. The tree-management program totals ≥ €55,924 across three direct awards in nine days.
*Why it matters:* identical amounts + identical scope + geographic splitting + adjacent dates is the canonical contract-splitting signature under L.4412/2016 (Article 6 prohibits splitting to stay under thresholds). This is the strongest single risk signal in the dataset. **Confidence: high for the pattern (fact); medium for the interpretation — a legitimate identical unit-price explanation is possible but would itself need documentation.**

**3. Threshold-hugging is systematic, not incidental.** Four of the 43 disclosed amounts sit within 2% *below* a round threshold:
€19,964.00 ×2 (under 20k, finding 2); €14,999.77 for pool chemicals (ΨΔΝ5ΩΛΚ-ΕΩΓ — 23 cents under €15,000); €11,999.73 for printing services (9Ο1ΦΩΛΚ-ΦΣΩ — 27 cents under €12,000). Amounts ending 23–36 cents below round numbers indicate quotes engineered to a ceiling, not market-priced offers. **Confidence: high (fact); the inference that internal approval tiers sit at 12k/15k/20k is medium and testable against the municipality's decision-delegation rules.**

**4. One natural person received four audio/lighting contracts in six weeks — €27,063 total.**
ΓΚΟΥΡΝΕΛΟΥ ΑΘΑΝΑΣΙΑ (AFM 136850449): €5,381.60 Koulouma audio (65ΝΗΩΛΚ-ΤΨΟ, 18 Feb, privateData), €17,239.72 carnival audio+lighting (6ΤΧ8ΩΛΚ-ΚΗΖ, 18 Feb, privateData), €349.99 anti-violence-week microphones (Ρ49ΤΩΛΚ-5Β6, 7 Mar), €4,092.00 youth-event audio (9ΔΠΒΩΛΚ-ΛΩΣ, 20 Mar). Two of the four are flagged privateData, reducing document visibility. She is the municipality's de facto sound vendor across *unrelated* event budgets — without any visible framework contract or competitive selection. Cumulative awards to one person approaching the €30k annual same-CPV ceiling within a quarter warrants monitoring of Q2–Q4. **Confidence: high (fact).**

**5. €27,900 to the regional TV broadcaster for a "conference co-organisation."**
STAR Κεντρικής Ελλάδος (AFM 094228018) received €27,900 — €2,100 under the legal ceiling — for "STAR FORUM IV" (ΨΜΡ1ΩΛΚ-Ο98, 25 Mar). A near-ceiling direct payment from a municipality to the dominant regional media outlet is a category auditors treat separately (media capture risk): it is simultaneously the largest discretionary award in the period and a payment to an entity that shapes coverage of the municipality. **Confidence: high (fact); the framing is a risk category, not an accusation.**

**6. Supplier concentration among disclosed awards is moderate — the risk is in what's undisclosed.**
Disclosed spend: €303,520 across 43 awards, 33 distinct suppliers. HHI ≈ 998 (below the 1,500 "moderately concentrated" line); top-3 share 44.8% (ΕΛΤΑ €68,199 postal amendment; ΚΑΝΔΗΛΑΡΗΣ €39,928; STAR €27,900). The carnival cluster (14 awards, ~€77k) was spread across 13 different local vendors — consistent with genuine small-lot event procurement rather than a single captured vendor. The transparency problem is not concentration among what's visible; it's the 59% that publishes nothing. **Confidence: high.**

---

## Secondary observations

**Repeat micro-vendors.** ΑΘ ΚΑΡΑΓΕΩΡΓΟΣ ΚΑΙ ΣΙΑ ΟΕ (999352208): 5 awards in 6 weeks (treats, meals ×2, tables, €3,948 total). NEXT PRINT EE (998917460): 3 print awards in one week (€2,486). Small values, but both are default vendors receiving serial awards with no visible rotation of quotes — a habit pattern rather than a corruption signal at these amounts.

**The ΝΤΕΛΗΣ duplicate resolved.** The earlier dossier flagged two €3,720.00 awards to ΝΤΕΛΗΣ ΓΕΩΡΓΙΟΣ (054108630) as a possible double-count. Full data confirms both are real, same-day-window awards for stage/seating at two different events (ΨΖΠΤΩΛΚ-Η7Ρ carnival; 9ΣΥΨΩΛΚ-ΥΙΕ Koulouma) — the identical pricing for different scopes remains odd but both decisions exist independently.

**Legal/professional outsourcing runs through Δ.1.** Legal-database subscription ΝΟΜΟΤΕΛΕΙΑ €1,674 (658ΘΩΛΚ-ΧΩΛ), occupational physician €12,160 (6ΧΥΠΩΛΚ-ΕΦ3) — consistent with the January external-lawyer mandate (901ΓΩΛΚ-ΓΙΣ) and the €18,600 outsourced internal audit (Ψ8ΣΝΩΛΚ-1ΤΜ) found previously. The municipality routinely buys professional functions by direct award.

**privateData usage.** 6 of 106 awards are flagged privateData — all natural-person vendors, all in the events category. Legitimate under GDPR practice, but it means the six least-scrutinizable awards are also personal-services contracts assigned without competition.

---

## What changed methodologically (the actual solution)

The working pipeline, now in `scripts/`:

```bash
# 1. COLLECT — bulk search, full objects inline, 1 call per month per type
python scripts/fetch_search_pages.py --org 6166 --type Δ.1 --from 2025-01-01 --to 2026-07-01

# 2. NORMALIZE — CSVs with correct supplier extraction (sponsor[] vs person[] vs org)
python scripts/build_normalized_tables.py --org 6166

# 3. ANALYZE — concentration, threshold-proximity, identical amounts, fragmentation
python scripts/analyze_awards.py --csv data/6166/normalized/procurements.csv

# 4. (Rarely needed) per-ADA hydration for special cases, via working opendata endpoint
python scripts/hydrate_candidate_details.py --org 6166 --limit 100
```

Key fixes vs. the stalled version: the API base is `diavgeia.gov.gr/opendata` (the `luminapi` endpoint is unreliable externally); search responses carry full `extraFieldValues`, eliminating ~95% of hydration calls; ADAs are percent-encoded in URLs; and "supplier" is extracted from `person[]` for awards but `sponsor[]` for payment records, which removes the municipality-as-its-own-supplier artifact (AFM 997947640) that poisoned the previous dataset.

---

## Recommended next runs

1. **Full-year Δ.1 sweep (2025 + 2026)** — ~15 API calls — to test whether the ΚΑΝΔΗΛΑΡΗΣ split, the ΓΚΟΥΡΝΕΛΟΥ serial awards, and the STAR payment are annual recurrences (prior-year carnival and "STAR FORUM I–III" would confirm structural patterns).
2. **Vehicle committee deep-dive:** fetch the PDF documents (`documentUrl`) for a sample of the 63 opaque fleet awards — the amounts and garages exist in the PDFs even though the metadata is empty; OCR ~10 documents to estimate the hidden aggregate.
3. ~~Cross-check the tree program~~ **Done — see Addendum.** Consultant is ΜΕΡΜΙΡΗΣ (052001878), distinct from contractor ΚΑΝΔΗΛΑΡΗΣ; remaining check is the independence of the supervision role.
4. **Δ.2 (contracts) + Α.2 (regulatory) sweep** for the same window to capture the €2.0M digital-transformation tender's progress and the EV tender award.

---

## Addendum — PDF verification round (2 July 2026)

The two priority follow-ups were executed by fetching decision PDFs directly
(`https://diavgeia.gov.gr/opendata/decisions/{ADA}/document.pdf` — returns extracted text).

**Finding 2 (tree cluster) — consultant identified, partially de-escalated.**
The €15,996 no-supplier consulting award (ΡΛ77ΩΛΚ-ΚΘΞ) went to **ΜΕΡΜΙΡΗΣ ΧΡΙΣΤΟΔΟΥΛΟΣ, forester–environmentalist (AFM 052001878)** — €12,900 + VAT for 23 technical reports and 400 hours of pruning supervision at €25/hr, through 31-12-2026. He is a *different person* from the pruning contractor ΚΑΝΔΗΛΑΡΗΣ (056254873): gatekeeper and executor are separated, which is the proper structure. What remains open on the tree cluster: the twin €19,964 pruning awards themselves (the splitting signature stands), and the fact that the consultant both *specifies* which trees need work and *supervises* the contractor's hours — a quantity-certifier role worth checking for independence. The missing supplier in the Diavgeia metadata was a publication error, not concealment: the name is plainly in the PDF.

**Finding 1 (63 opaque fleet awards) — downgraded from opacity to metadata negligence, sample-verified.**
Five of the 63 PDFs were pulled (ΨΑΙΒΩΛΚ-1ΣΚ, 9ΟΡ1ΩΛΚ-Ψ8Ο, ΨΖΜΘΩΛΚ-ΝΕΩ, 9ΘΗΗΩΛΚ-392, 6Α2ΚΩΛΚ-ΖΥΣ). Every PDF contains full detail the metadata omits: garage name, AFM, vehicle plate, inspection order number, net/VAT/total. The sample: €771.16 (ΤΣΟΓΚΑΣ), €322.40 (ΗΦΑΙΣΤΟΣ ΑΒΕ, Thessaloniki), €221.90 (ΝΤΟΤΣΙΚΑΣ ΕΤΑΣΕ), €625.73 (ΜΠΑΚΑ ΟΕ), €156.24 (ΜΠΡΑΖΑΣ) — **five different garages, mean €419**, per-vehicle emergency repairs under the 1975 fleet-repair decree, each backed by a numbered inspection order. Extrapolated, the 63 awards ≈ **€26k for the period** (~€130–160k/yr pace) spread across many vendors — not a hidden large-vendor scheme. The finding therefore shifts: the risk is not concealed spend but **systematic non-compliance with Diavgeia metadata rules by this committee** (0/63 decisions publish supplier or amount in metadata, making the register unsearchable for this whole category), plus a Thessaloniki-based parts vendor worth a raised eyebrow in an "emergency local repair" process. Full-population OCR would settle the aggregate precisely; the sample gives no reason to expect surprises.

*Nothing in this report asserts wrongdoing. It identifies publication gaps and structural patterns that merit the specific follow-ups listed, in line with the project's aim: transparency through evidence, not accusation.*
