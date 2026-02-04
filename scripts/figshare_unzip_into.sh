#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/logo_figshare_19149827_v2.zip}"
OUT_DIR="${2:-docs/lineD_figshare}"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: ZIP not found: $ZIP_PATH"
  exit 2
fi

if ! unzip -t "$ZIP_PATH" >/dev/null 2>&1; then
  echo "ERROR: unzip -t failed. You likely downloaded HTML/403 instead of a ZIP."
  echo "Hint: use browser 'Copy as cURL' and run:"
  echo "  python scripts/figshare_download_from_curl.py --curl-file /tmp/figshare.curl.txt --out /tmp/logo_figshare_19149827_v2.zip"
  exit 2
fi
mkdir -p "$OUT_DIR"
unzip -q "$ZIP_PATH" -d "$OUT_DIR"
find "$OUT_DIR" -type f | head -n 20
