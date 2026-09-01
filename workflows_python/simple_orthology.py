import os
import sys
import time
from itertools import combinations
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_connection

STOPWORDS = {
    "protein", "hypothetical", "putative", "family", "domain-containing",
    "domain", "containing", "like", "-like", "predicted", "uncharacterized",
    "conserved", "unknown", "possible", "probable", "related", "associated",
    "subunit", "component", "type", "the", "of", "and", "or", "a", "an",
}

MIN_SCORE = 0.5


def normalize(text):
    return (text or "").lower().strip()


def significant_words(text):
    words = normalize(text).replace(",", " ").replace("(", " ").replace(")", " ").split()
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def is_uninformative(product):
    norm = normalize(product)
    return norm in ("", "hypothetical protein", "putative protein", "uncharacterized protein")


def word_overlap_score(words_a, words_b):
    if not words_a or not words_b:
        return 0
    overlap = len(words_a & words_b)
    return overlap / max(len(words_a), len(words_b))


def build_inverted_index(genes):
    """word -> list of (gene_id, gene_name, word_set) for fast candidate lookup."""
    index = defaultdict(list)
    for g in genes:
        if is_uninformative(g["product"]):
            continue
        words = significant_words(g["product"])
        if not words:
            continue
        for w in words:
            index[w].append(g)
    return index


def find_orthologs_for_pair(conn, gid_a, gid_b, genes_a, genes_b):
    """Returns list of (gene_a_id, gene_b_id, score) tuples."""
    results = []

    # --- Pass 1: fast exact product-string match (O(N+M)) ---
    exact_map_b = {}
    for g in genes_b:
        norm = normalize(g["product"])
        if norm and not is_uninformative(g["product"]):
            exact_map_b.setdefault(norm, g)

    matched_a_ids = set()
    for g in genes_a:
        norm = normalize(g["product"])
        if norm and norm in exact_map_b:
            match = exact_map_b[norm]
            results.append((g["id"], match["id"], 100.0))
            matched_a_ids.add(g["id"])

    # --- Pass 2: fuzzy word-overlap for genes not already matched exactly ---
    index_b = build_inverted_index(genes_b)

    for g in genes_a:
        if g["id"] in matched_a_ids:
            continue  # already found an exact match in Pass 1
        if is_uninformative(g["product"]):
            continue

        words_a = significant_words(g["product"])
        if not words_a:
            continue

        # Gather only candidate genes sharing at least one significant word
        candidates = {}
        for w in words_a:
            for cand in index_b.get(w, []):
                candidates[cand["id"]] = cand

        best_match, best_score = None, 0.0
        for cand in candidates.values():
            words_b = significant_words(cand["product"])
            score = word_overlap_score(words_a, words_b)
            if score > best_score:
                best_score, best_match = score, cand

        if best_match and best_score >= MIN_SCORE:
            results.append((g["id"], best_match["id"], round(best_score * 100, 1)))

    return results


def find_orthologs():
    conn = get_connection()
    genomes = conn.execute("SELECT id, name FROM genomes").fetchall()
    genes_by_genome = {}
    for g in genomes:
        genes_by_genome[g["id"]] = conn.execute(
            "SELECT id, gene_name, product FROM genes WHERE genome_id=?", (g["id"],)
        ).fetchall()

    conn.execute("DELETE FROM comparative_genomics")
    conn.commit()
    conn.close()

    genome_pairs = list(combinations([(g["id"], g["name"]) for g in genomes], 2))
    total_pairs = len(genome_pairs)
    total_added = 0

    print(f"Comparing {len(genomes)} genomes -> {total_pairs} genome pairs to process.\n")
    print("(Safe to Ctrl+C anytime — progress is saved after each completed pair.)\n")

    for idx, ((gid_a, name_a), (gid_b, name_b)) in enumerate(genome_pairs, 1):
        genes_a = genes_by_genome[gid_a]
        genes_b = genes_by_genome[gid_b]

        t0 = time.time()
        pairs = find_orthologs_for_pair(None, gid_a, gid_b, genes_a, genes_b)
        elapsed = time.time() - t0

        conn = get_connection()
        for gene_a_id, gene_b_id, score in pairs:
            conn.execute(
                """INSERT INTO comparative_genomics
                   (genome_id, compared_genome_id, gene_id, ortholog_gene_id, identity_percent)
                   VALUES (?,?,?,?,?)""",
                (gid_a, gid_b, gene_a_id, gene_b_id, score)
            )
        conn.commit()
        conn.close()

        total_added += len(pairs)
        print(f"[{idx}/{total_pairs}] {name_a} vs {name_b}: "
              f"{len(genes_a)}x{len(genes_b)} genes -> {len(pairs)} orthologs "
              f"({elapsed:.1f}s)")

    print(f"\nDone. Total ortholog pairs stored: {total_added}")


if __name__ == "__main__":
    find_orthologs()