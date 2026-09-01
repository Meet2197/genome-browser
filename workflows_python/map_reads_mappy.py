import sys
import os
from collections import defaultdict
import mappy as mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import db_session


def map_reads(reference_fasta, reads_fastq):
    aligner = mp.Aligner(reference_fasta, preset="sr")
    if not aligner:
        raise RuntimeError("Failed to load/index reference FASTA")
    depth = defaultdict(int)
    read_count = 0
    for name, seq, qual in mp.fastx_read(reads_fastq):
        read_count += 1
        for hit in aligner.map(seq):
            for pos in range(hit.r_st, hit.r_en):
                depth[pos] += 1
    print(f"Mapped {read_count} reads.")
    return depth


def store_coverage(genome_id, depth_dict, bin_size=200):
    if not depth_dict:
        print("No coverage data to store.")
        return
    max_pos = max(depth_dict.keys())
    with db_session() as conn:
        conn.execute("DELETE FROM coverage WHERE genome_id=?", (genome_id,))
        pos = 0
        while pos <= max_pos:
            window = [depth_dict.get(p, 0) for p in range(pos, pos + bin_size)]
            avg_depth = sum(window) / len(window) if window else 0
            conn.execute(
                "INSERT INTO coverage (genome_id, position, depth) VALUES (?,?,?)",
                (genome_id, pos, int(avg_depth))
            )
            pos += bin_size
    print(f"Stored binned coverage for genome_id={genome_id}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python map_reads_mappy.py <reference.fasta> <reads.fastq> <genome_id>")
        sys.exit(1)
    depth = map_reads(sys.argv[1], sys.argv[2])
    store_coverage(depth_dict=depth, genome_id=int(sys.argv[3]))