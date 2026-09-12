#!/usr/bin/env python3

import argparse
from pathlib import Path

ALPHABET = b"ACGT"
DEFAULT_MOTIF = b"ACGTACGT"
DEFAULT_SEED = 0x4D4F5449  # ASCII-ish "MOTI"


def xorshift32(state: int) -> int:
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= state >> 17
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF


def exact_positions(sequence: bytes, motif: bytes) -> list[int]:
    limit = len(sequence) - len(motif) + 1
    if limit <= 0:
        return []
    return [
        i
        for i in range(limit)
        if sequence[i : i + len(motif)] == motif
    ]


def validate_motif(text: str) -> bytes:
    motif = text.encode("ascii")
    if not motif or any(base not in ALPHABET for base in motif):
        raise ValueError("motif must contain only uppercase A/C/G/T")
    return motif


def build_record(state: int, bases: int, motif: bytes) -> tuple[int, bytes]:
    sequence = bytearray(bases)
    for i in range(bases):
        state = xorshift32(state)
        sequence[i] = ALPHABET[state & 3]

    if bases >= len(motif):
        starts = {0, max(0, bases // 2 - len(motif) // 2), bases - len(motif)}
        for start in sorted(starts):
            sequence[start : start + len(motif)] = motif

    return state, bytes(sequence)


def write_fasta_record(handle, name: str, sequence: bytes) -> None:
    handle.write(f">{name}\n".encode("ascii"))
    for start in range(0, len(sequence), 80):
        handle.write(sequence[start : start + 80] + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--motif", default=DEFAULT_MOTIF.decode("ascii"))
    parser.add_argument("--records", type=int, default=8)
    parser.add_argument("--bases-per-record", type=int, default=1_048_576)
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=DEFAULT_SEED)
    args = parser.parse_args()

    if args.records <= 0 or args.bases_per_record <= 0:
        parser.error("records and bases-per-record must be positive")

    try:
        motif = validate_motif(args.motif)
    except ValueError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.oracle.parent.mkdir(parents=True, exist_ok=True)

    state = args.seed & 0xFFFFFFFF
    total = 0
    with args.output.open("wb") as fasta, args.oracle.open("w", encoding="ascii") as oracle:
        for record_index in range(args.records):
            name = f"synthetic_{record_index:03d}"
            state, sequence = build_record(state, args.bases_per_record, motif)
            write_fasta_record(fasta, name, sequence)
            for position in exact_positions(sequence, motif):
                oracle.write(f"{name}\t{position}\n")
                total += 1
        oracle.write(f"TOTAL\t{total}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
