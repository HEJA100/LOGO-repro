#!/usr/bin/env python3
import argparse
import csv
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict


def normalize_chrom(chrom):
    c = chrom.strip()
    if c.lower().startswith("chr"):
        c = "chr" + c[3:]
    else:
        c = "chr" + c
    c = c.replace("chrmt", "chrM").replace("chrMt", "chrM").replace("chrm", "chrM")
    if c == "chrM" or c == "chrm" or c == "chrMT":
        c = "chrM"
    return c


def open_text(path):
    if path.endswith((".gz", ".bgz", ".bgzip")):
        return gzip.open(path, "rt")
    return open(path, "r")


def detect_delim(line):
    if "\t" in line:
        return "\t"
    if "," in line:
        return ","
    return None


def sniff_file(path, sample_lines=50):
    header = None
    data_line = None
    delim = None
    with open_text(path) as f:
        for line in f:
            line = line.strip("\n")
            if not line or line.startswith("#"):
                continue
            if delim is None:
                delim = detect_delim(line)
            fields = line.split(delim) if delim else line.split()
            lower = [x.lower() for x in fields]
            if any(x in ("chrom", "chr", "chromosome", "pos", "position", "start", "end", "ref", "alt", "id", "rsid", "score") for x in lower):
                header = fields
                continue
            data_line = fields
            break
    if delim is None:
        delim = "\t"
    return header, data_line, delim


def guess_columns(header, data_fields):
    idx = {}
    if header:
        low = [h.lower() for h in header]
        def find(names):
            for n in names:
                if n in low:
                    return low.index(n)
            return None
        idx["chrom"] = find(["chrom", "chr", "chromosome"])
        idx["pos"] = find(["pos", "position", "start"])
        idx["ref"] = find(["ref"])
        idx["alt"] = find(["alt"])
        idx["id"] = find(["id", "rsid", "rs"])
    else:
        idx["chrom"] = 0
        idx["pos"] = 1
        if data_fields and len(data_fields) >= 5:
            idx["id"] = 2
            idx["ref"] = 3
            idx["alt"] = 4
    return idx


def parse_cols_arg(cols_arg):
    if not cols_arg:
        return None
    mapping = {}
    parts = [p.strip() for p in cols_arg.split(",") if p.strip()]
    for part in parts:
        if "=" not in part:
            continue
        key, val = part.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key == "score" and val == "*":
            mapping[key] = "*"
            continue
        if "-" in val:
            a, b = val.split("-", 1)
            mapping[key] = (int(a) - 1, int(b) - 1)
        else:
            mapping[key] = int(val) - 1
    return mapping


def select_files(figshare_dir):
    exts = (".tsv", ".csv", ".txt", ".tsv.gz", ".csv.gz", ".txt.gz", ".bgz", ".bgzip")
    files = []
    for root, _, fnames in os.walk(figshare_dir):
        for fn in fnames:
            if fn.endswith(".tbi") or fn.endswith(".csi"):
                continue
            if fn.lower().endswith(exts):
                files.append(os.path.join(root, fn))
    return files


def chrom_from_filename(name):
    m = re.search(r"(?i)(?:^|[^a-z0-9])(chr)?(1[0-9]|2[0-2]|[1-9]|x|y|m|mt)(?:[^a-z0-9]|$)", name)
    if not m:
        return None
    val = m.group(2)
    if val.lower() in ("x", "y", "m", "mt"):
        val = val.upper().replace("MT", "M")
        return f"chr{val}"
    return f"chr{int(val)}"


def has_index(path):
    return os.path.exists(path + ".tbi") or os.path.exists(path + ".csi")


def ensure_bgzip_and_index(path, chrom_idx, pos_idx, out_dir):
    bgzip = shutil.which("bgzip")
    tabix = shutil.which("tabix")
    if not bgzip or not tabix:
        return None
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.basename(path)
    if base.endswith(('.gz', '.bgz', '.bgzip')):
        base = base.rsplit('.', 1)[0]
    out_path = os.path.join(out_dir, base + ".bgz")
    if not os.path.exists(out_path):
        with open(out_path, "wb") as out:
            p = subprocess.run([bgzip, "-c", path], stdout=out)
            if p.returncode != 0:
                return None
    if not has_index(out_path):
        cmd = [tabix, "-s", str(chrom_idx + 1), "-b", str(pos_idx + 1), "-e", str(pos_idx + 1), out_path]
        p = subprocess.run(cmd)
        if p.returncode != 0:
            return None
    return out_path


