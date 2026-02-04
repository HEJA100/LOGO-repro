# LOGO Line D Full Run (Full Inference)

This is the full inference wrapper for the chromatin/variant pipeline using **real VCF**, **full hg19/GRCh37 reference**, and **official weights/vocab** (15638x128 embedding). It keeps all large assets and outputs out of git.

## Quick Start (2 steps)
1. Fetch/prepare assets
   ```bash
   bash docs/lineD_fetch_assets.sh
   ```
2. Run full inference
   ```bash
   bash docs/lineD_full_run.sh --vcf /path/to/your.vcf
   ```

By default the full-run wrapper is **strict**: it exits if any official asset (ref/bg/weights/vocab/config) is missing, and it requires UCSC `chr*` reference headers.  
For sanity-only runs with repo/smoke assets, add `--allow-fallback`.

## Default Asset Locations (ignored by git)
- Reference: `docs/lineD_assets/ref/hg19.fa`
- Weights: `docs/lineD_assets/weights/` (place a single `.h5/.hdf5` here)
- Vocab: `docs/lineD_assets/vocab/vocab.txt` (optional but recommended)
- Config: `docs/lineD_assets/config/bert_config.json` (optional)
- Background: `docs/lineD_assets/bg_full/` (must contain `*.json` + `*.pkl`)

Outputs and logs:
- Outputs: `docs/lineD_out_full/<run-id>/...`
- Logs: `docs/lineD_logs_full/<run-id>/lineD_full_run.log`

## Parameters (wrapper)
```
--vcf <path>       (required)
--ref <path>       default docs/lineD_assets/ref/hg19.fa
--bg <dir>         default docs/lineD_assets/bg_full
--weights <path>   default docs/lineD_assets/weights
--vocab <path>     default docs/lineD_assets/vocab/vocab.txt
--config <path>    default docs/lineD_assets/config/bert_config.json
--outdir <dir>     default docs/lineD_out_full
--logdir <dir>     default docs/lineD_logs_full
--cuda <int>       default 0
--run-id <string>  default timestamp
```

## Fixed Alignment (to avoid shape mismatch)
The wrapper **forces**:
- `--num-classes 51`
- `--max-position-embeddings 512`
- `--vocab-size 15638` (unless a vocab file is provided and counted)
- `--we-size 128`, `--model-dim 256`, `--transformer-depth 2`, `--num-heads 8`, `--ngram 5`

## Success Markers
Example outputs (official assets):
- `docs/lineD_out_full/<run-id>/<your.vcf>_32bs_5gram_51feature.out.ref.csv`
- `docs/lineD_out_full/<run-id>/<your.vcf>_32bs_5gram_51feature.out.evalue.csv`
- `docs/lineD_logs_full/<run-id>/lineD_full_run.log`

Fallback sanity mode (`--allow-fallback`) will also produce the same file shapes but logs will contain warnings about fallback assets; use it only for pipeline verification.

## Common Errors
- **Missing reference**: run `bash docs/lineD_fetch_assets.sh` or supply `--ref`.
- **Background JSON missing keys 0..50**: use correct background for 51 classes.
- **Weights missing**: place one `.h5/.hdf5` in `docs/lineD_assets/weights/` or pass `--weights`.
- **VCF chr prefix mismatch**: ensure reference and VCF match `chr1` vs `1` naming.
- **Position too long**: `seq_len` must be <= `max_position_embeddings` (fixed at 512).

## Notes
- Full background distributions (JSON + PKL) are large; upstream docs say a link will be provided separately.
- This wrapper writes outputs next to a symlinked VCF in the run output directory to keep git clean.
- If `docs/lineD_assets/weights/` is empty, the wrapper may fall back to a repo pretrain weight for sanity (with a warning). For real full runs, supply the official weights.
