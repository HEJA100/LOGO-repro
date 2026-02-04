#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.request
from urllib.error import HTTPError, URLError

CHUNK_SIZE = 8 * 1024 * 1024


def fetch_article(article_id):
    url = f"https://api.figshare.com/v2/articles/{article_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "LOGO-repro figshare_fetch"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def build_filter(include):
    if not include:
        return None
    try:
        pattern = re.compile(include)
        return lambda name: bool(pattern.search(name))
    except re.error:
        return lambda name: include in name


def list_files(files, include_fn=None):
    for f in files:
        name = f.get("name", "")
        if include_fn and not include_fn(name):
            continue
        size = f.get("size", "")
        url = f.get("download_url", "")
        print(f"{name}\t{size}\t{url}")


def download_file(f, out_dir, include_fn=None):
    name = f.get("name", "")
    if include_fn and not include_fn(name):
        return
    url = f.get("download_url")
    if not url:
        print(f"SKIP (no url): {name}")
        return
    size = f.get("size")
    target = os.path.join(out_dir, name)
    os.makedirs(out_dir, exist_ok=True)

    if os.path.exists(target):
        if size is not None and os.path.getsize(target) == size:
            print(f"SKIP (exists, size ok): {name}")
            return

    resume_from = 0
    mode = "wb"
    headers = {"User-Agent": "LOGO-repro figshare_fetch"}
    if os.path.exists(target) and size is not None:
        existing = os.path.getsize(target)
        if 0 < existing < size:
            resume_from = existing
            mode = "ab"
            headers["Range"] = f"bytes={resume_from}-"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp, open(target, mode) as out:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
    except HTTPError as e:
        if resume_from > 0:
            print(f"Resume failed, restarting: {name} ({e})")
            if os.path.exists(target):
                os.remove(target)
            download_file(f, out_dir, include_fn)
            return
        raise
    except URLError as e:
        print(f"ERROR downloading {name}: {e}")
        return

    if size is not None and os.path.getsize(target) != size:
        print(f"WARNING size mismatch: {name} expected {size} got {os.path.getsize(target)}")
    else:
        print(f"DOWNLOADED: {name}")


def main():
    p = argparse.ArgumentParser(description="Fetch files from Figshare by article ID.")
    p.add_argument("--article-id", type=int, default=19149827, help="Figshare article id (default: 19149827)")
    p.add_argument("--out", default="docs/lineD_figshare", help="Output directory (default: docs/lineD_figshare)")
    p.add_argument("--include", default=None, help="Regex or substring to filter filenames")
    p.add_argument("--list-only", action="store_true", help="Only list files, do not download")
    args = p.parse_args()

    try:
        meta = fetch_article(args.article_id)
    except HTTPError as e:
        print(f"ERROR fetching article {args.article_id}: {e}")
        return 2
    except URLError as e:
        print(f"ERROR fetching article {args.article_id}: {e}")
        return 2

    files = meta.get("files", [])
    include_fn = build_filter(args.include)

    list_files(files, include_fn=include_fn)
    if args.list_only:
        return 0

    for f in files:
        download_file(f, args.out, include_fn=include_fn)

    return 0


if __name__ == "__main__":
    sys.exit(main())
