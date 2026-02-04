#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$ROOT_DIR/docs/lineD_assets"
REF_DIR="$ASSETS/ref"
WEIGHT_DIR="$ASSETS/weights"
VOCAB_DIR="$ASSETS/vocab"
CONFIG_DIR="$ASSETS/config"
BG_DIR="$ASSETS/bg_full"

mkdir -p "$REF_DIR" "$WEIGHT_DIR" "$VOCAB_DIR" "$CONFIG_DIR" "$BG_DIR"

echo "Asset directories created under: $ASSETS"

echo "=== Reference (hg19/GRCh37) ==="
REF_FASTA="$REF_DIR/hg19.fa"
REF_GZ="$REF_DIR/GCF_000001405.25_GRCh37.p13_genomic.fna.gz"
if [[ ! -f "$REF_FASTA" ]]; then
  echo "Downloading GRCh37/hg19 reference (large)..."
  curl -L -C - -o "$REF_GZ" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.25_GRCh37.p13/GCF_000001405.25_GRCh37.p13_genomic.fna.gz"
  gzip -dc "$REF_GZ" > "$REF_FASTA"
  echo "Saved: $REF_FASTA"
else
  echo "Found: $REF_FASTA"
fi

if command -v samtools >/dev/null 2>&1; then
  if [[ ! -f "$REF_FASTA.fai" ]]; then
    samtools faidx "$REF_FASTA"
    echo "Generated: $REF_FASTA.fai"
  fi
else
  echo "samtools not found; to index, run: samtools faidx $REF_FASTA"
fi

echo "=== Weights ==="
if ls "$WEIGHT_DIR"/*.h5 "$WEIGHT_DIR"/*.hdf5 >/dev/null 2>&1; then
  echo "Found weights in $WEIGHT_DIR"
else
  echo "No weights found in $WEIGHT_DIR. You can use one of the repo weights or supply official weights:"
  echo "  99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5"
  echo "  04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/genebert_5_gram_2_layer_8_heads_256_dim_wanrenexp_tfrecord_5_1_[baseon27]_weights_119-0.9748-0.9765.hdf5"
  echo "Copy or symlink into: $WEIGHT_DIR"
  echo "Expected for formal weights: vocab_size=15638, we_size=128"
fi

echo "=== Vocab / Config ==="
if [[ ! -f "$VOCAB_DIR/vocab.txt" ]]; then
  echo "No vocab file found at $VOCAB_DIR/vocab.txt"
  echo "If you have official vocab/token dict, place it here."
fi
if [[ ! -f "$CONFIG_DIR/bert_config.json" ]]; then
  echo "No config found at $CONFIG_DIR/bert_config.json"
  echo "If you have official config, place it here."
fi

echo "=== Background (full) ==="
if ls "$BG_DIR"/*.json >/dev/null 2>&1; then
  echo "Found background JSON in $BG_DIR"
else
  echo "No background JSON found in $BG_DIR."
  echo "Upstream notes say full background (JSON+PKL) is large and provided separately."
  echo "Place the background directory contents here."
fi

echo "Done."
