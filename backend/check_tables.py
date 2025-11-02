import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'attendance.db'  # Always points to the backend folder
conn = sqlite3.connect(DB)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in attendance.db:", [t[0] for t in tables])
conn.close()
