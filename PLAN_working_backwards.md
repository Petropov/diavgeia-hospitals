# Working-Backwards Plan — from the destination to Monday morning

Written 2026-08-13, while the discovery + top-50 batch pulls are running.

---

## T-0: THE DESTINATION

> **A published, reproducible national analysis showing which Greek public hospitals
> can actually be held to account through open data — and which cannot — backed by
> evidence strong enough to survive institutional pushback, and specific enough to
> produce one concrete fix.**

Three outputs, one story:

| output | audience | precedent in this repo |
|---|---|---|
| **A.** National transparency ranking (DDQI, ~130 hospitals) | ministry / ΕΚΑΠΥ / press | `score_diavgeia_quality.py` |
| **B.** Corrected spending benchmarks (per bed, per category) | health-policy, researchers | `Rhodes_vs_Lamia_5Year.md` |
| **C.** Narrative piece | general public | `Lamia_Arthro_Kathimerini.html` ("Λαμία: Μια πόλη, διαβασμένη ολόκληρη") |

**The one concrete fix worth aiming at:** input validation on Diavgeia's
`expenseAmount` — reject `amount == supplier ΑΦΜ`, warn when a payment exceeds its
own certified budget line. Two rules that would have caught all 18 phantom records
(~€942M) in a single hospital. It is small, cheap, and unarguable — the best kind of
ask.

**Why this is the right destination:** the project's question is whether AI can
improve public function through transparency. The answer this work supports is
sharper than "yes": *the data was already public and already wrong, and nobody
noticed for five years because reading it at scale was too expensive.* That cost just
collapsed. The finding is not "Rhodes made errors" — it is **"the oversight layer was
never actually operating."**

---

## Working backwards: five gates

### GATE 5 — Publish & refer  *(last)*
**Done when:** article live, dataset citable, findings sent to the institutions named.
**Requires from Gate 4:** every published number carries a verified error bound; every
named entity has had right of reply.
- [ ] Ministry / ΕΚΑΠΥ / 2η ΥΠΕ notified **before** publication, not after
- [ ] Rhodes hospital given right of reply on the 18 records + structuring indicators
- [ ] Dataset + scripts public (done — repo live), DOI or permanent link
- [ ] Article drafted in the register of the Lamia piece
> ⚠️ **Decision required from you, no later than Gate 4:** do we name suppliers in the
> integrity findings publicly? Currently `Integrity_Signals` and `Fraud_Risk_Assessment`
> name companies against structuring *indicators*. Publishing unverified indicators
> against named private firms carries real legal and ethical exposure. Options: (a)
> name only after award-document verification, (b) publish patterns without names, (c)
> refer names privately to authorities and publish aggregates. **My recommendation: (c)
> then (a).** Nothing downstream should assume this is settled.

### GATE 4 — Credibility hardening  *(the actual critical path)*

> **Shortcut found — glossAPI corpus.** The gated HuggingFace dataset
> `glossAPI/diavgeia` holds OCR'd PDF text for ~2.8M Diavgeia documents keyed by ΑΔΑ.
> We already have access and had written it off after `from_issue_date` solved
> retrieval. But retrieval was never the expensive part — **document verification is**,
> and this is exactly that, in bulk. `scripts/glossapi_crosscheck.py` uses it to do at
> scale what we did 63 times by hand: verify amounts against document text, recover
> payees from "anonymous" records, and run the random-sample audit on hundreds rather
> than 60. **Coverage is only ~Jul 2025–Feb 2026**, so it accelerates but does not
> replace direct PDF work. Run `--coverage` first to measure real overlap.
**Done when:** we can state a measured reliability figure, not a caveat.
This gate exists because of `Known_Unknowns.md`. Skipping it means publishing a
national ranking built on outlier-only verification — **committing the exact error we
are documenting at Rhodes.** Nothing else in the plan matters if this fails.
- [ ] **Random-sample audit** — 60 random records × 5 hospitals, PDF-verified.
      Converts "we found 18 errors we hunted for" → "record-level error rate is X%
      (95% CI)". *This is the single highest-value remaining task.*
