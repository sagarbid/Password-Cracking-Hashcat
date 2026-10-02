#!/usr/bin/env python3
"""
crack_dictionary.py — pure-Python dictionary attack against the hash
files produced by generate_hashes.py. This is a CPU-bound stand-in for
the GPU-accelerated `hashcat -a 0` runs documented in the README; it
exists so the crack-rate comparison between MD5/SHA-1/bcrypt can be
demonstrated and timed without requiring a GPU or the Hashcat binary.

Usage:
    python crack_dictionary.py

Requires: pip install bcrypt
"""

import hashlib
import sys
import time

try:
    import bcrypt
except ImportError:
    print("Missing dependency: pip install bcrypt", file=sys.stderr)
    sys.exit(1)


def load_lines(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def crack_md5(hashes: list[str], wordlist: list[str]) -> dict:
    start = time.perf_counter()
    cracked = {}
    for h in hashes:
        for word in wordlist:
            if hashlib.md5(word.encode()).hexdigest() == h:
                cracked[h] = word
                break
    elapsed = time.perf_counter() - start
    return {"cracked": cracked, "elapsed_sec": elapsed, "total": len(hashes)}


def crack_sha1(hashes: list[str], wordlist: list[str]) -> dict:
    start = time.perf_counter()
    cracked = {}
    for h in hashes:
        for word in wordlist:
            if hashlib.sha1(word.encode()).hexdigest() == h:
                cracked[h] = word
                break
    elapsed = time.perf_counter() - start
    return {"cracked": cracked, "elapsed_sec": elapsed, "total": len(hashes)}


def crack_bcrypt(hashes: list[str], wordlist: list[str], time_budget_sec: float = 20.0) -> dict:
    """bcrypt is deliberately slow — each comparison re-runs the full cost-12
    KDF, so this enforces a time budget and reports how far it got rather
    than running to completion (which would take far longer than MD5/SHA-1)."""
    start = time.perf_counter()
    cracked = {}
    checked = 0
    for h in hashes:
        h_bytes = h.encode()
        for word in wordlist:
            checked += 1
            if time.perf_counter() - start > time_budget_sec:
                elapsed = time.perf_counter() - start
                return {
                    "cracked": cracked,
                    "elapsed_sec": elapsed,
                    "total": len(hashes),
                    "checked": checked,
                    "timed_out": True,
                }
            if bcrypt.checkpw(word.encode(), h_bytes):
                cracked[h] = word
                break
    elapsed = time.perf_counter() - start
    return {"cracked": cracked, "elapsed_sec": elapsed, "total": len(hashes), "checked": checked, "timed_out": False}


def report(name: str, result: dict) -> None:
    pct = (len(result["cracked"]) / result["total"] * 100) if result["total"] else 0
    timeout_note = " (time budget reached — see checked count)" if result.get("timed_out") else ""
    print(f"\n[{name}]")
    print(f"  Cracked: {len(result['cracked'])}/{result['total']} ({pct:.0f}%)")
    print(f"  Time:    {result['elapsed_sec']:.4f}s{timeout_note}")
    if "checked" in result:
        print(f"  Comparisons attempted: {result['checked']}")


def main():
    wordlist = load_lines("wordlist.txt")

    print(f"Dictionary attack using {len(wordlist)}-word list against each hash type.\n"
          f"(CPU-only Python implementation — see README for the GPU-accelerated Hashcat commands.)")

    md5_hashes = load_lines("hashes_md5.txt")
    report("MD5 — hashcat -m 0", crack_md5(md5_hashes, wordlist))

    sha1_hashes = load_lines("hashes_sha1.txt")
    report("SHA-1 — hashcat -m 100", crack_sha1(sha1_hashes, wordlist))

    bcrypt_hashes = load_lines("hashes_bcrypt.txt")
    report("bcrypt (cost 12) — hashcat -m 3200", crack_bcrypt(bcrypt_hashes, wordlist))


if __name__ == "__main__":
    main()
