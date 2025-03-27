import sys
from PyQt5.QtWidgets import QApplication
from gui.vertragsregistrierung import VertragsRegistrierung  # درست هست
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_path = os.path.join(os.path.dirname(__file__), "contracts.db")
    window = VertragsRegistrierung(db_path)  # اینجا درسته چون VertragsRegistrierung خودش db رو می‌سازه
    window.show()
    sys.exit(app.exec_())