from flask import Flask, jsonify, request, abort, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
from storage_client import get_presigned_url, is_available as minio_available
from database import get_connection, init_db, is_empty
import seed_data

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

app.secret_key = secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper

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



# ---------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "username already taken"}), 409

    pw_hash = generate_password_hash(password)
    cur = conn.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (username, pw_hash))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    session["user_id"] = user_id
    session["username"] = username
    return jsonify({"id": user_id, "username": username})


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"id": user["id"], "username": user["username"]})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"})


@app.route("/api/auth/me")
def me():
    if "user_id" not in session:
        return jsonify({"user": None})
    return jsonify({"user": {"id": session["user_id"], "username": session["username"]}})


# ---------------------------------------------------------------
# Bookmark endpoints
# ---------------------------------------------------------------
@app.route("/api/bookmarks", methods=["GET"])
@login_required
def list_bookmarks():
    conn = get_connection()
    rows = conn.execute(
        """SELECT b.*, g.name as genome_name FROM bookmarks b
           JOIN genomes g ON b.genome_id = g.id
           WHERE b.user_id=? ORDER BY b.created_at DESC""",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/bookmarks", methods=["POST"])
@login_required
def create_bookmark():
    data = request.get_json()
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO bookmarks (user_id, genome_id, start, end, label)
           VALUES (?,?,?,?,?)""",
        (session["user_id"], data["genome_id"], data["start"], data["end"], data.get("label", ""))
    )
    conn.commit()
    bookmark_id = cur.lastrowid
    conn.close()
    return jsonify({"id": bookmark_id})


@app.route("/api/bookmarks/<int:bookmark_id>", methods=["DELETE"])
@login_required
def delete_bookmark(bookmark_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM bookmarks WHERE id=? AND user_id=?",
        (bookmark_id, session["user_id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


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

@app.route("/api/storage/status")
def storage_status():
    return jsonify({"minio_available": minio_available()})


@app.route("/api/genomes/<int:genome_id>/files")
def genome_files(genome_id):
    conn = get_connection()
    genome = conn.execute("SELECT * FROM genomes WHERE id=?", (genome_id,)).fetchone()
    conn.close()
    if not genome:
        abort(404)

    acc = genome["assembly_accession"]

    if minio_available():
        return jsonify({
            "source": "minio",
            "fasta_url": get_presigned_url(f"jbrowse/{acc}.fa"),
            "fasta_index_url": get_presigned_url(f"jbrowse/{acc}.fa.fai"),
            "gff_url": get_presigned_url(f"jbrowse/{acc}.sorted.gff3.gz"),
            "gff_index_url": get_presigned_url(f"jbrowse/{acc}.sorted.gff3.gz.tbi"),
        })
    else:
        return jsonify({
            "source": "local",
            "fasta_url": f"/storage/jbrowse/{acc}.fa",
            "fasta_index_url": f"/storage/jbrowse/{acc}.fa.fai",
            "gff_url": f"/storage/jbrowse/{acc}.sorted.gff3.gz",
            "gff_index_url": f"/storage/jbrowse/{acc}.sorted.gff3.gz.tbi",
        })
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
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT g.*, genomes.name as genome_name
               FROM genes g
               JOIN gene_search fts ON g.id = fts.rowid
               JOIN genomes ON g.genome_id = genomes.id
               WHERE gene_search MATCH ?
               ORDER BY rank
               LIMIT 50""",
            (q + "*",)
        ).fetchall()
    except Exception:
        # Fallback if query has FTS5 special characters that break MATCH syntax
        rows = conn.execute(
            """SELECT g.*, genomes.name as genome_name
               FROM genes g JOIN genomes ON g.genome_id = genomes.id
               WHERE g.gene_name LIKE ? OR g.product LIKE ?
               LIMIT 50""",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/search/genomes")
def search_genomes_fulltext():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM genomes
           WHERE name LIKE ? OR organism LIKE ? OR host_plant LIKE ? OR environment LIKE ?
           LIMIT 50""",
        tuple(f"%{q}%" for _ in range(4))
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/pipeline_status")
def pipeline_status():
    """Reports which genomes have gene/ortholog/coverage data, useful
       for tracking which Phase 7 pipelines have been run."""
    conn = get_connection()
    genomes = conn.execute("SELECT id, name FROM genomes").fetchall()
    result = []
    for g in genomes:
        gene_count = conn.execute("SELECT COUNT(*) c FROM genes WHERE genome_id=?", (g["id"],)).fetchone()["c"]
        cov_count = conn.execute("SELECT COUNT(*) c FROM coverage WHERE genome_id=?", (g["id"],)).fetchone()["c"]
        ortholog_count = conn.execute(
            "SELECT COUNT(*) c FROM comparative_genomics WHERE genome_id=?", (g["id"],)
        ).fetchone()["c"]
        result.append({
            "genome_id": g["id"], "name": g["name"],
            "genes": gene_count, "coverage_windows": cov_count, "orthologs": ortholog_count
        })
    conn.close()
    return jsonify(result)

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
# Synteny comparison
# ---------------------------------------------------------------
@app.route("/api/synteny")
def synteny():
    genome_a = request.args.get("genome_a", type=int)
    genome_b = request.args.get("genome_b", type=int)
    if not genome_a or not genome_b:
        return jsonify({"error": "genome_a and genome_b required"}), 400

    conn = get_connection()
    rows = conn.execute(
        """SELECT cg.identity_percent,
                  ga.id as gene_a_id, ga.gene_name as gene_a_name, ga.start as a_start, ga.end as a_end,
                  gb.id as gene_b_id, gb.gene_name as gene_b_name, gb.start as b_start, gb.end as b_end
           FROM comparative_genomics cg
           JOIN genes ga ON cg.gene_id = ga.id
           JOIN genes gb ON cg.ortholog_gene_id = gb.id
           WHERE cg.genome_id=? AND cg.compared_genome_id=?
           ORDER BY ga.start""",
        (genome_a, genome_b)
    ).fetchall()

    genome_a_info = conn.execute("SELECT id, name, genome_size FROM genomes WHERE id=?", (genome_a,)).fetchone()
    genome_b_info = conn.execute("SELECT id, name, genome_size FROM genomes WHERE id=?", (genome_b,)).fetchone()
    conn.close()

    return jsonify({
        "genome_a": dict(genome_a_info),
        "genome_b": dict(genome_b_info),
        "links": [dict(r) for r in rows]
    })

# ---------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)