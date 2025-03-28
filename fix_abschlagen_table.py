import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # تغییر نام جدول فعلی به موقت
    try:
        cursor.execute("ALTER TABLE Abschlagen RENAME TO Abschlagen_old")
    except sqlite3.OperationalError:
        print("جدول Abschlagen از قبل وجود نداره، ادامه می‌دیم...")
    
    # ساخت جدول جدید با ساختار درست
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Abschlagen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Vertragsnummer TEXT,
            ZeitraumVon TEXT,
            ZeitraumBis TEXT,
            Abschlagsbetrag REAL,
            Status TEXT,
            FOREIGN KEY (Vertragsnummer) REFERENCES contracts(Vertragsnummer)
        )
    ''')
    
    # انتقال داده‌های قدیمی (اگه جدول قدیمی وجود داره)
    try:
        cursor.execute('''
            INSERT INTO Abschlagen (Vertragsnummer, ZeitraumVon, ZeitraumBis, Abschlagsbetrag, Status)
            SELECT Vertragsnummer, Abschlagsdatum, Abschlagsdatum, Abschlagsbetrag, Status
            FROM Abschlagen_old
        ''')
        cursor.execute("DROP TABLE Abschlagen_old")
    except sqlite3.OperationalError:
        print("داده قدیمی پیدا نشد، جدول جدید آماده است.")
    
    conn.commit()

print("جدول Abschlagen آپدیت شد!")