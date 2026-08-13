#!/usr/bin/env python3
"""
ramanujan128.py -- certified pi_R(Q) for Q far beyond 2^64.

pi_R(Q) = min_{y>=Q} f(y),   f(y) = pi(y) - pi(floor(y/2)).

Three regions, three tools:

  [Q, Q+D]      exact sieved walk         (sieve128, 128-bit)
  [Q+D, Y]      GRID BRACKETING           (exact pi at O(log) points only)
  [Y, inf)      Johnston / Dusart bounds  (analytic)

The middle region is what makes Q = 10^20 possible.  Brute-force sieving it
would mean 4.4e12 numbers AND a bucket sieve.  Instead we use:

  BRACKETING LEMMA.  For a <= y <= b,
        f(y) = pi(y) - pi(y//2) >= pi(a) - pi(b//2) = f(a) - [pi(b//2)-pi(a//2)]
  since pi is nondecreasing.  So exact pi values at the two ENDPOINTS lower-bound
  f on the whole interval -- no sieving inside at all.

Because f drifts upward at rate ~1/(2 log Q), the bound survives geometric
growth of the offset (y-Q), so O(log(W/D)) grid points cover the entire window.
Cost becomes ~15-25 primecount calls instead of 10^13 sieve operations.

Usage:
  python3 ramanujan128.py validate            # reproduce OEIS A181671 terms
  python3 ramanujan128.py run 1e20            # compute a new term
  python3 ramanujan128.py run 1e20 --largest  # also find the record prime
"""
import argparse, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from mpmath import mp, mpf, li, log, sqrt, floor

mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__))
SIEVE = os.path.join(HERE, "sieve128.exe" if os.name == "nt" else "sieve128")
CACHE = os.path.join(HERE, "pi_cache.json")
TIMING_LOG = os.path.join(HERE, "term_timings.csv")
JOHNSTON_LIMIT = mpf('1.101e26')

