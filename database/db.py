import sqlite3

DB_NAME = "vehicle.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db(reset=False):
    conn = get_connection()
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS noisy_variants;")
        cur.execute("DROP TABLE IF EXISTS models;")
        cur.execute("DROP TABLE IF EXISTS makes;")

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS noisy_variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        noisy_string TEXT NOT NULL,
        model_id TEXT NOT NULL,
        make_id TEXT NOT NULL,
        year INTEGER NOT NULL,
        noise_type TEXT,
        FOREIGN KEY (model_id, make_id, year) REFERENCES models(model_id, make_id, year)
    );
    """)

    conn.commit()
    conn.close()


def fetch_canonical_models(limit=1000, offset=0):
    """
    Fetch canonical model/make/year data from the database with a join, limit, and offset.
    Returns a list of tuples: (make_name, model_name, year)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT mk.make_name, m.model_name, m.year
        FROM models m
        JOIN makes mk ON m.make_id = mk.make_id
        WHERE m.model_name != mk.make_name
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cur.fetchall()
    conn.close()
    return rows
