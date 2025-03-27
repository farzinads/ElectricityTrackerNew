import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"

def create_zahlungen_table():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Zahlungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Vertragsnummer TEXT,
                Zahlungsdatum TEXT,
                Zahlungstyp TEXT,
                Zahlungsbetrag REAL
            )
        """)
        conn.commit()
        print("Table 'Zahlungen' created or already exists.")

def check_zahlungen_table():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Zahlungen")
        rows = cursor.fetchall()
        print("Contents of Zahlungen table:")
        for row in rows:
            print(row)

if __name__ == "__main__":
    create_zahlungen_table()
    check_zahlungen_table()