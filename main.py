from PyQt5.QtWidgets import QApplication
import sys
from gui.vertragsregistrierung import VertragsRegistrierung

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VertragsRegistrierung(db_path="C:/Projects/Stromverbrauch-Rechner/contracts.db")
    window.show()
    sys.exit(app.exec_())