from database import get_connection

def migrate():
    conn = get_connection()
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(genes)")]
    if "cog_lookup_checked" not in cols:
        conn.execute("ALTER TABLE genes ADD COLUMN cog_lookup_checked INTEGER DEFAULT 0")
        conn.commit()
        print("Added column: cog_lookup_checked")
    else:
        print("Already up to date.")
    conn.close()

if __name__ == "__main__":
    migrate()