def _log_timing(label, Q, seconds, grid_points):
    new = not os.path.exists(TIMING_LOG)
    with open(TIMING_LOG, "a", encoding="utf-8") as f:
        if new:
            f.write("term,Q,seconds,minutes,grid_points,finished_at\n")
        f.write(f"{label},{Q},{seconds},{seconds/60:.2f},{grid_points},"
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")

A181671 = {9: 24491666, 10: 220098288, 11: 1998400235, 12: 18299775876,
           13: 168773875190, 14: 1566017986235, 15: 14606736768049,
           16: 136860923837558, 17: 1287462389890262,
           18: 12153997721169239, 19: 115097677588071134}

# --------------------------------------------------------------- pi(x), cached
_cache = {}
_cache_lock = threading.Lock()          # prewarming writes from several threads

def atomic_write_json(path, obj, **json_kwargs):
    """Write JSON so a kill mid-write can never leave a truncated/corrupt file.

    open(path, "w") truncates immediately, before any bytes land -- a kill in
    that window (this session force-killed processes repeatedly) leaves the
    file empty or broken. Writing to a sibling temp file and os.replace()-ing
    it into place is atomic on both Windows and POSIX: the target either has
    the old complete contents or the new complete contents, never a partial
    write.
    """
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = __import__("tempfile").mkstemp(dir=d, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, **json_kwargs)
        os.replace(tmp, path)          # atomic rename, same filesystem
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise

def _load():
    global _cache
    if os.path.exists(CACHE):
        _cache = json.load(open(CACHE))
def _save():
    atomic_write_json(CACHE, _cache)

def _run_primecount(x, primecount, threads, verbose, tag, extra_args=()):
    """One primecount subprocess call; returns the exact pi(x) value."""
    cmd = [primecount, str(x), "--status", *extra_args]
    if threads:
        cmd.append(f"--threads={threads}")
    t0 = time.time()
    # --status just gives us a heartbeat so we know it's alive; we don't
    # show primecount's internal phase/percent breakdown, only elapsed time.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    last_num = None
    last_print = 0.0
    if verbose:
        print(f"      {tag}: counting exact primes (can take a while)...", end="", flush=True)
    for line in proc.stdout:
        s = line.strip()
        if s.isdigit():
            last_num = s
            continue
        now = time.time()
        if verbose and now - last_print >= 2.0:
            last_print = now
            print(f"\r      {tag}: still counting...  {now - t0:5.0f}s elapsed   ", end="", flush=True)
    proc.wait()
    if proc.returncode != 0 or last_num is None:
        if verbose:
            print()
        raise RuntimeError(f"primecount failed on {x} (exit {proc.returncode})")
    v = int(last_num)
    if verbose:
        print(f"\r      {tag}: done = {v:,}   ({time.time()-t0:.0f}s)" + " " * 25, flush=True)
    return v

def pi(x, primecount="primecount", threads=None, verbose=True, label=None,
      verify_independent=False):
    """Exact pi(x) for arbitrary x (primecount handles up to 10^31).

    If verify_independent, the value is computed TWICE with two different
    primecount algorithms (Gourdon, the default, and Deleglise-Rivat) and
    an exception is raised if they disagree -- a much stronger guarantee
    than re-running the same algorithm twice, used for record-defining
    anchors.
    """
    k = str(x)
    tag = label or f"pi({x:.3e})"
    if k in _cache:
        if verbose:
            print(f"      {tag}: already known (cached) = {int(_cache[k]):,}", flush=True)
        return int(_cache[k])
    v = _run_primecount(x, primecount, threads, verbose, tag)
    if verify_independent:
        v2 = _run_primecount(x, primecount, threads, verbose, tag + " [cross-check, Deleglise-Rivat]",
                             extra_args=["--deleglise-rivat"])
        if v2 != v:
            raise RuntimeError(f"CROSS-CHECK MISMATCH for {tag}: "
                               f"Gourdon={v:,} vs Deleglise-Rivat={v2:,}")
        if verbose:
            print(f"      {tag}: cross-check PASSED -- Gourdon and Deleglise-Rivat agree", flush=True)
    _cache[k] = str(v); _save()
    return v

# --------------------------------------------------- parallel checkpoint prewarm
# A single primecount process only saturates ~4 of 12 logical cores (its Sigma
# and Phi0 phases are largely serial), so most of the machine sits idle.  The
# grid checkpoints are deterministic -- offset_{n+1} = int(offset_n * growth) --
# and the two calls per checkpoint are independent, so they can be computed
# ahead of the main loop, several at a time, and simply handed over via _cache.
#
# Only CHECKPOINTS are prewarmed, never the anchors: pi() returns early on a
# cache hit, so prewarming pi(Q)/pi(Q/2) would silently skip their independent
# cross-verification.

def checkpoint_targets(Q, D, growth, n):
    """The exact pi() arguments certified_count's grid loop will ask for."""
    targets, y = [], Q + D
    for _ in range(n):
        step = int((y - Q) * growth)
        nxt = Q + step
        targets.append(nxt // 2)
        targets.append(nxt)
        y = nxt
    return targets

def predict_checkpoints(Q, D, growth, margin=2):
    """How many grid checkpoints the loop will need (li-estimate of the count;
    verified to reproduce a(20)'s 16 exactly).  Margin covers estimate slop."""
    Q = mpf(Q)
    m = int(li(Q) - li(Q / 2))
    y = Q + D
    n = 0
    while int(floor(G(y))) < m and n < 90:
        n += 1
        y = Q + (y - Q) * mpf(growth)
    return n + margin

def _free_ram_gb():
    """Physically available RAM, or None if we cannot tell.

    Tried in order: Windows API, Linux /proc/meminfo, macOS/BSD via psutil if
    present. Returning None (rather than guessing) makes safe_workers() fall
    back to "no limit" explicitly, not silently -- see its docstring.
    """
    if os.name == "nt":
        try:
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullAvailPhys / (1024 ** 3)
        except Exception:
            return None
    try:
        # Linux: MemAvailable already accounts for reclaimable cache/buffers,
        # which is what actually matters for "can a new process fit".
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, _, rest = line.partition(":")
                info[k] = rest.strip()
        kb = info.get("MemAvailable") or info.get("MemFree")
        if kb:
            return int(kb.split()[0]) / (1024 ** 2)
    except Exception:
        pass
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return None

def safe_workers(Q, requested, verbose=True):
    """Cap concurrency so the batch cannot exhaust RAM.

    Footprint measured across two machines: 0.36 GB at 5e20, 0.95 GB at 5e21,
    1.26 GB at 1e22 (laptop) and 5.9 GB at 1e23 (desktop, measured directly
    ahead of the a(23) run). The old exponent (0.42, fit from only the first
    three points) underpredicted the 1e23 figure by ~1.8x. Refit as
    exponent 0.67 anchored + 15% margin at Q=1e22, which matches both the
    1e22 and 1e23 measurements and stays conservative (over- rather than
    under-predicts) at the smaller Q values where it matters less. An OOM
    kill mid-call would waste hours, so size off the measured rate and keep
    headroom.
    """
    free = _free_ram_gb()
    if free is None:
        return requested
    per = max(0.2, 1.45 * (float(Q) / 1e22) ** 0.67)
    fits = max(1, int(free * 0.95 / per))
    n = max(1, min(requested, fits))
    if verbose and n < requested:
        print(f"  [ram] {free:.1f} GB free, ~{per:.1f} GB per call -> "
              f"using {n} workers instead of {requested}", flush=True)
    return n

def prewarm(Q, D, growth, primecount, workers, threads, verbose=True):
    """Fill _cache with checkpoint values, `workers` primecount calls at once."""
    workers = safe_workers(Q, workers, verbose)
    n = predict_checkpoints(Q, D, growth)
    targets = [t for t in checkpoint_targets(Q, D, growth, n)
               if str(t) not in _cache]
    if not targets:
        return
    if verbose:
        print(f"  [0/3] prewarming ~{n} checkpoints "
              f"({len(targets)} values, {workers} at a time on {threads} threads each)",
              flush=True)
    t0 = time.time()
    done = {"n": 0}

    def one(x):
        r = subprocess.run([primecount, str(x), f"--threads={threads}"],
                           capture_output=True, text=True)
        v = r.stdout.strip()
        if r.returncode != 0 or not v.isdigit():
            return                      # leave it; the main loop will compute it
        with _cache_lock:
            _cache[str(x)] = v
            _save()                     # atomic (see atomic_write_json)
            done["n"] += 1
            k, tot = done["n"], len(targets)
            el = time.time() - t0
            if verbose:
                print(f"      prewarm {k}/{tot}   elapsed {el/60:.0f}m   "
                      f"ETA {el/k*(tot-k)/60:.0f}m", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, targets))
    if verbose:
        print(f"  [0/3] prewarm done [{(time.time()-t0)/60:.0f}m]", flush=True)

# ------------------------------------------------------- analytic tail bounds
def G(y):
    """Johnston 2022 lower bound for f(y); valid 5314 <= y <= 1.101e26."""
    y = mpf(y)
    err = (sqrt(y) * log(y) + sqrt(y / 2) * log(y / 2)) / (8 * mp.pi)
    return li(y) - li(y / 2) - err

def dusart_ok(m):
    """f(y) >= m for all y >= 1.101e26, via Dusart 2010."""
    y = JOHNSTON_LIMIT; L = log(y); L2 = log(y / 2)
    lb = y / L * (1 + 1 / L + 2 / L**2)
    ub = (y / 2) / L2 * (1 + 1 / L2 + mpf('2.334') / L2**2)
    return (lb - ub) >= m

# ----------------------------------------------------------- exact local walk
def walk(Q, L, S, verbose=True):
    """Exact walk of f on (Q, Q+L]; returns (min_rel, min_off, end_rel)."""
    t0 = time.time()
    n_chunks = max(1, -(-L // S))
    if verbose:
        print(f"      scanning the {L:.2e}-wide region right after Q "
              f"(~{n_chunks} chunks)...", end="", flush=True)
    proc = subprocess.Popen([SIEVE, "walk", str(Q), str(L), str(S)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    seg = 0
    for line in proc.stderr:
        if line.strip().startswith("seg"):
            seg += 1
            if verbose:
                print(f"\r      scanning near Q... chunk {seg}/{n_chunks}   "
                      f"({time.time()-t0:.0f}s)   ", end="", flush=True)
    out, _ = proc.communicate()
    if proc.returncode != 0:
        if verbose:
            print()
        raise RuntimeError(f"sieve128 walk failed (exit {proc.returncode})")
    d = dict(l.split() for l in out.strip().split("\n"))
    if verbose:
        print(f"\r      scanned near Q: done   ({time.time()-t0:.0f}s)" + " " * 25, flush=True)
    return int(d["min_rel"]), int(d["min_off"]), int(d["end_rel"])

# ------------------------------------------------------------ main certifier
def certified_count(Q, D=10**9, S=10**8, growth=1.7, threads=None,
                    primecount="primecount", verbose=True, term_label=None,
                    verify_anchors=False):
    """Certified pi_R(Q).  Returns (count, info dict).

    verify_anchors=True cross-checks the two record-defining anchors
    (pi(Q), pi(Q/2)) with an independent algorithm -- use for genuinely
    new terms, not needed for validate/replay of already-known ones.
    """
    Q = int(Q)
    t0 = time.time()
    label = term_label or f"Q={Q:.3e}"
    if verbose:
        print()
        print("=" * 64)
        print(f"  NOW WORKING ON: {label}   (Q = {Q:,})")
        if verify_anchors:
            print("  (main anchors will be independently cross-verified)")
        print("=" * 64)
        print("  step 1 of 3 -- exact prime counts near Q")
    piQ = pi(Q, primecount, threads, verbose, label="pi(Q)", verify_independent=verify_anchors)
    piH = pi(Q // 2, primecount, threads, verbose, label="pi(Q/2)", verify_independent=verify_anchors)
    fQ = piQ - piH
    if verbose:
        print("  step 2 of 3 -- scanning the region right after Q")
    mn_rel, mn_off, end_rel = walk(Q, D, S, verbose)
    m = fQ + mn_rel                       # running minimum, exact on [Q, Q+D]
    y = Q + D
    f_y = fQ + end_rel                    # exact f at the right edge
    pi_half = {Q // 2: piH,
               y // 2: pi(y // 2, primecount, threads, verbose, label="pi((Q+D)/2)")}
    if verbose:
        print("  step 3 of 3 -- extending the safety net out to the analytic tail")
    grid = 0
    while int(floor(G(y))) < m:
        step = int((y - Q) * growth)
        nxt = Q + step
        # bracketing lemma: min over [y, nxt] >= f(y) - (pi(nxt//2) - pi(y//2))
        while True:
            if nxt // 2 not in pi_half:
                pi_half[nxt // 2] = pi(nxt // 2, primecount, threads, verbose,
                                       label=f"checkpoint {grid + 1} (pi half)")
            ph = pi_half[nxt // 2]
            bound = f_y - (ph - pi_half[y // 2])
            if bound >= m:
                break
            # bound too weak: refine. NOTE this makes the checkpoint land
            # somewhere prewarm()/checkpoint_targets() did NOT predict (they
            # only model the non-refined path) -- any prewarmed value for the
            # original nxt is simply wasted, not wrong; correctness is
            # unaffected since pi() below computes whatever is actually
            # needed, cache hit or not. Flagged because it's never happened
            # in a(20)/a(21) and is worth noticing if it starts happening.
            if verbose:
                print(f"\n    [refine] bound {bound:,} < min {m:,} at Q+{nxt-Q:.3e}; "
                      f"halving step (prewarm prediction no longer applies here)",
                      flush=True)
            step //= 2
            nxt = Q + step
            if nxt - y < 10**6:
                raise RuntimeError("grid refinement stalled; raise D")
        pn = pi(nxt, primecount, threads, verbose, label=f"checkpoint {grid + 1}")
        f_n = pn - pi_half[nxt // 2]
        if f_n < m:                       # cannot happen if bound held, but check
            raise RuntimeError("grid endpoint below running minimum")
        grid += 1
        if verbose:
            print(f"    checkpoint {grid} verified safe out to Q+{nxt-Q:.2e}  [OK]", flush=True)
        y, f_y = nxt, f_n
    assert dusart_ok(m), "far-tail check failed"
    info = dict(Q=Q, pi_Q=piQ, pi_halfQ=piH, f_at_Q=fQ, count=m,
                min_offset=mn_off, walk_width=D, grid_points=grid,
                window_end=y, seconds=round(time.time() - t0),
                anchors_cross_verified=verify_anchors)
    _log_timing(label, Q, info['seconds'], grid)
    if verbose:
        mins, secs = divmod(info['seconds'], 60)
        print("-" * 64)
        print(f"  RESULT  {label} = {m:,}")
        print(f"  took {mins}m {secs}s, {grid} safety checkpoints")
        print("-" * 64)
    return m, info

NOTES = os.path.join(HERE, "NOTES.md")
def _write_notes(k, m, info):
    """Append a human-readable record of a newly-found term to NOTES.md."""
    is_new_file = not os.path.exists(NOTES)
    with open(NOTES, "a", encoding="utf-8") as f:
        if is_new_file:
            f.write("# Ramanujan primes beyond a(19) -- new terms\n\n")
            f.write(
                "OEIS A181671 publishes real data only through a(17). a(18) and a(19) "
                "were prior self-computed extensions with this same pipeline, never "
                "independently published. Everything from a(20) onward here is a "
                "genuinely new, first-time result.\n\n"
                "None of these terms were reachable with the old primesieve-based "
                "pipeline: it sieves the *entire* certification window, which needs "
                "128-bit positions above 2^64 and roughly 10^13 sieve operations at "
                "Q=10^20 alone -- infeasible past ~10^19. This custom pipeline "
                "(see README.md) instead proves a lower bound using the bracketing "
                "lemma: exact pi(x) (via `primecount`) at O(log) endpoints, plus an "
                "exact 128-bit sieve walk (`sieve128`) only in a small window near Q, "
                "backed by the published Johnston (2022) and Dusart (2010) analytic "
                "tail bounds. That is what makes terms this large computable at all.\n\n"
            )
        f.write(f"## a({k}) = {m:,}\n\n")
        f.write(f"- Q = 10^{k}\n")
        f.write(f"- found: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        mins, secs = divmod(info['seconds'], 60)
        f.write(f"- wall time: {mins}m {secs}s ({info['seconds']}s)\n")
        f.write(f"- safety checkpoints (grid bracketing): {info['grid_points']}\n")
        f.write(f"- main anchors pi(Q), pi(Q/2) cross-verified with two independent "
                f"primecount algorithms (Gourdon vs Deleglise-Rivat): "
                f"{'yes, agreed' if info.get('anchors_cross_verified') else 'no'}\n")
        if info.get("largest_R"):
            f.write(f"- largest Ramanujan prime <= 10^{k}: {info['largest_R']:,}\n")
        f.write(f"- certificate file: piR_1e{k}_certificate.json\n\n")

def largest_R(Q, count, L=10**9, S=10**8, verbose=True):
    """Largest Ramanujan prime <= Q (index = count)."""
    piQ = int(_cache[str(Q)]); piH = int(_cache[str(Q // 2)])
    delta = count - 1 - (piQ - piH)
    r = subprocess.run([SIEVE, "back", str(Q), str(L), str(S), str(delta)],
                       stdout=subprocess.PIPE, stderr=None, text=True)
    if r.returncode != 0 or r.stdout.startswith("NOTFOUND"):
        return None
    x = int(r.stdout.split()[1])
    return x + 1

# ------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["validate", "run", "explore"])
    ap.add_argument("Q", nargs="?", default="1e20")
    ap.add_argument("--D", default="1e9", help="exact-walk width near Q")
    ap.add_argument("--S", default="1e8", help="sieve segment size")
    ap.add_argument("--growth", type=float, default=1.7)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--primecount", default="primecount")
    ap.add_argument("--largest", action="store_true")
    ap.add_argument("--upto", type=int, default=13,
                    help="validate exponents 9..UPTO")
    ap.add_argument("--workers", type=int, default=3,
                    help="concurrent primecount processes during prewarm "
                         "(one process alone only uses ~4 of 12 cores)")
    ap.add_argument("--pc-threads", type=int, default=4,
                    help="threads per primecount process during prewarm")
    ap.add_argument("--no-prewarm", action="store_true",
                    help="disable parallel checkpoint prewarming")
    a = ap.parse_args()
    _load()
    D, S = int(float(a.D)), int(float(a.S))

    if a.mode == "validate":
        terms = list(range(9, a.upto + 1))
        print(f"Checking a(9) .. a({a.upto}) against known values ({len(terms)} terms total).")
        print("a(9)-a(17) are real published OEIS data; anything above that is only")
        print("a self-consistency check against earlier runs of this same code.\n")
        ok = True
        results = []
        for i, k in enumerate(terms, 1):
            print(f"[[ term {i} of {len(terms)}: a({k}) ]]")
            m, info = certified_count(10**k, D=min(D, 10**8), S=S,
                                      growth=a.growth, threads=a.threads,
                                      primecount=a.primecount, term_label=f"a({k})")
            exp = A181671[k]
            good = (m == exp)
            ok &= good
            mark = "MATCH" if good else f"MISMATCH (expected {exp:,})"
            results.append((k, m, good))
            print(f"  >> a({k}) {mark}\n")
        print("=" * 64)
        for k, m, good in results:
            print(f"  {'OK ' if good else 'XX '} a({k}) = {m:,}")
        print("=" * 64)
        print("VALIDATION", "PASSED - all terms matched" if ok else "FAILED - see MISMATCH above")
        return 0 if ok else 1

    if a.mode == "explore":
        k = int(a.Q) if "e" not in a.Q.lower() else int(round(log(mpf(a.Q), 10)))
        print(f"Exploring new terms starting at a({k}), continuing indefinitely "
              f"(each term ~4.6x more expensive than the last). Stop with Ctrl+C.\n")
        while True:
            Qk = 10 ** k
            label = f"a({k})"
            if not a.no_prewarm:
                prewarm(Qk, D, a.growth, a.primecount, a.workers, a.pc_threads)
            m, info = certified_count(Qk, D=D, S=S, growth=a.growth, threads=a.threads,
                                      primecount=a.primecount, term_label=label,
                                      verify_anchors=True)
            print(f"\n*** {label} = {m:,}   (NEW, previously unknown term) ***")
            print("Searching for the actual largest Ramanujan prime <= Q "
                  "(quick sieve scan, no more heavy counting)...")
            R = largest_R(Qk, m, L=D, S=S)
            if R:
                print(f"largest Ramanujan prime <= 10^{k}:  R_{m:,} = {R:,}")
                info["largest_R"] = R
            out = f"piR_1e{k}_certificate.json"
            atomic_write_json(out, info, indent=1, default=str)
            print("certificate ->", out)
            _write_notes(k, m, info)
            print(f"note appended -> {NOTES}\n")
            k += 1
        return 0

    Q = int(float(a.Q)) if "e" in a.Q.lower() else int(a.Q)
    print(f"Computing a NEW, previously unknown term at Q={a.Q} ...")
    m, info = certified_count(Q, D=D, S=S, growth=a.growth, threads=a.threads,
                              primecount=a.primecount, term_label=f"a(new) at Q={a.Q}",
                              verify_anchors=True)
    print(f"\n*** pi_R({a.Q}) = {m:,} ***")
    if a.largest:
        print("Now searching for the actual largest Ramanujan prime <= Q "
              "(this is a quick sieve scan, no more heavy counting)...")
        R = largest_R(Q, m, L=D, S=S)
        if R:
            print(f"largest Ramanujan prime <= {a.Q}:  R_{m:,} = {R:,}")
            info["largest_R"] = R
    out = f"piR_{a.Q}_certificate.json"
    atomic_write_json(out, info, indent=1, default=str)
    print("certificate ->", out)
    _write_notes(int(round(log(mpf(a.Q), 10))), m, info)
    print(f"note appended -> {NOTES}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
