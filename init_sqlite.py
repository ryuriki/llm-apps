import glob
import os
import subprocess

CSV_DIR = "100knocks-preprocess/docker/work/data"
DB_FILE = "sample.db"

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    
csv_file_paths = glob.glob(f"{CSV_DIR}/*.csv")

for csv_file_path in csv_file_paths:
    table_name = os.path.basename(csv_file_path).replace(".csv", "")
    subprocess.run(["sqlite3","-separator", ",",  DB_FILE, f".import {csv_file_path} {table_name}"])
    subprocess.run(["sqlite3", DB_FILE, f"select count(*) from {table_name}"])