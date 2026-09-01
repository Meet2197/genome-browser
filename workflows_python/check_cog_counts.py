import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_connection

conn = get_connection()
rows = conn.execute("""
    SELECT genomes.name, COUNT(*) as c
    FROM cog_categories
    JOIN genes ON cog_categories.gene_id = genes.id
    JOIN genomes ON genes.genome_id = genomes.id
    GROUP BY genes.genome_id
    ORDER BY c DESC
""").fetchall()
for r in rows:
    print(f"{r['name']}: {r['c']} COG annotations")
conn.close()