from database import get_connection

def column_exists(conn, table, column):
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
    return column in cols

def migrate():
    conn = get_connection()
    added = []
    for col, coltype in [
        ("drought_treatment", "TEXT"),
        ("precipitation_reduction_percent", "REAL"),
        ("study_reference", "TEXT"),
    ]:
        if not column_exists(conn, "environmental_metadata", col):
            conn.execute(f"ALTER TABLE environmental_metadata ADD COLUMN {col} {coltype}")
            added.append(col)
    conn.commit()
    conn.close()
    print(f"Migration complete. Added columns: {added or 'none (already up to date)'}")

if __name__ == "__main__":
    migrate()