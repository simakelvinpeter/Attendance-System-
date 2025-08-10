from flask import Flask, jsonify, request, send_file
import sqlite3, os
from dotenv import load_dotenv
load_dotenv()
DB = os.getenv('DATABASE_PATH', 'attendance.db')

app = Flask(__name__)

def get_conn():
    return sqlite3.connect(DB, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)

@app.route('/api/health')
def health():
    return jsonify({'status':'ok'})

@app.route('/api/attendance', methods=['GET'])
def list_attendance():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance ORDER BY scan_time DESC LIMIT 500")
    rows = cur.fetchall()
    conn.close()
    columns = [c[0] for c in cur.description] if cur else []
    data = [dict(zip(columns, r)) for r in rows]
    return jsonify(data)

# simple export to excel endpoint
@app.route('/api/export', methods=['GET'])
def export():
    import pandas as pd
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    path = 'attendance_export.xlsx'
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
