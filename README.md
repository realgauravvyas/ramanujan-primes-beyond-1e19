<div align="center">
<img src="assets/ramanujan.jpg" width="220" alt="Srinivasa Ramanujan" />
</div>

<h1 align="center">Ramanujan Primes Beyond 10¹⁹</h1>

<p align="center">
<b>Extending OEIS A181671 — computed entirely on a laptop and a desktop, no institute, no cluster.</b>
</p>

<div align="center">

![Status](https://img.shields.io/badge/a(1)--a(23)-certified-6C63FF?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-6C63FF?style=flat-square)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/-C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![LaTeX](https://img.shields.io/badge/-LaTeX-008080?style=flat-square&logo=latex&logoColor=white)

**[Read the paper →](paper/main.pdf)**

</div>

---

A Ramanujan prime $R_n$ is the least integer such that $\pi(x) - \pi(x/2) \geq n$
for all $x \geq R_n$ — Ramanujan's own 1919 strengthening of Bertrand's postulate.
[OEIS A181671](https://oeis.org/A181671) tabulates how many such primes lie below
each power of ten, but publishes real data only through $10^{17}$. This repo pushes
that to $10^{23}$ — certified, cross-verified, and reproducible.

```
while (curious) {
    pick_an_equation();
    make_it_certified();
    ask("did two different algorithms agree?");
}
```

---

### 🔭 The result

| $k$ | $a(k)$ | status |
|---|---|---|
| 1–17 | — | OEIS A181671 published |
| 18–19 | 12,153,997,721,169,239 / 115,097,677,588,071,134 | prior, unpublished — independently reproduced on a second machine here |
| 20 | 1,093,039,678,770,734,297 | **new**, cross-algorithm verified |
| 21 | 10,406,559,368,229,726,028 | **new**, cross-algorithm + Miller–Rabin verified |
| 22 | 99,306,360,875,818,676,888 | **new**, cross-algorithm verified |
| 23 | 949,634,047,203,617,038,366 | **new**, cross-algorithm + Miller–Rabin + external π(x) reference verified |

Full table, methodology, and every verification layer: **[`paper/main.pdf`](paper/main.pdf)**.

---

### 🧭 How it works

Sieving directly to certify $a(k)$ at $Q=10^{20}$ and beyond is infeasible — the
certification window alone spans roughly $10^{12}$ integers, entirely above the
$2^{64}$ limit of general-purpose sieve libraries. Instead:

1. **Bracketing lemma** — exact $\pi(x)$ at $O(\log)$ grid endpoints
   (via [`primecount`](https://github.com/kimwalisch/primecount)) lower-bounds
   $f(x)=\pi(x)-\pi(x/2)$ across entire intervals, no sieving of the interior.
2. **Custom 128-bit segmented sieve** (`sieve128.cpp`) — handles the small region
   immediately above $Q$ exactly, since it's the one part the bracketing lemma
   can't cover and general sieve libraries stop at $2^{64}$.
3. **Analytic tail bounds** — [Dusart (2010)](https://arxiv.org/abs/1002.0442) and
   [Johnston (2022)](https://arxiv.org/abs/2109.02249) certify everything beyond
   the sieved-and-bracketed region, for free.
4. **Cross-algorithm verification** — every new term's defining anchors are
   computed independently by two `primecount` algorithms (Gourdon and
   Deleglise–Rivat) and must agree exactly.

---

### 📁 Repo layout

| path | contents |
|---|---|
| `paper/` | LaTeX source + PDF — full paper, a(1)–a(23) |
| `src/` | `ramanujan128.py` (orchestration driver), `sieve128.cpp` (128-bit sieve), build scripts |
| `certificates/` | Machine-checkable JSON certificates for a(1)–a(23), incl. an independent cross-machine reproduction of a(18)/a(19) |
| `data/` | `pi_cache.json` (every exact π(x) ever computed), timing tables, independent external π(x) reference |
| `TIME_COMPLEXITY_ANALYSIS.md` | Empirical scaling: ~3.5–3.7× per decade of Q |
| `OEIS_SUBMISSION_NOTES.md` | Submission-readiness notes for A181671 |

---

### ⚙️ Reproducing

```bash
git clone --depth 1 https://github.com/kimwalisch/primecount
cmake -S primecount -B primecount/build -DCMAKE_BUILD_TYPE=Release
cmake --build primecount/build -j$(nproc)
pip install mpmath sympy

g++ -O3 -march=native -fopenmp -std=c++17 src/sieve128.cpp -o sieve128 -lprimesieve

python3 src/ramanujan128.py validate                 # reproduce OEIS-published terms first
python3 src/ramanujan128.py run 1e20 --D 1e9 --S 1e8 --largest --threads 12 \
    --primecount primecount/build/primecount
```

`data/pi_cache.json` seeds every exact π(x) already computed, so reproducing any
term in `certificates/` should be a cache hit, not a full recomputation.

---

### ✅ Verified, not just computed

- Anchors cross-checked by two independent `primecount` algorithms — exact agreement
- a(21)'s and a(23)'s defining dips independently reproduced via direct Miller–Rabin testing, bypassing the sieve entirely
- a(23)'s primary anchor π(Q) matches an independently published external reference value exactly
- a(18)/a(19) independently recomputed on a second machine, matched exactly
- Growth-ratio (9.47× → 9.56× per decade) and analytic li(Q) − li(Q/2) agreement, both clean
- Dusart/Johnston bound formulas checked against the original papers, not just transcribed on trust

See the paper's Verification section for the full list.

---

### 🤖 How this was built

The paper's prose and this project's code (`ramanujan128.py`, `sieve128.cpp`, and
the orchestration/verification tooling) were developed with the assistance of
Claude (Anthropic), directed and reviewed throughout by the author, who verified
every mathematical claim and result against primary sources and independent
computation. See the paper's AI Disclosure section for the full statement.

---

### License

[MIT](LICENSE) for the code. The paper is © the author; cite it if you use the
results.
