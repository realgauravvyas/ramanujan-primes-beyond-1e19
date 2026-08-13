#!/usr/bin/env python3
"""
merge_cache.py -- fold prewarm_cache.json into pi_cache.json.

Run this only when the main explore run is STOPPED: a live run holds its own
in-memory copy of the cache and rewrites the whole file after every pi() call,
so writing here at the same time races it -- last writer wins, and whichever
write loses silently vanishes. This script checks for a live process and
refuses to run if it finds one, rather than trusting you to remember.

Any key present in both must agree -- a disagreement would mean two independent
primecount runs produced different values for the same x, which is a red flag,
so this refuses to merge rather than silently picking one.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ramanujan128 import atomic_write_json

MAIN = os.path.join(HERE, "pi_cache.json")
PRE = os.path.join(HERE, "prewarm_cache.json")

def load(p):
    return json.load(open(p)) if os.path.exists(p) else {}

def _live_explore_pid():
    """Best-effort check for a running `ramanujan128.py ... explore` process.
    Returns a pid to report, or None. Never raises -- if we can't tell, we
    proceed (a human running this manually is expected to know what they're
    doing; this is a safety net, not a lock)."""
    try:
        if os.name == "nt":
            import subprocess
            out = subprocess.run(
                ["wmic", "process", "where", "name='python.exe'", "get",
                 "processid,commandline"],
                capture_output=True, text=True, timeout=10).stdout
            for line in out.splitlines():
                if "ramanujan128" in line and "explore" in line:
                    return line.split()[-1]
        else:
            import subprocess
            out = subprocess.run(["pgrep", "-af", "ramanujan128.*explore"],
                                 capture_output=True, text=True, timeout=10).stdout
            if out.strip():
                return out.splitlines()[0].split()[0]
    except Exception:
        pass
    return None

def main():
    pid = _live_explore_pid()
    if pid:
        print(f"REFUSING TO MERGE -- a live 'explore' process appears to be "
              f"running (pid {pid}). Stop it first: merging now would race "
              f"its own writes to pi_cache.json.")
        return 1

    main_c, pre = load(MAIN), load(PRE)
    if not pre:
        print("no prewarm_cache.json (or empty); nothing to merge")
        return 0

    conflicts = [k for k in pre if k in main_c and main_c[k] != pre[k]]
    if conflicts:
        print("REFUSING TO MERGE -- values disagree for:")
        for k in conflicts[:10]:
            print(f"  pi({k}): main={main_c[k]}  prewarm={pre[k]}")
        return 1

    added = [k for k in pre if k not in main_c]
    main_c.update(pre)
    atomic_write_json(MAIN, main_c)
    print(f"merged {len(added)} new values ({len(pre)-len(added)} already present "
          f"and identical -- a free cross-check)")
    print(f"pi_cache.json now holds {len(main_c)} values")
    return 0

if __name__ == "__main__":
    sys.exit(main())
