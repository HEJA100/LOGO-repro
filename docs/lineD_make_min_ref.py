import os
import pandas as pd

vcf_path = "05_LOGO_Variant_Prioritization/1. script/05_LOGO-C2P/GWAS_C2P/1000G_GWAS_1408.vcf"
max_position = 1000000
out_path = "docs/lineD_ref/male.hg19.fasta"

vcf = pd.read_csv(vcf_path, sep='\t', header=None, comment='#')
vcf.columns = ['chr','pos','name','ref','alt'] + list(vcf.columns[5:])
vcf.pos = vcf.pos.astype(int)
vcf = vcf[vcf.pos <= max_position]
chroms = sorted(vcf['chr'].unique())

os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    for chrom in chroms:
        chrom_max = int(vcf[vcf['chr'] == chrom].pos.max())
        length = chrom_max + 1000
        f.write(f">{chrom}\n")
        f.write("A" * length + "\n")

print(out_path)
print("chroms", chroms)
print("max_position", max_position)
