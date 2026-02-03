# LOGO Chromatin/Variant Smoke Test (Line D)

This is a minimal, reproducible smoke test for `GeneBert_predict_vcf_slice_e8.py` using a tiny reference FASTA and a minimal background ECDF.

## Environment
- Python: 3.8.x
- TensorFlow: 2.13.0
- NumPy: 1.23.5

## One-Command Run
```bash
cd /Users/jason/Desktop/LOGO
bash docs/lineD_run.sh
```

Outputs are written next to the VCF input:
- `05_LOGO_Variant_Prioritization/1. script/05_LOGO-C2P/GWAS_C2P/1000G_GWAS_1408.vcf_2bs_5gram_51feature.out.*.csv`

Logs:
- `docs/lineD_logs/session.log`
- `docs/lineD_logs/lineD_run.log`

## What The Script Does
- Patches `pyfasta` for Python 3 (`scripts/patch_pyfasta.py`)
- Uses a minimal reference FASTA: `docs/lineD_ref/male.hg19.fasta`
- Uses a minimal ECDF background: `docs/lineD_background/`
- Forces `max_position_embeddings=512` and `seq-len=256`
- Fixes `num_classes=51` (model output, dummy labels, background JSON)

## Optional: Full hg19 Reference
If you want the full hg19 FASTA (large), run:
```bash
bash docs/lineD_hg19_fetch.sh
```
This downloads to `Genomics/` and is ignored by git.
