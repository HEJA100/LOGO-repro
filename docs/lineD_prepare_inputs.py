import os
import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VCF_SRC = os.path.join(BASE_DIR, "..", "05_LOGO_Variant_Prioritization", "1. script", "05_LOGO-C2P", "GWAS_C2P", "1000G_GWAS_1408.vcf")
OUT_DIR = os.path.join(BASE_DIR, "lineD_out")
OUT_VCF = os.path.join(OUT_DIR, "lineD_input.vcf")
MAX_POSITION = 1_000_000
MAX_VARIANTS = 20


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    vcf = pd.read_csv(VCF_SRC, sep='\t', header=None, comment='#')
    vcf.columns = ['chr','pos','name','ref','alt'] + list(vcf.columns[5:])
    vcf.pos = vcf.pos.astype(int)
    vcf = vcf[vcf.pos <= MAX_POSITION]
    vcf = vcf.head(MAX_VARIANTS)
    vcf.to_csv(OUT_VCF, sep='\t', header=False, index=False)
    print(os.path.relpath(OUT_VCF))


if __name__ == "__main__":
    main()
