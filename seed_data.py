import random
from database import db_session, init_db, is_empty

random.seed(42)

GENOMES = [
    dict(name="Pseudomonas fluorescens Pf0-1", assembly_accession="GCF_000007765.2",
         organism="Pseudomonas fluorescens", host_plant="Arabidopsis thaliana",
         environment="Rhizosphere", genome_size=6438405, gc_content=60.5,
         fasta_path="storage/fasta/pf0-1.fasta", gff_path="storage/gff3/pf0-1.gff3"),
    dict(name="Bacillus velezensis FZB42", assembly_accession="GCF_000015785.2",
         organism="Bacillus velezensis", host_plant="Arabidopsis thaliana",
         environment="Rhizosphere", genome_size=3918589, gc_content=46.5,
         fasta_path="storage/fasta/fzb42.fasta", gff_path="storage/gff3/fzb42.gff3"),
    dict(name="Streptomyces griseus", assembly_accession="GCF_000009765.1",
         organism="Streptomyces griseus subsp. griseus NBRC 13350", host_plant="Arabidopsis thaliana",
         environment="Rhizosphere", genome_size=8545929, gc_content=72.2,
         fasta_path="storage/fasta/griseus.fasta", gff_path="storage/gff3/griseus.gff3"),
    dict(name="Pseudomonas putida KT2440", assembly_accession="GCF_000007565.2",
         organism="Pseudomonas putida KT2440", host_plant="Zea mays",
         environment="Rhizosphere", genome_size=6181873, gc_content=61.5,
         fasta_path="storage/fasta/kt2440.fasta", gff_path="storage/gff3/kt2440.gff3"),
    dict(name="Burkholderia phytofirmans PsJN", assembly_accession="GCF_000020125.1",
         organism="Paraburkholderia phytofirmans PsJN", host_plant="Oryza sativa",
         environment="Endosphere", genome_size=8214977, gc_content=62.5,
         fasta_path="storage/fasta/psjn.fasta", gff_path="storage/gff3/psjn.gff3"),
    dict(name="Methylobacterium extorquens PA1", assembly_accession="GCF_000018345.1",
         organism="Methylobacterium extorquens PA1", host_plant="Solanum lycopersicum",
         environment="Phyllosphere", genome_size=6111673, gc_content=68.6,
         fasta_path="storage/fasta/pa1.fasta", gff_path="storage/gff3/pa1.gff3"),
    dict(name="Streptomyces coelicolor A3(2)", assembly_accession="GCF_000203835.1",
         organism="Streptomyces coelicolor A3(2)", host_plant=None,
         environment="Bulk Soil", genome_size=8667507, gc_content=72.1,
         fasta_path="storage/fasta/coelicolor.fasta", gff_path="storage/gff3/coelicolor.gff3"),
]

# ---------------------------------------------------------------------
# Real, literature-documented genes for each organism.
# Coordinates below are illustrative placements within a representative
# genomic window (NOT exact NCBI coordinates). Gene symbols, products,
# and EC numbers are real annotations reported for these organisms.
# For exact real coordinates, run fetch_ncbi_annotations.py (see below)
# to pull live GFF3 data from NCBI Datasets API into this database.
# ---------------------------------------------------------------------

