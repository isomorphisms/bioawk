#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$here/large/seqkit" "$here/large/ena" "$here/large/htslib"

# SeqKit's published benchmark corpus. The upstream benchmark documentation
# describes this as a 2.2 GB archive containing dataset_A.fa, dataset_B.fa,
# dataset_C.fq, and companion benchmark inputs.
curl -fL \
  https://app.shenwei.me/data/seqkit/seqkit-benchmark-data.tar.gz \
  -o "$here/large/seqkit/seqkit-benchmark-data.tar.gz"

# Real FASTQ data used by the Biopython cookbook: 41,892 reads, about 19 MB
# after decompression.
curl -fL \
  ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR020/SRR020192/SRR020192.fastq.gz \
  -o "$here/large/ena/SRR020192.fastq.gz"

# HTSlib's larger C. elegans/reference-style FASTA test fixture.
curl -fL \
  https://raw.githubusercontent.com/samtools/htslib/develop/test/ce.fa \
  -o "$here/large/htslib/ce.fa"
