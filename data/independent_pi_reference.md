# Independent pi(10^n) reference values (from Wikipedia's prime-counting function table)

Source: https://en.wikipedia.org/wiki/Prime-counting_function -- a table of
record pi(x) computations, independent of and (for n<=22) predating this
project. Fetched and digit-verified 2026-08-12 (two separate fetches,
consistent).

**Use:** cross-check pi(Q) for each new term against these BEFORE or ALONGSIDE
the internal Gourdon-vs-Deleglise-Rivat cross-check. An independent external
source disagreeing (or agreeing) is stronger evidence than checking a tool
against itself twice.

## Already confirmed to match our own computed + cross-verified values exactly

| n | pi(10^n) | matches our pi_Q in certificate? |
|---|---|---|
| 19 | 234,057,667,276,344,607 | yes |
| 20 | 2,220,819,602,560,918,840 | yes (piR_1e20_certificate.json) |
| 21 | 21,127,269,486,018,731,928 | yes (piR_1e21_certificate.json) |
| 22 | 201,467,286,689,315,906,290 | yes (piR_1e22_certificate.json) |

## Not yet computed by us -- check against these when you get there

| n | pi(10^n) | source |
|---|---|---|
| 23 | 1,925,320,391,606,803,968,923 | uncited in table |
| 24 | 18,435,599,767,349,200,867,866 | Buethe, Franke, Jost, Kleinjung; verified by Platt |
| 25 | 176,846,309,399,143,769,411,680 | same four authors |
| 26 | 1,699,246,750,872,437,141,327,603 | D. B. Staple |

Note: a(26) is this method's own mathematical ceiling (see PROJECT_STATE.md /
MIGRATION_NOTES.md) -- the Johnston (2022) tail bound is only valid up to
1.101e26, so a(27) is unreachable regardless of hardware. The table above
covers every term this method can ever produce.

## Not needed (beyond this method's reach anyway)

n=27 (Baugh & Walisch 2015), n=28 (2020), n=29 (Walisch 2022) -- listed here
only for completeness; a(27)+ cannot be certified by this pipeline's tail
bound at all.
