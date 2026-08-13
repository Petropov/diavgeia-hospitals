# Procurement Integrity Signals — ΓΝ Ρόδου vs ΓΝ Λαμίας (Aug 2021 – Aug 2026)

Structuring, concentration, recurring-contract and supplier-pattern analysis on the matched
five-year payment datasets. Rhodes corrected; Lamia as published.

> **Read this first.** Everything below is computed from **payment orders** (Β.2.2), not from
> **award decisions** (Δ.2.2). Greek procurement thresholds apply to the *award*, not to the
> payment. So a monthly payment sitting under €30,000 net proves nothing on its own — it is
> equally consistent with (a) a properly tendered multi-year contract invoiced monthly, and
> (b) serially repeated direct awards. **Payment data cannot distinguish these.** Everything
> here is a *signal to check*, not a finding of irregularity. The award pull needed to
> resolve it is specified at the end.

---

## 1. Threshold structuring — no differential signal

Direct-award ceiling is €30,000 net (Ν.4782/2021, in force across our whole window).
Counting payments in the 10% band just below the ceiling against the 10% band just above:

| | just-below | just-above | ratio |
|---|---:|---:|---:|
| **Rhodes** @30k net | 97 | 80 | **1.21** |
| **Rhodes** @37.2k gross (24% VAT) | 79 | 58 | **1.36** |
| **Lamia** @30k net | 70 | 56 | **1.25** |
| **Lamia** @37.2k gross | 87 | 64 | **1.36** |

**The two hospitals are statistically indistinguishable** (1.21/1.36 vs 1.25/1.36). Both show
mild just-below clustering, which is expected and largely benign — contracts are routinely
written *to* a ceiling rather than arbitrarily around it.

**This is a negative finding and should be reported as one.** There is no evidence of
differential threshold-gaming between these two hospitals in payment data — *at the
aggregate level*. See §1b: the per-destination view is different.

## 1b. Per-destination structuring screen — the aggregate test was hiding it

The right structuring question is not "how many payments sit under the ceiling" but **"does
the same destination repeatedly receive payments sized just under it."** Screen: suppliers
with ≥4 payments whose net value (tested under 6%/13%/24% VAT) falls within 10% below the
€30,000 ceiling.

**Rhodes — flagged destinations:**

| supplier | near-ceiling pmts | near € | % of that supplier's total | worst year |
|---|---:|---:|---:|---|
| ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ | **28** | 970,176 | **45%** | 10× in 2022 |
| ΑΦΟΙ ΚΟΜΠΑΤΣΙΑΡΗ (catering) | **22** | 731,025 | **50%** | 9× in 2024 |
| MY SERVICES (security/staffing) | **20** | 606,485 | **71%** | **12× in 2025** |

**Lamia — top of the same screen:**

| supplier | near-ceiling pmts | near € | % of supplier's total |
|---|---:|---:|---:|
| UNISON FACILITY SERVICES | 23 | 841,152 | **11%** |
| ABBOTT LABORATORIES | 13 | 419,766 | **13%** |
| ΔΕΛΤΑ ΙΑΤΡΙΚΗ | 12 | 358,248 | 23% |

**The discriminator is the last column.** Lamia's flagged suppliers are large vendors whose
main contracts sit far *above* the threshold (UNISON's recurring instalments are €75k–128k
gross) — their near-band payments are incidental spillover from big tendered contracts, with
no incentive to structure. Rhodes' flagged trio earn **45–71% of their entire five-year
revenue from this hospital inside the near-ceiling band**, i.e. their business with the
hospital is largely *composed of* payments sized just under the direct-award limit. MY
SERVICES hit the band 12 times in 2025 alone.

**Caveats, in order of importance:**
1. **The VAT test is permissive** — it flags if *any* common rate puts the net in-band.
   Security services carry 24% VAT, under which MY SERVICES' typical €30,068 gross is
   ~€24,250 net — *not* near the ceiling. Its 20 flags rest partly on VAT assumptions that
   may not apply. ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ is the clean case: €34,968 gross at its documented 24%
   VAT = **€28,200 net, 6% under the ceiling, 28 times**.
2. Payments ≠ awards (as §1): instalments of one tendered contract would produce this
   pattern innocently. The award documents settle it.
3. Screen run on Β.2.2 only; Rhodes' Β.2.1 layer is unscreened.

**Bottom line: the earlier "no structuring signal" conclusion was an artifact of aggregating.
Per destination, Rhodes shows a concentrated near-ceiling pattern in three recurring service
suppliers (~€2.3M) that has no counterpart at Lamia.** Still a signal to verify against
award records — not a finding of wrongdoing.

## 2. Same-supplier, same-day clustering — mostly explained

| | supplier-days with 3+ payments | value |
|---|---:|---:|
| Rhodes | 85 | €6,627,243 |
| Lamia | 487 | €19,934,308 |

