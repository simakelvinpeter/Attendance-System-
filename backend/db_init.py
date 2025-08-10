# Creates SQLite tables
import sqlite3
from pathlib import Path
DB = Path(__file__).parent / 'attendance.db'

sql_users = """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  full_name TEXT,
  role TEXT,
  template_pos INTEGER,
  date_enrolled DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

sql_attendance = """
CREATE TABLE IF NOT EXISTS attendance (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  scan_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT,
  course_code TEXT,
  synced INTEGER DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);
"""

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute(sql_users)
cur.execute(sql_attendance)
conn.commit()
conn.close()
print("Database initialized at", DB)

if __name__ == '__main__':
    print("Database initialized at", DB)
