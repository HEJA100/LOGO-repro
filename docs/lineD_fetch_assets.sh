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
if [[ -f "$REF_FASTA" && ! -s "$REF_FASTA" ]]; then
  echo "ERROR: Reference FASTA is empty: $REF_FASTA"
  exit 1
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
  echo "No weights found in $WEIGHT_DIR."
  echo "You must place exactly one official .h5/.hdf5 weight file here."
  echo "Expected for formal weights: vocab_size=15638, we_size=128"
fi

echo "=== Vocab / Config ==="
missing_vocab=0
missing_config=0
if [[ ! -f "$VOCAB_DIR/vocab.txt" ]]; then
  echo "No vocab file found at $VOCAB_DIR/vocab.txt"
  missing_vocab=1
fi
if [[ ! -f "$CONFIG_DIR/bert_config.json" ]]; then
  echo "No config found at $CONFIG_DIR/bert_config.json"
  missing_config=1
fi

echo "=== Background (full) ==="
missing_bg=0
if ls "$BG_DIR"/*.json >/dev/null 2>&1; then
  echo "Found background JSON in $BG_DIR"
else
  echo "No background JSON found in $BG_DIR."
  echo "Upstream notes say full background (JSON+PKL) is large and provided separately."
  missing_bg=1
fi

echo "=== Missing Assets Checklist ==="
if ! ls "$WEIGHT_DIR"/*.h5 "$WEIGHT_DIR"/*.hdf5 >/dev/null 2>&1; then
  echo "WEIGHTS:"
  echo "  File: <official_weights>.hdf5"
  echo "  Purpose: model weights for Line D full inference (15638x128 embedding)"
  echo "  Place: $WEIGHT_DIR/"
fi
if [[ "$missing_vocab" -eq 1 ]]; then
  echo "VOCAB:"
  echo "  File: vocab.txt"
  echo "  Purpose: token/vocab mapping for 15638 tokens"
  echo "  Place: $VOCAB_DIR/vocab.txt"
fi
if [[ "$missing_config" -eq 1 ]]; then
  echo "CONFIG:"
  echo "  File: bert_config.json"
  echo "  Purpose: model config (vocab_size/hidden_size/num_heads/max_position_embeddings)"
  echo "  Place: $CONFIG_DIR/bert_config.json"
fi
if [[ "$missing_bg" -eq 1 ]]; then
  echo "BACKGROUND:"
  echo "  Files: *.json + *.pkl"
  echo "  Purpose: ECDF background for 51 classes"
  echo "  Place: $BG_DIR/"
fi

echo "Done."
