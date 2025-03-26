import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rechnungen")
    rows = cursor.fetchall()
    print("Contents of Rechnungen table:")
    for row in rows:
        print(row)