ROOT := ../..
BUILD := .build

CC ?= cc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Werror
PYTHON ?= python3
BIOAWK ?= $(ROOT)/bioawk
MOTIF := ACGTACGT
REPEATS ?= 5
BENCH_RECORDS ?= 8
BENCH_BASES_PER_RECORD ?= 1048576

C_SEARCH := $(BUILD)/motif_search
BENCH_FASTA := $(BUILD)/benchmark.fa
BENCH_ORACLE := $(BUILD)/benchmark.oracle.tsv

.PHONY: check check-all benchmark benchmark-all corpus clean

$(BIOAWK):
	$(MAKE) -C $(ROOT) bioawk

$(C_SEARCH): motif_search.c
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $< -o $@

check: $(BIOAWK) $(C_SEARCH)
	$(PYTHON) run.py \
		--input fixture.fa \
		--oracle oracle.tsv \
		--motif $(MOTIF) \
		--bioawk $(BIOAWK) \
		--c-search $(C_SEARCH)

check-all: $(BIOAWK) $(C_SEARCH)
	$(PYTHON) run.py \
		--input fixture.fa \
		--oracle oracle.tsv \
		--motif $(MOTIF) \
		--bioawk $(BIOAWK) \
		--c-search $(C_SEARCH) \
		--require-biostrings

corpus: generate_corpus.py
	mkdir -p $(BUILD)
	$(PYTHON) generate_corpus.py \
		--output $(BENCH_FASTA) \
		--oracle $(BENCH_ORACLE) \
		--motif $(MOTIF) \
		--records $(BENCH_RECORDS) \
		--bases-per-record $(BENCH_BASES_PER_RECORD)

benchmark: $(BIOAWK) $(C_SEARCH) corpus
	$(PYTHON) run.py \
		--input $(BENCH_FASTA) \
		--oracle $(BENCH_ORACLE) \
		--motif $(MOTIF) \
		--bioawk $(BIOAWK) \
		--c-search $(C_SEARCH) \
		--repeats $(REPEATS)

benchmark-all: $(BIOAWK) $(C_SEARCH) corpus
	$(PYTHON) run.py \
		--input $(BENCH_FASTA) \
		--oracle $(BENCH_ORACLE) \
		--motif $(MOTIF) \
		--bioawk $(BIOAWK) \
		--c-search $(C_SEARCH) \
		--repeats $(REPEATS) \
		--require-biostrings

clean:
	rm -rf $(BUILD)
