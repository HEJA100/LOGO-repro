#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/logo_figshare_19149827_v2.zip}"
OUT_DIR="${2:-docs/lineD_figshare}"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: ZIP not found: $ZIP_PATH"
  exit 2
fi

unzip -t "$ZIP_PATH" >/dev/null
mkdir -p "$OUT_DIR"
unzip -q "$ZIP_PATH" -d "$OUT_DIR"
find "$OUT_DIR" -type f | head -n 20