- [ ] **Reverse-direction test** — deliberately hunt ÷100 / ×10 understatement, which
      no current screen can see. If found, all totals are floors, not estimates.
- [ ] **Reconcile one hospital-year against its απολογισμός** — bounds omission (payments
      never posted at all), the one blind spot Diavgeia cannot self-report.
- [ ] Award-document (Δ.2.2/Δ.1) pull for the ~50 flagged structuring payments →
      converts indicator to finding, or clears it
- [ ] ΓΕΜΗ ownership check on ΤΕΧΝΙΚΗ ΥΠΟΣΤΗΡΙΞΗ ΝΟΣΟΚΟΜΕΙΟΥ ΡΟΔΟΥ

### GATE 3 — National analysis
**Done when:** the three outputs (A/B/C) exist in draft from clean data.
- [ ] DDQI ranking, all discovered hospitals → **output A**
- [ ] Run the ×100 + ΑΦΜ-in-amount screens nationally; PDF-verify every hit
      (Rhodes took ~50 PDFs; nationally expect 200–600)
- [ ] Bed counts for top 50 (external; error-prone — treat as indicative)
- [ ] Per-bed / per-category benchmarks → **output B**
- [ ] **Fork in the road, decided by data:**
      - *If Rhodes-type errors are widespread* → story is systemic portal failure;
        the ask is national validation rules. Stronger, less adversarial.
      - *If Rhodes is an outlier* → story is institutional accountability; needs
        right-of-reply discipline and much more care with names.

### GATE 2 — Scale-up  *(← RUNNING NOW)*
- [x] Discovery + ranking scripts built and compiling
- [ ] `discover_and_rank_hospitals.py` completes → national hospital registry
- [ ] `batch_pull_hospitals.py --top 50` completes (~4h, resumable)
- [ ] Spot-check 2–3 pulled hospitals by hand before trusting the batch
      *(Ground Rule #1: prove the data path on real records)*
- [ ] Commit with extraction date

### GATE 1 — Foundation  *(DONE)*
- [x] Method proven end-to-end on 2 hospitals
- [x] Two error classes PDF-proven (×100; ΑΦΜ-in-amount)
- [x] 5-year extraction solved (`from_issue_date`, max-span not recency cap)
- [x] Public repo with evidence PDFs
- [x] Blind spots documented before they became embarrassments

---

## Critical path (what actually gates the finish)

```
batch pull (running) → national screens → RANDOM-SAMPLE AUDIT → right of reply → publish
                                          ▲
                                    the bottleneck
```

Everything except the audit can run in parallel. The audit is sequential, needs human
PDF reading, and **cannot be compressed** — 300 documents is 300 documents. Start it
the moment the first 5 hospitals finish pulling; do not wait for all 50.

## Sequencing risks

| risk | why it bites | mitigation |
|---|---|---|
| Publishing before the audit | we become the thing we criticise | Gate 4 is non-negotiable |
| Naming firms on unverified indicators | legal + ethical exposure | decision at Gate 4; default to private referral |
| Bed counts are unreliable | per-bed comparisons are the most quotable and most fragile number | publish totals primarily, per-bed with vintage caveats |
| Diavgeia data drifts mid-analysis | €5,549 moved between two runs minutes apart | freeze an extraction date; re-pull once at the end and diff |
| Discovery misses hospitals | ranking looks authoritative but isn't complete | cross-check against the ΥΠΕ lists and the BI-health press figures |
| Scope creep to all 130 | 50 is already a national story | hold at 50 until Gate 4 clears |

## Immediate next actions (while the batch runs)

1. **Nothing that touches the network** — the two jobs own the connection.
2. Draft the random-sample audit script now so it runs the instant data lands.
3. Decide the naming question (Gate 5 ⚠️) — it changes what we write, not just how.
4. Collect bed counts for the top 50 (manual/desk work, no API contention).
5. Sanity-check the ranking's top 10 against the BI-health press figures
   (Ευαγγελισμός, ΠΓΝ Πατρών, Αττικόν, ΚΑΤ). **If Ευαγγελισμός is not near the top of
   our ranking, that discrepancy is itself a finding** — either it under-publishes to
   Diavgeia, or our discovery is incomplete. Check before building on the ranking.
