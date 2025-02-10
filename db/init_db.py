import sqlite3
import os
from datetime import datetime, timedelta
import random

# Ensure db directory exists
os.makedirs('db', exist_ok=True)

# Database file path
DB_PATH = os.path.join('db', 'measurements.db')

def init_database():
    """Initialize the database with test data."""
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create measurements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Generate test data for the last 30 days
    today = datetime.now()
    test_data = []
    for i in range(30):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        temperature = round(random.uniform(15.0, 30.0), 2)
        humidity = round(random.uniform(40.0, 80.0), 2)
        test_data.append((date, temperature, humidity))

    # Insert test data
    cursor.executemany(
        'INSERT INTO measurements (date, temperature, humidity) VALUES (?, ?, ?)',
        test_data
    )

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Database initialized at {DB_PATH}")
    print(f"Added {len(test_data)} test records")

if __name__ == '__main__':
    init_database()
