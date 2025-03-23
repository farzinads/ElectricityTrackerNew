from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from gui.vertragsregistrierung import VertragsRegistrierung
from gui.vertragsverwaltung import VertragsVerwaltung
from gui.ablesung import Ablesung
from gui.energiekosten import Energiekosten
from gui.rechnung import Rechnung

class MainMenu(QWidget):
    def __init__(self, db, parent=None):
        super().__init__()
        self.setWindowTitle("Hauptmenü - Stromverbrauch-Rechner")
        self.resize(400, 300)
        self.db = db
        self.parent = parent  # parent رو نگه می‌دارم برای برگشت
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        vertragsregistrierung_btn = QPushButton("Vertragsregistrierung")
        vertragsregistrierung_btn.clicked.connect(self.open_vertragsregistrierung)

        vertragsverwaltung_btn = QPushButton("Vertragsverwaltung")
        vertragsverwaltung_btn.clicked.connect(self.open_vertragsverwaltung)

        ablesung_btn = QPushButton("Ablesung")
        ablesung_btn.clicked.connect(self.open_ablesung)

        energiekosten_btn = QPushButton("Energiekosten")
        energiekosten_btn.clicked.connect(self.open_energiekosten)

        rechnung_btn = QPushButton("Rechnung")
        rechnung_btn.clicked.connect(self.open_rechnung)

        zurück_btn = QPushButton("Zurück")
        zurück_btn.clicked.connect(self.back_to_parent)

        beenden_btn = QPushButton("Beenden")
        beenden_btn.clicked.connect(self.close)

        layout.addWidget(vertragsregistrierung_btn)
        layout.addWidget(vertragsverwaltung_btn)
        layout.addWidget(ablesung_btn)
        layout.addWidget(energiekosten_btn)
        layout.addWidget(rechnung_btn)
        layout.addWidget(zurück_btn)
        layout.addWidget(beenden_btn)
        layout.addStretch()

        self.setLayout(layout)

        self.setStyleSheet("""
            QPushButton {
                background-color: #676b6d;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #676b6d;
            }
        """)

    def open_vertragsregistrierung(self):
        self.vertragsregistrierung = VertragsRegistrierung(self.db.db_path)
        self.vertragsregistrierung.show()
        self.hide()

    def open_vertragsverwaltung(self):
        self.vertragsverwaltung = VertragsVerwaltung(self.db, None, self)
        self.vertragsverwaltung.show()
        self.hide()

    def open_ablesung(self):
        self.ablesung = Ablesung(self.db, self)
        self.ablesung.show()
        self.hide()

    def open_energiekosten(self):
        self.energiekosten = Energiekosten(self.db, self)
        self.energiekosten.show()
        self.hide()

    def open_rechnung(self):
        self.rechnung = Rechnung(self.db, self)
        self.rechnung.show()
        self.hide()

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()