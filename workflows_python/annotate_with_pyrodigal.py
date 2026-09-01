import os
import pyrodigal
from Bio import SeqIO
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session, get_connection

FASTA_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "fasta")


def annotate_fasta(fasta_path: str):
    orf_finder = pyrodigal.GeneFinder(meta=True)
    genes_found = []
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_bytes = bytes(record.seq)
        genes = orf_finder.find_genes(seq_bytes)
        for i, gene in enumerate(genes):
            genes_found.append({
                "locus_tag": f"{record.id}_orf{i+1:04d}",
                "gene_name": f"orf{i+1:04d}",
                "start": gene.begin,
                "end": gene.end,
                "strand": "+" if gene.strand == 1 else "-",
                "product": "Predicted protein (Pyrodigal ab initio gene call)",
            })
    return genes_found


def import_predicted_genes(genome_id: int, genes: list):
    with db_session() as conn:
        for g in genes:
            conn.execute(
                """INSERT INTO genes
                   (genome_id, locus_tag, gene_name, start, end, strand, feature_type, product)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (genome_id, g["locus_tag"], g["gene_name"], g["start"], g["end"],
                 g["strand"], "CDS", g["product"])
            )
    print(f"  -> Inserted {len(genes)} predicted genes for genome_id={genome_id}")


def main():
    conn = get_connection()
    genomes = conn.execute("SELECT id, name, assembly_accession FROM genomes").fetchall()
    conn.close()

    for g in genomes:
        fasta_path = os.path.join(FASTA_DIR, f"{g['assembly_accession']}.fasta")
        if not os.path.exists(fasta_path):
            print(f"Skipping {g['name']}: FASTA not found ({fasta_path})")
            continue

        conn2 = get_connection()
        existing_count = conn2.execute(
            "SELECT COUNT(*) as c FROM genes WHERE genome_id=?", (g["id"],)
        ).fetchone()["c"]
        conn2.close()

        if existing_count > 0:
            print(f"Skipping {g['name']}: already has {existing_count} genes")
            continue

        print(f"Annotating {g['name']} with Pyrodigal...")
        genes = annotate_fasta(fasta_path)
        import_predicted_genes(g["id"], genes)


if __name__ == "__main__":
    main()