# OEIS A181671 submission readiness — a(20), a(21), a(22)

Written 2026-08-12.

## What's genuinely new here

OEIS A181671 ("number of Ramanujan primes < 10^n") publishes real data only
through **a(17)**. a(18)/a(19) exist only as prior self-computed,
never-published extensions. **a(20), a(21), a(22) are first-time results --
nobody has published Ramanujan-prime counts this large anywhere.**

Important distinction for anyone reviewing this: pi(x) (the ordinary prime-
counting function) at these same Q values IS already published elsewhere
(Wikipedia's prime-counting-function table -- see below). That does NOT
make a(n) unoriginal -- pi(Q) is only an intermediate ingredient in
a(n) = min_{y>=Q} [pi(y) - pi(y/2)]; the final Ramanujan-prime counts
themselves are unpublished.

## Values

| n | a(n) |
|---|---|
| 20 | 1,093,039,678,770,734,297 |
| 21 | 10,406,559,368,229,726,028 |
| 22 | 99,306,360,875,818,676,888 |

Full detail (anchors, checkpoints, largest Ramanujan prime under each bound)
in the certificate files `piR_1e20_certificate.json` etc. and `NOTES.md`.

## Verification already done

1. **Anchors cross-verified internally**: pi(Q) and pi(Q/2) for all three
   terms computed independently by two different `primecount` algorithms
   (Gourdon and Deleglise-Rivat) -- exact agreement in every case.
2. **Independent EXTERNAL verification found**: Wikipedia's prime-counting
   function table lists pi(10^19) through pi(10^22); all four match our
   values exactly, digit-for-digit (see `independent_pi_reference.md`).
   This is a genuinely separate source, not a self-check.
3. **a(21)'s sieve-walk result reproduced independently**: the certified
   minimum (a dip of 3 below f(Q), at offset 58) was reproduced via direct
   Miller-Rabin primality testing, bypassing `sieve128` entirely.
4. **Record primes confirmed genuinely prime**: the largest Ramanujan prime
   under each bound (e.g. 99,999,999,999,999,999,989 for a(20)) verified
   via deterministic Miller-Rabin.
5. **Analytic sanity check**: all three match li(Q)-li(Q/2) to within
   0.000000% (six decimal places) relative difference.
6. **Growth-ratio check**: a(21)/a(20) = 9.5208, a(22)/a(21) = 9.5427,
   both consistent with the expected ~9.5x per decade for this sequence.
7. **Clean, reproducible, publication-quality timings** for all three (and
   for a(1)-a(19) too) -- see `published_results.csv` /
   `TIME_COMPLEXITY_ANALYSIS.md`. No cache-replay artifacts.
8. **Fresh single-pass reproduction**: a(21) and a(22) were each
   independently recomputed a second time from scratch (bypassing all
   cache) and matched the original certified values exactly.

## Still open before publishing — this is the one that matters

**The Johnston (2022) and Dusart (2010) analytic tail-bound formulas
(`G()` and `dusart_ok()` in `ramanujan128.py`) have never been checked
against the original source papers.** This is the piece of the proof that
certifies no smaller value of f(y) exists anywhere beyond the checked
window, out to infinity -- i.e. it's what turns "we found a candidate
value" into "we proved this is the minimum." Everything else in this list
verifies the computed NUMBERS are right; this is the one piece that
verifies the MATHEMATICAL ARGUMENT is right. Recommended: locate both
papers, check the formula transcription line-by-line before submitting.

## Minor, lower-priority gaps

- Grid-checkpoint pi values (not the anchors) are single-algorithm only,
  not cross-verified like the anchors. Low risk given the built-in
  consistency guard (`bound >= m` check in the code), but worth stating
  explicitly in the submission rather than leaving implicit.
- Everything so far ran on one machine (plus the fresh recomputes, still
  the same laptop). Independent reproduction on the desktop, once a(23)
  work resumes there, would close the "single machine" gap for a(20)-a(22)
  too if time allows (rerun `explore` there against the migrated
  `pi_cache.json` -- cache hits would make this fast, but a genuinely
  fresh independent run would be stronger).

## Suggested submission approach

1. Extend A181671's b-file with a(20), a(21), a(22).
2. In the submission comment, describe the method (bracketing lemma +
   `primecount` + Johnston/Dusart tail bounds -- see `README.md`) and cite
   the independent pi(10^n) match against Wikipedia's table as external
   corroboration.
3. Make the certificates / cache / code available (e.g. link this
   repository) so the computation is independently checkable by reviewers.
4. Close the Johnston/Dusart formula-verification gap above first.