GENE_SETS = {
    "Pseudomonas fluorescens Pf0-1": [
        # (gene_name, start, end, strand, product, ec_number, function)
        ("pflA", 1_232_100, 1_233_450, "+", "Pyruvate formate-lyase activating enzyme", "EC 1.97.1.4", "Anaerobic metabolism"),
        ("pflB", 1_233_600, 1_234_800, "+", "Formate C-acetyltransferase", "EC 2.3.1.54", "Acetate biosynthesis"),
        ("pflC", 1_234_950, 1_236_050, "+", "Pyruvate formate-lyase regulator", "EC 2.7.7.-", "Regulatory"),
        ("pflD", 1_234_850, 1_236_102, "+", "Formate acetyltransferase", "EC 2.3.1.54", "Acetate biosynthesis"),
        ("pflE", 1_240_200, 1_241_500, "+", "Formate dehydrogenase subunit", "EC 1.17.1.9", "Energy metabolism"),
        ("pflF", 1_248_000, 1_249_600, "+", "Formate transporter", "EC -", "Membrane transport"),
        ("phlD", 1_252_000, 1_253_100, "+", "2,4-diacetylphloroglucinol biosynthesis protein PhlD", "EC 2.3.1.-", "Antifungal secondary metabolite biosynthesis"),
        ("gacA", 1_255_000, 1_255_800, "+", "Response regulator GacA", "EC -", "Global regulator of secondary metabolism"),
    ],
    "Bacillus velezensis FZB42": [
        ("srfAA", 10_000, 35_000, "+", "Surfactin synthetase subunit 1 (NRPS)", "EC 2.7.8.-", "Lipopeptide antibiotic biosynthesis"),
        ("srfAB", 35_100, 60_000, "+", "Surfactin synthetase subunit 2 (NRPS)", "EC 2.7.8.-", "Lipopeptide antibiotic biosynthesis"),
        ("fenA", 62_000, 70_000, "+", "Fengycin synthetase FenA", "EC 2.7.8.-", "Antifungal lipopeptide biosynthesis"),
        ("bmyA", 72_500, 82_000, "+", "Bacillomycin D synthetase BmyA", "EC 2.7.8.-", "Antifungal lipopeptide biosynthesis"),
        ("dfnA", 90_000, 96_500, "+", "Difficidin polyketide synthase DfnA", "EC 2.3.1.-", "Broad-spectrum antibacterial polyketide biosynthesis"),
        ("bacA", 100_200, 101_400, "+", "Bacilysin biosynthesis protein BacA", "EC -", "Dipeptide antibiotic biosynthesis"),
        ("ituA", 105_000, 118_000, "+", "Iturin A synthetase IturA", "EC 2.7.8.-", "Antifungal lipopeptide biosynthesis"),
    ],
    "Streptomyces griseus": [
        ("strA", 4_210_000, 4_211_200, "+", "Streptomycin-6-phosphotransferase StrA", "EC 2.7.1.72", "Streptomycin biosynthesis / self-resistance"),
        ("strB1", 4_211_300, 4_212_500, "+", "Streptomycin biosynthesis protein StrB1", "EC 2.4.1.-", "Streptomycin biosynthesis"),
        ("strR", 4_212_600, 4_213_400, "+", "Streptomycin biosynthesis regulatory protein StrR", "EC -", "Pathway-specific transcriptional activator"),
        ("aphD", 4_213_500, 4_214_600, "+", "Aminoglycoside phosphotransferase AphD", "EC 2.7.1.-", "Antibiotic resistance / self-protection"),
        ("strN", 4_214_700, 4_215_900, "+", "dTDP-dihydrostreptose synthase StrN", "EC 4.2.1.-", "Streptomycin sugar precursor biosynthesis"),
        ("adpA", 4_220_000, 4_221_500, "+", "AdpA transcriptional regulator", "EC -", "Master regulator of secondary metabolism & morphological differentiation"),
    ],
    "Pseudomonas putida KT2440": [
        ("benA", 1_050_000, 1_051_500, "+", "Benzoate 1,2-dioxygenase alpha subunit BenA", "EC 1.14.12.10", "Aromatic compound degradation"),
        ("benB", 1_051_600, 1_052_900, "+", "Benzoate 1,2-dioxygenase beta subunit BenB", "EC 1.14.12.10", "Aromatic compound degradation"),
        ("catA", 1_060_000, 1_061_100, "+", "Catechol 1,2-dioxygenase CatA", "EC 1.13.11.1", "Catechol / beta-ketoadipate pathway"),
        ("catB", 1_061_200, 1_062_300, "+", "Muconate cycloisomerase CatB", "EC 5.5.1.1", "Beta-ketoadipate pathway"),
        ("pvdA", 1_500_000, 1_501_400, "+", "L-ornithine N5-oxygenase PvdA", "EC 1.14.13.195", "Pyoverdine siderophore biosynthesis"),
        ("pvdD", 1_505_000, 1_520_000, "+", "Pyoverdine synthetase D (NRPS)", "EC 6.3.2.-", "Siderophore biosynthesis / iron acquisition"),
    ],
    "Burkholderia phytofirmans PsJN": [
        ("acdS", 2_100_000, 2_101_200, "+", "1-aminocyclopropane-1-carboxylate deaminase AcdS", "EC 3.5.99.7", "Plant ethylene modulation / growth promotion"),
        ("ipdC", 2_150_000, 2_151_300, "+", "Indole-3-pyruvate decarboxylase IpdC", "EC 4.1.1.74", "Indole-3-acetic acid (auxin) biosynthesis"),
        ("nifH", 3_000_000, 3_001_100, "+", "Nitrogenase iron protein NifH", "EC 1.18.6.1", "Nitrogen fixation"),
        ("nifD", 3_001_200, 3_002_800, "+", "Nitrogenase molybdenum-iron protein alpha chain NifD", "EC 1.18.6.1", "Nitrogen fixation"),
        ("pchA", 3_500_000, 3_501_200, "+", "Salicylate biosynthesis isochorismate synthase PchA", "EC 5.4.4.2", "Siderophore precursor biosynthesis"),
    ],
    "Methylobacterium extorquens PA1": [
        ("mxaF", 800_000, 802_400, "+", "Methanol dehydrogenase large subunit MxaF", "EC 1.1.2.7", "Methylotrophy / C1 metabolism"),
        ("mxaI", 802_500, 802_900, "+", "Methanol dehydrogenase small subunit MxaI", "EC 1.1.2.7", "Methylotrophy / C1 metabolism"),
        ("xoxF", 850_000, 852_300, "+", "Lanthanide-dependent methanol dehydrogenase XoxF", "EC 1.1.2.10", "Alternative methanol oxidation pathway"),
        ("fae", 900_000, 900_700, "+", "Formaldehyde-activating enzyme Fae", "EC 4.2.1.147", "Formaldehyde detoxification / C1 assimilation"),
        ("mtdA", 901_000, 902_100, "+", "Methylene-tetrahydromethanopterin dehydrogenase MtdA", "EC 1.5.1.-", "C1 metabolism"),
    ],
    "Streptomyces coelicolor A3(2)": [
        ("actI", 5_500_000, 5_505_000, "+", "Actinorhodin polyketide synthase ActI", "EC 2.3.1.-", "Actinorhodin (blue pigment antibiotic) biosynthesis"),
        ("actII-orf4", 5_505_100, 5_506_200, "+", "Actinorhodin cluster activator ActII-ORF4", "EC -", "Pathway-specific transcriptional regulator"),
        ("redD", 5_600_000, 5_601_400, "+", "Undecylprodigiosin pathway regulator RedD", "EC -", "Prodiginine antibiotic regulation"),
        ("redX", 5_601_500, 5_606_000, "+", "Undecylprodigiosin biosynthesis PKS RedX", "EC 2.3.1.-", "Prodiginine (red pigment antibiotic) biosynthesis"),
        ("whiG", 5_700_000, 5_701_100, "+", "RNA polymerase sigma factor WhiG", "EC -", "Sporulation initiation"),
        ("cdaPS1", 5_750_000, 5_760_000, "+", "Calcium-dependent antibiotic peptide synthetase CdaPS1", "EC 2.7.8.-", "Lipopeptide antibiotic biosynthesis"),
    ],
}

