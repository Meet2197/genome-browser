import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session

with db_session() as conn:
    cur = conn.execute("""
        UPDATE genes SET protein_accession = locus_tag
        WHERE genome_id = 1 AND protein_accession IS NULL
        AND locus_tag GLOB '[A-Z][A-Z]_*.*'
    """)
    print(f"Backfilled protein_accession for {cur.rowcount} genes in Pf0-1 (genome_id=1)")