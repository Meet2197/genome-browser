from database import db_session, get_connection
from itertools import combinations

def normalize(product):
    return (product or "").lower().strip()

def find_and_store_orthologs():
    conn = get_connection()
    genomes = conn.execute("SELECT id, name FROM genomes").fetchall()
    genes_by_genome = {}
    for g in genomes:
        rows = conn.execute("SELECT id, gene_name, product, start FROM genes WHERE genome_id=?", (g["id"],)).fetchall()
        genes_by_genome[g["id"]] = rows
    conn.close()

    pairs_added = 0
    with db_session() as conn:
        conn.execute("DELETE FROM comparative_genomics")  # rebuild fresh
        for (gid_a, name_a), (gid_b, name_b) in combinations(
            [(g["id"], g["name"]) for g in genomes], 2
        ):
            product_map_b = {}
            for gene in genes_by_genome[gid_b]:
                key = normalize(gene["product"])
                if key:
                    product_map_b.setdefault(key, gene)

            for gene_a in genes_by_genome[gid_a]:
                key = normalize(gene_a["product"])
                if key in product_map_b:
                    gene_b = product_map_b[key]
                    conn.execute(
                        """INSERT INTO comparative_genomics
                           (genome_id, compared_genome_id, gene_id, ortholog_gene_id, identity_percent)
                           VALUES (?,?,?,?,?)""",
                        (gid_a, gid_b, gene_a["id"], gene_b["id"], 75.0)  # placeholder identity
                    )
                    pairs_added += 1

    print(f"Ortholog pairs stored: {pairs_added}")

if __name__ == "__main__":
    find_and_store_orthologs()