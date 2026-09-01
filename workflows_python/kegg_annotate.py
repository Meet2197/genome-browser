import os
import sys
import time
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session, get_connection

KEGG_API = "https://rest.kegg.jp"
BATCH_SIZE = 10          # KEGG's practical limit for multi-ID queries
REQUEST_DELAY = 0.35     # ~3 requests/sec, polite to free public API

session = requests.Session()


def load_all_pathway_names() -> dict:
    """Fetches the complete KEGG pathway name list in ONE request.
       This eliminates the need for a separate HTTP call per pathway."""
    print("Loading full KEGG pathway name list (one-time bulk fetch)...")
    resp = session.get(f"{KEGG_API}/list/pathway", timeout=30)
    resp.raise_for_status()

    pathway_names = {}
    for line in resp.text.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            pid = parts[0].replace("path:", "")
            pathway_names[pid] = parts[1]
    print(f"  Loaded {len(pathway_names)} pathway names.")
    return pathway_names


def batch_ec_to_pathways(ec_batch: list) -> dict:
    """Looks up KEGG pathways for up to 10 EC numbers in a single request.
       Returns {ec_number: [pathway_ids]}."""
    query = "+".join(f"ec:{ec}" for ec in ec_batch)
    try:
        resp = session.get(f"{KEGG_API}/link/pathway/{query}", timeout=15)
        if resp.status_code != 200 or not resp.text.strip():
            return {}
    except requests.RequestException:
        return {}

    results = {}
    for line in resp.text.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            ec_id = parts[0].replace("ec:", "")
            pathway_id = parts[1].replace("path:", "")
            results.setdefault(ec_id, []).append(pathway_id)
    return results


def annotate_all_genomes():
    pathway_names = load_all_pathway_names()

    conn = get_connection()
    # Pull every gene (across all genomes) that has a real EC number
    # and doesn't already have a KEGG pathway assigned.
    genes = conn.execute("""
        SELECT g.id, g.ec_number FROM genes g
        LEFT JOIN kegg_pathways k ON g.id = k.gene_id
        WHERE g.ec_number IS NOT NULL AND g.ec_number != '' AND g.ec_number != 'EC -'
        AND k.id IS NULL
    """).fetchall()
    conn.close()

    if not genes:
        print("No genes need KEGG annotation (either none have EC numbers, "
              "or all are already annotated).")
        return

    print(f"Found {len(genes)} genes with EC numbers needing KEGG annotation.")

    # Normalize EC numbers, group genes by cleaned EC value
    ec_to_gene_ids = {}
    for g in genes:
        ec_clean = g["ec_number"].replace("EC ", "").strip()
        if not ec_clean or ec_clean == "-":
            continue
        ec_to_gene_ids.setdefault(ec_clean, []).append(g["id"])

    unique_ecs = list(ec_to_gene_ids.keys())
    print(f"  ({len(unique_ecs)} unique EC numbers to look up)")

    total_annotated = 0
    start_time = time.time()

    for i in range(0, len(unique_ecs), BATCH_SIZE):
        batch = unique_ecs[i:i + BATCH_SIZE]
        ec_pathway_map = batch_ec_to_pathways(batch)
        time.sleep(REQUEST_DELAY)

        with db_session() as conn:
            for ec, pathway_ids in ec_pathway_map.items():
                gene_ids = ec_to_gene_ids.get(ec, [])
                for pid in pathway_ids[:2]:  # limit to top 2 pathways per EC
                    pname = pathway_names.get(pid, pid)
                    for gene_id in gene_ids:
                        conn.execute(
                            "INSERT INTO kegg_pathways (gene_id, kegg_id, pathway_name) VALUES (?,?,?)",
                            (gene_id, pid, pname)
                        )
                        total_annotated += 1

        done = min(i + BATCH_SIZE, len(unique_ecs))
        elapsed = time.time() - start_time
        print(f"  Processed {done}/{len(unique_ecs)} unique ECs "
              f"({total_annotated} gene-pathway links so far, {elapsed:.1f}s elapsed)")

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s. Total KEGG pathway annotations added: {total_annotated}")


if __name__ == "__main__":
    annotate_all_genomes()