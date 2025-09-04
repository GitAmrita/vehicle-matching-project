import sqlite3
from database.db import get_connection, init_db
from .noise import generate_variants

BATCH_SIZE = 5000
VARIANTS_PER_ROW = 4
TEST_LIMIT = 100  # Set a number for testing

def insert_batch(cur, batch_variants):
    cur.executemany(
        "INSERT INTO noisy_variants (noisy_string, model_id, make_id, year, noise_type) VALUES (?, ?, ?, ?, ?)",
        batch_variants
    )

def get_total_rows(cur):
    cur.execute("SELECT COUNT(*) FROM models")
    return cur.fetchone()[0]

def load_noise():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    total_rows = get_total_rows(cur)
    if TEST_LIMIT:
        total_rows = min(total_rows, TEST_LIMIT)
    print(f"Total rows to process: {total_rows}")

    offset = 0
    processed = 0
    batch_number = 1

    while True:
        batch_limit = BATCH_SIZE
        if TEST_LIMIT:
            remaining = TEST_LIMIT - processed
            if remaining <= 0:
                break
            batch_limit = min(batch_limit, remaining)

        cur.execute("""
            SELECT m.model_id, m.model_name, mk.make_id, mk.make_name, m.year
            FROM models m
            JOIN makes mk ON m.make_id = mk.make_id
            LIMIT ? OFFSET ?
        """, (batch_limit, offset))

        rows = cur.fetchall()
        if not rows:
            break

        batch_variants = []
        for model_id, model_name, make_id, make_name, year in rows:
            variants = generate_variants(model_name, make_name, year, n_variants=VARIANTS_PER_ROW)
            for v, choice in variants:
                batch_variants.append((v, model_id, make_id, year, choice))

        insert_batch(cur, batch_variants)
        conn.commit()

        processed += len(rows)
        print(f"[Batch {batch_number}] Processed {len(rows)} rows, "
              f"inserted {len(batch_variants)} variants. "
              f"Total processed: {processed}/{total_rows} "
              f"({processed/total_rows*100:.2f}%)")
        batch_number += 1
        offset += batch_limit

    conn.close()
    print("✅ All noisy variants generated and loaded into DB.")

