import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    # بررسی ساختار جدول Abschlagen
    cursor.execute("PRAGMA table_info(Abschlagen)")
    columns = cursor.fetchall()
    print("ستون‌های جدول Abschlagen:")
    for column in columns:
        print(column)
    
    # بررسی محتوای جدول Abschlagen
    cursor.execute("SELECT * FROM Abschlagen")
    rows = cursor.fetchall()
    print("\nمحتوای جدول Abschlagen:")
    for row in rows:
        print(row)