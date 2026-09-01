from database import db_session

OLD_ACCESSION = "GCF_000009225.1"
NEW_ACCESSION = "GCF_931907645.1"

with db_session() as conn:
    cur = conn.execute(
        "SELECT id, name FROM genomes WHERE assembly_accession=?",
        (OLD_ACCESSION,)
    )
    rows = cur.fetchall()

    if not rows:
        print(f"No genomes found with accession {OLD_ACCESSION}. Nothing to update.")
    else:
        for r in rows:
            print(f"Updating genome_id={r['id']} ({r['name']}): "
                  f"{OLD_ACCESSION} -> {NEW_ACCESSION}")

        conn.execute(
            """UPDATE genomes
               SET assembly_accession = ?,
                   fasta_path = ?,
                   gff_path = ?
               WHERE assembly_accession = ?""",
            (NEW_ACCESSION,
             f"storage/fasta/{NEW_ACCESSION}.fasta",
             f"storage/gff3/{NEW_ACCESSION}.gff3",
             OLD_ACCESSION)
        )

        # Also clear out any genes/rna imported under the old (wrong) accession's
        # data, in case a previous partial fetch attempt inserted anything
        for r in rows:
            conn.execute("DELETE FROM genes WHERE genome_id=?", (r["id"],))
            conn.execute("DELETE FROM rna_features WHERE genome_id=?", (r["id"],))

        print(f"\nUpdated {len(rows)} genome(s) successfully.")