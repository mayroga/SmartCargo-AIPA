# storage.py
import json
import os

DB_FILE = "storage.json"

def save_record(data):
    records = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            records = json.load(f)

    records.append(data)

    with open(DB_FILE, "w") as f:
        json.dump(records, f, indent=2)
