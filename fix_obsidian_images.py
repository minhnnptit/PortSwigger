#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_toc.py  (v2)
----------------
CHI tao MUC LUC tinh hien duoc tren GitHub. KHONG dung toi anh.

Cach lam AN TOAN (duyet tung dong, khong dung regex tham lam):
  - Tim khoi  ```table-of-contents ... ```  va thay bang muc luc tinh
    DUNG TAI VI TRI do.
  - Neu file khong co khoi do -> chen muc luc len DAU file.
  - Lay TAT CA heading tu # den ######  (ke ca H1).
  - Khong dem nham heading nam ben trong code block ```...```.
  - Chay lai nhieu lan duoc (dung cap danh dau an <!-- TOC -->).

CACH DUNG
=========
  cd D:\\ivanesk\\ivanesk315\\Port
  py add_toc.py            <- chay thu, khong sua gi
  py add_toc.py --apply    <- chay that (co backup tu dong)
"""

import os
import re
import sys
import shutil
from datetime import datetime

TOC_MARKER = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def github_anchor(title):
    """Tao anchor giong cach GitHub sinh cho 1 heading (giu chu tieng Viet)."""
    a = title.strip().lower()
    a = re.sub(r"[^\w\s-]", "", a, flags=re.UNICODE)
    a = a.replace(" ", "-")
    return a


def collect_headings(lines):
    """Lay heading, BO QUA dong nam trong code block."""
    headings = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return headings


def build_toc(headings):
    """Tao khoi muc luc tinh tu danh sach heading."""
    if not headings:
        return None
    min_level = min(h[0] for h in headings)
    lines, seen = [], {}
    for level, title in headings:
        anchor = github_anchor(title)
        if anchor in seen:
            seen[anchor] += 1
            anchor = f"{anchor}-{seen[anchor]}"
        else:
            seen[anchor] = 0
        indent = "  " * (level - min_level)
        lines.append(f"{indent}- [{title}](#{anchor})")
    body = "\n".join(lines)
    return f"{TOC_MARKER}\n## Mục lục\n\n{body}\n{TOC_END}\n"


def find_block(lines, opener_substring):
    """
    Tim 1 khoi fence co dong mo chua opener_substring.
    Tra ve (start_index, end_index) bao gom ca dong mo va dong dong,
    hoac None neu khong tim thay.
    """
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("```" + opener_substring):
            # tim dong fence dong gan nhat
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith("```"):
                    return (i, j)
            # khong co dong dong -> chi coi dong mo
            return (i, i)
    return None


def find_existing_toc(lines):
    """Tim muc luc do script tao truoc do (cap <!-- TOC --> ... <!-- /TOC -->)."""
    start = end = None
    for i, line in enumerate(lines):
        if line.strip() == TOC_MARKER:
            start = i
        elif line.strip() == TOC_END:
            end = i
            break
    if start is not None and end is not None and end >= start:
        return (start, end)
    return None


def process_file(md_file, apply):
    with open(md_file, "r", encoding="utf-8") as fh:
        content = fh.read()
    lines = content.split("\n")
    original = content

    # 1) Lay heading (truoc khi xoa gi)
    headings = collect_headings(lines)
    toc_block = build_toc(headings)
    if toc_block is None:
        return 0  # file khong co heading -> bo qua

    toc_lines = toc_block.rstrip("\n").split("\n")

    # 2) Xac dinh vi tri can thay
    existing = find_existing_toc(lines)
    if existing:
        s, e = existing
        new_lines = lines[:s] + toc_lines + lines[e + 1:]
        note = "cap nhat lai muc luc"
    else:
        plugin = find_block(lines, "table-of-contents")
        if plugin:
            s, e = plugin
            new_lines = lines[:s] + toc_lines + lines[e + 1:]
            note = "thay khoi plugin bang muc luc tinh"
        else:
            # chen len dau file
            new_lines = toc_lines + [""] + lines
            note = "them moi muc luc o dau file"

    new_content = "\n".join(new_lines)
    # don dong trong thua
    new_content = re.sub(r"\n{4,}", "\n\n\n", new_content)

    if new_content != original:
        print(f"[FILE] {md_file}\n    -> {note}  ({len(headings)} heading)")
        if apply:
            with open(md_file, "w", encoding="utf-8") as fh:
                fh.write(new_content)
        return 1
    return 0


def main():
    apply = "--apply" in sys.argv
    root = os.getcwd()

    print("=" * 60)
    print("ADD / UPDATE TABLE OF CONTENTS  v2")
    print("Thu muc:", root)
    print("Che do:", "AP DUNG (sua file)" if apply else "THU (dry-run)")
    print("=" * 60)

    md_files = []
    for dirpath, _dirs, files in os.walk(root):
        if "_backup_md" in dirpath or os.sep + ".git" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(".md"):
                md_files.append(os.path.join(dirpath, f))
    print(f"\nTim thay {len(md_files)} file .md.\n")

    if apply:
        backup = os.path.join(root, "_backup_md",
                              datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(backup, exist_ok=True)
        for md in md_files:
            rel = os.path.relpath(md, root)
            dst = os.path.join(backup, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(md, dst)
        print(f"Da backup vao: {backup}\n")

    total = sum(process_file(md, apply) for md in md_files)

    print("\n" + "=" * 60)
    print(f"XONG. {total}/{len(md_files)} file da duoc cap nhat.")
    if not apply:
        print("\n>>> Day la che do THU, chua sua gi.")
        print(">>> Chay that:  py add_toc.py --apply")
    else:
        print("\n>>> Da sua xong. Commit & push:")
        print(">>>   git add .")
        print('>>>   git commit -m "Add table of contents"')
        print(">>>   git push")
    print("=" * 60)


if __name__ == "__main__":
    main()