Lamia has ~6× more, but also 2.8× the payment volume and a much smaller mean payment — its
administrative style is high-volume/low-value, so this is expected, not suspicious.

Top cases are explained on inspection:
- **Lamia's** top five are all **ΜΤΠΥ ΚΛΠ ΤΑΜΕΙΑ** — a public-servants' pension fund.
  Statutory contributions, not procurement.
- **Rhodes'** largest is **SIEMENS HEALTHCARE, 2021-09-24, 3 payments totalling €1,988,960**.
  All three were individually PDF-verified during the data-quality work and are **genuine**
  (equipment purchase split across payment orders). A splitting detector would flag this;
  the documents clear it.

Lesson: same-day clustering has a high false-positive rate against statutory transfers and
capital purchases. Not useful without document checks.

## 3. Recurring fixed-fee contracts — a real difference

This is where the hospitals diverge. Both run recurring service contracts at identical
repeating amounts. The question is where those amounts sit relative to the €30,000 net ceiling.

**Rhodes**

| supplier | count | gross € | **net €** |
|---|---:|---:|---:|
| ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ | 24× | 34,968.00 | **28,200.00** ← 6% under ceiling |
| ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ | 15× | 38,464.80 | 31,020.00 |
| MYSERVICES HUMAN RESOURCES | 17× | 30,068.40 | 24,248.71 |
| SARP FACILITY MANAGEMENT | 8× | 86,473.36 | 69,736.58 |

**Lamia**

| supplier | count | gross € | net € |
|---|---:|---:|---:|
| UNISON FACILITY SERVICES | 13× | 128,439.76 | 103,580.45 |
| ΙΝΤΕΡΚΑΤ ΑΦΟΙ ΠΑΠΑΪΩΑΝΝΟΥ | 15× | 75,160.06 | 60,612.95 |
| ΙΝΤΕΡΚΑΤ ΑΦΟΙ ΠΑΠΑΪΩΑΝΝΟΥ | 11× | 62,319.94 | 50,258.02 |
| ΗΦΑΙΣΤΟΣ SECURITY | 9× | 60,966.00 | 49,166.13 |

**Rhodes' single most-repeated contract instalment sits at €28,200 net — 6% below the
direct-award ceiling — and recurs 24 times. Lamia's recurring instalments are all 1.6–3.5×
*above* the ceiling**, i.e. unambiguously in tendered territory.

Again: if Rhodes' €28,200 instalments are draws against one properly tendered contract, this
is entirely normal and the proximity is coincidence. The payment records cannot tell us.

## 4. Supplier flagged for follow-up — ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ

**ΑΦΜ 997563888** · 54 payments · **€2,154,859.60** over five years

| | |
|---|---|
| Name (translated) | *"Technical Support of Rhodes Hospital"* |
| Active | 2021-08-19 → 2026-07-23 (continuous) |
| Annual value | €198k (2021, part) · €420k · €385k · €426k · **€496k** (2025) · €230k (2026, part) |
| Dominant instalment | 24× @ €34,968.00 gross (**€28,200 net**) |
| Second instalment | 15× @ €38,464.80 gross (€31,020 net) |
| CPV | 50710000-5 (repair/maintenance of building installations) — 26 of 54 |
| KAE | 9723 — 29 of 54; **25 of 54 carry no KAE at all** |

Three things make this worth a look, none of which is evidence of wrongdoing:

1. **The company is named after its client.** A supplier whose corporate name is the service
   it provides to one specific public hospital. This can be entirely legitimate — a
   special-purpose vehicle or a long-standing local specialist — but it is unusual enough to
   verify ownership and how the contract was originally awarded.
2. **Rank 7 by value at Rhodes** (2.3% of corrected spend), rising year-on-year to €496k in
   2025 — its largest year, with 2026 already at €230k by August.
3. **Nearly half its payments (25/54) publish no budget code.**

Note €69,936.00 = exactly 2 × €34,968.00, so some entries are double instalments (catch-up),
not a separate rate. The underlying monthly rate is stable across five years.

**What would settle it:** the original award/contract decision. If there is a tendered
multi-year contract, this is a normal facilities arrangement and the threshold proximity is
noise. If instead there is a series of separate direct awards each sized at €28,200 net,
that is textbook threshold structuring and the €2.15M cumulative value should have gone to
open tender long ago.

## 4b. Direct awards ARE visible — inside the Β.2.1 PDFs

The Β.2.1 records whose supplier field is empty turn out, on inspection, to include
**direct-award decisions** (ΠΡΑΞΗ ΑΝΑΠΛΗΡΩΤΗ ΔΙΟΙΚΗΤΗ). Their PDFs state the legal basis
verbatim:

