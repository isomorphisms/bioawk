#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../.." && pwd)

printf '%s\n' '== build bioawk reference lane =='
make -C "$root" bioawk

printf '%s\n' '== execute deterministic FASTA/FASTQ motif oracle =='
BIOAWK="$root/bioawk" sh "$here/check.sh"
