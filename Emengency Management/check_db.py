import sqlite3

conn = sqlite3.connect('emergency.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM cases")
rows = cursor.fetchall()

print(f"Total rows in cases table: {len(rows)}")
for row in rows:
    print(row)

conn.close()