> *"direct procurement is carried out when total expenditure excluding VAT is equal to or
> less than €30,000"* (art. 118, Ν.4412/2016)

and then record how many bids arrived:

| ADA | supplier | offers received | note |
|---|---|---:|---|
| `9ΕΙΘ46907Κ-3ΩΝ` | SPECIFAR A.B.E.E. | **1** | *"no contract in force from a regular tender for this code"* |
| `6ΔΖ946907Κ-ΞΛΔ` | GILEAD SCIENCES ΕΛΛΑΣ | **1** | |
| `6Ε9Λ46907Κ-ΔΓΧ` | ΒΙΑΝΕΞ Α.Ε. | **1** | |
| `6ΔΓΥ46907Κ-9ΑΖ` | *(pharma)* | 2 | |
| `ΨΔΘ946907Κ-4ΕΔ` | *(pharma)* | 2 | |

**3 of 5 sampled direct awards attracted exactly one bid**, and at least one states outright
that no tender contract existed for the item. For high-cost patented oncology and
rare-disease drugs (KEYTRUDA, OPDIVO, TECENTRIQ, OCREVUS, REPLAGAL, FABRAZYME dominate these
subject lines) a single bid is often *structurally unavoidable* — there may be only one
authorised distributor in Greece. So this is **not** presumptive irregularity.

But it is measurable, and it is the direct-award evidence base the payment data could not
provide. With a full Β.2.1 PDF pass one could report, for the first time here:
single-bid rate, direct-award value as a share of spend, and which suppliers repeatedly win
uncontested awards.

**Caveat that matters:** these PDFs have a broken text encoding (mojibake — Greek rendered
through a wrong character map). `pdftotext` returns garbled but *parseable* text; naive
extraction silently returns nothing, which is exactly what happened on the first attempt
here and would have been misread as "no supplier disclosed anywhere."

## 5. What is missing — the award layer

Everything above analyses **payments**. The procurement-integrity questions the user actually
asked — *direct awards*, *structuring*, *suspicious suppliers* — live in the **award**
records, which we have not pulled for either hospital:

| type | meaning | pulled? |
|---|---|---|
| Β.2.2 | ΕΝΤΑΛΜΑ ΠΛΗΡΩΜΗΣ — payment order | ✅ both |
| Β.2.1 | ΧΕ — payment warrant | ✅ both |
| **Δ.2.2** | **ΑΝΑΘΕΣΗ / ΚΑΤΑΚΥΡΩΣΗ — the award itself** | ❌ **neither** |
| **Δ.1** | **ΣΥΜΒΑΣΗ — the contract** | ❌ neither |
| Δ.2.1 | ΠΕΡΙΛΗΨΗ ΔΙΑΚΗΡΥΞΗΣ — tender notice | ❌ neither |

With Δ.2.2 we could finally test the real questions:
- **Direct-award rate**: what share of awards are απευθείας ανάθεση vs tendered?
- **Genuine threshold test**: award values against €30,000 net — the threshold as it actually
  applies in law.
- **Serial direct awards**: same supplier receiving repeated sub-threshold awards, which is
  the actual structuring pattern.
- **Award-to-payment linkage**: does ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ's €2.15M trace to one contract or 54
  separate awards? That single answer resolves section 4.

```
python3 scripts/fetch_payments_history.py --org 99221940 --start 2021-08-01 --type "Δ.2.2" --outdir data/99221940/awards
python3 scripts/fetch_payments_history.py --org 99221923 --start 2021-08-01 --type "Δ.2.2" --outdir data/99221923/awards
```

⚠️ The script's classifier is built for payments (`sponsor[]` / `expenseAmount`). Δ.2.2 stores
its payee in **`person[]`** and value in **`awardAmount`**, so it will need a parallel branch
before those pulls yield usable output — the run will otherwise report near-zero. Prior work
in this project also found most Δ.2.2 records have `person: []` empty (procedural steps), so
expect a lower yield than the payment pulls.

## 6. Honest summary

| question | answer |
|---|---|
| Threshold structuring in payments? | **No differential signal.** Rhodes ≈ Lamia. |
| Same-day splitting? | Present in both; top cases explained (statutory transfers, verified equipment purchase). |
| Concentration? | Both low. Rhodes HHI 202, Lamia 329 — both far below the 1,500 "unconcentrated" line. |
| Suspicious supplier? | **One flagged for follow-up** (ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ, €2.15M, eponymous, instalments 6% under ceiling). Not an allegation. |
| Direct awards? | **Cannot answer from payment data.** Requires the Δ.2.2 pull. |

The strongest integrity findings in this project so far remain the **data-quality** and
**disclosure** ones (57% inflation; 28.8% of value with no payee), not the procurement-pattern
ones. On the classic structuring/concentration tests, Rhodes looks broadly normal — and where
it differs from Lamia, the difference is currently unexplained rather than incriminating.
