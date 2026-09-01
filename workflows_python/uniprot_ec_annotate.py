import os
import sys
import time
import re
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session, get_connection

UNIPROT_API = "https://rest.uniprot.org"
BATCH_SIZE = 3000    # UniProt comfortably handles large batches per job
POLL_TIMEOUT = 180

session = requests.Session()


def is_refseq_accession(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}_\d+\.\d+$", value or ""))


def submit_id_mapping_job(accessions: list) -> str:
    resp = session.post(
        f"{UNIPROT_API}/idmapping/run",
        data={"from": "RefSeq_Protein", "to": "UniProtKB", "ids": ",".join(accessions)},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["jobId"]


def poll_job_status(job_id: str, timeout=POLL_TIMEOUT) -> bool:
    """Exponential backoff polling: starts fast (1s), backs off to a 5s cap."""
    elapsed = 0
    delay = 1.0
    while elapsed < timeout:
        resp = session.get(f"{UNIPROT_API}/idmapping/status/{job_id}", timeout=30)
        data = resp.json()
        if data.get("jobStatus") == "FINISHED" or "results" in data:
            return True
        if data.get("jobStatus") == "ERROR":
            return False
        time.sleep(delay)
        elapsed += delay
        delay = min(delay * 1.5, 5.0)
    return False


def fetch_id_mapping_results(job_id: str) -> dict:
    results = {}
    url = (f"{UNIPROT_API}/idmapping/uniprotkb/results/{job_id}"
           f"?fields=accession,ec&format=json&size=500")
    while url:
        resp = session.get(url, timeout=30)
        data = resp.json()
        for item in data.get("results", []):
            refseq_id = item.get("from")
            uniprot_entry = item.get("to", {})
            ec_numbers = []
            rec_name = uniprot_entry.get("proteinDescription", {}).get("recommendedName", {})
            for ec in rec_name.get("ecNumbers", []):
                ec_numbers.append(ec.get("value"))
            if ec_numbers:
                results[refseq_id] = ec_numbers[0]

        link_header = resp.headers.get("Link", "")
        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        url = next_match.group(1) if next_match else None
    return results


def process_batch(batch: list, batch_num: int, total_batches: int, max_retries=3) -> int:
    """Submits one batch job, polls, and writes results to DB. Returns count updated.
       Retries up to max_retries times on timeout/error, with backoff between attempts."""
    accession_list = [acc for _, acc in batch]
    gene_id_by_accession = {acc: gid for gid, acc in batch}

    ec_results = None
    for attempt in range(1, max_retries + 1):
        print(f"  Batch {batch_num}/{total_batches}: submitting {len(accession_list)} "
              f"accessions (attempt {attempt}/{max_retries})...")
        try:
            job_id = submit_id_mapping_job(accession_list)
        except requests.RequestException as e:
            print(f"    [WARNING] Failed to submit batch: {e}")
            time.sleep(5 * attempt)
            continue

        if not poll_job_status(job_id):
            print(f"    [WARNING] Batch {batch_num} timed out (attempt {attempt}).")
            time.sleep(5 * attempt)
            continue

        try:
            ec_results = fetch_id_mapping_results(job_id)
            break  # success
        except requests.RequestException as e:
            print(f"    [WARNING] Failed to fetch results: {e}")
            time.sleep(5 * attempt)
            continue

    # Mark ALL genes in this batch as checked, regardless of outcome,
    # so a future run doesn't endlessly retry permanently-failing batches.
    # (If you want failed batches retried indefinitely instead, remove this
    #  fallback block and only mark genes found in ec_results as checked.)
    updated = 0
    with db_session() as conn:
        if ec_results is not None:
            for refseq_acc, ec_number in ec_results.items():
                gene_id = gene_id_by_accession.get(refseq_acc)
                if gene_id:
                    conn.execute(
                        "UPDATE genes SET ec_number=?, ec_lookup_checked=1 WHERE id=?",
                        (f"EC {ec_number}", gene_id)
                    )
                    updated += 1
            # Mark remaining genes in this batch (no EC found) as checked too
            found_ids = {gene_id_by_accession[acc] for acc in ec_results.keys()}
            for gene_id in gene_id_by_accession.values():
                if gene_id not in found_ids:
                    conn.execute(
                        "UPDATE genes SET ec_lookup_checked=1 WHERE id=?", (gene_id,)
                    )
        else:
            print(f"    [WARNING] Batch {batch_num} failed after {max_retries} attempts, "
                  f"leaving genes unchecked for a future run.")

    if ec_results is not None:
        print(f"    -> {updated}/{len(accession_list)} accessions had EC numbers")
    return updated


def main():
    conn = get_connection()
    genes = conn.execute("""
        SELECT id, protein_accession FROM genes
        WHERE protein_accession IS NOT NULL AND protein_accession != ''
        AND ec_lookup_checked = 0
    """).fetchall()
    conn.close()

    refseq_genes = [(g["id"], g["protein_accession"]) for g in genes
                    if is_refseq_accession(g["protein_accession"])]

    if not refseq_genes:
        print("No genes with unassigned EC numbers and valid RefSeq accessions found.")
        return

    print(f"Found {len(refseq_genes)} genes across all genomes needing EC lookup.")
    total_batches = (len(refseq_genes) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Processing in {total_batches} batch(es) of up to {BATCH_SIZE} accessions each.\n")

    start_time = time.time()
    total_updated = 0

    for i in range(0, len(refseq_genes), BATCH_SIZE):
        batch = refseq_genes[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_updated += process_batch(batch, batch_num, total_batches)
        time.sleep(3)  # brief cooldown between batches to avoid server-side throttling

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s. Total genes updated with real EC numbers: {total_updated}")
    print("Note: many genes (e.g. 'hypothetical protein') genuinely have no")
    print("known EC number in UniProt — this is expected, not a bug.")


if __name__ == "__main__":
    main()