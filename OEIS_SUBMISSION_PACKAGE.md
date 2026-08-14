# OEIS A181671 submission — ready-to-paste package

Everything below is prepped so you just need to register, log in, and paste.
**I cannot do the actual submission — it has to be your account.**

## Step 1: Register (only you can do this)

Go to https://oeis.org/wiki/Special:RequestAccount and register. Account
approval is manual and can take anywhere from minutes to a couple of days.

## Step 2: Log in, go to the sequence, click Edit

https://oeis.org/A181671 → once logged in, an "edit" link appears next to
"history" under the DATA line.

## Step 3: Extend the DATA field

Current published DATA (a(1)–a(17)):
```
1, 10, 72, 559, 4459, 36960, 316066, 2760321, 24491666, 220098288,
1998400235, 18299775876, 168773875190, 1566017986235, 14606736768049,
136860923837558, 1287462389890262
```

New values to append (a(18)–a(23)):
```
12153997721169239, 115097677588071134, 1093039678770734297,
10406559368229726028, 99306360875818676888, 949634047203617038366
```

At this length the inline DATA field will be too long for OEIS's normal
display convention (roughly 3 lines / 200–500 characters) — this is why the
b-file matters (Step 4). It's still fine to paste the full extended DATA
into the edit field; OEIS's own tooling will tell you if it wants the b-file
instead/as well.

## Step 4: Upload the b-file

File ready at `D:\Claude Code\RamanujanPrimes\b181671.txt` — 23 lines,
`n a(n)` format, matches OEIS's required convention exactly (verified
against their own example files). In the edit screen's Links section,
there's an upload slot for exactly this — upload it, and OEIS will
auto-generate the link line for you (something like `Gaurav Vyas, Table of
n, a(n) for n=1..23`).

## Step 5: Suggested COMMENT (paste into the Comments section)

```
a(18) and a(19) were computed via a bracketing-lemma method using exact
pi(x) values from the primecount library, cross-verified across two
independently implemented algorithms (Gourdon and Deleglise-Rivat) and
reproduced independently on a second machine. a(20)-a(23) are certified via
the same method plus a custom 128-bit segmented sieve for the region
immediately above each Q (since general sieve libraries are limited to
2^64), backed by the explicit analytic tail bounds of Dusart (2010,
arXiv:1002.0442) and Johnston (2022, arXiv:2109.02249). a(21)'s and
a(23)'s defining minima were additionally reproduced via direct
Miller-Rabin primality testing, independent of the sieve, and a(23)'s
primary anchor pi(10^23) matches an independently published external
reference value (Wikipedia's prime-counting-function table) exactly. Full
methodology, source code, JSON certificates for every term, and the
complete verification record:
https://github.com/realgauravvyas/ramanujan-primes-beyond-1e19
```

## Step 6: Suggested EXTENSIONS line

Matches the existing convention used by prior contributors on this exact
sequence (e.g. "a(15)-a(17) from Dana Jacobsen, Apr 26 2017"):

```
a(18)-a(23) from Gaurav Vyas, [today's date]
```

## Step 7: Submit for review

Click "These changes are ready for review by an OEIS Editor." Review time
varies from minutes to a couple of months depending on backlog. You can
check your pending changes any time via the "draft edits" link before then.

## Notes

- a(23) is now certified too, so this submission covers a(18)–a(23) in
  one go — no need for a second edit.
- The `more` keyword is already on this sequence, meaning past
  contributors explicitly flagged "please extend this" — your submission
  is directly answering an open request, not an unsolicited addition.
- If an editor asks questions, the GitHub repo (certificates, pi_cache.json,
  full verification writeup) has everything needed to answer them.
