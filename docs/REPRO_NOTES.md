
## Chromatin Feature demo (Line B: extract_sigvar_demo)

Command:
cd "04_LOGO_Chromatin_Feature/2. result/0. demodata"
python extract_sigvar_demo.py demo_output.csv demo_sig.csv 3357 > extract_sigvar_demo.log 2>&1

Outputs:
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_sig.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.log
- docs/lineB_sha256.txt


## Chromatin Feature demo (Line B: extract_sigvar_demo)

### Command
cd "04_LOGO_Chromatin_Feature/2. result/0. demodata"
python extract_sigvar_demo.py demo_output.csv demo_sig.csv 3357 > extract_sigvar_demo.log 2>&1

### Inputs
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_output.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.py

### Outputs
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_sig.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.log

### Evidence
- SHA256: docs/lineB_inputs_sha256.txt
- demo_sig.csv head: docs/lineB_demo_sig_head.txt
- env/pip freeze: docs/lineB_env.txt


## Chromatin Feature demo (Line C: GeneBert_predict_vcf_slice_e8)

### Command
PYTHONPATH="$PWD" conda run -n logo-lite --no-capture-output python "04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/GeneBert_predict_vcf_slice_e8.py" -h | head -n 80 | tee docs/lineC_genebert_run.log

### Inputs
- 04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/demo.vcf
- BG: MISSING (background distribution)
- REF: MISSING (hg19 fasta)
- 04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/genebert_5_gram_2_layer_8_heads_256_dim_wanrenexp_tfrecord_5_1_[baseon27]_weights_119-0.9748-0.9765.hdf5

### Outputs
- docs/lineC_genebert_run.log
- docs/lineC_inputs_sha256.txt
- docs/lineC_env.txt

### Notes
- Set PYTHONPATH to repo root so the `bgi` package is importable.

## Chromatin/Variant smoke test (Line D)

### Command
bash docs/lineD_run.sh

### Inputs
- 05_LOGO_Variant_Prioritization/1. script/05_LOGO-C2P/GWAS_C2P/1000G_GWAS_1408.vcf
- docs/lineD_background/all_bdg_51_pkl.json
- docs/lineD_background/ecdf.pkl
- docs/lineD_ref/male.hg19.fasta
- 99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5

### Outputs
- 05_LOGO_Variant_Prioritization/1. script/05_LOGO-C2P/GWAS_C2P/1000G_GWAS_1408.vcf_2bs_5gram_51feature.out.*.csv
- docs/lineD_logs/lineD_run.log
- docs/lineD_logs/session.log

### Notes
- `scripts/patch_pyfasta.py` is called in `docs/lineD_run.sh` to fix Python3 compatibility.
- `num_classes` is fixed to 51 and `max_position_embeddings` to 512.
