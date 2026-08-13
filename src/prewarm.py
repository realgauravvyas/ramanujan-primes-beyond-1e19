#!/usr/bin/env python3
"""
prewarm.py -- STANDALONE / manual version of the checkpoint prewarming that
ramanujan128.py's `explore` mode now does automatically on every term.

You normally do NOT need this file: `explore` calls its own prewarm()
internally before each certified_count(), using the SAME checkpoint_targets()
(imported from here, not duplicated -- two copies of "must exactly match the
grid arithmetic" is how that silently drifts).  This script exists for the
one situation `explore` can't handle by itself: recovering after something
external killed the main run mid-checkpoint, when you want to burn idle cores
computing the *remaining* values before restarting it.

DANGER: writes to a SEPARATE file (prewarm_cache.json), never to
pi_cache.json directly, and for a good reason -- a live `explore` process
holds its own in-memory copy of pi_cache.json and rewrites the whole file
after every call, so a second writer would race it. Run this only while
`explore` is NOT running against the same project directory. Merge the
result in with merge_cache.py once `explore` is stopped (merge_cache.py
itself checks for a live process and will refuse to run if it finds one).

Usage:
  python prewarm.py K [--checkpoints N] [--workers W] [--threads T] [--forward]
    K  exponent, i.e. Q = 10**K
"""
import argparse, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ramanujan128 import checkpoint_targets, atomic_write_json  # single source of truth

MAIN_CACHE = os.path.join(HERE, "pi_cache.json")
OUT = os.path.join(HERE, "prewarm_cache.json")

def load(path):
    if os.path.exists(path):
        try:
            return json.load(open(path))
        except Exception:
            return {}
    return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("K", type=int, help="exponent: Q = 10**K")
    ap.add_argument("--D", default="1e9")
    ap.add_argument("--growth", type=float, default=1.7)
    ap.add_argument("--checkpoints", type=int, default=22,
                    help="how many to precompute (a few extra is harmless)")
    ap.add_argument("--workers", type=int, default=2,
                    help="concurrent primecount processes")
    ap.add_argument("--threads", type=int, default=4,
                    help="threads per primecount process")
    ap.add_argument("--primecount", default=os.path.join(HERE, "primecount", "build", "primecount.exe"))
    ap.add_argument("--forward", action="store_true",
                    help="compute low->high (default is high->low, to avoid "
                         "duplicating a live main run working upward)")
    a = ap.parse_args()

    Q, D = 10 ** a.K, int(float(a.D))
    targets = checkpoint_targets(Q, D, a.growth, a.checkpoints)
    if not a.forward:
        targets = targets[::-1]

    done = load(OUT)
    already = load(MAIN_CACHE)
    todo = [t for t in targets
            if str(t) not in done and str(t) not in already]

    print(f"Q = 10^{a.K}")
    print(f"{len(targets)} checkpoint values total; {len(todo)} still to compute")
    print(f"{a.workers} concurrent processes x {a.threads} threads "
          f"({'low->high' if a.forward else 'high->low'})\n", flush=True)
    if not todo:
        print("nothing to do")
        return 0

    lock = threading.Lock()
    t_start = time.time()
    counter = {"n": 0}

    def compute(x):
        t0 = time.time()
        r = subprocess.run([a.primecount, str(x), f"--threads={a.threads}"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  FAILED {x}: {r.stderr.strip()[:200]}", flush=True)
            return
        v = r.stdout.strip()
        if not v.isdigit():
            print(f"  BAD OUTPUT for {x}: {v[:200]}", flush=True)
            return
        with lock:
            done[str(x)] = v
            atomic_write_json(OUT, done)
            counter["n"] += 1
            n, tot = counter["n"], len(todo)
            el = time.time() - t_start
            eta = el / n * (tot - n)
            print(f"  [{n}/{tot}] pi({x}) = {int(v):,}   "
                  f"({time.time()-t0:.0f}s)   elapsed {el/60:.0f}m  ETA {eta/60:.0f}m",
                  flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(compute, todo))

    print(f"\ndone: {len(done)} values in {OUT}  [{(time.time()-t_start)/60:.0f} min]")
    print("merge into pi_cache.json with:  python merge_cache.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
