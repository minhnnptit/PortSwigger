#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_toc.py
----------
CHI lam mot viec: dam bao moi file .md deu co MUC LUC tinh hien duoc tren GitHub.
KHONG dung toi anh, khong dung toi noi dung khac.

  - File CO khoi ```table-of-contents``` (cua plugin Obsidian) -> thay bang muc luc tinh.
  - File KHONG co -> chen muc luc moi ngay sau tieu de H1 dau tien.
  - File da co muc luc do script nay tao -> cap nhat lai (khong chen trung).

CACH DUNG
=========
1. Dat file nay vao thu muc goc cua vault (vd: D:\\ivanesk\\ivanesk315\\Port).
2. Mo PowerShell tai thu muc do.
3. Chay thu (khong sua gi):   py add_toc.py
4. Chay that:                 py add_toc.py --apply

AN TOAN
=======
- Khi --apply, moi file .md goc duoc backup vao _backup_md/<thoi gian>/.
"""

import os
import re
import sys
import shutil
from datetime import datetime

TOC_BLOCK_RE = re.compile(
    r"```table-of-contents\s*\n(?:.*?\n)?```", re.IGNORECASE | re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+.*$", re.MULTILINE)

# Cap danh dau an de chay lai nhieu lan ma khong chen trung.
# GitHub khong hien thi comment HTML nay.
TOC_MARKER = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"
EXISTING_TOC_RE = re.compile(
    re.escape(TOC_MARKER) + r".*?" + re.escape(TOC_END), re.DOTALL)


def github_anchor(title):
    """Tao anchor giong cach GitHub sinh ra cho 1 heading."""
    a = title.strip().lower()
    a = re.sub(r"[^\w\s-]", "", a, flags=re.UNICODE)  # giu chu tieng Viet
    a = a.replace(" ", "-")
    return a


def build_toc(content):
    """Sinh muc luc tinh tu cac heading cap 2 tro xuong."""
    headings = [(h, t) for h, t in HEADING_RE.findall(content) if len(h) >= 2]
    if not headings:
        return None
    min_level = min(len(h[0]) for h in headings)
    lines, seen = [], {}
    for hashes, title in headings:
        level = len(hashes)
        anchor = github_anchor(title)
        if anchor in seen:
            seen[anchor] += 1
            anchor = f"{anchor}-{seen[anchor]}"
        else:
            seen[anchor] = 0
        indent = "  " * (level - min_level)
        lines.append(f"{indent}- [{title}](#{anchor})")
    body = "\n".join(lines)
    return f"{TOC_MARKER}\n## Mục lục\n\n{body}\n{TOC_END}"


def process_file(md_file, apply):
    with open(md_file, "r", encoding="utf-8") as fh:
        content = fh.read()
    original = content
    note = ""

    # bo khoi plugin ```table-of-contents``` neu con
    had_plugin_toc = bool(TOC_BLOCK_RE.search(content))
    content = TOC_BLOCK_RE.sub("", content)

    toc = build_toc(content)
    if toc:
        if EXISTING_TOC_RE.search(content):
            content = EXISTING_TOC_RE.sub(lambda m: toc, content, count=1)
            note = "cap nhat lai muc luc"
        else:
            m = H1_RE.search(content)
            if m:
                pos = m.end()
                content = content[:pos] + "\n\n" + toc + content[pos:]
            else:
                content = toc + "\n\n" + content
            note = ("thay khoi plugin bang muc luc tinh"
                    if had_plugin_toc else "them moi muc luc")
    else:
        if had_plugin_toc:
            note = "xoa khoi plugin (file khong co heading)"

    # don dong trong thua
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    if content != original:
        print(f"[FILE] {md_file}\n    toc: {note}")
        if apply:
            with open(md_file, "w", encoding="utf-8") as fh:
                fh.write(content)
        return 1
    return 0


def main():
    apply = "--apply" in sys.argv
    root = os.getcwd()

    print("=" * 60)
    print("ADD / UPDATE TABLE OF CONTENTS  (chi muc luc, khong dung anh)")
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
    print(f"\nTim thay {len(md_files)} file .md.")

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
    