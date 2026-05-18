#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_obsidian_images.py
----------------------
Chuyển cú pháp ảnh wikilink của Obsidian  ![[Pasted image 2026....png]]
sang cú pháp Markdown chuẩn mà GitHub hiểu  ![](images/Pasted%20image%202026....png)

CÁCH DÙNG
=========
1. Đặt file này vào THƯ MỤC GỐC của vault Obsidian (cùng cấp với các topic).
2. Mở terminal / cmd tại thư mục đó.
3. Chạy:   python fix_obsidian_images.py
4. Lần đầu nó chạy ở chế độ THỬ (dry-run): chỉ in ra những gì SẼ đổi,
   KHÔNG sửa file. Xem kết quả, nếu ổn thì chạy lại với:
       python fix_obsidian_images.py --apply

AN TOÀN
=======
- Khi chạy --apply, toàn bộ file .md gốc được backup vào thư mục
  "_backup_md/" trước khi sửa. Muốn khôi phục chỉ cần copy đè lại.
- Script KHÔNG xoá hay đổi tên file ảnh. Chỉ sửa link trong file .md.
"""

import os
import re
import sys
import shutil
import urllib.parse
from datetime import datetime

# Phần mở rộng ảnh được nhận diện
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}

# --- Regex bắt 2 loại cú pháp Obsidian -------------------------------------
# 1) Wikilink:  ![[ten anh.png]]  hoặc  ![[ten anh.png|300]]
WIKILINK_RE = re.compile(r"!\[\[([^\]\|]+?)(?:\|[^\]]*)?\]\]")
# 2) Markdown nhưng đường dẫn còn dấu cách chưa encode: ![alt](Pasted image x.png)
MD_SPACE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*\s[^)]*)\)")


def build_image_index(root):
    """Quét toàn bộ vault, tạo map: tên_file_ảnh (lowercase) -> đường dẫn tuyệt đối."""
    index = {}
    for dirpath, _dirs, files in os.walk(root):
        # Bỏ qua thư mục backup và .git
        if "_backup_md" in dirpath or os.sep + ".git" in dirpath:
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in IMG_EXT:
                key = f.lower()
                # Nếu trùng tên ở 2 thư mục, giữ cái đầu nhưng cảnh báo
                if key in index:
                    print(f"  [!] Trùng tên ảnh: {f}  (có ở nhiều thư mục)")
                else:
                    index[key] = os.path.join(dirpath, f)
    return index


def rel_url(md_file, img_abspath):
    """Tính đường dẫn tương đối từ file .md tới ảnh, rồi URL-encode (xử lý %20)."""
    rel = os.path.relpath(img_abspath, os.path.dirname(md_file))
    rel = rel.replace(os.sep, "/")  # GitHub dùng dấu /
    # Encode từng phần, giữ nguyên dấu /
    parts = [urllib.parse.quote(p) for p in rel.split("/")]
    return "/".join(parts)


def process_file(md_file, img_index, apply):
    with open(md_file, "r", encoding="utf-8") as fh:
        content = fh.read()
    original = content
    changes = []

    # --- Xử lý wikilink ![[...]] ------------------------------------------
    def repl_wiki(m):
        name = m.group(1).strip()
        base = os.path.basename(name)  # phòng khi có đường dẫn trong wikilink
        hit = img_index.get(base.lower())
        if hit:
            url = rel_url(md_file, hit)
            new = f"![]({url})"
            changes.append(f"    {m.group(0)}  ->  {new}")
            return new
        else:
            changes.append(f"    [KHÔNG TÌM THẤY ẢNH] {m.group(0)}  (giữ nguyên)")
            return m.group(0)

    content = WIKILINK_RE.sub(repl_wiki, content)

    # --- Xử lý markdown link còn dấu cách ---------------------------------
    def repl_space(m):
        alt, path = m.group(1), m.group(2).strip()
        # Bỏ qua link http
        if path.startswith("http"):
            return m.group(0)
        encoded = "/".join(urllib.parse.quote(p) for p in path.replace("\\", "/").split("/"))
        new = f"![{alt}]({encoded})"
        changes.append(f"    {m.group(0)}  ->  {new}")
        return new

    content = MD_SPACE_RE.sub(repl_space, content)

    if content != original:
        print(f"\n[FILE] {md_file}")
        for c in changes:
            print(c)
        if apply:
            with open(md_file, "w", encoding="utf-8") as fh:
                fh.write(content)
        return len([c for c in changes if "->" in c])
    return 0


def main():
    apply = "--apply" in sys.argv
    root = os.getcwd()

    print("=" * 60)
    print("FIX OBSIDIAN IMAGE LINKS  ->  GITHUB MARKDOWN")
    print("Thư mục:", root)
    print("Chế độ:", "ÁP DỤNG (sẽ sửa file)" if apply else "THỬ (dry-run, không sửa)")
    print("=" * 60)

    print("\n[1] Đang quét ảnh trong vault...")
    img_index = build_image_index(root)
    print(f"    Tìm thấy {len(img_index)} file ảnh.")

    print("\n[2] Đang quét file .md...")
    md_files = []
    for dirpath, _dirs, files in os.walk(root):
        if "_backup_md" in dirpath or os.sep + ".git" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(".md"):
                md_files.append(os.path.join(dirpath, f))
    print(f"    Tìm thấy {len(md_files)} file .md.")

    # Backup trước khi sửa
    if apply:
        backup_dir = os.path.join(root, "_backup_md",
                                  datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(backup_dir, exist_ok=True)
        for md in md_files:
            rel = os.path.relpath(md, root)
            dst = os.path.join(backup_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(md, dst)
        print(f"\n[3] Đã backup {len(md_files)} file vào: {backup_dir}")

    print("\n[4] Đang xử lý...")
    total = 0
    for md in md_files:
        total += process_file(md, img_index, apply)

    print("\n" + "=" * 60)
    print(f"XONG. Tổng cộng {total} link ảnh được chuyển đổi.")
    if not apply:
        print("\n>>> Đây mới là chế độ THỬ. Chưa có gì bị sửa.")
        print(">>> Nếu kết quả ở trên ổn, chạy lại lệnh:")
        print(">>>     python fix_obsidian_images.py --apply")
    else:
        print("\n>>> Đã sửa xong. Giờ commit & push lên GitHub:")
        print(">>>     git add .")
        print('>>>     git commit -m "Fix Obsidian image links"')
        print(">>>     git push")
    print("=" * 60)


if __name__ == "__main__":
    main()
