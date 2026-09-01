from database import get_connection

def migrate():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS bookmarks (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        genome_id   INTEGER NOT NULL REFERENCES genomes(id) ON DELETE CASCADE,
        start       INTEGER NOT NULL,
        end         INTEGER NOT NULL,
        label       TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print("Auth tables created.")

if __name__ == "__main__":
    migrate()