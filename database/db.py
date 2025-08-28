import sqlite3

DB_NAME = "vehicle.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS makes (
        make_id TEXT PRIMARY KEY,     
        make_name TEXT UNIQUE NOT NULL,
        data_source TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS models (
        model_id TEXT,
        model_name TEXT NOT NULL,
        make_id TEXT NOT NULL,
        year INTEGER NOT NULL,
        PRIMARY KEY (model_id, year),
        FOREIGN KEY (make_id) REFERENCES makes(make_id)
    );
    """)

    conn.commit()
    conn.close()
