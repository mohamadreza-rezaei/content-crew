#!/usr/bin/env python3
"""Fail if any non-empty line starts with a Latin letter, digit, URL, '#' or '@'.
Useful for RTL languages (Persian, Arabic, Hebrew) where a leading Latin word
flips the paragraph direction on most platforms.
Usage: check_lines.py file1.txt [file2.txt ...]"""
import re, sys
bad = re.compile(r"^[A-Za-z0-9#@]")
fails = 0
for path in sys.argv[1:]:
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.strip()
        if s and (bad.match(s)):
            fails += 1
            print(f"{path}:{n}: {s[:60]}")
print(f"{fails} failure(s)")
sys.exit(1 if fails else 0)
