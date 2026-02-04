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

## Notes
- The script auto-detects per-chromosome files by name (`chr1`, `chr2`, `chrX`, etc.).
- It attempts to infer column mapping; if inference fails, pass `--cols`, e.g.
  - `--cols chrom=1,pos=2,ref=4,alt=5,id=3,score=6-56`
- If indexed (`.tbi`) files are available, the script uses tabix for fast region queries. Otherwise it streams through the file for the requested positions.
- Use `--make-index` to create bgzip+tabix indexes in `docs/lineD_figshare/indexed/` (original files remain unchanged).

## Strict/full-run remains recommended
For arbitrary or novel variants (non-dbSNP), use the strict/full-run pipeline.
