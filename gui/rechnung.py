from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox
from PyQt5.QtCore import Qt

class Rechnungen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Rechnungen")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        table_frame = QGroupBox("Rechnungen")
        table_layout = QVBoxLayout()

        self.rechnungen_table = QTableWidget()
        self.rechnungen_table.setColumnCount(7)
        self.rechnungen_table.setHorizontalHeaderLabels([
            "Vertragsnummer", "Rechnungsdatum", "Rechnungsnummer", "Zeitraum", "Menge", "Preis netto", "Betrag netto"
        ])
        self.rechnungen_table.setColumnWidth(0, 150)
        self.rechnungen_table.setColumnWidth(1, 120)
        self.rechnungen_table.setColumnWidth(2, 120)
        self.rechnungen_table.setColumnWidth(3, 180)
        self.rechnungen_table.setColumnWidth(4, 135)
        self.rechnungen_table.setColumnWidth(5, 135)
        self.rechnungen_table.setColumnWidth(6, 135)
        self.rechnungen_table.setEditTriggers(QTableWidget.NoEditTriggers)

        table_layout.addWidget(self.rechnungen_table)
        table_frame.setLayout(table_layout)

        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(100, 25)

        main_layout.addWidget(table_frame)
        main_layout.addWidget(back_btn, alignment=Qt.AlignBottom | Qt.AlignLeft)
        main_layout.setStretch(1, 10)

        self.setLayout(main_layout)
        self.load_data()

        self.setStyleSheet("""
            QWidget { 
                font-size: 14px; 
                background-color: #434f5a; 
                color: #ffffff; 
            }
            QGroupBox { 
                font-size: 16px; 
                font-weight: bold; 
                border: 2px solid #000000; 
                border-radius: 10px; 
                margin-top: 10px; 
                padding: 10px; 
                background-color: #F5F6F5; 
                color: #000000; 
            }
            QTableWidget { 
                border: 1px solid #000000; 
                background-color: #F5F6F5; 
                color: #000000; 
                gridline-color: #000000; 
            }
            QTableWidget::item { 
                padding: 5px; 
                border: none; 
            }
            QPushButton { 
                background-color: #676b6d; 
                color: white; 
                font-weight: bold; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #676b6d; 
            }
            QLabel { 
                background-color: #434f5a; 
                color: #ffffff; 
                padding: 5px; 
            }
        """)

    def load_data(self):
        rechnungen = self.db.get_all_rechnungen()
        self.rechnungen_table.setRowCount(len(rechnungen))
        for row, rechnung in enumerate(rechnungen):
            self.rechnungen_table.setItem(row, 0, QTableWidgetItem(rechnung["Vertragsnummer"]))
            self.rechnungen_table.setItem(row, 1, QTableWidgetItem(rechnung["Rechnungsdatum"]))
            self.rechnungen_table.setItem(row, 2, QTableWidgetItem(rechnung["Rechnungsnummer"]))
            self.rechnungen_table.setItem(row, 3, QTableWidgetItem(rechnung["Zeitraum"]))
            self.rechnungen_table.setItem(row, 4, QTableWidgetItem(rechnung["Menge"]))
            self.rechnungen_table.setItem(row, 5, QTableWidgetItem(rechnung["Preis_netto"]))
            self.rechnungen_table.setItem(row, 6, QTableWidgetItem(rechnung["Betrag_netto"]))

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()