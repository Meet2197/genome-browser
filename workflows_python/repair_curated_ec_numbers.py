import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session, get_connection

# Known-correct curated annotations (matches seed_data.py PFL_GENES)
CURATED_EC_DATA = {
    "pflA": ("EC 1.97.1.4", "Anaerobic metabolism"),
    "pflB": ("EC 2.3.1.54", "Acetate biosynthesis"),
    "pflC": ("EC 2.7.7.-", "Regulatory"),
    "pflD": ("EC 2.3.1.54", "Acetate biosynthesis"),
    "pflE": ("EC 1.17.1.9", "Energy metabolism"),
    "pflF": ("EC -", "Membrane transport"),
    "phlD": ("EC 2.3.1.-", "Antifungal secondary metabolite biosynthesis"),
    "gacA": ("EC -", "Global regulator of secondary metabolism"),
}


def repair():
    conn = get_connection()
    genome = conn.execute(
        "SELECT id FROM genomes WHERE name LIKE 'Pseudomonas fluorescens Pf0-1%'"
    ).fetchone()
    conn.close()

    if not genome:
        print("Pf0-1 genome not found in database.")
        return

    genome_id = genome["id"]
    updated = 0

    with db_session() as conn:
        for gene_name, (ec, func) in CURATED_EC_DATA.items():
            cur = conn.execute(
                """UPDATE genes SET ec_number=?, function=?
                   WHERE genome_id=? AND gene_name=?""",
                (ec, func, genome_id, gene_name)
            )
            if cur.rowcount > 0:
                updated += cur.rowcount
                print(f"  Restored EC data for {gene_name}: {ec}")
            else:
                print(f"  [WARNING] Gene '{gene_name}' not found for genome_id={genome_id} "
                      f"(may have different locus_tag or was renamed)")

    print(f"\nRepaired {updated} genes with EC numbers for Pf0-1.")


if __name__ == "__main__":
    repair()