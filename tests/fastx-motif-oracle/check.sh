#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../.." && pwd)
bioawk=${BIOAWK:-"$root/bioawk"}
motif=ACGTACGT

fail()
{
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

[ -x "$bioawk" ] ||
    fail "bioawk executable not found at $bioawk; build it separately or set BIOAWK"

check_sha256()
{
    expected=$1
    path=$2
    actual=$(sha256sum "$path" | awk '{print $1}')
    [ "$actual" = "$expected" ] ||
        fail "SHA-256 mismatch for $path: $actual"
}

check_sha256 521ddceeaaf59dd94ac33bf66c54e2f0500f7b8746424c9ceb894732e836160e "$here/fixture.fasta"
check_sha256 af81dbf7cdb2d08e94e91f77d2d496a24b3a1e7da4b13f759f4b023ca44fa464 "$here/fixture.fastq"

actual=$(mktemp)
trap 'rm -f "$actual"' EXIT HUP INT TERM

{
    "$bioawk" -c fastx -v motif="$motif" -v input_format=FASTA \
        -f "$here/scan.awk" "$here/fixture.fasta"
    "$bioawk" -c fastx -v motif="$motif" -v input_format=FASTQ \
        -f "$here/scan.awk" "$here/fixture.fastq"
} > "$actual"

if ! diff -u "$here/expected.tsv" "$actual"; then
    fail 'motif oracle output changed'
fi

printf 'PASS: FASTA/FASTQ motif oracle\n'
printf 'motif\t%s\n' "$motif"
printf 'fasta_sha256\t%s\n' 521ddceeaaf59dd94ac33bf66c54e2f0500f7b8746424c9ceb894732e836160e
printf 'fastq_sha256\t%s\n' af81dbf7cdb2d08e94e91f77d2d496a24b3a1e7da4b13f759f4b023ca44fa464
printf 'direct_idric_arm\tNOT_VERIFIED\n'
