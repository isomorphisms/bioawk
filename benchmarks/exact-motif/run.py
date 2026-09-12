#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time


def sequence_bases(path: Path) -> int:
    total = 0
    with path.open("rb") as handle:
        for raw_line in handle:
            if raw_line.startswith(b">"):
                continue
            total += len(b"".join(raw_line.split()))
    return total


def check_biostrings(rscript: str) -> bool:
    result = subprocess.run(
        [
            rscript,
            "-e",
            "quit(status=if (requireNamespace('Biostrings', quietly=TRUE)) 0 else 1)",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def run_checked(name: str, command: list[str], expected: bytes, repeats: int) -> list[float]:
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        elapsed = time.perf_counter() - started
        if completed.returncode != 0:
            sys.stderr.write(f"{name} failed with exit {completed.returncode}\n")
            sys.stderr.buffer.write(completed.stderr)
            raise SystemExit(1)
        if completed.stdout != expected:
            sys.stderr.write(f"{name} did not match the exact oracle\n")
            sys.stderr.write("command: " + " ".join(command) + "\n")
            raise SystemExit(1)
        samples.append(elapsed)
    return samples


def print_row(name: str, samples: list[float], bases: int) -> None:
    median = statistics.median(samples)
    minimum = min(samples)
    mb_per_second = (bases / 1_000_000.0) / median if median > 0 else float("inf")
    print(f"{name}\t{len(samples)}\t{minimum:.6f}\t{median:.6f}\t{mb_per_second:.3f}")


def main() -> int:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--motif", default="ACGTACGT")
    parser.add_argument("--bioawk", required=True, type=Path)
    parser.add_argument("--c-search", required=True, type=Path)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--require-biostrings", action="store_true")
    args = parser.parse_args()

    if args.repeats <= 0:
        parser.error("repeats must be positive")

    expected = args.oracle.read_bytes()
    bases = sequence_bases(args.input)
    environment_path = os.environ.get("PATH", "")
    rscript = shutil.which("Rscript", path=environment_path)

    implementations: list[tuple[str, list[str]]] = [
        (
            "bioawk-index",
            [
                str(args.bioawk),
                "-c",
                "fastx",
                "-v",
                f"motif={args.motif}",
                "-f",
                str(here / "bioawk.awk"),
                str(args.input),
            ],
        ),
        (
            "c-scalar",
            [
                str(args.c_search),
                "--algorithm",
                "scalar",
                "--motif",
                args.motif,
                str(args.input),
            ],
        ),
        (
            "c-shift-or",
            [
                str(args.c_search),
                "--algorithm",
                "shift-or",
                "--motif",
                args.motif,
                str(args.input),
            ],
        ),
    ]

    have_biostrings = rscript is not None and check_biostrings(rscript)
    if have_biostrings:
        for algorithm in ("auto", "shift-or", "boyer-moore"):
            implementations.append(
                (
                    f"Biostrings-{algorithm}",
                    [
                        rscript,
                        str(here / "biostrings.R"),
                        algorithm,
                        str(args.input),
                        args.motif,
                    ],
                )
            )
    elif args.require_biostrings:
        sys.stderr.write("Rscript + Biostrings are required for this target\n")
        return 2
    else:
        sys.stderr.write("SKIP: Rscript + Biostrings not available\n")

    print(f"bases\t{bases}")
    print("implementation\truns\tmin_seconds\tmedian_seconds\twhole_process_Mbases_per_second")
    for name, command in implementations:
        samples = run_checked(name, command, expected, args.repeats)
        print_row(name, samples, bases)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
