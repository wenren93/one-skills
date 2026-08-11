#!/usr/bin/env python3
"""Inject version / source into a SKILL.md frontmatter (used when installing a
third-party skill repo into WorkBuddy). Only adds the fields if missing; never
touches the body. Avoids YAML parsing so it is safe for any valid frontmatter.

Usage: python3 augment_frontmatter.py PATH_TO_SKILL_MD [repo-version]
"""
import re
import sys

path = sys.argv[1]
repo_ver = sys.argv[2] if len(sys.argv) > 2 else "0.0.0"
source = "https://github.com/OWNER/REPO"  # overwrite callers pass real URL


def main() -> None:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        # No frontmatter: wrap with a minimal one.
        new = (
            f"---\nname: unknown\ndescription: (see body)\n"
            f'version: "{repo_ver}"\nsource: {source}\n---\n' + text
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"wrapped: {path}")
        return

    fm = m.group(1)
    body = text[m.end():]
    add = []
    if not re.search(r"(?mi)^version\s*:", fm):
        add.append(f'version: "{repo_ver}"')
    if not re.search(r"(?mi)^source\s*:", fm):
        add.append(f"source: {source}")
    if add:
        new_fm = fm + "\n" + "\n".join(add) + "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write("---\n" + new_fm + "---\n" + body)
        print(f"augmented: {path}")
    else:
        print(f"unchanged: {path}")


if __name__ == "__main__":
    main()
