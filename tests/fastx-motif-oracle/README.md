# FASTA/FASTQ motif oracle

This is the first executable reference-lane fixture for issue #3,
"Use FASTA/FASTQ motif scanning as an Idriç/ARM control-flow fixture."

It deliberately does not implement a direct Idriç or ARM backend path.

## Exact semantics

The fixed motif is `ACGTACGT`.

- Input is plain, uncompressed FASTA or FASTQ.
- Matching is exact, uppercase, and case-sensitive.
- Positions are zero-based within one sequence record.
- Overlapping matches count.
- Only the sequence field is searched. FASTQ quality bytes are not searched.
- FASTA sequence line wrapping is not a semantic boundary: the `wrapped`
  record has a match spanning the checked-in line break.
- Record boundaries are semantic boundaries: `boundary_left` followed by
  `boundary_right` would form the motif if concatenated, but both records
  correctly report no match.
- This reference lane gives bioawk complete parsed records before scanning.
  Arbitrary streaming-buffer chunk boundaries are therefore not claimed here.
  Direct byte-span/chunk behavior remains part of the later ARM Gate C work.
- Gzip is intentionally absent from this first oracle.

The exact expected table is checked in as `expected.tsv`. A zero-hit record is
reported explicitly with count `0` and positions `-`.

The fixture bytes are also pinned by SHA-256 in `check.sh`:

- `fixture.fasta`: `521ddceeaaf59dd94ac33bf66c54e2f0500f7b8746424c9ceb894732e836160e`
- `fixture.fastq`: `af81dbf7cdb2d08e94e91f77d2d496a24b3a1e7da4b13f759f4b023ca44fa464`

## Run

`run.sh` resolves the repository from its own location, builds the unmodified
bioawk reference executable, and then runs the exact checker as a separate
stage:

```sh
sh /path/to/bioawk/tests/fastx-motif-oracle/run.sh
```

To keep build and execution fully separate, build bioawk first and then run:

```sh
BIOAWK=/path/to/bioawk/bioawk \
  sh /path/to/bioawk/tests/fastx-motif-oracle/check.sh
```

A passing run ends with an explicit
`direct_idric_arm<TAB>NOT_VERIFIED` receipt field.

## Reference workload links

The examples added to issue #3 are workload shapes and reference behavior, not
generators of this oracle and not new biological claims:

- `bioinformatics_primer/bash-fq2fa/fq2fa.awk` — record/state dispatch shape.
- `bioinformatics_primer/fasta-gc/solution.py` — scalar counting baseline.
- `bioinformatics_primer/revcomp/solution.py` — lookup-table counterexample.
- `bioinformatics_primer/common-kmers/kmer_count.py` — sequence-window/span
  workload.

The expected motif output above remains hand-checkable and independent of those
programs.

## Backend boundary

This fixture is a consumer specification for the branching/search work, not
backend acceptance.

- `isomorphisms/Idric#72` currently defines the branching ladder and explicitly
  keeps function calls outside that milestone.
- `isomorphisms/idric-arm-thumb#31` requires Gates A-C before fixed-string
  search is promoted as direct generated ARM/Thumb evidence.
- No RefC/C bridge, generated-ARM claim, emulator claim, or physical-device
  claim is made by this test.

When those gates are green, a direct Idriç/ARM candidate can consume these same
fixture bytes and `expected.tsv`; its compiler representation, emitted
assembly/object, execution evidence, and any `NOT_VERIFIED` stages must remain
separate.

Draft PR #1, "Add exact canonical DNA motif benchmark," remains a separate
FASTA timing/comparison experiment. This oracle does not stack on it or make
its performance comparisons part of issue #3's first semantic gate.
