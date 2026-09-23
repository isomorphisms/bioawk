#define _POSIX_C_SOURCE 200809L

#include <ctype.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *DEFAULT_MOTIF = "ACGTACGT";

typedef enum {
    ALGORITHM_SCALAR,
    ALGORITHM_SHIFT_OR
} algorithm_t;

typedef struct {
    char *data;
    size_t length;
    size_t capacity;
} sequence_buffer_t;

typedef struct {
    unsigned long masks[256];
    unsigned long match_bit;
    size_t motif_length;
} shift_or_t;

static void die(const char *message)
{
    fprintf(stderr, "%s\n", message);
    exit(2);
}

static int is_canonical_dna_char(unsigned char c)
{
    return c == 'A' || c == 'C' || c == 'G' || c == 'T';
}

static void validate_motif(const char *motif)
{
    size_t i;
    size_t length = strlen(motif);

    if (length == 0)
        die("motif must not be empty");
    if (length >= sizeof(unsigned long) * CHAR_BIT)
        die("motif is too long for this one-machine-word Shift-Or probe");

    for (i = 0; i < length; i++) {
        if (!is_canonical_dna_char((unsigned char)motif[i]))
            die("motif must contain only uppercase A/C/G/T");
    }
}

static void buffer_reset(sequence_buffer_t *buffer)
{
    buffer->length = 0;
    if (buffer->data != NULL)
        buffer->data[0] = '\0';
}

static void buffer_append(sequence_buffer_t *buffer, const char *line)
{
    size_t i;

    for (i = 0; line[i] != '\0'; i++) {
        unsigned char c = (unsigned char)line[i];
        char *new_data;
        size_t new_capacity;

        if (isspace(c))
            continue;
        if (!is_canonical_dna_char(c))
            die("fixture sequence must contain only uppercase A/C/G/T");

        if (buffer->length + 2 > buffer->capacity) {
            new_capacity = buffer->capacity == 0 ? 256 : buffer->capacity * 2;
            new_data = realloc(buffer->data, new_capacity);
            if (new_data == NULL)
                die("out of memory");
            buffer->data = new_data;
            buffer->capacity = new_capacity;
        }

        buffer->data[buffer->length++] = (char)c;
        buffer->data[buffer->length] = '\0';
    }
}

static char *parse_record_name(char *header)
{
    char *name = header + 1;
    char *end;

    while (*name != '\0' && isspace((unsigned char)*name))
        name++;
    if (*name == '\0')
        die("FASTA record name must not be empty");

    end = name;
    while (*end != '\0' && !isspace((unsigned char)*end))
        end++;
    *end = '\0';
    return name;
}

static uint64_t scan_scalar(const char *record_name, const char *sequence,
                            size_t sequence_length, const char *motif,
                            size_t motif_length)
{
    uint64_t count = 0;
    size_t i;

    if (sequence_length < motif_length)
        return 0;

    for (i = 0; i + motif_length <= sequence_length; i++) {
        if (sequence[i] == motif[0] &&
            memcmp(sequence + i, motif, motif_length) == 0) {
            printf("%s\t%zu\n", record_name, i);
            count++;
        }
    }

    return count;
}

static void shift_or_init(shift_or_t *state, const char *motif)
{
    size_t i;

    state->motif_length = strlen(motif);
    state->match_bit = 1UL << state->motif_length;

    for (i = 0; i < 256; i++)
        state->masks[i] = ULONG_MAX;
    for (i = 0; i < state->motif_length; i++)
        state->masks[(unsigned char)motif[i]] &= ~(1UL << i);
}

static uint64_t scan_shift_or(const char *record_name, const char *sequence,
                              size_t sequence_length, const shift_or_t *compiled)
{
    unsigned long state = ~1UL;
    uint64_t count = 0;
    size_t i;

    for (i = 0; i < sequence_length; i++) {
        state |= compiled->masks[(unsigned char)sequence[i]];
        state <<= 1;
        if ((state & compiled->match_bit) == 0) {
            size_t start = i + 1 - compiled->motif_length;
            printf("%s\t%zu\n", record_name, start);
            count++;
        }
    }

    return count;
}

static uint64_t scan_record(algorithm_t algorithm, const char *record_name,
                            const sequence_buffer_t *sequence,
                            const char *motif, const shift_or_t *compiled)
{
    if (algorithm == ALGORITHM_SCALAR) {
        return scan_scalar(record_name, sequence->data, sequence->length,
                           motif, strlen(motif));
    }

    return scan_shift_or(record_name, sequence->data, sequence->length,
                         compiled);
}

static algorithm_t parse_algorithm(const char *name)
{
    if (strcmp(name, "scalar") == 0)
        return ALGORITHM_SCALAR;
    if (strcmp(name, "shift-or") == 0)
        return ALGORITHM_SHIFT_OR;
    die("algorithm must be scalar or shift-or");
    return ALGORITHM_SCALAR;
}

static void usage(const char *program)
{
    fprintf(stderr,
            "usage: %s --algorithm scalar|shift-or [--motif ACGT...] FASTA\n",
            program);
}

int main(int argc, char **argv)
{
    algorithm_t algorithm = ALGORITHM_SCALAR;
    const char *motif = DEFAULT_MOTIF;
    const char *path = NULL;
    FILE *input;
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t line_length;
    char *record_name = NULL;
    char *record_name_storage = NULL;
    sequence_buffer_t sequence = {0};
    shift_or_t compiled;
    uint64_t total = 0;
    int i;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--algorithm") == 0 && i + 1 < argc) {
            algorithm = parse_algorithm(argv[++i]);
        } else if (strcmp(argv[i], "--motif") == 0 && i + 1 < argc) {
            motif = argv[++i];
        } else if (argv[i][0] == '-') {
            usage(argv[0]);
            return 2;
        } else if (path == NULL) {
            path = argv[i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (path == NULL) {
        usage(argv[0]);
        return 2;
    }

    validate_motif(motif);
    shift_or_init(&compiled, motif);

    input = fopen(path, "r");
    if (input == NULL) {
        perror(path);
        return 2;
    }

    while ((line_length = getline(&line, &line_capacity, input)) >= 0) {
        (void)line_length;
        if (line[0] == '>') {
            char *name;

            if (record_name != NULL)
                total += scan_record(algorithm, record_name, &sequence,
                                     motif, &compiled);

            buffer_reset(&sequence);
            free(record_name_storage);
            record_name_storage = strdup(line);
            if (record_name_storage == NULL)
                die("out of memory");
            name = parse_record_name(record_name_storage);
            record_name = name;
        } else {
            if (record_name == NULL)
                die("FASTA sequence data appeared before the first header");
            buffer_append(&sequence, line);
        }
    }

    if (ferror(input)) {
        perror(path);
        return 2;
    }

    if (record_name != NULL)
        total += scan_record(algorithm, record_name, &sequence, motif, &compiled);

    printf("TOTAL\t%" PRIu64 "\n", total);

    free(sequence.data);
    free(record_name_storage);
    free(line);
    fclose(input);
    return 0;
}
