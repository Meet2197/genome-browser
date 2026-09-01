from database import get_connection

def column_exists(conn, table, column):
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
    return column in cols

def migrate():
    conn = get_connection()
    if not column_exists(conn, "genes", "protein_accession"):
        conn.execute("ALTER TABLE genes ADD COLUMN protein_accession TEXT")
        conn.commit()
        print("Added column: protein_accession")
    else:
        print("Already up to date.")
    conn.close()

if __name__ == "__main__":
    migrate()