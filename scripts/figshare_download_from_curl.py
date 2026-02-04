#!/usr/bin/env python3
import argparse
import os
import re
import shlex
import sys

ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
HTML_HINTS = [b"<html", b"forbidden", b"access denied", b"cloudflare", b"captcha"]
CHUNK = 8 * 1024 * 1024


def is_html_hint(data):
    lower = data.lower()
    return any(h in lower for h in HTML_HINTS)


def parse_curl(cmd_text):
    tokens = shlex.split(cmd_text)
    if not tokens:
        raise ValueError("Empty curl command")
    if tokens[0] == "curl":
        tokens = tokens[1:]

    headers = {}
    data = None
    method = None
    url = None

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("-H", "--header"):
            i += 1
            if i < len(tokens):
                h = tokens[i]
                if ":" in h:
                    k, v = h.split(":", 1)
                    headers[k.strip()] = v.strip()
        elif t in ("-A", "--user-agent"):
            i += 1
            if i < len(tokens):
                headers["User-Agent"] = tokens[i]
        elif t in ("-e", "--referer"):
            i += 1
            if i < len(tokens):
                headers["Referer"] = tokens[i]
        elif t in ("-b", "--cookie"):
            i += 1
            if i < len(tokens):
                cookie_val = tokens[i]
                if os.path.isfile(cookie_val):
                    try:
                        with open(cookie_val, "r") as f:
                            raw = f.read().strip()
                        if raw:
                            headers["Cookie"] = raw
                    except Exception:
                        pass
                else:
                    headers["Cookie"] = cookie_val
        elif t in ("--cookie-jar",):
            i += 1
        elif t in ("-X", "--request"):
            i += 1
            if i < len(tokens):
                method = tokens[i].upper()
        elif t in ("-d", "--data", "--data-raw", "--data-binary"):
            i += 1
            if i < len(tokens):
                data = tokens[i]
                if not method:
                    method = "POST"
        elif t in ("-o", "--output"):
            i += 1
        elif t == "--url":
            i += 1
            if i < len(tokens):
                url = tokens[i]
        else:
            if re.match(r"https?://", t):
                url = t
        i += 1

    if not url:
        raise ValueError("No URL found in curl command")

    return url, headers, method or "GET", data


def download_with_requests(url, headers, method, data, out_path, min_size):
    try:
        import requests
    except Exception:
        print("ERROR: requests is required. Install with: python -m pip install requests")
        return 2

    with requests.request(method, url, headers=headers, data=data, stream=True, allow_redirects=True) as r:
        if r.status_code >= 400:
            print(f"ERROR: HTTP {r.status_code}")
            return 2

        ctype = (r.headers.get("Content-Type") or "").lower()
        if "text/html" in ctype:
            print("ERROR: content-type is text/html (likely blocked HTML/403).")
            return 2

        first = b""
        try:
            first = next(r.iter_content(chunk_size=4096))
        except StopIteration:
            first = b""

        if not any(first.startswith(m) for m in ZIP_MAGIC):
            if is_html_hint(first):
                print("ERROR: response looks like HTML/403, not a ZIP.")
            else:
                print("ERROR: missing ZIP magic header.")
            print("First 200 bytes:")
            print(first[:200])
            return 2

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        tmp = out_path + ".part"
        with open(tmp, "wb") as f:
            f.write(first)
            for chunk in r.iter_content(chunk_size=CHUNK):
                if not chunk:
                    continue
                f.write(chunk)

        size = os.path.getsize(tmp)
        if size < min_size:
            print(f"ERROR: downloaded file too small: {size} bytes (< {min_size})")
            return 2

        os.replace(tmp, out_path)
        return 0


def main():
    p = argparse.ArgumentParser(description="Download Figshare ZIP using a browser 'Copy as cURL' command.")
    p.add_argument("--curl-file", required=True, help="Path to file containing full curl command")
    p.add_argument("--out", required=True, help="Output ZIP path")
    p.add_argument("--min-size", type=int, default=10 * 1024 * 1024, help="Minimum ZIP size in bytes (default: 10MB)")
    args = p.parse_args()

    with open(args.curl_file, "r") as f:
        cmd_text = f.read().strip()

    try:
        url, headers, method, data = parse_curl(cmd_text)
    except ValueError as e:
        print(f"ERROR: {e}")
        return 2

    return download_with_requests(url, headers, method, data, args.out, args.min_size)


if __name__ == "__main__":
    sys.exit(main())
