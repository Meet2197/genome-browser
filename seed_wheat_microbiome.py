import random
from database import db_session, get_connection

random.seed(7)

WHEAT_GENOMES = [
    dict(name="Pseudomonas fluorescens SBW25", assembly_accession="GCF_931907645.1",
         organism="Pseudomonas fluorescens SBW25", host_plant="Triticum aestivum",
         environment="Wheat Rhizosphere - Control", genome_size=6722539, gc_content=60.5,
         drought_treatment="Control", precipitation_reduction_percent=0,
         study_reference="Long-term drought manipulation experiment, ZALF (Azarbad et al.-style)"),

    dict(name="Pseudomonas fluorescens SBW25 (Drought)", assembly_accession="GCF_931907645.1",
         organism="Pseudomonas fluorescens SBW25", host_plant="Triticum aestivum",
         environment="Wheat Rhizosphere - Drought-stressed", genome_size=6722539, gc_content=60.5,
         drought_treatment="Drought", precipitation_reduction_percent=30,
         study_reference="Long-term drought manipulation experiment, ZALF (Azarbad et al.-style)"),

    dict(name="Azospirillum brasilense Sp245", assembly_accession="GCF_000237365.1",
         organism="Azospirillum brasilense Sp245", host_plant="Triticum aestivum",
         environment="Wheat Endosphere", genome_size=7544719, gc_content=68.0,
         drought_treatment="Control", precipitation_reduction_percent=0,
         study_reference="Wheat root endophyte N2-fixation & drought tolerance study"),

    dict(name="Bacillus subtilis subsp. subtilis str. 168", assembly_accession="GCF_000009045.1",
         organism="Bacillus subtilis 168", host_plant="Triticum aestivum",
         environment="Wheat Rhizosphere - Drought-stressed", genome_size=4215606, gc_content=43.5,
         drought_treatment="Drought", precipitation_reduction_percent=30,
         study_reference="PGPR biocontrol / drought resilience screening"),

    dict(name="Arthrobacter aurescens TC1", assembly_accession="GCF_000014925.1",
         organism="Arthrobacter aurescens TC1", host_plant="Triticum aestivum",
         environment="Bulk Agricultural Soil - Long-term reduced precipitation", genome_size=4642942, gc_content=62.4,
         drought_treatment="Drought", precipitation_reduction_percent=50,
         study_reference="Actinobacteria enrichment under long-term drought (ZALF field trial)"),

    dict(name="Paenibacillus polymyxa E681", assembly_accession="GCF_000237805.1",
         organism="Paenibacillus polymyxa E681", host_plant="Triticum aestivum",
         environment="Wheat Rhizosphere - Control", genome_size=5541009, gc_content=45.8,
         drought_treatment="Control", precipitation_reduction_percent=0,
         study_reference="Wheat root-associated biocontrol PGPR reference strain"),

    dict(name="Sinorhizobium meliloti 1021", assembly_accession="GCF_000006965.1",
         organism="Sinorhizobium meliloti 1021", host_plant="Triticum aestivum",
         environment="Bulk Agricultural Soil - Long-term reduced precipitation", genome_size=6691694, gc_content=62.1,
         drought_treatment="Rewetting", precipitation_reduction_percent=30,
         study_reference="Soil rhizobiaceae community shift under rewetting after drought"),
]


def seed_wheat():
    with db_session() as conn:
        for g in WHEAT_GENOMES:
            existing = conn.execute(
                "SELECT id FROM genomes WHERE name=?", (g["name"],)
            ).fetchone()
            if existing:
                print(f"Skipping (already exists): {g['name']}")
                continue

            cur = conn.execute(
                """INSERT INTO genomes
                   (name, assembly_accession, organism, host_plant, environment,
                    genome_size, gc_content, fasta_path, gff_path)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (g["name"], g["assembly_accession"], g["organism"], g["host_plant"],
                 g["environment"], g["genome_size"], g["gc_content"],
                 f"storage/fasta/{g['assembly_accession']}.fasta",
                 f"storage/gff3/{g['assembly_accession']}.gff3")
            )
            genome_id = cur.lastrowid

            conn.execute(
                """INSERT INTO environmental_metadata
                   (genome_id, sample_location, collection_date, ph, temperature,
                    isolation_source, latitude, longitude,
                    drought_treatment, precipitation_reduction_percent, study_reference)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (genome_id, "ZALF experimental field site, Müncheberg, Germany",
                 "2022-07-01", round(random.uniform(6.0, 7.2), 1),
                 round(random.uniform(15, 24), 1),
                 f"{g['environment']} - Triticum aestivum field trial",
                 52.8667, 14.1333,   # ZALF Müncheberg approx. coordinates
                 g["drought_treatment"], g["precipitation_reduction_percent"],
                 g["study_reference"])
            )
            print(f"Added: {g['name']} ({g['assembly_accession']})")

    print("\nWheat microbiome genomes seeded successfully.")


if __name__ == "__main__":
    seed_wheat()