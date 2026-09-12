args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
    stop("usage: biostrings.R ALGORITHM FASTA MOTIF", call. = FALSE)
}

algorithm <- args[[1]]
input <- args[[2]]
motif_text <- args[[3]]

if (!(algorithm %in% c("auto", "shift-or", "boyer-moore"))) {
    stop("algorithm must be auto, shift-or, or boyer-moore", call. = FALSE)
}
if (!grepl("^[ACGT]+$", motif_text)) {
    stop("motif must contain only uppercase A/C/G/T", call. = FALSE)
}
if (!requireNamespace("Biostrings", quietly = TRUE)) {
    stop("Biostrings is not installed", call. = FALSE)
}

sequences <- Biostrings::readDNAStringSet(input, format = "fasta")
motif <- Biostrings::DNAString(motif_text)
matches <- Biostrings::vmatchPattern(
    motif,
    sequences,
    fixed = TRUE,
    algorithm = algorithm
)
positions_by_record <- lapply(Biostrings::startIndex(matches), function(x) x - 1L)
total <- 0L

for (i in seq_along(positions_by_record)) {
    positions <- positions_by_record[[i]]
    if (length(positions) > 0L) {
        for (position in positions) {
            cat(names(sequences)[[i]], "\t", position, "\n", sep = "")
        }
    }
    total <- total + length(positions)
}

cat("TOTAL\t", total, "\n", sep = "")
