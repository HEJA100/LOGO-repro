# LOGO Chromatin/Variant Smoke Test (Line D)

Minimal, reproducible smoke test for `GeneBert_predict_vcf_slice_e8.py` with auto-generated background and reference.

## Environment
- Python: 3.8.x
- TensorFlow: 2.13.0
- NumPy: 1.23.5 (or 1.24+ with in-repo fixes)

## One-Command Run
```bash
git clone <repo-url>
cd <repo-folder>
bash docs/lineD_run.sh
```

## What It Does
- Patches `pyfasta` for Python 3 via `scripts/patch_pyfasta.py`
- Auto-generates minimal background ECDF in `docs/lineD_background/` (ignored by git)
- Auto-generates minimal reference FASTA in `docs/lineD_ref/` (<=1,000,000 bp, ignored by git)
- Creates a small VCF subset in `docs/lineD_out/lineD_input.vcf` (ignored by git)
- Runs a 1-epoch / 1-step smoke test with fixed parameters

## Classes (51)
This smoke test uses **51 classes** to match the model output dimension and the background ECDF mapping. The pipeline expects the background JSON to provide one ECDF per class (keys `0..50`). Using 25 would cause shape mismatches in the generator/model/output.

## Outputs (ignored by git)
- `docs/lineD_out/lineD_input.vcf_2bs_5gram_51feature.out.*.csv`
- `docs/lineD_logs/lineD_run.log`
- `docs/lineD_logs/session.log`

Example success markers:
- `docs/lineD_out/lineD_input.vcf_2bs_5gram_51feature.out.ref.csv`
- `docs/lineD_out/lineD_input.vcf_2bs_5gram_51feature.out.evalue.csv`
- `docs/lineD_logs/lineD_run.log`

## Common Errors
- **BG/REF missing**: `docs/lineD_run.sh` auto-generates them on first run.
- **Shape mismatch (25 vs 51)**: ensure `--num-classes 51` and background JSON has keys `0..50`.
- **pyfasta errors**: re-run `python scripts/patch_pyfasta.py`.

## Optional Full hg19 Reference
Download full hg19 (large, ignored by git):
```bash
bash docs/lineD_hg19_fetch.sh
```
