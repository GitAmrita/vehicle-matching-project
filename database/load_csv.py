import csv
from .db import get_connection

def normalize_make(make_id, make_name):
    """
    Use NHTSA make_id if available,
    otherwise fallback to make_name as primary key.
    """
    if make_id and make_id.strip() != "":
        return make_id.strip(), make_name.strip(), "NHTSA"
    else:
        return make_name.strip().lower(), make_name.strip(), "EPA"

def normalize_model(model_id, model_name):
    """
    Use NHTSA model_id if available,
    otherwise fallback to model_name as id (optional)
    """
    if model_id and model_id.strip() != "":
        return model_id.strip(), model_name.strip()
    else:
        return model_name.strip().lower(), model_name.strip()

def load_csv(csv_file):
    conn = get_connection()
    cur = conn.cursor()

    with open(csv_file, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Normalize make
            make_id, make_name, data_source = normalize_make(row.get("Make_ID"), row.get("Make_Name"))

            # Normalize model
            model_id, model_name = normalize_model(row.get("Model_ID"), row.get("Model_Name"))
            year = int(row.get("Year"))

            # Insert make (deduplicated)
            cur.execute("""
                INSERT OR IGNORE INTO makes (make_id, make_name, data_source)
                VALUES (?, ?, ?)
            """, (make_id, make_name, data_source))

            # Insert model with year
            cur.execute("""
                INSERT OR IGNORE INTO models (model_id, model_name, make_id, year)
                VALUES (?, ?, ?, ?)
            """, (model_id, model_name, make_id, year))

    conn.commit()
    conn.close()
    print(f"✅ Loaded data from {csv_file}")
