# Sample data

Shared biology fixtures for bioawk/search/compiler-backend experiments.

The small text fixtures are copied byte-for-byte from upstream test suites so they can be used without network access. Each copied file remains subject to the upstream project's license; the source project, path, and Git blob SHA are recorded in `SOURCES.tsv`.

## Checked in

### Biopython

- `biopython/f002.fasta` — multi-record FASTA with many ambiguous `N` bases.
- `biopython/example.fastq` — ordinary FASTQ reads and qualities.
- `biopython/tricky.fastq` — wrapped FASTQ and quality text containing characters that make naive four-line parsing fail.
- `biopython/zero_length.fastq` — includes a zero-length sequence/quality record.

Biopython's own documented upstream regression runner is the preferred first parser/fixture baseline:

```text
cd Tests
python run_tests.py --offline test_SeqIO test_SeqIO_QualityIO
```

That is parser/format correctness. Search workloads on these same bytes should be declared separately so timing/search claims do not get confused with Biopython's general unit tests.

### HTSlib

- `htslib/realn01.fa` — reference FASTA.
- `htslib/realn01.sam` — coordinate-sorted SAM with CIGAR, quality strings, and optional tags.
- `htslib/vcf44_1.vcf` — VCF 4.4 genotype/phasing edge cases.

### bedtools

- `bedtools/a.bed` — small six-column BED fixture.
- `bedtools/gdc.gff` — GFF features including UTR, CDS, intron, exon, mRNA, tRNA, and gene records on both strands.

## Large and binary corpus

`fetch-large.sh` downloads the large/reference material into `sample data/large/` rather than pretending multi-gigabyte archives belong in one ordinary Git blob. This includes:

- SeqKit's published 2.2 GB benchmark archive, containing its large FASTA/FASTQ benchmark datasets;
- the ENA `SRR020192.fastq.gz` real-read example used in the Biopython cookbook;
- HTSlib's roughly 1 MB `ce.fa` reference fixture.

These are deliberately not required by the tiny correctness suite. Use them for scaling, whole-program, parsing, compression, and throughput comparisons.

## Standing use

When search or branching changes in a compiler backend, use these bytes as a recurring contrast suite rather than inventing a fresh toy input each time. The broader comparison protocol is recorded in `isomorphisms/ai-ci` PR #27 and cross-linked from `isomorphisms/computer-science` issues #23, #24, and #26.
