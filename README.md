# Ramanujan Primes Beyond 10^19

Certified computation extending [OEIS A181671](https://oeis.org/A181671)
(number of Ramanujan primes ≤ 10^n) to n = 20, 21, 22, computed entirely on
consumer hardware — no institutional or cloud compute.

**Paper:** [`paper/main.pdf`](paper/main.pdf) (full version, includes a(23) in
progress) or [`paper_a22/main.pdf`](paper_a22/main.pdf) (final version through
a(22) only). Author: Gaurav Vyas (gaurav.vyas.1729@gmail.com).

## What's here

| path | contents |
|---|---|
| `paper/` | LaTeX source + PDF, full version (a(1)–a(22), a(23) placeholder) |
| `paper_a22/` | LaTeX source + PDF, final version through a(22) |
| `src/` | `ramanujan128.py` (orchestration driver), `sieve128.cpp` (custom 128-bit segmented sieve), build/support scripts |
| `certificates/` | Machine-checkable JSON certificates for a(1)–a(22), including an independent cross-machine reproduction of a(18)/a(19) |
| `data/` | `pi_cache.json` (every exact π(x) value ever computed), published timing tables, independent external π(x) reference values |
| `TIME_COMPLEXITY_ANALYSIS.md` | Empirical scaling analysis (~3.5–3.7× per decade of Q) |
| `OEIS_SUBMISSION_NOTES.md` | Submission-readiness notes for OEIS A181671 |
| `PUBLISHED_RESULTS.md` | Human-readable results summary with provenance |

## Method, in one paragraph

A Ramanujan prime $R_n$ is the least integer such that
$\pi(x) - \pi(x/2) \geq n$ for all $x \geq R_n$. Sieving directly to certify
this at $Q = 10^{20}$ and beyond is infeasible (the certification window
alone spans ~10^12 integers, entirely above the 2^64 limit of general-purpose
sieve libraries). Instead: exact $\pi(x)$ (via
[`primecount`](https://github.com/kimwalisch/primecount)) at O(log) grid
endpoints lower-bounds $f(x)=\pi(x)-\pi(x/2)$ across entire intervals via an
elementary bracketing lemma, a custom 128-bit segmented sieve
(`sieve128.cpp`) handles the small region immediately above Q exactly, and
the published analytic tail bounds of
[Dusart (2010)](https://arxiv.org/abs/1002.0442) and
[Johnston (2022)](https://arxiv.org/abs/2109.02249) certify everything
beyond that with no further computation. Every new term's defining anchors
are cross-verified by two independent `primecount` algorithms (Gourdon vs.
Deleglise–Rivat). See the paper for full details, including the RAM-aware
adaptive scheduling and crash-safe checkpointing needed to run this reliably
on ordinary desktop/laptop hardware.

## Reproducing

```bash
# dependencies
git clone --depth 1 https://github.com/kimwalisch/primecount
cmake -S primecount -B primecount/build -DCMAKE_BUILD_TYPE=Release
cmake --build primecount/build -j$(nproc)
pip install mpmath sympy

g++ -O3 -march=native -fopenmp -std=c++17 src/sieve128.cpp -o sieve128 -lprimesieve

# reproduce OEIS-published terms first (sanity check)
python3 src/ramanujan128.py validate

# a new term
python3 src/ramanujan128.py run 1e20 --D 1e9 --S 1e8 --largest --threads 12 \
    --primecount primecount/build/primecount
```

`data/pi_cache.json` seeds every exact π(x) value already computed, so
reproducing any term in `certificates/` should be near-instant (cache hit)
rather than a full recomputation.

## Status

a(1)–a(22): complete, certified, multiply cross-verified (see the paper,
Section 5 "Verification"). a(23) (Q = 10^23): in progress. The method's
absolute mathematical ceiling is a(26) — beyond that the Johnston (2022)
bound's domain of validity (x ≤ 1.101×10^26) is exceeded and stronger
published tail bounds would be required regardless of hardware.
