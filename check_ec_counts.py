import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_connection

conn = get_connection()

print("=== Genes with EC numbers, per genome ===")
rows = conn.execute("""
    SELECT genomes.name, COUNT(*) as gene_count
    FROM genes
    JOIN genomes ON genes.genome_id = genomes.id
    WHERE genes.ec_number IS NOT NULL AND genes.ec_number != ''
    GROUP BY genes.genome_id
    ORDER BY gene_count DESC
""").fetchall()

if not rows:
    print("  (none found)")
else:
    for r in rows:
        print(f"  {r['name']}: {r['gene_count']} genes")

print("\n=== Total KEGG pathway annotations ===")
count = conn.execute("SELECT COUNT(*) as c FROM kegg_pathways").fetchone()
print(f"  {count['c']} total gene-pathway links")

conn.close()