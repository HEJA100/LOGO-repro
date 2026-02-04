# Line D Full-Run Assets & Entry Points

This note summarizes where the Line D full-run entry points live and what assets they expect.

## Entry Scripts
- Main CLI: `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/GeneBert_predict_vcf_slice_e8.py`
- Example runner: `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/run_GeneBert_919_2002_3357_3540.sh`
- Upstream notes: `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/README.txt`

## CLI Parameters (from help)
See `docs/lineD_cli_help.txt` for full options. Key inputs:
- `--inputfile` (VCF)
- `--backgroundfile` (background directory)
- `--reffasta` (reference FASTA)
- `--weight-path` (weights `.hdf5`)
- `--ngram`, `--vocab-size`, `--we-size`
- `--num-classes`, `--max-position-embeddings`
- `--seq-len`, `--slice-size`, `--stride`, `--batch-size`

## Weights Found in This Repo
These exist locally (small enough to be in git):
- `99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5`
- `99_PreTrain_Model_Weight/LOGO_3_gram_2_layer_8_heads_256_dim_weights_18-0.8937.hdf5`
- `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/genebert_5_gram_2_layer_8_heads_256_dim_wanrenexp_tfrecord_5_1_[baseon27]_weights_119-0.9748-0.9765.hdf5`
- `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/genebert_5_gram_2_layer_8_heads_256_dim_expecto_[mat]_weights_134-0.9633-0.9671.hdf5`
- `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/deepsea_5_gram_2_layer_8_heads_256_dim_weights_128-0.982105-0.983445.hdf5`
- `04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_919/deepsea_5_gram_2_layer_8_heads_256_dim_990_weights_99-0.982516-0.983271.hdf5`

## Background (Full)
The upstream README notes full background distributions are large (20-40GB) and stored under a `2.background/` directory with entries like:
- `1.2002mark_5gram/`
- `2.3357mark_5gram/`
- `5.919mark_5gram/`
- `6.3540mark_5gram/`
No download link is included in the repo; the README says a link will be provided later.

A minimal smoke background exists in `docs/lineD_background/` but is not suitable for full runs.

## Reference (Full)
- Upstream default expects hg19/GRCh37 FASTA.
- `docs/lineD_hg19_fetch.sh` downloads `GCF_000001405.25_GRCh37.p13_genomic.fna.gz` and writes `Genomics/male.hg19.fasta`.
- Full-run wrapper defaults to `docs/lineD_assets/ref/hg19.fa` (ignored by git).

## Vocab / Token Dictionary
No vocab/token-dict file exists in the repo. The model builds a word dict programmatically via:
- `bgi/common/refseq_utils.py:get_word_dict_for_n_gram_number`
`--vocab-size` controls embedding size. The formal weight set described by the request uses `vocab_size=15638` and `we_size=128` (15638x128 embedding). Supply the official vocab file if you have it; otherwise the wrapper will warn and proceed with `--vocab-size 15638` by default.

## External Links Found
- No official download links for full background or full weights were found in the repo docs. The upstream README indicates a link will be provided later.
