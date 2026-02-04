BASE=$(conda info --base)
source "$BASE/etc/profile.d/conda.sh"
conda activate logo-lite
mkdir -p docs/lineD_logs docs/lineD_out docs/lineD_ref docs/lineD_background
python scripts/patch_pyfasta.py
if [ ! -f docs/lineD_background/ecdf.pkl ] || [ ! -f docs/lineD_background/all_bdg_51_pkl.json ]; then
  python docs/lineD_make_background.py
fi
python docs/lineD_prepare_inputs.py
if [ ! -f docs/lineD_ref/male.hg19.fasta ]; then
  python docs/lineD_make_min_ref.py
fi
PYTHONPATH="$PWD:$PWD/docs/lineD_background:$PYTHONPATH" python "04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/GeneBert_predict_vcf_slice_e8.py" \
  --inputfile "docs/lineD_out/lineD_input.vcf" \
  --backgroundfile "docs/lineD_background" \
  --reffasta "docs/lineD_ref/male.hg19.fasta" \
  --weight-path "99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5" \
  --task test \
  --epochs 1 \
  --steps-per-epoch 1 \
  --ngram 5 \
  --vocab-size 3138 \
  --transformer-depth 2 \
  --num-heads 8 \
  --model-dim 256 \
  --we-size 128 \
  --num-classes 51 \
  --seq-len 256 \
  --max-position-embeddings 512 \
  --max-position 1000000 \
  --max-variants 20 \
  --batch-size 2 \
  --slice-size 10 \
  --stride 1 \
  --pool-size 1 \
  --verbose 2 \
  > docs/lineD_logs/lineD_run.log 2>&1
