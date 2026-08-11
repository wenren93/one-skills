#!/usr/bin/env python3
"""Safe recoverable move of files in batches (<=10), verifying each batch.

Usage:
    safe_delete.py <dest_dir> <path_file>

  dest_dir  : recoverable target folder, e.g. ~/Downloads/_deleted_2026.../
  path_file : text file, one absolute source path per line

Behavior:
  - Creates dest_dir if missing.
  - Moves files in batches of 10; collision-safe renaming on duplicate names.
  - Verifies each batch (original must no longer exist) before continuing.
  - On ANY failure: stops immediately, prints what moved vs not, exits non-zero,
    so nothing is left half-done and originals are never silently lost.

This is the MOVE step only. Run the read-only SCAN and AskUserQuestion
CONFIRM before calling this script.
"""
import shutil
import sys
import os

BATCH = 10


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: safe_delete.py <dest_dir> <path_file>")
    dest = os.path.expanduser(sys.argv[1])
    os.makedirs(dest, exist_ok=True)
    with open(sys.argv[2], encoding="utf-8") as f:
        paths = [l.rstrip("\n") for l in f if l.strip()]

    print("Total: %d files -> %s" % (len(paths), dest))
    idx = 0
    batch = 0
    while idx < len(paths):
        b = paths[idx:idx + BATCH]
        batch += 1
        print("\n=== Batch %d: %d files ===" % (batch, len(b)))
        moved = []
        for p in b:
            try:
                name = os.path.basename(p)
                target = os.path.join(dest, name)
                if os.path.exists(target):
                    base, ext = os.path.splitext(name)
                    i = 1
                    while os.path.exists(target):
                        target = os.path.join(dest, "%s_%d%s" % (base, i, ext))
                        i += 1
                shutil.move(p, target)
                moved.append(p)
                print("moved ->", target)
            except Exception as e:
                print("FAILED:", p, e)
                print("Already moved this batch:", moved)
                print("Not moved:", paths[idx + len(moved):])
                sys.exit(2)
        bad = [p for p in moved if os.path.exists(p)]
        if bad:
            print("WARNING still at original location:", bad)
            sys.exit(3)
        print("Batch %d OK." % batch)
        idx += len(b)
    print("\nALL DONE: %d files moved to %s (recoverable)." % (len(paths), dest))


if __name__ == "__main__":
    main()
