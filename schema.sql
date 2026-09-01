-- ==========================================================
-- Plant Microbiome Genome Browser - SQLite Reference Schema
-- ==========================================================

CREATE TABLE IF NOT EXISTS genomes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    assembly_accession  TEXT,
    organism            TEXT,
    host_plant          TEXT,
    environment         TEXT,
    genome_size         INTEGER,
    gc_content          REAL,
    fasta_path          TEXT,
    gff_path            TEXT,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Gene / CDS annotation
CREATE TABLE IF NOT EXISTS genes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id    INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    locus_tag    TEXT,
    gene_name    TEXT,
    start        INTEGER NOT NULL,
    end          INTEGER NOT NULL,
    strand       TEXT CHECK(strand IN ('+','-')),
    feature_type TEXT DEFAULT 'CDS',
    product      TEXT,
    ec_number    TEXT,
    function     TEXT
);
CREATE INDEX IF NOT EXISTS idx_genes_genome_pos ON genes(genome_id, start, end);

-- tRNA / rRNA
CREATE TABLE IF NOT EXISTS rna_features (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id  INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    rna_type   TEXT CHECK(rna_type IN ('tRNA','rRNA')),
    start      INTEGER NOT NULL,
    end        INTEGER NOT NULL,
    strand     TEXT,
    product    TEXT
);
CREATE INDEX IF NOT EXISTS idx_rna_genome_pos ON rna_features(genome_id, start, end);

-- KEGG pathway mapping
CREATE TABLE IF NOT EXISTS kegg_pathways (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id       INTEGER NOT NULL REFERENCES genes(id) ON DELETE CASCADE,
    kegg_id       TEXT,
    pathway_name  TEXT
);

-- COG functional categories
CREATE TABLE IF NOT EXISTS cog_categories (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id        INTEGER NOT NULL REFERENCES genes(id) ON DELETE CASCADE,
    cog_id         TEXT,
    category_code  TEXT,
    category_desc  TEXT
);

-- Mobile genetic elements
CREATE TABLE IF NOT EXISTS mobile_elements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id    INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    element_type TEXT,
    start        INTEGER NOT NULL,
    end          INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mge_genome_pos ON mobile_elements(genome_id, start, end);

-- SNPs / Variants
CREATE TABLE IF NOT EXISTS snps (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id  INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL,
    ref_base   TEXT,
    alt_base   TEXT,
    effect     TEXT
);
CREATE INDEX IF NOT EXISTS idx_snp_genome_pos ON snps(genome_id, position);

-- Windowed GC content
CREATE TABLE IF NOT EXISTS gc_windows (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id   INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL,
    gc_percent  REAL
);
CREATE INDEX IF NOT EXISTS idx_gc_genome_pos ON gc_windows(genome_id, position);

-- Metagenomic read coverage
CREATE TABLE IF NOT EXISTS coverage (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id  INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL,
    depth      INTEGER
);
CREATE INDEX IF NOT EXISTS idx_cov_genome_pos ON coverage(genome_id, position);

-- Metatranscriptomic expression
CREATE TABLE IF NOT EXISTS expression (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id    INTEGER NOT NULL REFERENCES genes(id) ON DELETE CASCADE,
    sample_id  TEXT,
    condition  TEXT,
    tpm        REAL
);

-- Comparative genomics (orthologs across genomes)
CREATE TABLE IF NOT EXISTS comparative_genomics (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id           INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    compared_genome_id  INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    gene_id             INTEGER REFERENCES genes(id),
    ortholog_gene_id    INTEGER,
    identity_percent    REAL
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    genome_id   INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    start       INTEGER NOT NULL,
    end         INTEGER NOT NULL,
    label       TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Environmental metadata (FAIR / MIxS-style)
CREATE TABLE IF NOT EXISTS environmental_metadata (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    genome_id         INTEGER UNIQUE NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
    sample_location   TEXT,
    collection_date   TEXT,
    ph                REAL,
    temperature       REAL,
    isolation_source  TEXT,
    latitude          REAL,
    longitude         REAL
);

-- Full-text search over genes
CREATE VIRTUAL TABLE IF NOT EXISTS gene_search USING fts5(
    gene_name, product, function, locus_tag,
    content='genes', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS genes_ai AFTER INSERT ON genes BEGIN
  INSERT INTO gene_search(rowid, gene_name, product, function, locus_tag)
  VALUES (new.id, new.gene_name, new.product, new.function, new.locus_tag);
END;

CREATE TRIGGER IF NOT EXISTS genes_ad AFTER DELETE ON genes BEGIN
  INSERT INTO gene_search(gene_search, rowid, gene_name, product, function, locus_tag)
  VALUES('delete', old.id, old.gene_name, old.product, old.function, old.locus_tag);
END;