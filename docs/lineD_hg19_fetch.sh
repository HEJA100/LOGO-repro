BASE=$(conda info --base)
source "$BASE/etc/profile.d/conda.sh"
conda activate logo-lite
mkdir -p Genomics
curl -L -C - -o Genomics/GCF_000001405.25_GRCh37.p13_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.25_GRCh37.p13/GCF_000001405.25_GRCh37.p13_genomic.fna.gz
gzip -dc Genomics/GCF_000001405.25_GRCh37.p13_genomic.fna.gz > Genomics/male.hg19.fasta
