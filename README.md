# 🔐 Password Cracking with Hashcat

> **Cybersecurity project demonstrating brute-force and dictionary-based password attacks using Hashcat, automated with Python and Bash scripting.**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Bash](https://img.shields.io/badge/Bash-Scripting-green?style=flat-square&logo=gnubash)
![Hashcat](https://img.shields.io/badge/Tool-Hashcat-red?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-purple?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)

---

## 📌 Project Overview

This project was completed as part of the **Monash University Cybersecurity Bootcamp (2024)** and presented at the bootcamp's final conference. It demonstrates the practical mechanics of password cracking using Hashcat — one of the most widely used tools in both offensive security and blue team password auditing workflows.

The project highlights how weak passwords can be compromised rapidly using automated tooling, and why strong password policies and hashing algorithms matter in real-world systems.

---

## 🎯 Objectives

- Demonstrate brute-force and dictionary attacks against hashed password files
- Automate repetitive cracking tasks using Python and Bash scripts
- Understand and compare hash algorithm strength (MD5, SHA-1, bcrypt)
- Communicate security implications to a non-technical audience

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|------|---------|
| Hashcat | GPU-accelerated cracking engine (commands documented below) |
| Python 3 + `hashlib` / `bcrypt` | Hash generation, and a CPU-only dictionary-attack fallback for comparing algorithm strength without a GPU |
| Bash | Orchestration for the Hashcat commands |
| 20-word custom wordlist (`wordlist.txt`) | Dictionary attack source — see note below on why this isn't RockYou |

> **Honesty note:** this repo's actual runnable code (`generate_hashes.py`, `crack_dictionary.py`) uses a small custom wordlist and pure-Python hashing, not a live GPU Hashcat run against RockYou. The Hashcat commands below are documented as the real-world methodology for a GPU-equipped Kali box; the numbers in **Key Findings** come from the Python scripts actually included and run in this repo, not from Hashcat. If you have a GPU and RockYou installed, the Hashcat commands will run as shown and should crack this wordlist's hashes near-instantly for MD5/SHA-1.

---

## 🔬 Methodology

### 1. Hash Generation — `generate_hashes.py`
Reads `wordlist.txt` and writes three hash files — `hashes_md5.txt`, `hashes_sha1.txt`, `hashes_bcrypt.txt` (cost factor 12) — in the one-hash-per-line format Hashcat expects for modes `-m 0`, `-m 100`, and `-m 3200` respectively.

```bash
pip install bcrypt
python3 generate_hashes.py
```

### 2. Dictionary Attack (documented GPU methodology)
```bash
hashcat -m 0   -a 0 hashes_md5.txt    /usr/share/wordlists/rockyou.txt
hashcat -m 100 -a 0 hashes_sha1.txt   /usr/share/wordlists/rockyou.txt
hashcat -m 3200 -a 0 hashes_bcrypt.txt /usr/share/wordlists/rockyou.txt
```

### 3. Brute-Force / Mask Attack (documented GPU methodology)
```bash
hashcat -m 0 -a 3 hashes_md5.txt ?a?a?a?a?a?a
```

### 4. CPU-only Python equivalent — `crack_dictionary.py`
Runs the same dictionary attack against all three hash files using pure Python (`hashlib` for MD5/SHA-1, `bcrypt.checkpw` for bcrypt), with a 20-second time budget on the bcrypt pass since each comparison re-runs the full cost-12 KDF:

```bash
python3 crack_dictionary.py
```

### 5. Results Analysis
Compare crack rate and elapsed time across the three hash files to show algorithm strength in practice, not just in theory.

---

## 📊 Key Findings

Actual output from `crack_dictionary.py` against the 20-password wordlist in this repo:

| Hash type | Cracked | Time | Notes |
|---|---|---|---|
| MD5 (`-m 0`) | 20/20 (100%) | 0.0002s | Every password recovered near-instantly — no salting, no cost factor |
| SHA-1 (`-m 100`) | 20/20 (100%) | 0.0003s | Faster per-hash than MD5 in this run, but equally trivial to brute-force — length alone isn't security |
| bcrypt, cost 12 (`-m 3200`) | 11/20 (55%) | 20.1s (hit time budget) | Only 72 word-comparisons completed in 20 seconds — compare that to MD5/SHA-1 finishing 400 comparisons (20 hashes × 20 words) in under half a millisecond |

That gap — 72 comparisons vs. effectively instant — is the actual argument for bcrypt over MD5/SHA-1: it's not that bcrypt is "unbreakable," it's that the cost factor makes each guess expensive enough that a dictionary attack which finishes in microseconds against MD5 doesn't even finish one pass against bcrypt in 20 seconds on CPU. A real GPU-accelerated Hashcat run against RockYou would crack more of both MD5/SHA-1 (larger wordlist) while bcrypt's relative resistance would still hold, just with different absolute numbers than shown here.

---

## 🔐 Security Implications

This project reinforces why organisations must enforce:
- Minimum password length and complexity requirements
- Use of strong, slow hashing algorithms (bcrypt, Argon2, scrypt)
- Multi-factor authentication as a compensating control
- Regular credential auditing using tools like this in controlled environments

---

## 💡 Lessons Learned

- **The cost factor is the entire point of bcrypt** — not an implementation detail. Seeing 72 comparisons complete against bcrypt in the same 20 seconds that MD5/SHA-1 finished 400 comparisons in under a millisecond made the "slow hash" concept concrete instead of textbook.
- **MD5 and SHA-1 being "broken" doesn't mean broken in a complicated way** — it means a dictionary attack against them is fast enough that elapsed time barely registers. The security problem isn't an exotic flaw, it's that the hash function was never designed to be slow.
- **Hash algorithm choice matters more than password complexity** for this specific attack. An MD5 hash of a complex password is still crackable far faster than a bcrypt hash of a weak one, if the dictionary happens to contain it — the defense needs to be at the storage layer, not just the password policy.

## 🔧 What I'd Improve

- **Run the actual GPU Hashcat commands against a GPU-equipped Kali box with the real RockYou wordlist**, and report those numbers alongside the Python ones here — right now the repo documents the Hashcat methodology but the measured results come from the CPU fallback, and I should close that gap rather than leave the Hashcat commands unverified against real output.
- **Extend `crack_dictionary.py` to support mask/brute-force attacks**, not just dictionary — right now the Python side only replicates methodology #2 (dictionary), while methodology #3 (mask attack) is Hashcat-only and unverified in this repo.
- **Test against a larger, more realistic wordlist** than 20 hand-picked passwords — the 100%/100%/55% figures above would look different (and more representative) against a few thousand real leaked passwords.
- **Add per-hash timing, not just aggregate** — right now I only report total elapsed time per algorithm, not which specific passwords took longest, which would be more useful for understanding where in the wordlist bcrypt's time budget actually got spent.

---

## ⚠️ Legal & Ethical Disclaimer

This project was conducted in a controlled, isolated lab environment for **educational purposes only** as part of an accredited cybersecurity bootcamp. Password cracking against systems without explicit written authorisation is illegal. All techniques demonstrated here should only be applied in authorised penetration testing or security auditing contexts.

---

## 👤 Author

**Sagar Bidari**
CompTIA Security+ CE | Monash University Cybersecurity Bootcamp Graduate
🌐 [bidarisagar.com](https://bidarisagar.com) | 💼 [LinkedIn](https://linkedin.com/in/sagarbidari)
