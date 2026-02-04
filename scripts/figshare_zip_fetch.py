#!/usr/bin/env python3
import argparse
import os
import sys
import time
import urllib.request
from urllib.error import HTTPError, URLError

DEFAULT_URL = "https://figshare.com/ndownloader/articles/19149827/versions/2"
DEFAULT_REFERER = "https://doi.org/10.6084/m9.figshare.19149827.v2"
DEFAULT_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
HTML_HINTS = [b"<html", b"forbidden", b"access denied", b"cloudflare", b"captcha"]

CHUNK = 8 * 1024 * 1024


def is_html_hint(data):
    lower = data.lower()
    return any(h in lower for h in HTML_HINTS)


def head_or_range_probe(url, headers, probe_bytes=4096):
    try:
        req = urllib.request.Request(url, method="HEAD", headers=headers)
        with urllib.request.urlopen(req) as resp:
            return resp, b""
    except Exception:
        pass
    req = urllib.request.Request(url, headers={**headers, "Range": f"bytes=0-{probe_bytes-1}"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read(probe_bytes)
        return resp, data


def print_probe(resp, data):
    status = getattr(resp, "status", None) or resp.getcode()
    ctype = resp.headers.get("Content-Type", "")
    clen = resp.headers.get("Content-Length", "")
    final_url = resp.geturl()
    print(f"status={status}")
    print(f"content-type={ctype}")
    print(f"content-length={clen}")
    print(f"final-url={final_url}")
    if data:
        if is_html_hint(data):
            print("probe-body-hint=HTML/403")


def validate_prefix(resp, prefix):
    ctype = (resp.headers.get("Content-Type", "") or "").lower()
    if "text/html" in ctype:
        return False, "content-type text/html"
    if is_html_hint(prefix):
        return False, "body contains HTML/403/Cloudflare"
    if not any(prefix.startswith(m) for m in ZIP_MAGIC):
        return False, "missing ZIP magic"
    return True, ""


def download(url, out_path, headers, min_size, retries, retry_delay):
    attempt = 0
    while attempt <= retries:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                if status >= 400:
                    raise HTTPError(url, status, f"HTTP {status}", resp.headers, None)

                prefix = resp.read(4096)
                ok, reason = validate_prefix(resp, prefix)
                if not ok:
                    raise ValueError(f"Download is not ZIP: {reason}")

                os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                tmp_path = out_path + ".part"
                with open(tmp_path, "wb") as out:
                    out.write(prefix)
                    while True:
                        chunk = resp.read(CHUNK)
                        if not chunk:
                            break
                        out.write(chunk)

                size = os.path.getsize(tmp_path)
                if size < min_size:
                    raise ValueError(f"Downloaded file too small: {size} bytes (< {min_size})")

                os.replace(tmp_path, out_path)
                return 0
        except (HTTPError, URLError, ValueError) as e:
            attempt += 1
            if attempt > retries:
                print(f"ERROR: {e}")
                print("This looks like HTML/403 instead of a ZIP.")
                print("Alternative: open the Figshare page in a browser, click 'Download all',")
                print("then use \"Copy as cURL\" and run:")
                print("  python scripts/figshare_download_from_curl.py --curl-file /tmp/figshare.curl.txt --out /tmp/logo_figshare_19149827_v2.zip")
                print("  bash scripts/figshare_unzip_into.sh /tmp/logo_figshare_19149827_v2.zip docs/lineD_figshare")
                return 2
            time.sleep(retry_delay)
    return 2


def main():
    p = argparse.ArgumentParser(description="Robust Figshare ZIP downloader with validation.")
    p.add_argument("--url", default=DEFAULT_URL, help=f"Download URL (default: {DEFAULT_URL})")
    p.add_argument("--out", default="/tmp/logo_figshare_19149827_v2.zip", help="Output ZIP path")
    p.add_argument("--retry", type=int, default=5, help="Retry count (default: 5)")
    p.add_argument("--retry-delay", type=int, default=2, help="Retry delay seconds (default: 2)")
    p.add_argument("--ua", default=DEFAULT_UA, help="User-Agent")
    p.add_argument("--referer", default=DEFAULT_REFERER, help="Referer")
    p.add_argument("--probe-only", action="store_true", help="Probe HEAD/GET without downloading")
    p.add_argument("--min-size", type=int, default=50 * 1024 * 1024, help="Minimum ZIP size in bytes (default: 50MB)")
    args = p.parse_args()

    headers = {
        "User-Agent": args.ua,
        "Referer": args.referer,
        "Accept": "*/*",
    }

    if args.probe_only:
        try:
            resp, data = head_or_range_probe(args.url, headers)
            print_probe(resp, data)
            return 0
        except Exception as e:
            print(f"ERROR: probe failed: {e}")
            return 2

    return download(args.url, args.out, headers, args.min_size, args.retry, args.retry_delay)


if __name__ == "__main__":
    sys.exit(main())
