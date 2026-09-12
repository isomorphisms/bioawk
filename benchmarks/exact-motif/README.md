# Exact canonical DNA motif benchmark

This is the first deliberately narrow genomics/search experiment from
`isomorphisms/computer-science#26`.

It asks one question only:

> For one exact uppercase canonical DNA motif, do several reasonable search
> implementations return exactly the same overlapping match positions, and
> what whole-process scan times do they show on the same plain FASTA input?

The fixed motif is:

```text
ACGTACGT
```

## Exact semantics and oracle

- Input is plain, uncompressed FASTA.
- The motif and fixture sequences contain only uppercase `A/C/G/T`.
- Matches are exact and case-sensitive.
- Overlapping matches count.
- Positions are zero-based within each FASTA record.
- A match never continues across a FASTA-record boundary.
- Output is `record<TAB>position` followed by `TOTAL<TAB>count`.

`fixture.fa` and `oracle.tsv` are the small hand-checkable correctness gate.
They include an overlap, a hit at the end of a record, a near miss, two hits in
one record, and two adjacent records whose concatenation would create a false
cross-record hit. The exact total is five.

## Comparison points

The benchmark intentionally keeps the implementations easy to identify:

1. **bioawk-index** — unmodified bioawk `-c fastx`, using awk's native
   `index()` substring operation on `$seq`; it advances one base after a hit so
   overlapping matches are retained. This is not a character-by-character awk
   loop invented to make bioawk look slow.
2. **c-scalar** — a straightforward C candidate scan with a first-byte check
   and `memcmp()` verification.
3. **c-shift-or** — exact Shift-Or / Bitap using one `unsigned long` state word
   and one precomputed mask per input byte.
4. **Biostrings-auto** — vectorized `vmatchPattern(..., algorithm="auto")`.
5. **Biostrings-shift-or** — the same vectorized Biostrings path with forced
   Shift-Or.
6. **Biostrings-boyer-moore** — the same vectorized path with forced
   Boyer-Moore for the exact motif.

The C scalar and Shift-Or paths share the same small FASTA reader so their
parser boundary is identical. The bioawk and Biostrings rows deliberately use
their ordinary FASTA-facing APIs instead of replacing their parsers with the C
harness.

## Run the correctness gate

From the repository root:

```sh
make -C benchmarks/exact-motif check
```

If `Rscript` plus Biostrings are installed, the Biostrings rows are checked too;
otherwise they are reported as skipped. To require every comparison point:

```sh
make -C benchmarks/exact-motif check-all
```

Every executed row must reproduce `oracle.tsv` byte-for-byte. Timing output is
secondary to that equality check.

## Run the reproducible synthetic benchmark

```sh
make -C benchmarks/exact-motif benchmark
```

This generates, under `.build/`, eight deterministic 1 MiB canonical-DNA FASTA
records using a fixed xorshift32 stream, injects the same motif at known places,
and then performs a simple independent scalar Python scan to write the exact
oracle (including any additional accidental matches). The generated FASTA and
oracle are not source files and are removed by `make clean`.

The default is five executions per implementation. Override the size or repeat
count without changing the search problem:

```sh
make -C benchmarks/exact-motif benchmark \
  BENCH_RECORDS=16 \
  BENCH_BASES_PER_RECORD=2097152 \
  REPEATS=7
```

Use `benchmark-all` when Biostrings is required rather than optional.

## What the timing means

The reported timing is deliberately labeled **whole process**. It includes
program startup, FASTA parsing, matcher setup, scanning, and writing the exact
match list. That makes the rows reproducible and honest, but it is not yet a
claim about isolated search-kernel cycles or direct Idriç lowering.

Before using this as compiler evidence, preserve the same motif/input/oracle and
add a symmetric in-process or cycle-count protocol for every implementation
being compared. Do not subtract startup from only one row.

## Explicitly out of scope for this branch

Keep these as separate experiments:

- gzip/zlib input;
- SIMD/NEON candidate scans;
- multiple motifs or dictionary matching;
- explicit 2-bit DNA packing;
- FPGA realization or offload;
- IUPAC ambiguity, mismatches, reverse complements, or FASTQ quality work.

This branch is only the exact single-motif software baseline those later
experiments can reuse.