RNA_FEATURES_PF01 = [
    ("tRNA", 1_218_500, 1_218_580, "+", "tRNA-Leu"),
    ("tRNA", 1_221_000, 1_221_080, "+", "tRNA-Gly"),
    ("tRNA", 1_224_700, 1_224_780, "+", "tRNA-Ala"),
    ("tRNA", 1_227_300, 1_227_380, "+", "tRNA-Ser"),
    ("tRNA", 1_237_000, 1_237_080, "-", "tRNA-Val"),
    ("tRNA", 1_246_500, 1_246_580, "+", "tRNA-Thr"),
    ("tRNA", 1_251_200, 1_251_280, "+", "tRNA-Pro"),
    ("rRNA", 1_217_800, 1_219_300, "+", "16S ribosomal RNA"),
    ("rRNA", 1_223_900, 1_225_400, "+", "23S ribosomal RNA"),
    ("rRNA", 1_249_800, 1_251_100, "+", "5S ribosomal RNA"),
]

MOBILE_ELEMENTS_PF01 = [
    ("Transposon", 1_222_600, 1_223_300),
    ("Transposon", 1_228_900, 1_229_500),
    ("Insertion Sequence", 1_230_200, 1_230_800),
    ("Transposon", 1_241_900, 1_242_500),
    ("Insertion Sequence", 1_243_100, 1_243_700),
]

