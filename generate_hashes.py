#!/usr/bin/env python3
"""
generate_hashes.py — create MD5, SHA-1, and bcrypt hash files from a
plaintext wordlist, simulating a leaked-credential file for each hash
algorithm so the cracking methodology can be compared side by side.

Output files use the plain hash-per-line format Hashcat expects for
each mode:
  hashes_md5.txt    -> hashcat -m 0
  hashes_sha1.txt   -> hashcat -m 100
  hashes_bcrypt.txt -> hashcat -m 3200

Requires: pip install bcrypt
"""

import hashlib
import sys

try:
    import bcrypt
except ImportError:
    print("Missing dependency: pip install bcrypt", file=sys.stderr)
    sys.exit(1)

WORDLIST_PATH = "wordlist.txt"
BCRYPT_COST = 12  # matches the cost factor referenced in the README


def load_passwords(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def main():
    passwords = load_passwords(WORDLIST_PATH)
    print(f"[*] Loaded {len(passwords)} passwords from {WORDLIST_PATH}")

    with open("hashes_md5.txt", "w") as f_md5, \
         open("hashes_sha1.txt", "w") as f_sha1, \
         open("hashes_bcrypt.txt", "w") as f_bcrypt:

        for pwd in passwords:
            f_md5.write(hashlib.md5(pwd.encode()).hexdigest() + "\n")
            f_sha1.write(hashlib.sha1(pwd.encode()).hexdigest() + "\n")

            bcrypt_hash = bcrypt.hashpw(
                pwd.encode(), bcrypt.gensalt(rounds=BCRYPT_COST)
            )
            f_bcrypt.write(bcrypt_hash.decode() + "\n")

    print("[+] Wrote hashes_md5.txt, hashes_sha1.txt, hashes_bcrypt.txt")
    print(f"[+] bcrypt cost factor: {BCRYPT_COST}")


if __name__ == "__main__":
    main()
