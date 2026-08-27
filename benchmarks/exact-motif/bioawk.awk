BEGIN {
    motif_length = length(motif)
    total = 0
    if (motif_length == 0) {
        print "motif must not be empty" > "/dev/stderr"
        exit 2
    }
}

{
    rest = $seq
    base = 0

    # Use awk's native substring search rather than a character-by-character
    # loop in awk source. Advancing one base after each hit preserves overlaps.
    while (length(rest) >= motif_length) {
        hit = index(rest, motif)
        if (hit == 0)
            break

        printf "%s\t%d\n", $name, base + hit - 1
        total++
        base += hit
        rest = substr(rest, hit + 1)
    }
}

END {
    printf "TOTAL\t%d\n", total
}
