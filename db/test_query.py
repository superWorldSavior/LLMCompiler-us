import sqlite3
import os

# Database file path
DB_PATH = os.path.join('db', 'measurements.db')

def test_query():
    """Test querying the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Test query
    cursor.execute('''
    SELECT date, temperature, humidity 
    FROM measurements 
    ORDER BY date DESC 
    LIMIT 5
    ''')

    # Fetch results
    results = cursor.fetchall()
    
    print("\nLast 5 measurements:")
    print("Date | Temperature | Humidity")
    print("-" * 40)
    for row in results:
        print(f"{row[0]} | {row[1]}°C | {row[2]}%")

    conn.close()

if __name__ == '__main__':
    test_query()
