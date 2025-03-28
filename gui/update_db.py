import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE Abschlagen RENAME TO Abschlagen_old")
    cursor.execute("""
        CREATE TABLE Abschlagen (
            Vertragsnummer TEXT,
            ZeitraumVon TEXT,
            ZeitraumBis TEXT,
            Abschlagsbetrag REAL
        )
    """)
    cursor.execute("INSERT INTO Abschlagen (Vertragsnummer, ZeitraumVon, ZeitraumBis, Abschlagsbetrag) SELECT Vertragsnummer, Abschlagsdatum AS ZeitraumVon, Abschlagsdatum AS ZeitraumBis, Abschlagsbetrag FROM Abschlagen_old")
    cursor.execute("DROP TABLE Abschlagen_old")
    conn.commit()
print("دیتابیس آپدیت شد!")