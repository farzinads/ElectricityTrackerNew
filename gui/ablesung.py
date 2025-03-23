from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QLabel, QComboBox, QMenu
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler

class Ablesung(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Ablesung")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.is_editing = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # نمایش Vertragsnummer
        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        # فرم ورودی
        input_frame = QGroupBox("Ablesung")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Ablesungsdatum
        self.ablesungsdatum = QLineEdit()
        self.ablesungsdatum.setPlaceholderText("DD.MM.YYYY")
        self.ablesungsdatum.setFixedWidth(350)

        # Ablesungstyp (منوی کشویی)
        self.ablesungstyp = QComboBox()
        self.ablesungstyp.addItems(["A1", "A2", "A3", "A4", "B1", "B2", "B3"])
        self.ablesungstyp.setFixedWidth(100)
        self.ablesungstyp.currentTextChanged.connect(self.update_description)

        # فیلد توضیحات
        self.description = QLineEdit()
        self.description.setReadOnly(True)
        self.description.setFixedWidth(230)
        self.update_description(self.ablesungstyp.currentText())  # مقدار اولیه

        ablesungstyp_layout = QHBoxLayout()
        ablesungstyp_layout.addWidget(self.ablesungstyp)
        ablesungstyp_layout.addWidget(self.description)

        # Zählerstand HT
        self.zählerstand_ht = QLineEdit()
        self.zählerstand_ht.setFixedWidth(350)

        # Zählerstand NT
        self.zählerstand_nt = QLineEdit()
        self.zählerstand_nt.setFixedWidth(350)

        form_layout.addRow("Ablesungsdatum:", self.ablesungsdatum)
        form_layout.addRow("Ablesungstyp:", ablesungstyp_layout)
        form_layout.addRow("Zählerstand HT (kWh):", self.zählerstand_ht)
        form_layout.addRow("Zählerstand NT (kWh):", self.zählerstand_nt)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_ablesung)
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setFixedSize(100, 25)

        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(100, 25)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()

        input_layout.addLayout(form_layout)
        input_layout.addLayout(btn_layout)
        input_layout.addStretch()
        input_frame.setLayout(input_layout)

        # جدول
        table_frame = QGroupBox("Ablesungen")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.ablesung_table = QTableWidget()
        self.ablesung_table.setColumnCount(4)
        self.ablesung_table.setHorizontalHeaderLabels(["Ablesungsdatum", "Ablesungstyp", "Zählerstand HT (kWh)", "Zählerstand NT (kWh)"])
        self.ablesung_table.setColumnWidth(0, 240)
        self.ablesung_table.setColumnWidth(1, 240)
        self.ablesung_table.setColumnWidth(2, 240)
        self.ablesung_table.setColumnWidth(3, 240)
        self.ablesung_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ablesung_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ablesung_table.customContextMenuRequested.connect(self.show_context_menu)

        self.ablesung_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.ablesung_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.ablesung_table)
        table_frame.setLayout(table_layout)

        main_layout.addWidget(input_frame)
        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_ablesungen()

        self.setStyleSheet("""
            QWidget { 
                font-size: 14px; 
                background-color: #434f5a; 
                color: #ffffff; 
            }
            QLineEdit { 
                padding: 5px; 
                background-color: #c2d7ea; 
                color: #000000; 
                border-radius: 10px; 
                border: 2px solid #5DADE2; 
            }
            QComboBox { 
                padding: 5px; 
                background-color: #c2d7ea; 
                color: #000000; 
                border-radius: 10px; 
                border: 2px solid #5DADE2; 
            }
            QLineEdit[readOnly="true"] { 
                background-color: #e0e0e0; 
                color: #000000; 
                border-radius: 10px; 
                border: 2px solid #5DADE2; 
            }
            QLabel { 
                background-color: #73BBF7; 
                color: black; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #5DADE2; 
                min-width: 100px; 
            }
            QGroupBox { 
                font-size: 16px; 
                font-weight: bold; 
                border: 2px solid #5DADE2; 
                border-radius: 10px; 
                margin-top: 10px; 
                padding: 10px; 
                background-color: #F5F6F5; 
                color: #000000; 
            }
            QGroupBox#table_frame { 
                border: 2px solid #000000; 
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
            QTableWidget::item:selected { 
                background-color: #D3D3D3; 
                color: red; 
            }
            QPushButton { 
                background-color: #676b6d; 
                color: white; 
                font-weight: bold; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #676b6d; 
            }
            QPushButton#save_btn { 
                background-color: #676b6d; 
                color: white; 
                font-weight: bold; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #676b6d;
            }
            QPushButton#save_btn.editing { 
                background-color: #676b6d; 
                color: red; 
                font-weight: bold; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #676b6d;
            }
        """)

    def update_description(self, typ):
        descriptions = {
            "A1": "Ablesung Messstellenbetrieber",
            "A2": "Ablesung Netzbetrieber",
            "A3": "Ablesung Lieferant",
            "A4": "Ablesung Kunde",
            "B1": "Berechnung Messstellenbetrieber",
            "B2": "Berechnung Netzbetrieber",
            "B3": "Berechnung Lieferant"
        }
        self.description.setText(descriptions.get(typ, ""))

    def save_ablesung(self):
        if not all([self.ablesungsdatum.text(), self.ablesungstyp.currentText(), 
                    self.zählerstand_ht.text(), self.zählerstand_nt.text()]):
            QMessageBox.warning(self, "Warnung", "Bitte füllen Sie alle Felder aus!")
            return
        
        ablesung = {
            "Ablesungsdatum": self.ablesungsdatum.text(),
            "Ablesungstyp": self.ablesungstyp.currentText(),
            "Zählerstand HT": self.zählerstand_ht.text(),
            "Zählerstand NT": self.zählerstand_nt.text()
        }
        self.db.add_ablesung(ablesung)
        self.load_ablesungen()
        self.clear_form()
        if self.is_editing:
            self.is_editing = False
            self.save_btn.setText("Speichern")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: white; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")

    def edit_ablesung(self):
        selected_row = self.ablesung_table.currentRow()
        if selected_row >= 0:
            ablesung = self.db.get_all_ablesungen()[selected_row]
            self.ablesungsdatum.setText(ablesung["Ablesungsdatum"])
            self.ablesungstyp.setCurrentText(ablesung["Ablesungstyp"])
            self.zählerstand_ht.setText(ablesung["Zählerstand HT"])
            self.zählerstand_nt.setText(ablesung["Zählerstand NT"])
            self.db.delete_ablesung(ablesung["Ablesungsdatum"], ablesung["Ablesungstyp"])
            self.load_ablesungen()
            self.is_editing = True
            self.save_btn.setText("Aktualisieren")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: red; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie eine Ablesung aus!")

    def delete_ablesung(self):
        selected_row = self.ablesung_table.currentRow()
        if selected_row >= 0:
            ablesung = self.db.get_all_ablesungen()[selected_row]
            self.db.delete_ablesung(ablesung["Ablesungsdatum"], ablesung["Ablesungstyp"])
            self.load_ablesungen()
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie eine Ablesung aus!")

    def load_ablesungen(self):
        ablesungen = self.db.get_all_ablesungen()
        self.ablesung_table.setRowCount(0)
        for ablesung in ablesungen:
            row = self.ablesung_table.rowCount()
            self.ablesung_table.insertRow(row)
            self.ablesung_table.setItem(row, 0, QTableWidgetItem(ablesung["Ablesungsdatum"]))
            self.ablesung_table.setItem(row, 1, QTableWidgetItem(ablesung["Ablesungstyp"]))
            self.ablesung_table.setItem(row, 2, QTableWidgetItem(ablesung["Zählerstand HT"]))
            self.ablesung_table.setItem(row, 3, QTableWidgetItem(ablesung["Zählerstand NT"]))

    def clear_form(self):
        self.ablesungsdatum.clear()
        self.ablesungstyp.setCurrentIndex(0)
        self.zählerstand_ht.clear()
        self.zählerstand_nt.clear()

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()

    def show_context_menu(self, pos):
        selected_row = self.ablesung_table.currentRow()
        if selected_row >= 0:
            menu = QMenu(self)
            edit_action = menu.addAction("Bearbeiten")
            delete_action = menu.addAction("Löschen")

            edit_action.triggered.connect(self.edit_ablesung)
            delete_action.triggered.connect(self.delete_ablesung)

            menu.exec_(self.ablesung_table.viewport().mapToGlobal(pos))