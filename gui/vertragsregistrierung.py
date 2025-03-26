from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox, QLabel, QMenu
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler
from gui.tarifdaten import Tarifdaten
from gui.ablesung import Ablesung
from gui.energiekosten import Energiekosten
from gui.rechnung import Rechnungen
from gui.zahlungen import Zahlungen
from gui.raten import Raten
from gui.charts import Charts
from gui.verbrauchsmengen import Verbrauchsmengen

class VertragsRegistrierung(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__()
        self.setWindowTitle("Vertragsregistrierung")
        self.resize(1200, 800)
        self.db = DatabaseHandler(db_path)
        self.parent = parent
        self.is_editing = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        input_frame = QGroupBox("Vertrag registrieren")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()
        vertragsnummer_label = QLabel("Vertragsnummer:")
        vertragsnummer_label.setObjectName("form_label")
        self.vertragsnummer = QLineEdit()
        self.vertragsnummer.setFixedWidth(350)

        stromanbieter_label = QLabel("Stromanbieter:")
        stromanbieter_label.setObjectName("form_label")
        self.stromanbieter = QLineEdit()
        self.stromanbieter.setFixedWidth(350)

        vertragstyp_label = QLabel("Vertragstyp:")
        vertragstyp_label.setObjectName("form_label")
        self.vertragstyp = QLineEdit()
        self.vertragstyp.setFixedWidth(350)

        startdatum_label = QLabel("Startdatum:")
        startdatum_label.setObjectName("form_label")
        self.startdatum = QLineEdit()
        self.startdatum.setPlaceholderText("DD.MM.YYYY")
        self.startdatum.setFixedWidth(350)

        zählernummer_label = QLabel("Zählernummer:")
        zählernummer_label.setObjectName("form_label")
        self.zählernummer = QLineEdit()
        self.zählernummer.setFixedWidth(350)

        form_layout.addRow(vertragsnummer_label, self.vertragsnummer)
        form_layout.addRow(stromanbieter_label, self.stromanbieter)
        form_layout.addRow(vertragstyp_label, self.vertragstyp)
        form_layout.addRow(startdatum_label, self.startdatum)
        form_layout.addRow(zählernummer_label, self.zählernummer)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_contract)
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setFixedSize(100, 25)

        beenden_btn = QPushButton("Beenden")
        beenden_btn.clicked.connect(self.close)
        beenden_btn.setFixedSize(100, 25)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(beenden_btn)
        btn_layout.addStretch()

        input_layout.addLayout(form_layout)
        input_layout.addLayout(btn_layout)
        input_layout.addStretch()
        input_frame.setLayout(input_layout)

        table_frame = QGroupBox("Verträge")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.contract_table = QTableWidget()
        self.contract_table.setColumnCount(5)
        self.contract_table.setHorizontalHeaderLabels(["Vertragsnummer", "Stromanbieter", "Vertragstyp", "Startdatum", "Zählernummer"])
        self.contract_table.setColumnWidth(0, 240)
        self.contract_table.setColumnWidth(1, 240)
        self.contract_table.setColumnWidth(2, 240)
        self.contract_table.setColumnWidth(3, 240)
        self.contract_table.setColumnWidth(4, 240)
        self.contract_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contract_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contract_table.customContextMenuRequested.connect(self.show_context_menu)

        self.contract_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.contract_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.contract_table)
        table_frame.setLayout(table_layout)

        main_layout.addWidget(input_frame)
        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_contracts()

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
            QLabel#form_label { 
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

    def save_contract(self):
        if not all([self.vertragsnummer.text(), self.stromanbieter.text(), self.vertragstyp.text(), 
                    self.startdatum.text(), self.zählernummer.text()]):
            QMessageBox.warning(self, "Warnung", "Bitte füllen Sie alle Felder aus!")
            return
        
        contract = {
            "Vertragsnummer": self.vertragsnummer.text(),
            "Stromanbieter": self.stromanbieter.text(),
            "Vertragstyp": self.vertragstyp.text(),
            "Startdatum": self.startdatum.text(),
            "Zählernummer": self.zählernummer.text()
        }
        self.db.add_contract(contract)
        self.load_contracts()
        self.clear_form()
        if self.is_editing:
            self.is_editing = False
            self.save_btn.setText("Speichern")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: white; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")

    def edit_contract(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            contract = self.db.get_all_contracts()[selected_row]
            self.vertragsnummer.setText(contract["Vertragsnummer"])
            self.stromanbieter.setText(contract["Stromanbieter"])
            self.vertragstyp.setText(contract["Vertragstyp"])
            self.startdatum.setText(contract["Startdatum"])
            self.zählernummer.setText(contract["Zählernummer"])
            self.db.delete_contract(contract["Vertragsnummer"])
            self.load_contracts()
            self.is_editing = True
            self.save_btn.setText("Aktualisieren")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: red; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Vertrag aus!")

    def load_contracts(self):
        contracts = self.db.get_all_contracts()
        self.contract_table.setRowCount(0)
        for contract in contracts:
            row = self.contract_table.rowCount()
            self.contract_table.insertRow(row)
            self.contract_table.setItem(row, 0, QTableWidgetItem(contract["Vertragsnummer"]))
            self.contract_table.setItem(row, 1, QTableWidgetItem(contract["Stromanbieter"]))
            self.contract_table.setItem(row, 2, QTableWidgetItem(contract["Vertragstyp"]))
            self.contract_table.setItem(row, 3, QTableWidgetItem(contract["Startdatum"]))
            self.contract_table.setItem(row, 4, QTableWidgetItem(contract["Zählernummer"]))

    def clear_form(self):
        self.vertragsnummer.clear()
        self.stromanbieter.clear()
        self.vertragstyp.clear()
        self.startdatum.clear()
        self.zählernummer.clear()

    def delete_contract(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.contract_table.item(selected_row, 0).text()
            self.db.delete_contract(vertragsnummer)
            self.load_contracts()
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Vertrag aus!")

    def get_selected_vertragsnummer(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            return self.contract_table.item(selected_row, 0).text()
        return None

    def open_tarifdaten(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.tarifdaten_window = Tarifdaten(self.db, self, vertragsnummer)
            self.tarifdaten_window.show()
            self.hide()

    def open_ablesung(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.ablesung_window = Ablesung(self.db, self, vertragsnummer)
            self.ablesung_window.show()
            self.hide()

    def open_energiekosten(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.energiekosten_window = Energiekosten(self.db, self, vertragsnummer)
            self.energiekosten_window.show()
            self.hide()

    def open_rechnung(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.rechnungen_window = Rechnungen(self.db, self, vertragsnummer)
            self.rechnungen_window.show()
            self.hide()

    def open_zahlungen(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.zahlungen_window = Zahlungen(self.db, self, vertragsnummer)
            self.zahlungen_window.show()
            self.hide()

    def open_raten(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.raten_window = Raten(self.db, self, vertragsnummer)
            self.raten_window.show()
            self.hide()

    def open_charts(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.charts_window = Charts(self.db, self, vertragsnummer)
            self.charts_window.show()
            self.hide()

    def open_verbrauchsmengen(self):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            vertragsnummer = self.get_selected_vertragsnummer()
            self.verbrauchsmengen_window = Verbrauchsmengen(self.db, self, vertragsnummer)
            self.verbrauchsmengen_window.show()
            self.hide()

    def show_context_menu(self, pos):
        selected_row = self.contract_table.currentRow()
        if selected_row >= 0:
            menu = QMenu(self)
            menu_action = menu.addAction("Menü")
            edit_action = menu.addAction("Bearbeiten")
            delete_action = menu.addAction("Löschen")

            submenu = QMenu("Verwaltung", self)
            submenu.addAction("Tarifdaten").triggered.connect(self.open_tarifdaten)
            submenu.addAction("Ablesung").triggered.connect(self.open_ablesung)
            submenu.addAction("Verbrauchsmengen").triggered.connect(self.open_verbrauchsmengen)
            submenu.addAction("Energiekosten").triggered.connect(self.open_energiekosten)
            submenu.addAction("Rechnungen").triggered.connect(self.open_rechnung)
            submenu.addAction("Zahlungen").triggered.connect(self.open_zahlungen)
            submenu.addAction("Raten").triggered.connect(self.open_raten)
            submenu.addAction("Charts").triggered.connect(self.open_charts)
            menu_action.setMenu(submenu)

            edit_action.triggered.connect(self.edit_contract)
            delete_action.triggered.connect(self.delete_contract)

            menu.exec_(self.contract_table.viewport().mapToGlobal(pos))

    def load_rechnungen_data(self):
        if hasattr(self, 'rechnungen_window'):
            self.rechnungen_window.load_data()