import sys
from PyQt5.QtWidgets import QApplication
from gui.vertragsregistrierung import VertragsRegistrierung
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_path = os.path.join(os.path.dirname(__file__), "contracts.db")
    window = VertragsRegistrierung(db_path)  # مستقیم VertragsRegistrierung باز می‌شه
    window.show()
    sys.exit(app.exec_())