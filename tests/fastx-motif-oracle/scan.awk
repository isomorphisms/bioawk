BEGIN {
    motif_length = length(motif)
    total = 0
    invalid_motif = 0

    if (motif_length == 0 || motif ~ /[^ACGT]/) {
        print "motif must contain only uppercase A/C/G/T" > "/dev/stderr"
        invalid_motif = 1
        exit 2
    }
}

{
    rest = $seq
    base = 0
    count = 0
    positions = ""

    while (length(rest) >= motif_length) {
        hit = index(rest, motif)
        if (hit == 0)
            break

        position = base + hit - 1
        if (count != 0)
            positions = positions ","
        positions = positions position
        count++
        total++

        # Advance one base past the beginning of the hit so overlaps count.
        base += hit
        rest = substr(rest, hit + 1)
    }

    if (count == 0)
        positions = "-"

    printf "%s\t%s\t%d\t%s\n", input_format, $name, count, positions
}

END {
    if (!invalid_motif)
        printf "%s\tTOTAL\t%d\t-\n", input_format, total
}
