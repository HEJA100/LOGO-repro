# Figshare Lookup Route (Line D)

This is an **optional** lookup-based route that annotates variants with **precomputed LOGO dbSNP scores** from Figshare (DOI: 10.6084/m9.figshare.19149827.v2). It does **not** replace strict/full-run inference, and is best for known dbSNP variants.

## When to use
- You have a VCF with known dbSNP variants.
- You want fast lookup instead of running the model.

## Quick start
1) List available files (no download):
```
python scripts/figshare_fetch.py --article-id 19149827 --list-only
```

2) Download files to the local cache (default: `docs/lineD_figshare`):
```
python scripts/figshare_fetch.py --article-id 19149827 --out docs/lineD_figshare
```

3) Lookup on a small VCF:
```
python scripts/logo_lookup_figshare.py \
  --vcf docs/lineD_out/lineD_input.vcf \
  --figshare-dir docs/lineD_figshare \
  --out docs/lineD_out/lineD_input.vcf.logo_figshare.tsv
```

The output TSV contains original VCF columns plus lookup details:
- `matched_rows`, `match_note`, `hit_file`, `raw_hit`

## Recommended download flow (Copy as cURL)
When Cloudflare blocks direct downloads, use the browser's **Copy as cURL** flow:

1) In the browser, click **Download all** on Figshare, then **Copy as cURL**. Save it to `/tmp/figshare.curl.txt`.

2) Download using the cURL file:
```
python scripts/figshare_download_from_curl.py \
  --curl-file /tmp/figshare.curl.txt \
  --out /tmp/logo_figshare_19149827_v2.zip
```

3) Unzip into the figshare directory:
```
bash scripts/figshare_unzip_into.sh /tmp/logo_figshare_19149827_v2.zip docs/lineD_figshare
```

4) Run lookup:
```
python scripts/logo_lookup_figshare.py \
  --vcf docs/lineD_out/lineD_input.vcf \
  --figshare-dir docs/lineD_figshare \
  --out docs/lineD_out/lineD_input.vcf.logo_figshare.tsv
```

## Troubleshooting: downloaded file is not a zip (118 bytes / HTML / 403)
If you see a tiny file (e.g., 118 bytes) or unzip errors, you likely downloaded an HTML/403 page instead of the ZIP.

1) Probe only (no download):
```
python scripts/figshare_zip_fetch.py --probe-only
```

2) Download the ZIP with validation:
```
python scripts/figshare_zip_fetch.py --out /tmp/logo_figshare_19149827_v2.zip
```

3) Unzip into the figshare directory:
```
bash scripts/figshare_unzip_into.sh /tmp/logo_figshare_19149827_v2.zip docs/lineD_figshare
```

4) Run lookup:
```
python scripts/logo_lookup_figshare.py \
  --vcf docs/lineD_out/lineD_input.vcf \
  --figshare-dir docs/lineD_figshare \
  --out docs/lineD_out/lineD_input.vcf.logo_figshare.tsv
```

If you are blocked by Cloudflare/403, use the **Copy as cURL** flow above.

## Notes
- The script auto-detects per-chromosome files by name (`chr1`, `chr2`, `chrX`, etc.).
- The **full Figshare ZIP** contains `*_FSResult.vcf.tar.gz` (one per chromosome). These files are **CSV-like** (comma-separated, not standard VCF). The lookup script automatically switches to **VCF-TAR mode** when it detects these files and will match by `CHROM/POS/REF/ALT`.
- It attempts to infer column mapping; if inference fails, pass `--cols`, e.g.
  - `--cols chrom=1,pos=2,ref=4,alt=5,id=3,score=6-56`
- If indexed (`.tbi`) files are available, the script uses tabix for fast region queries. Otherwise it streams through the file for the requested positions.
- Use `--make-index` to create bgzip+tabix indexes in `docs/lineD_figshare/indexed/` (original files remain unchanged).

## Full ZIP (VCF-TAR mode) quick chain
```
mkdir -p docs/lineD_figshare/extracted_full
bash scripts/figshare_unzip_into.sh docs/lineD_figshare/LOGO_dbSNP_score_chr_full.zip docs/lineD_figshare/extracted_full
python scripts/logo_lookup_figshare.py \
  --vcf docs/lineD_out/lineD_input.vcf \
  --figshare-dir docs/lineD_figshare/extracted_full \
  --out docs/lineD_out/lineD_input.vcf.logo_figshare.tsv
awk -F'\t' 'NR>1 && $6>0 {c++} END{print "matched_variants:", c+0}' docs/lineD_out/lineD_input.vcf.logo_figshare.tsv
```

## Strict/full-run remains recommended
For arbitrary or novel variants (non-dbSNP), use the strict/full-run pipeline.
