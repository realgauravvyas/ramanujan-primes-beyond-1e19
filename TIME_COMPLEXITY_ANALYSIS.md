# Time complexity pattern — a(1) through a(22), plus a note on a(23)

Analysis written 2026-08-12, based on the clean, single-pass timings in
`published_results.csv` (a(1)-a(18) freshly recomputed bypassing cache;
a(19)-a(20) genuine first-time measurements; a(21)-a(22) freshly
recomputed after the originals were contaminated by interruptions).

**a(23) (computed 2026-08-14) is deliberately excluded from every fit
below, and its recorded time must not be used for any complexity
comparison.** Its 95911s (26h38m) figure suffers the exact same
contamination the a(21)/a(22) originals did: it reflects only the final
continuous run segment of a computation spread across multiple
interrupted sessions (RAM-pressure restarts, a concurrent unrelated
workload) whose earlier attempts had already cached several checkpoints
and partial anchors. Unlike a(21)/a(22), a(23) has **not** been
re-verified with a clean, cache-bypassed, single-pass run, so there is
currently no reliable a(23) timing at all — only a lower bound (the true
cost is *at least* 95911s, likely well above it). If the pattern below
held exactly, a(22)'s 53002.1s would predict roughly 51.5-54.5 hours for
a clean a(23) run (53002.1 x 3.5 to x3.7); the contaminated 26.6h figure
being far below that range is consistent with under-counting, not
evidence the pattern broke. Nobody should treat this as a real
data point until a fresh recompute is done — see the end of this file
for what that would take.

## Three regimes

**Regime 1, n=1-11: flat, ~0.35s.** Fixed overhead (spawning `primecount`,
etc.), not real computation -- Q is trivially small, 0 checkpoints needed
in every case.

**Regime 2, n=12-19: rapid, accelerating growth** as checkpoints appear and
multiply (single-algorithm anchors, no cross-verification):

| n | time | checkpoints | ratio to previous |
|---|---|---|---|
| 12 | 0.41s | 1 | -- |
| 13 | 0.59s | 3 | 1.4x |
| 14 | 1.40s | 6 | 2.4x |
| 15 | 4.41s | 8 | 3.2x |
| 16 | 16.57s | 10 | 3.8x |
| 17 | 91.81s | 13 | 5.5x |
| 18 | 343.37s | 15 | 3.7x |
| 19 | 678s | 17 | 2.0x |

**Regime 3, n=20-22: cross-verified anchors** (2 algorithms instead of 1,
so not directly comparable in absolute terms to regime 2 -- see caveat
below):

| n | time | checkpoints | ratio to previous |
|---|---|---|---|
| 20 | 3839s | 16 | 5.7x |
| 21 | 16307.3s | 18 | 4.2x |
| 22 | 53002.1s | 12* | 3.3x |

\* a(22) used D=1e11 instead of 1e9 (deliberate: trades a longer sieve walk
for fewer checkpoints), so its lower checkpoint count is a methodology
choice, not part of the natural pattern.

## Fitted growth rate

Log-linear regression on ln(time) vs n, excluding the flat overhead floor:

- **n=13-19 (single-algorithm regime): x3.51 per decade of Q**
- **n=20-22 (cross-verified regime): x3.72 per decade of Q**

Both land in the same **~3.5-3.7x per decade** range despite different
methodology -- a reasonably robust empirical estimate. In terms of Q: time
grows roughly as **Q^0.56** (since 10^0.556 ~= 3.6).

## Important correction

Mid-session (before clean timings existed), a(19)->a(20) was reported as
scaling ~11x, called "much worse than theory." That number came from
**contaminated data** -- timings from interrupted, resumed, RAM-crisis-
affected runs, not clean single-pass measurements.

The real, clean-data answer: **~3.5-3.7x per decade, which is actually
BETTER than the ~4.64x (Q^0.667) textbook asymptotic** for this class of
algorithm (Gourdon's method), not worse. The x11 figure was purely an
artifact of how the number was forced to be measured at the time under
memory pressure and multiple restarts, not a real property of the
algorithm or the growth of the underlying mathematics.

## Checkpoint count (grid bracketing) growth

Checkpoints needed: 0 (n<=11), then 1,3,6,8,10,13,15,17 (n=12-19), then
16,18 (n=20-21, cross-verified regime, same D=1e9), then 12 (n=22, at the
larger D=1e11). This is consistent with the theoretical O(log(W/D))
prediction -- slow, sub-linear growth in n -- and confirms the checkpoint
COUNT is not what's driving the ~3.5-3.7x per-decade time growth; the
dominant driver is the cost of each individual `primecount` call growing
with Q, not the number of calls needed.

## Caveat: regime 2 vs regime 3 aren't perfectly apples-to-apples

a(9)-a(19) used a single algorithm (Gourdon only) for anchors; a(20)-a(22)
cross-verify with a second algorithm (Deleglise-Rivat), which is
measurably slower (see PROJECT_STATE.md section 6: D-R ran ~3-4x slower
than Gourdon at the same Q in direct comparison). The a(19)->a(20) jump in
particular mixes a real Q-scaling increase with this methodology change,
so it should not be read as pure algorithmic complexity growth. The
n=13-19 and n=20-22 regressions above are each internally consistent,
which is why they're reported separately rather than as one combined fit.

## What it would take to get a real a(23) data point

Same fix already applied to a(21)/a(22): a fresh run with `pi_cache.json`
bypassed entirely, run to completion with nothing else competing for
RAM/CPU on the machine, timed start-to-finish in one continuous session.
Based on the ~51.5-54.5h prediction above, budget roughly 2-3 days of
dedicated compute. Until that exists, treat n=23 as unmeasured, not as
"~26.6h" -- the number in `published_results.csv` is there for the
record, not for use.