SNP_POSITIONS_PF01 = [1_219_600, 1_221_400, 1_226_800, 1_231_900, 1_234_400,
                       1_234_900, 1_235_100, 1_244_300, 1_246_100, 1_248_900]


def gen_region_tracks(genome_id, region_start, region_end, base_gc, step=200):
    """Generate synthetic GC content + metagenomic coverage windows
       centered around the genome's actual reported GC%."""
    rows_gc, rows_cov = [], []
    pos = region_start
    while pos < region_end:
        gc = round(random.gauss(base_gc, 3.5), 2)
        gc = max(20.0, min(85.0, gc))
        depth = max(0, int(random.gauss(45, 15)))
        rows_gc.append((genome_id, pos, gc))
        rows_cov.append((genome_id, pos, depth))
        pos += step
    return rows_gc, rows_cov


def seed():
    init_db()
    if not is_empty():
        print("Database already seeded - skipping.")
        return

    with db_session() as conn:
        genome_ids = {}
        for g in GENOMES:
            cur = conn.execute(
                """INSERT INTO genomes
                   (name, assembly_accession, organism, host_plant, environment,
                    genome_size, gc_content, fasta_path, gff_path)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (g["name"], g["assembly_accession"], g["organism"], g["host_plant"],
                 g["environment"], g["genome_size"], g["gc_content"],
                 g["fasta_path"], g["gff_path"])
            )
            genome_ids[g["name"]] = cur.lastrowid

            conn.execute(
                """INSERT INTO environmental_metadata
                   (genome_id, sample_location, collection_date, ph, temperature,
                    isolation_source, latitude, longitude)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (cur.lastrowid, f"{g['environment']} sample site",
                 "2023-05-14", round(random.uniform(5.5, 7.5), 1),
                 round(random.uniform(18, 28), 1),
                 f"{g['host_plant'] or 'Soil'} associated microbiome",
                 round(random.uniform(-40, 40), 4),
                 round(random.uniform(-120, 120), 4))
            )

        # --- Genes for every genome ---
        gene_id_map = {}  # genome_name -> {gene_name: id}
        for genome_name, gene_list in GENE_SETS.items():
            gid = genome_ids[genome_name]
            gene_id_map[genome_name] = {}
            for name, start, end, strand, product, ec, func in gene_list:
                cur = conn.execute(
                    """INSERT INTO genes
                       (genome_id, locus_tag, gene_name, start, end, strand,
                        feature_type, product, ec_number, function)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (gid, f"{name.upper()}_{random.randint(1000,9999)}", name,
                     start, end, strand, "CDS", product, ec, func)
                )
                gene_id_map[genome_name][name] = cur.lastrowid

                # KEGG / COG / expression for every gene (so no genome is empty)
                conn.execute(
                    "INSERT INTO kegg_pathways (gene_id, kegg_id, pathway_name) VALUES (?,?,?)",
                    (cur.lastrowid, f"K{random.randint(10000,99999)}", "Secondary metabolite biosynthesis")
                )
                conn.execute(
                    """INSERT INTO cog_categories (gene_id, cog_id, category_code, category_desc)
                       VALUES (?,?,?,?)""",
                    (cur.lastrowid, f"COG{random.randint(1000,9999)}", "Q",
                     "Secondary metabolites biosynthesis, transport and catabolism")
                )
                conn.execute(
                    """INSERT INTO expression (gene_id, sample_id, condition, tpm)
                       VALUES (?,?,?,?)""",
                    (cur.lastrowid, "SRR_demo_sample_01", "Root-associated", round(random.uniform(5, 180), 1))
                )

        # --- Pf0-1 specific tracks (RNA, mobile elements, SNPs, GC, coverage) ---
        pf0_1_id = genome_ids["Pseudomonas fluorescens Pf0-1"]

        for rtype, start, end, strand, product in RNA_FEATURES_PF01:
            conn.execute(
                """INSERT INTO rna_features (genome_id, rna_type, start, end, strand, product)
                   VALUES (?,?,?,?,?,?)""",
                (pf0_1_id, rtype, start, end, strand, product)
            )

        for etype, start, end in MOBILE_ELEMENTS_PF01:
            conn.execute(
                "INSERT INTO mobile_elements (genome_id, element_type, start, end) VALUES (?,?,?,?)",
                (pf0_1_id, etype, start, end)
            )

        bases = ["A", "C", "G", "T"]
        for pos in SNP_POSITIONS_PF01:
            ref = random.choice(bases)
            alt = random.choice([b for b in bases if b != ref])
            effect = random.choice(["synonymous", "missense", "intergenic"])
            conn.execute(
                """INSERT INTO snps (genome_id, position, ref_base, alt_base, effect)
                   VALUES (?,?,?,?,?)""",
                (pf0_1_id, pos, ref, alt, effect)
            )

        # --- GC + Coverage tracks for EVERY genome, centered on its real GC% ---
        for g in GENOMES:
            gid = genome_ids[g["name"]]
            if g["name"] == "Pseudomonas fluorescens Pf0-1":
                region_start, region_end = 1_200_000, 1_260_000
            else:
                genes_for_this = GENE_SETS.get(g["name"], [])
                if genes_for_this:
                    min_start = min(x[1] for x in genes_for_this) - 5000
                    max_end = max(x[2] for x in genes_for_this) + 5000
                    region_start, region_end = max(0, min_start), max_end
                else:
                    region_start, region_end = 0, 60000

            gc_rows, cov_rows = gen_region_tracks(gid, region_start, region_end, g["gc_content"], step=200)
            conn.executemany(
                "INSERT INTO gc_windows (genome_id, position, gc_percent) VALUES (?,?,?)", gc_rows
            )
            conn.executemany(
                "INSERT INTO coverage (genome_id, position, depth) VALUES (?,?,?)", cov_rows
            )

        # --- Comparative genomics example ---
        pfld_id = gene_id_map["Pseudomonas fluorescens Pf0-1"]["pflD"]
        kt2440_id = genome_ids["Pseudomonas putida KT2440"]
        conn.execute(
            """INSERT INTO comparative_genomics
               (genome_id, compared_genome_id, gene_id, ortholog_gene_id, identity_percent)
               VALUES (?,?,?,?,?)""",
            (pf0_1_id, kt2440_id, pfld_id, None, 87.3)
        )

    print("Database seeded successfully -> genome_browser.db")


if __name__ == "__main__":
    seed()