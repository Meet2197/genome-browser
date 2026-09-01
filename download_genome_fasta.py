
import io
import os
import zipfile
import urllib.request
from database import get_connection

NCBI_SEQ_API = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/{}/download?include_annotation_type=GENOME_FASTA"

os.makedirs("storage/fasta", exist_ok=True)


def download_fasta(accession):
    out_path = f"storage/fasta/{accession}.fasta"
    if os.path.exists(out_path):
        print(f"  Already exists, skipping: {out_path}")
        return

    url = NCBI_SEQ_API.format(accession)
    print(f"Downloading FASTA for {accession} ...")
    with urllib.request.urlopen(url, timeout=120) as resp:
        data = resp.read()

    zf = zipfile.ZipFile(io.BytesIO(data))
    fna_files = [n for n in zf.namelist() if n.endswith(".fna")]
    if not fna_files:
        raise RuntimeError("No FASTA (.fna) file found in NCBI package")

    with open(out_path, "wb") as f:
        f.write(zf.read(fna_files[0]))
    print(f"  -> saved {out_path}")


def main():
    conn = get_connection()
    accessions = [r["assembly_accession"] for r in conn.execute(
        "SELECT DISTINCT assembly_accession FROM genomes"
    ).fetchall()]
    conn.close()

    print(f"Found {len(accessions)} unique assembly accessions to download.\n")

    for acc in accessions:
        try:
            download_fasta(acc)
        except Exception as e:
            print(f"  [WARNING] {acc} failed: {e}")


if __name__ == "__main__":
    main()