import sqlite3

# Connect Database
conn = sqlite3.connect("stock_app.db")

# Create Cursor
cursor = conn.cursor()

# Create Portfolio Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_name TEXT,
    quantity INTEGER,
    buy_price REAL
)
""")

# Save Changes
conn.commit()

# Close Connection
conn.close()

print("Database Created Successfully!")