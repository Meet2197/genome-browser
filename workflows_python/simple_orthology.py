import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session, get_connection


def product_similarity_score(product_a, product_b):
    a, b = (product_a or "").lower(), (product_b or "").lower()
    if not a or not b:
        return 0
    a_words, b_words = set(a.split()), set(b.split())
    if not a_words or not b_words:
        return 0
    overlap = len(a_words & b_words)
    return overlap / max(len(a_words), len(b_words))


def find_orthologs():
    conn = get_connection()
    genomes = conn.execute("SELECT id, name FROM genomes").fetchall()
    genes_by_genome = {
        g["id"]: conn.execute(
            "SELECT id, gene_name, product FROM genes WHERE genome_id=?", (g["id"],)
        ).fetchall()
        for g in genomes
    }
    conn.close()

    pairs_added = 0
    with db_session() as conn:
        conn.execute("DELETE FROM comparative_genomics")
        for (gid_a, _), (gid_b, _) in combinations([(g["id"], g["name"]) for g in genomes], 2):
            for gene_a in genes_by_genome[gid_a]:
                best_match, best_score = None, 0.0
                for gene_b in genes_by_genome[gid_b]:
                    score = product_similarity_score(gene_a["product"], gene_b["product"])
                    if score > best_score:
                        best_score, best_match = score, gene_b
                if best_match and best_score >= 0.5:
                    conn.execute(
                        """INSERT INTO comparative_genomics
                           (genome_id, compared_genome_id, gene_id, ortholog_gene_id, identity_percent)
                           VALUES (?,?,?,?,?)""",
                        (gid_a, gid_b, gene_a["id"], best_match["id"], round(best_score * 100, 1))
                    )
                    pairs_added += 1
    print(f"Ortholog pairs stored: {pairs_added}")


if __name__ == "__main__":
    find_orthologs()