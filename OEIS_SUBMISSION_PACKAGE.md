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

Keep the comment purely mathematical — OEIS convention puts URLs in the
LINKS section (Step 5b), not in comments; editors move them otherwise.

```
a(18)-a(23) were computed by a bracketing method: exact pi(x) values (from
the primecount library, each anchor cross-verified with two independently
implemented algorithms, Gourdon and Deleglise-Rivat) at O(log) grid
points, an exact 128-bit segmented sieve of the region immediately above
each 10^n, and the explicit analytic tail bounds of Dusart (2010) and
Johnston (2022) beyond the last grid point. The defining minima of a(21)
(at 10^21 + 58) and a(23) (at 10^23 + 42) were additionally reproduced by
direct Miller-Rabin testing, independent of the sieve.
```

## Step 5b: Suggested LINKS entries (added via the Links section)

The b-file link is auto-generated when you upload the file. Additionally
add:

```
Gaurav Vyas, <a href="https://github.com/realgauravvyas/ramanujan-primes-beyond-1e19">Certified computation of a(18)-a(23): paper, source code, and machine-checkable certificates</a>
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
