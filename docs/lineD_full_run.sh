#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: bash docs/lineD_full_run.sh --vcf <path> [options]

Required:
  --vcf <path>                 Path to input VCF

Optional:
  --ref <path>                 Reference FASTA (default: docs/lineD_assets/ref/hg19.fa)
  --bg <dir>                   Background directory (default: docs/lineD_assets/bg_full)
  --weights <path/dir>         Weights file or directory (default: docs/lineD_assets/weights)
  --vocab <path>               Vocab file (optional; default: docs/lineD_assets/vocab/vocab.txt)
  --config <path>              Config file (optional; default: docs/lineD_assets/config/bert_config.json)
  --outdir <dir>               Output base dir (default: docs/lineD_out_full)
  --logdir <dir>               Log base dir (default: docs/lineD_logs_full)
  --cuda <int>                 CUDA device id (default: 0)
  --run-id <string>            Run id (default: timestamp)
  --allow-fallback             Allow using repo/smoke assets if official assets are missing
USAGE
}

abs_path() {
  local p="$1"
  if [[ "$p" = /* ]]; then
    echo "$p"
  else
    echo "$ROOT_DIR/$p"
  fi
}

VCF=""
REF="docs/lineD_assets/ref/hg19.fa"
BG="docs/lineD_assets/bg_full"
WEIGHTS="docs/lineD_assets/weights"
VOCAB="docs/lineD_assets/vocab/vocab.txt"
CONFIG="docs/lineD_assets/config/bert_config.json"
OUTDIR="docs/lineD_out_full"
LOGDIR="docs/lineD_logs_full"
CUDA="0"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
ALLOW_FALLBACK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --vcf) VCF="$2"; shift 2;;
    --ref) REF="$2"; shift 2;;
    --bg) BG="$2"; shift 2;;
    --weights) WEIGHTS="$2"; shift 2;;
    --vocab) VOCAB="$2"; shift 2;;
    --config) CONFIG="$2"; shift 2;;
    --outdir) OUTDIR="$2"; shift 2;;
    --logdir) LOGDIR="$2"; shift 2;;
    --cuda) CUDA="$2"; shift 2;;
    --run-id) RUN_ID="$2"; shift 2;;
    --allow-fallback) ALLOW_FALLBACK=1; shift 1;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
 done

if [[ -z "$VCF" ]]; then
  echo "ERROR: --vcf is required"
  usage
  exit 1
fi

VCF="$(abs_path "$VCF")"
REF="$(abs_path "$REF")"
BG="$(abs_path "$BG")"
WEIGHTS="$(abs_path "$WEIGHTS")"
VOCAB="$(abs_path "$VOCAB")"
CONFIG="$(abs_path "$CONFIG")"
OUTDIR="$(abs_path "$OUTDIR")"
LOGDIR="$(abs_path "$LOGDIR")"

DEFAULT_ASSETS="$ROOT_DIR/docs/lineD_assets"
if [[ "$WEIGHTS" == "$DEFAULT_ASSETS/weights" ]]; then
  mkdir -p "$WEIGHTS"
fi
if [[ "$BG" == "$DEFAULT_ASSETS/bg_full" ]]; then
  mkdir -p "$BG"
fi
if [[ "$REF" == "$DEFAULT_ASSETS/ref/hg19.fa" ]]; then
  mkdir -p "$(dirname "$REF")"
fi
if [[ "$VOCAB" == "$DEFAULT_ASSETS/vocab/vocab.txt" ]]; then
  mkdir -p "$(dirname "$VOCAB")"
fi
if [[ "$CONFIG" == "$DEFAULT_ASSETS/config/bert_config.json" ]]; then
  mkdir -p "$(dirname "$CONFIG")"
fi

RUN_OUT="$OUTDIR/$RUN_ID"
RUN_LOG="$LOGDIR/$RUN_ID"
mkdir -p "$RUN_OUT" "$RUN_LOG"
LOG_FILE="$RUN_LOG/lineD_full_run.log"

{
  echo "lineD_full_run.sh"
  echo "RUN_ID=$RUN_ID"
  echo "VCF=$VCF"
  echo "REF=$REF"
  echo "BG=$BG"
  echo "WEIGHTS=$WEIGHTS"
  echo "VOCAB=$VOCAB"
  echo "CONFIG=$CONFIG"
  echo "OUTDIR=$RUN_OUT"
  echo "LOGDIR=$RUN_LOG"
  echo "CUDA=$CUDA"
  echo "ALLOW_FALLBACK=$ALLOW_FALLBACK"
} | tee -a "$LOG_FILE"

PYTHON_CMD="python"
if command -v conda >/dev/null 2>&1; then
  if conda env list 2>/dev/null | awk '{print $1}' | grep -q '^logo-lite$'; then
    PYTHON_CMD="conda run -n logo-lite --no-capture-output python"
  fi
fi

if [[ ! -f "$VCF" ]]; then
  echo "ERROR: VCF not found: $VCF" | tee -a "$LOG_FILE"
  exit 1
fi

expected_ref="$DEFAULT_ASSETS/ref/hg19.fa"
expected_bg="$DEFAULT_ASSETS/bg_full"
expected_weights="$DEFAULT_ASSETS/weights"
expected_vocab="$DEFAULT_ASSETS/vocab/vocab.txt"
expected_config="$DEFAULT_ASSETS/config/bert_config.json"

missing=()
add_missing() { missing+=("$1"); }

WEIGHT_FILE=""
BG_JSON=""

if [[ ! -f "$REF" ]]; then
  add_missing "ref: $REF (expected $expected_ref)"
fi

if [[ -d "$BG" ]]; then
  if ls "$BG"/*.json >/dev/null 2>&1; then
    BG_JSON="$(ls "$BG"/*.json | head -n 1)"
  else
    add_missing "bg_full JSON: $BG/*.json (expected $expected_bg)"
  fi
else
  add_missing "bg_full: $BG (expected $expected_bg)"
fi

if [[ -d "$WEIGHTS" ]]; then
  wfiles=($(find "$WEIGHTS" -maxdepth 1 -type f -name "*.h5" -print 2>/dev/null; find "$WEIGHTS" -maxdepth 1 -type f -name "*.hdf5" -print 2>/dev/null))
  if [[ ${#wfiles[@]} -eq 1 ]]; then
    WEIGHT_FILE="${wfiles[0]}"
  elif [[ ${#wfiles[@]} -eq 0 ]]; then
    add_missing "weights: $WEIGHTS/*.h5 (expected $expected_weights)"
  else
    echo "ERROR: Multiple weights found in $WEIGHTS; please pass --weights <file>" | tee -a "$LOG_FILE"
    printf '%s\n' "${wfiles[@]}" | tee -a "$LOG_FILE"
    exit 1
  fi
elif [[ -f "$WEIGHTS" ]]; then
  WEIGHT_FILE="$WEIGHTS"
else
  add_missing "weights: $WEIGHTS (expected $expected_weights)"
fi

if [[ ! -f "$VOCAB" ]]; then
  add_missing "vocab: $VOCAB (expected $expected_vocab)"
fi

if [[ ! -f "$CONFIG" ]]; then
  add_missing "config: $CONFIG (expected $expected_config)"
fi

if [[ ${#missing[@]} -gt 0 ]]; then
  if [[ "$ALLOW_FALLBACK" -eq 0 ]]; then
    echo "ERROR: Missing required full-run assets:" | tee -a "$LOG_FILE"
    for m in "${missing[@]}"; do
      echo "  - $m" | tee -a "$LOG_FILE"
    done
    echo "Expected asset roots:" | tee -a "$LOG_FILE"
    echo "  ref:     $expected_ref" | tee -a "$LOG_FILE"
    echo "  bg_full: $expected_bg" | tee -a "$LOG_FILE"
    echo "  weights: $expected_weights" | tee -a "$LOG_FILE"
    echo "  vocab:   $expected_vocab" | tee -a "$LOG_FILE"
    echo "  config:  $expected_config" | tee -a "$LOG_FILE"
    echo "Run: bash docs/lineD_fetch_assets.sh" | tee -a "$LOG_FILE"
    exit 1
  else
    echo "WARN: Missing full-run assets (allow-fallback enabled):" | tee -a "$LOG_FILE"
    for m in "${missing[@]}"; do
      echo "  - $m" | tee -a "$LOG_FILE"
    done
    echo "Attempting fallback to repo/smoke assets..." | tee -a "$LOG_FILE"

    if [[ ! -f "$REF" ]]; then
      if [[ -f "$ROOT_DIR/docs/lineD_ref/lineD_min.fa" ]]; then
        REF="$ROOT_DIR/docs/lineD_ref/lineD_min.fa"
      elif [[ -f "$ROOT_DIR/docs/lineD_ref/male.hg19.fasta" ]]; then
        REF="$ROOT_DIR/docs/lineD_ref/male.hg19.fasta"
      else
        echo "ERROR: fallback reference not found in docs/lineD_ref/" | tee -a "$LOG_FILE"
        exit 1
      fi
      echo "WARN: Using fallback reference: $REF" | tee -a "$LOG_FILE"
    fi

    if [[ ! -d "$BG" ]] || ! ls "$BG"/*.json >/dev/null 2>&1; then
      if [[ -d "$ROOT_DIR/docs/lineD_background" ]] && ls "$ROOT_DIR/docs/lineD_background"/*.json >/dev/null 2>&1; then
        BG="$ROOT_DIR/docs/lineD_background"
      else
        echo "ERROR: fallback background not found in docs/lineD_background" | tee -a "$LOG_FILE"
        exit 1
      fi
      echo "WARN: Using fallback background: $BG" | tee -a "$LOG_FILE"
    fi

    if [[ -z "$WEIGHT_FILE" ]]; then
      if [[ -f "$ROOT_DIR/99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5" ]]; then
        WEIGHT_FILE="$ROOT_DIR/99_PreTrain_Model_Weight/LOGO_5_gram_2_layer_8_heads_256_dim_weights_32-0.885107.hdf5"
      else
        echo "ERROR: fallback weight not found in 99_PreTrain_Model_Weight" | tee -a "$LOG_FILE"
        exit 1
      fi
      echo "WARN: Using fallback weight: $WEIGHT_FILE" | tee -a "$LOG_FILE"
    fi
  fi
fi

if [[ ! -f "$VOCAB" ]]; then
  echo "WARN: Vocab file not found at $VOCAB (proceeding with --vocab-size 15638)" | tee -a "$LOG_FILE"
fi

if [[ ! -f "$CONFIG" ]]; then
  echo "WARN: Config file not found at $CONFIG" | tee -a "$LOG_FILE"
fi

BG_JSON=""
if ls "$BG"/*.json >/dev/null 2>&1; then
  BG_JSON="$(ls "$BG"/*.json | head -n 1)"
fi
if [[ -z "$BG_JSON" ]]; then
  echo "ERROR: No background JSON found in $BG" | tee -a "$LOG_FILE"
  exit 1
fi

NUM_CLASSES=51
python - <<PY "$BG_JSON" "$BG" "$NUM_CLASSES" | tee -a "$LOG_FILE"
import json, os, sys
json_path = sys.argv[1]
bg_dir = sys.argv[2]
num_classes = int(sys.argv[3])
with open(json_path, 'r') as f:
    data = json.load(f)
missing = [str(i) for i in range(num_classes) if str(i) not in data]
if missing:
    print("ERROR: background JSON missing keys:", ','.join(missing[:10]), "...")
    sys.exit(1)
missing_files = [v for v in data.values() if not os.path.exists(os.path.join(bg_dir, v))]
if missing_files:
    print("ERROR: missing PKL files referenced by JSON:")
    for v in missing_files[:10]:
        print("  ", v)
    sys.exit(1)
print("Background JSON OK:", os.path.basename(json_path))
PY

{
  echo "FINAL_REF=$REF"
  echo "FINAL_BG=$BG"
  echo "FINAL_WEIGHT=$WEIGHT_FILE"
} | tee -a "$LOG_FILE"

ref_header=$(head -n 1 "$REF" || true)
if [[ "$ref_header" != ">chr"* ]]; then
  echo "WARN: Reference FASTA headers do not start with 'chr'." | tee -a "$LOG_FILE"
  echo "      Ensure VCF chromosome naming matches reference (chr1 vs 1)." | tee -a "$LOG_FILE"
fi

vcf_chrom=$(grep -v '^#' "$VCF" | head -n 1 | cut -f1 || true)
if [[ -n "$vcf_chrom" ]]; then
  if [[ "$vcf_chrom" != chr* && "$ref_header" == ">chr"* ]]; then
    echo "WARN: VCF chrom does not start with 'chr' but reference does." | tee -a "$LOG_FILE"
  fi
  if [[ "$vcf_chrom" == chr* && "$ref_header" != ">chr"* ]]; then
    echo "WARN: VCF chrom starts with 'chr' but reference does not." | tee -a "$LOG_FILE"
  fi
fi

VOCAB_SIZE=15638
if [[ -f "$VOCAB" ]]; then
  count=$(grep -cve '^\s*$' "$VOCAB" || true)
  if [[ "$count" -gt 0 ]]; then
    VOCAB_SIZE="$count"
  fi
fi

if [[ -f "$CONFIG" ]]; then
  python - <<PY "$CONFIG" | tee -a "$LOG_FILE"
import json, sys
cfg = json.load(open(sys.argv[1]))
keys = ["vocab_size", "hidden_size", "num_attention_heads", "num_hidden_layers", "max_position_embeddings"]
print("Config summary:")
for k in keys:
    if k in cfg:
        print(f"  {k}: {cfg[k]}")
PY
fi

INPUT_LINK="$RUN_OUT/$(basename "$VCF")"
if [[ -e "$INPUT_LINK" ]]; then
  rm -f "$INPUT_LINK"
fi
ln -sf "$VCF" "$INPUT_LINK"

$PYTHON_CMD "$ROOT_DIR/scripts/patch_pyfasta.py" | tee -a "$LOG_FILE"

PYTHONPATH="$ROOT_DIR:$BG:${PYTHONPATH:-}" CUDA_VISIBLE_DEVICES="$CUDA" \
$PYTHON_CMD "$ROOT_DIR/04_LOGO_Chromatin_Feature/1. script/04_LOGO_Chrom_predict/GeneBert_predict_vcf_slice_e8.py" \
  --inputfile "$INPUT_LINK" \
  --backgroundfile "$BG" \
  --reffasta "$REF" \
  --weight-path "$WEIGHT_FILE" \
  --task test \
  --num-classes 51 \
  --max-position-embeddings 512 \
  --ngram 5 \
  --stride 1 \
  --vocab-size "$VOCAB_SIZE" \
  --we-size 128 \
  --model-dim 256 \
  --transformer-depth 2 \
  --num-heads 8 \
  --seq-len 512 \
  --slice-size 10000 \
  --batch-size 32 \
  --verbose 2 \
  | tee -a "$LOG_FILE"

OUTPUT_PREFIX="$INPUT_LINK"_"32bs"_"5gram"_"51feature"
{
  echo "SUCCESS markers:"
  echo "  ${OUTPUT_PREFIX}.out.ref.csv"
  echo "  ${OUTPUT_PREFIX}.out.evalue.csv"
  echo "  $LOG_FILE"
} | tee -a "$LOG_FILE"
