# Ramanujan primes a(1)-a(22): values and timing for publication

See `published_results.csv` for the machine-readable table. Methodology notes:

## How each number was obtained

- **a(1)-a(18):** freshly recomputed on 2026-08-11, bypassing the cache
  entirely, so every timing is a genuine single clean run (not a cache
  replay). All matched OEIS A181671's published values exactly.
- **a(19)-a(20):** genuine single-pass timings captured live the first time
  each was ever computed, no interruptions.
- **a(21)-a(22):** these were originally computed across multiple
  interrupted/resumed sessions (hardware limits, deliberate cancellations),
  so their first recorded "wall time" only reflected the final resumed pass,
  not a clean measurement. Both are being (or have been) freshly recomputed,
  bypassing cache, in a single clean run, for a true publishable time.
  - **a(21): DONE.** Fresh clean run = 16,307.3s (4h 31m 47s), confirmed
    MATCH against the original certified value. Notably faster than the
    original run's real compute time (~12h) -- the difference is overhead
    from the original's multiple interruptions/restarts, not a change in the
    underlying computation.
  - **a(22): DONE.** Fresh clean run = 53,002.1s (14h 43m 22s), confirmed
    MATCH, 12 grid checkpoints (matches the original). All 22 terms now have
    genuine, publication-quality single-pass timings in
    `published_results.csv` -- this task is complete.

## Hardware

Laptop: 13th Gen Intel Core i5-13420H (8 cores / 12 threads), 13.7 GB RAM.
a(21) and a(22) at this scale approach or exceed this machine's practical
limits (see `PROJECT_STATE.md` / `MIGRATION_NOTES.md` for the RAM wall hit at
a(23), which is why later terms are being continued on a higher-RAM desktop).

## Method

Certified via the bracketing lemma (see `README.md`): exact pi(x) via
`primecount` at O(log) endpoints plus a small exact 128-bit sieve walk near Q,
backed by the published Johnston (2022) and Dusart (2010) analytic tail
bounds. a(20)-a(22) additionally cross-verify their record-defining anchors
with two independent `primecount` algorithms (Gourdon and Deleglise-Rivat).
