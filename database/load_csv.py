import csv
from .db import get_connection
import re

def clean_string(s):
    """
    Strips leading/trailing spaces, removes surrounding quotes, and normalizes whitespace.
    """
    s = s.strip()                       # remove leading/trailing spaces
    s = re.sub(r'^["\']|["\']$', '', s) # remove surrounding quotes
    s = re.sub(r'\s+', ' ', s)          # collapse multiple spaces
    return s

def normalize_make(make_id, make_name):
    """
    Normalize make:
    - Use NHTSA make_id if available, else fallback to make_name as primary key
    - Clean up name, remove quotes, collapse spaces, convert casing
    """
    clean_name = clean_string(make_name)
    if make_id and make_id.strip() != "":
        return make_id.strip(), clean_name.upper(), "NHTSA"
    else:
        return clean_name.lower(), clean_name.upper(), "EPA"

def normalize_model(model_id, model_name):
    """
    Normalize model:
    - Use NHTSA model_id if available, else fallback to model_name as id
    - Clean up model name, remove quotes, collapse spaces, convert casing
    """
    clean_name = clean_string(model_name)
    if model_id and model_id.strip() != "":
        return model_id.strip(), clean_name.upper()
    else:
        return clean_name.lower(), clean_name.upper()

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
