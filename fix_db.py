import sqlite3

db_path = "C:/Projects/ElectricityTracker/contracts.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE Rechnungen SET Selected_rows = '[]' WHERE Selected_rows IS NULL")
    conn.commit()
print("ردیف‌های بدون Selected_rows آپدیت شدند.")