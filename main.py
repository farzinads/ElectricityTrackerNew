import sys
from PyQt5.QtWidgets import QApplication
from gui.vertragsregistrierung import VertragsRegistrierung
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # مسیر دیتابیس رو نسبت به محل فایل main.py تنظیم می‌کنیم
    db_path = os.path.join(os.path.dirname(__file__), "contracts.db")
    window = VertragsRegistrierung(db_path=db_path)
    window.show()
    sys.exit(app.exec_())