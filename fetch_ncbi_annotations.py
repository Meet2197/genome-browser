
import io
import re
import zipfile
import urllib.request
from database import db_session, get_connection

NCBI_API = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/{}/download?include_annotation_type=GENOME_GFF"


def download_gff(accession: str) -> str:
    url = NCBI_API.format(accession)
    print(f"Downloading annotation for {accession} ...")
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()

    zf = zipfile.ZipFile(io.BytesIO(data))
    gff_files = [n for n in zf.namelist() if n.endswith(".gff")]
    if not gff_files:
        raise RuntimeError(f"No GFF3 file found in NCBI package for {accession}")
    return zf.read(gff_files[0]).decode("utf-8")

import re

EC_PATTERN = re.compile(r"EC[:\s]?(\d+\.\d+\.\d+\.[\d-]+)")


def extract_ec_number(product: str, dbxref: str) -> str:
    """Extracts EC number from product text or Dbxref attribute, if present."""
    for source in (product, dbxref):
        if not source:
            continue
        match = EC_PATTERN.search(source)
        if match:
            return f"EC {match.group(1)}"
    return ""


def parse_gff(gff_text: str):
    genes, rnas = [], []
    for line in gff_text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 9:
            continue
        seqid, source, ftype, start, end, score, strand, phase, attrs = cols
        attr_dict = dict(
            kv.split("=", 1) for kv in attrs.split(";") if "=" in kv
        )
        name = attr_dict.get("gene", attr_dict.get("Name", attr_dict.get("ID", "unknown")))
        product = attr_dict.get("product", "")
        dbxref = attr_dict.get("Dbxref", "")
        # protein_id is the reliable RefSeq protein accession, independent of gene= presence
        protein_accession = attr_dict.get("protein_id", attr_dict.get("Name", ""))
        ec_number = extract_ec_number(product, dbxref)

        if ftype == "CDS":
            genes.append((name, int(start), int(end), strand, product, ec_number, protein_accession))
        elif ftype in ("tRNA", "rRNA"):
            rnas.append((ftype, int(start), int(end), strand, product or name))

    return genes, rnas


def update_genome_annotations(genome_id: int, accession: str):
    gff_text = download_gff(accession)
    genes, rnas = parse_gff(gff_text)

    with db_session() as conn:
        conn.execute(
            "DELETE FROM comparative_genomics WHERE gene_id IN (SELECT id FROM genes WHERE genome_id=?)",
            (genome_id,)
        )
        conn.execute("DELETE FROM genes WHERE genome_id=?", (genome_id,))
        conn.execute("DELETE FROM rna_features WHERE genome_id=?", (genome_id,))

        for name, start, end, strand, product, ec_number, protein_accession in genes:
            conn.execute(
                """INSERT INTO genes
                   (genome_id, locus_tag, gene_name, start, end, strand,
                    feature_type, product, ec_number, protein_accession)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (genome_id, name, name, start, end, strand, "CDS", product, ec_number, protein_accession)
            )

PROTECTED_GENOMES = ["Pseudomonas fluorescens Pf0-1"]

def main():
    conn = get_connection()
    genomes = conn.execute("SELECT id, name, assembly_accession FROM genomes").fetchall()
    conn.close()

    for g in genomes:
        if g["name"] in PROTECTED_GENOMES:
            print(f"Skipping {g['name']}: protected curated demo genome (not overwritten by NCBI fetch)")
            continue
        try:
            update_genome_annotations(g["id"], g["assembly_accession"])
        except Exception as e:
            print(f"  [WARNING] Failed to fetch {g['name']} ({g['assembly_accession']}): {e}")


if __name__ == "__main__":
    main()