def tabix_fetch(path, chrom, pos):
    try:
        import pysam
        tbx = pysam.TabixFile(path)
        region = f"{chrom}:{pos}-{pos}"
        return [l for l in tbx.fetch(region=region) if not l.startswith("#")]
    except Exception:
        pass
    tabix = shutil.which("tabix")
    if not tabix:
        return []
    region = f"{chrom}:{pos}-{pos}"
    p = subprocess.run([tabix, "-h", path, region], capture_output=True, text=True)
    if p.returncode != 0:
        return []
    return [l for l in p.stdout.splitlines() if l and not l.startswith("#")]


def read_vcf(vcf_path):
    variants = []
    opener = gzip.open if vcf_path.endswith((".gz", ".bgz")) else open
    with opener(vcf_path, "rt") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            chrom, pos, vid, ref, alt = parts[0], parts[1], parts[2], parts[3], parts[4]
            try:
                pos_i = int(pos)
            except ValueError:
                continue
            variants.append({
                "chrom": chrom,
                "chrom_norm": normalize_chrom(chrom),
                "pos": pos_i,
                "id": vid,
                "ref": ref,
                "alt": alt,
            })
    return variants


def main():
    p = argparse.ArgumentParser(description="Lookup LOGO scores in Figshare precomputed dbSNP tables.")
    p.add_argument("--vcf", required=True, help="Input VCF (CHROM POS ID REF ALT ...)")
    p.add_argument("--figshare-dir", default="docs/lineD_figshare", help="Figshare data directory")
    p.add_argument("--out", default=None, help="Output file (default: <vcf>.logo_figshare.tsv)")
    p.add_argument("--format", default="tsv", choices=["tsv", "csv"], help="Output format")
    p.add_argument("--make-index", action="store_true", help="Convert to bgzip+tabix if needed (writes to figshare_dir/indexed)")
    p.add_argument("--cols", default=None, help="Explicit column mapping chrom=1,pos=2,ref=4,alt=5,id=3,score=6-56 or score=*")
    p.add_argument("--keep-multi", action="store_true", help="Keep multiple matches per variant")
    p.add_argument("--allow-empty", action="store_true", help="Allow empty figshare-dir and emit no_match output")
    args = p.parse_args()

    out_path = args.out or (args.vcf + ".logo_figshare.tsv")
    delim_out = "\t" if args.format == "tsv" else ","

    variants = read_vcf(args.vcf)
    if not variants:
        print("No variants found in VCF.")
        return 2

    by_chrom = defaultdict(list)
    positions = defaultdict(set)
    for v in variants:
        by_chrom[v["chrom_norm"]].append(v)
        positions[v["chrom_norm"]].add(v["pos"])

    files = select_files(args.figshare_dir)
    if not files and not args.allow_empty:
        print(f"ERROR: No data files found under {args.figshare_dir}.")
        print("Hint: fetch and unzip the Figshare ZIP first:")
        print("  python scripts/figshare_zip_fetch.py --out /tmp/logo_figshare_19149827_v2.zip")
        print("  bash scripts/figshare_unzip_into.sh /tmp/logo_figshare_19149827_v2.zip docs/lineD_figshare")
        return 2
    if not files and args.allow_empty:
        print(f"No data files found under {args.figshare_dir}. Proceeding with empty lookups (--allow-empty).")

    chrom_files = defaultdict(list)
    global_files = []
    for f in files:
        c = chrom_from_filename(os.path.basename(f))
        if c:
            chrom_files[c].append(f)
        else:
            global_files.append(f)

    cols_override = parse_cols_arg(args.cols)

    hits = defaultdict(list)

    for chrom in by_chrom:
        target_files = chrom_files.get(chrom, []) or global_files
        if not target_files:
            continue
        for f in target_files:
            header, data_line, delim = sniff_file(f)
            idx = guess_columns(header, data_line)

            if cols_override:
                idx = {k: v for k, v in cols_override.items() if k != "score"}
                score_override = cols_override.get("score")
            else:
                score_override = None

            chrom_idx = idx.get("chrom") if isinstance(idx.get("chrom"), int) else None
            pos_idx = idx.get("pos") if isinstance(idx.get("pos"), int) else None

            file_path = f
            if args.make_index and pos_idx is not None:
                indexed = ensure_bgzip_and_index(f, chrom_idx or 0, pos_idx, os.path.join(args.figshare_dir, "indexed"))
                if indexed:
                    file_path = indexed

            if has_index(file_path):
                for pos in positions[chrom]:
                    lines = tabix_fetch(file_path, chrom, pos)
                    for line in lines:
                        fields = line.split(delim) if delim in line else line.split()
                        if pos_idx is None:
                            continue
                        if chrom_idx is not None:
                            chrom_val = normalize_chrom(fields[chrom_idx])
                        else:
                            chrom_val = chrom
                        try:
                            pos_val = int(fields[pos_idx])
                        except Exception:
                            continue
                        if chrom_val != chrom or pos_val != pos:
                            continue
                        hits[(chrom, pos)].append({"fields": fields, "file": file_path, "delim": delim, "idx": idx, "header": header})
                continue

            pos_set = positions[chrom]
            with open_text(f) as fh:
                for line in fh:
                    if not line or line.startswith("#"):
                        continue
                    line = line.rstrip("\n")
                    fields = line.split(delim) if delim in line else line.split()
                    if pos_idx is None or pos_idx >= len(fields):
                        continue
                    if chrom_idx is not None:
                        if chrom_idx >= len(fields):
                            continue
                        chrom_val = normalize_chrom(fields[chrom_idx])
                    else:
                        chrom_val = chrom
                    try:
                        pos_val = int(fields[pos_idx])
                    except Exception:
                        continue
                    if chrom_val != chrom or pos_val not in pos_set:
                        continue
                    hits[(chrom, pos_val)].append({"fields": fields, "file": f, "delim": delim, "idx": idx, "header": header})

    out_rows = []
    for v in variants:
        key = (v["chrom_norm"], v["pos"])
        cand = hits.get(key, [])
        match_note = "no_match"
        matched_rows = 0
        selected = []
        if cand:
            match_note = "pos_match"
            matched_rows = len(cand)
            ref = v["ref"].upper()
            alt = v["alt"].upper()
            vid = v["id"]

            def filt_by_ref_alt(rows):
                out = []
                for r in rows:
                    idx = r["idx"]
                    rref_i = idx.get("ref") if isinstance(idx.get("ref"), int) else None
                    ralt_i = idx.get("alt") if isinstance(idx.get("alt"), int) else None
                    if rref_i is None or ralt_i is None:
                        continue
                    if rref_i >= len(r["fields"]) or ralt_i >= len(r["fields"]):
                        continue
                    if r["fields"][rref_i].upper() == ref and r["fields"][ralt_i].upper() == alt:
                        out.append(r)
                return out

            def filt_by_id(rows):
                out = []
                if not vid or vid == ".":
                    return out
                for r in rows:
                    idx = r["idx"]
                    rid_i = idx.get("id") if isinstance(idx.get("id"), int) else None
                    if rid_i is None or rid_i >= len(r["fields"]):
                        continue
                    if r["fields"][rid_i] == vid:
                        out.append(r)
                return out

            ref_alt = filt_by_ref_alt(cand)
            if ref_alt:
                cand = ref_alt
                match_note = "ref_alt_match"

            id_match = filt_by_id(cand)
            if id_match:
                cand = id_match
                match_note = "id_match"

            if args.keep_multi:
                selected = cand
            else:
                selected = cand[:1]
                if matched_rows > 1:
                    match_note = match_note + ":multi"
        else:
            selected = []

        if not selected:
            out_rows.append({
                "CHROM": v["chrom"], "POS": v["pos"], "ID": v["id"], "REF": v["ref"], "ALT": v["alt"],
                "matched_rows": matched_rows, "match_note": match_note, "hit_file": "", "raw_hit": "",
            })
        else:
            for r in selected:
                raw = r["delim"].join(r["fields"]) if r.get("delim") else "\t".join(r["fields"])
                out_rows.append({
                    "CHROM": v["chrom"], "POS": v["pos"], "ID": v["id"], "REF": v["ref"], "ALT": v["alt"],
                    "matched_rows": matched_rows, "match_note": match_note, "hit_file": os.path.basename(r["file"]), "raw_hit": raw,
                })

    with open(out_path, "w", newline="") as out_f:
        writer = csv.writer(out_f, delimiter=delim_out)
        writer.writerow(["CHROM", "POS", "ID", "REF", "ALT", "matched_rows", "match_note", "hit_file", "raw_hit"])
        for row in out_rows:
            writer.writerow([row["CHROM"], row["POS"], row["ID"], row["REF"], row["ALT"], row["matched_rows"], row["match_note"], row["hit_file"], row["raw_hit"]])

    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
