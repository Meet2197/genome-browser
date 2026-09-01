from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS

from database import get_connection, init_db, is_empty
import seed_data

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ---------------------------------------------------------------
# Startup: init DB + seed if empty
# ---------------------------------------------------------------
def startup():
    init_db()
    if is_empty():
        seed_data.seed()

startup()


# ---------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/genomes/<int:genome_id>/first_genes")
def get_first_genes(genome_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM genes WHERE genome_id=? ORDER BY start LIMIT 5",
        (genome_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ---------------------------------------------------------------
# Genome endpoints
# ---------------------------------------------------------------
@app.route("/api/genomes")
def list_genomes():
    host_plant = request.args.get("host_plant")
    environment = request.args.get("environment")
    q = request.args.get("q")

    conn = get_connection()
    sql = "SELECT * FROM genomes WHERE 1=1"
    params = []
    if host_plant:
        sql += " AND host_plant = ?"
        params.append(host_plant)
    if environment:
        sql += " AND environment = ?"
        params.append(environment)
    if q:
        sql += " AND (name LIKE ? OR organism LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/genomes/<int:genome_id>")
def get_genome(genome_id):
    conn = get_connection()
    genome = conn.execute("SELECT * FROM genomes WHERE id=?", (genome_id,)).fetchone()
    if not genome:
        conn.close()
        abort(404, description="Genome not found")

    meta = conn.execute(
        "SELECT * FROM environmental_metadata WHERE genome_id=?", (genome_id,)
    ).fetchone()
    conn.close()

    result = dict(genome)
    result["environmental_metadata"] = dict(meta) if meta else None
    return jsonify(result)


# ---------------------------------------------------------------
# Track endpoints (region-based queries: ?start=&end=)
# ---------------------------------------------------------------
def region_query(table, genome_id, start, end, extra_cols="*"):
    conn = get_connection()
    rows = conn.execute(
        f"""SELECT {extra_cols} FROM {table}
            WHERE genome_id=? AND end >= ? AND start <= ?
            ORDER BY start""",
        (genome_id, start, end)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.route("/api/genomes/<int:genome_id>/genes")
def get_genes(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    return jsonify(region_query("genes", genome_id, start, end))


@app.route("/api/genomes/<int:genome_id>/rna")
def get_rna(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    return jsonify(region_query("rna_features", genome_id, start, end))


@app.route("/api/genomes/<int:genome_id>/mobile_elements")
def get_mobile_elements(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    return jsonify(region_query("mobile_elements", genome_id, start, end))


@app.route("/api/genomes/<int:genome_id>/snps")
def get_snps(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM snps WHERE genome_id=? AND position BETWEEN ? AND ?
           ORDER BY position""",
        (genome_id, start, end)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/genomes/<int:genome_id>/gc")
def get_gc(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    conn = get_connection()
    rows = conn.execute(
        """SELECT position, gc_percent FROM gc_windows
           WHERE genome_id=? AND position BETWEEN ? AND ?
           ORDER BY position""",
        (genome_id, start, end)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/genomes/<int:genome_id>/coverage")
def get_coverage(genome_id):
    start = request.args.get("start", 0, type=int)
    end = request.args.get("end", 10_000_000, type=int)
    conn = get_connection()
    rows = conn.execute(
        """SELECT position, depth FROM coverage
           WHERE genome_id=? AND position BETWEEN ? AND ?
           ORDER BY position""",
        (genome_id, start, end)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------
# Gene detail (annotation, KEGG, COG, expression)
# ---------------------------------------------------------------
@app.route("/api/genes/<int:gene_id>")
def get_gene_detail(gene_id):
    conn = get_connection()
    gene = conn.execute("SELECT * FROM genes WHERE id=?", (gene_id,)).fetchone()
    if not gene:
        conn.close()
        abort(404, description="Gene not found")

    genome = conn.execute("SELECT * FROM genomes WHERE id=?", (gene["genome_id"],)).fetchone()
    kegg = conn.execute("SELECT * FROM kegg_pathways WHERE gene_id=?", (gene_id,)).fetchall()
    cog = conn.execute("SELECT * FROM cog_categories WHERE gene_id=?", (gene_id,)).fetchall()
    expr = conn.execute("SELECT * FROM expression WHERE gene_id=?", (gene_id,)).fetchall()
    conn.close()

    result = dict(gene)
    result["genome"] = dict(genome) if genome else None
    result["kegg_pathways"] = [dict(r) for r in kegg]
    result["cog_categories"] = [dict(r) for r in cog]
    result["expression"] = [dict(r) for r in expr]
    return jsonify(result)


# ---------------------------------------------------------------
# Full-text search across genes (FTS5)
# ---------------------------------------------------------------
@app.route("/api/search")
def search_genes():
    q = request.args.get("q", "")
    conn = get_connection()
    rows = conn.execute(
        """SELECT g.* FROM genes g
           JOIN gene_search fts ON g.id = fts.rowid
           WHERE gene_search MATCH ?
           LIMIT 50""",
        (q,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------
# Comparative genomics
# ---------------------------------------------------------------
@app.route("/api/genomes/<int:genome_id>/comparative")
def get_comparative(genome_id):
    compare_to = request.args.get("compare_to", type=int)
    conn = get_connection()
    sql = "SELECT * FROM comparative_genomics WHERE genome_id=?"
    params = [genome_id]
    if compare_to:
        sql += " AND compared_genome_id=?"
        params.append(compare_to)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)