# Ground Rules — Public Tech data pipelines

Lessons from the Diavgeia stall (Feb–Jul 2026). Read before building anything new.

## 1. Prove the data path with one real record before writing pipeline code
No script gets built until a single end-to-end fetch of real data has succeeded
and been inspected by hand. The Diavgeia pipeline was built, tested and "shipped"
entirely on synthetic fixtures because the endpoint was dead. A 5-minute curl
would have exposed it on day one.

**Rule: first artifact of any integration is one saved raw response, not code.**

## 2. Enumerate the API surface before accepting a constraint
We architected around "hydration is expensive" without checking whether a bulk
variant existed. Most government/open-data platforms have BOTH an internal app
API and a public opendata/bulk API — always look for: `/opendata`, `/api/v*`,
`/export`, CSV dumps, OpenAPI docs, a "developers" page.

**Rule: before optimizing around a limit, spend 30 minutes trying to make the
limit disappear. Write down which endpoints were tested and what each returned.**

## 3. Inspect one raw payload before trusting any extracted field
The supplier-AFM contamination (municipality's own AFM in 14,683 rows) survived
because extraction logic was written against assumed structure. Payment records
keep the payee in `sponsor[]`, awards in `person[]` — visible in any single
raw JSON, invisible in aggregated CSVs.

**Rule: every new field extraction is validated against 3 hand-read raw records,
including one of each decision type it will touch.**

## 4. Distrust analysis built on >20% missing data — fix collection first
The old dossier hedged everything ("amounts sparse", "names missing") instead of
asking why the gaps existed. Missing data was treated as a caveat when it was
actually the bug. The moment >20% of a key field is empty, stop analyzing and
diagnose collection.

## 5. Keep a tested-endpoints log
`data/ENDPOINTS.md` — every URL pattern tried, date, result (works / blocked /
truncated / format). Prevents re-litigating dead ends and losing working ones.

### Known-good (verified 2026-07-02)
- `https://diavgeia.gov.gr/opendata/search.json?org=&type=&from_date=&to_date=&size=500&page=`
  → full decision objects incl. extraFieldValues (supplier, amount, CPV). 500/page.
  from/to filter on SUBMISSION date; default issueDate window ≈ last 6 months.
- `https://diavgeia.gov.gr/opendata/decisions/{ADA}.json` → single decision, full detail.
  ADA must be percent-encoded (Greek chars).
- `https://diavgeia.gov.gr/opendata/decisions/{ADA}/document.pdf` → decision PDF; fetch
  tools return its extracted TEXT. Recovers supplier/amount when metadata is empty
  (verified 2026-07-02 on vehicle-committee decisions).
### Known-bad
- `https://diavgeia.gov.gr/luminapi/api/...` → internal app API, unreliable externally. Do not use.
