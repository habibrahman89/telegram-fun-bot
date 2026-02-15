import sqlite3

conn = sqlite3.connect("bot.db")
cur = conn.cursor()

# Show tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cur.fetchall())

# Show users
cur.execute("SELECT * FROM users")
rows = cur.fetchall()

print("Users:", rows)

conn.close()