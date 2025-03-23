from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QLabel, QMenu
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler

class Tarifdaten(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Tarifdaten")
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
        input_frame = QGroupBox("Tarifdaten")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()
        
        self.von_datum = QLineEdit()
        self.von_datum.setPlaceholderText("DD.MM.YYYY")
        self.von_datum.setFixedWidth(350)
        self.bis_datum = QLineEdit()
        self.bis_datum.setPlaceholderText("DD.MM.YYYY")
        self.bis_datum.setFixedWidth(350)
        zeitraum_layout = QHBoxLayout()
        zeitraum_layout.addWidget(QLabel("von:"))
        zeitraum_layout.addWidget(self.von_datum)
        zeitraum_layout.addWidget(QLabel("bis:"))
        zeitraum_layout.addWidget(self.bis_datum)

        self.tarif_id = QLineEdit()
        self.tarif_id.setFixedWidth(350)

        self.arbeitspreis_ht = QLineEdit()
        self.arbeitspreis_ht.setFixedWidth(350)

        self.arbeitspreis_nt = QLineEdit()
        self.arbeitspreis_nt.setFixedWidth(350)

        self.grundpreis = QLineEdit()
        self.grundpreis.setFixedWidth(350)

        self.zähler = QLineEdit()
        self.zähler.setFixedWidth(350)

        form_layout.addRow("Zeitraum:", zeitraum_layout)
        form_layout.addRow("Tarif-ID:", self.tarif_id)
        form_layout.addRow("Arbeitspreis HT (ct/kWh):", self.arbeitspreis_ht)
        form_layout.addRow("Arbeitspreis NT (ct/kWh):", self.arbeitspreis_nt)
        form_layout.addRow("Grundpreis (jahr/€):", self.grundpreis)
        form_layout.addRow("Zähler (jahr/€):", self.zähler)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_tarif)
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

        # جدول تعرفه‌ها
        table_frame = QGroupBox("Tarife")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.tarif_table = QTableWidget()
        self.tarif_table.setColumnCount(7)
        self.tarif_table.setHorizontalHeaderLabels(["Von", "Bis", "Tarif-ID", "Arbeitspreis HT (ct/kWh)", "Arbeitspreis NT (ct/kWh)", "Grundpreis (jahr/€)", "Zähler (jahr/€)"])
        self.tarif_table.setColumnWidth(0, 150)
        self.tarif_table.setColumnWidth(1, 150)
        self.tarif_table.setColumnWidth(2, 150)
        self.tarif_table.setColumnWidth(3, 150)
        self.tarif_table.setColumnWidth(4, 150)
        self.tarif_table.setColumnWidth(5, 150)
        self.tarif_table.setColumnWidth(6, 150)
        self.tarif_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tarif_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tarif_table.customContextMenuRequested.connect(self.show_context_menu)

        self.tarif_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.tarif_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.tarif_table)
        table_frame.setLayout(table_layout)

        main_layout.addWidget(input_frame)
        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_tarifs()

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

    def save_tarif(self):
        if not all([self.von_datum.text(), self.bis_datum.text(), self.tarif_id.text(), 
                    self.arbeitspreis_ht.text(), self.arbeitspreis_nt.text(), self.grundpreis.text(), self.zähler.text()]):
            QMessageBox.warning(self, "Warnung", "Bitte füllen Sie alle Felder aus!")
            return
        
        tarif = {
            "Von": self.von_datum.text(),
            "Bis": self.bis_datum.text(),
            "Tarif-ID": self.tarif_id.text(),
            "Arbeitspreis HT": self.arbeitspreis_ht.text(),
            "Arbeitspreis NT": self.arbeitspreis_nt.text(),
            "Grundpreis": self.grundpreis.text(),
            "Zähler": self.zähler.text()
        }
        self.db.add_tarif(tarif)
        self.load_tarifs()
        self.clear_form()
        if self.is_editing:
            self.is_editing = False
            self.save_btn.setText("Speichern")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: white; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")

    def edit_tarif(self):
        selected_row = self.tarif_table.currentRow()
        if selected_row >= 0:
            tarif = self.db.get_all_tarifs()[selected_row]
            self.von_datum.setText(tarif["Von"])
            self.bis_datum.setText(tarif["Bis"])
            self.tarif_id.setText(tarif["Tarif-ID"])
            self.arbeitspreis_ht.setText(tarif["Arbeitspreis HT"])
            self.arbeitspreis_nt.setText(tarif["Arbeitspreis NT"])
            self.grundpreis.setText(tarif["Grundpreis"])
            self.zähler.setText(tarif["Zähler"])
            self.db.delete_tarif(tarif["Tarif-ID"])
            self.load_tarifs()
            self.is_editing = True
            self.save_btn.setText("Aktualisieren")
            self.save_btn.setStyleSheet("QPushButton#save_btn { background-color: #676b6d; color: red; font-weight: bold; padding: 5px; border-radius: 10px; border: 2px solid #676b6d; }")
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Tarif aus!")

    def delete_tarif(self):
        selected_row = self.tarif_table.currentRow()
        if selected_row >= 0:
            tarif_id = self.tarif_table.item(selected_row, 2).text()
            self.db.delete_tarif(tarif_id)
            self.load_tarifs()
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Tarif aus!")

    def load_tarifs(self):
        tarifs = self.db.get_all_tarifs()
        self.tarif_table.setRowCount(0)
        for tarif in tarifs:
            row = self.tarif_table.rowCount()
            self.tarif_table.insertRow(row)
            self.tarif_table.setItem(row, 0, QTableWidgetItem(tarif["Von"]))
            self.tarif_table.setItem(row, 1, QTableWidgetItem(tarif["Bis"]))
            self.tarif_table.setItem(row, 2, QTableWidgetItem(tarif["Tarif-ID"]))
            self.tarif_table.setItem(row, 3, QTableWidgetItem(tarif["Arbeitspreis HT"]))
            self.tarif_table.setItem(row, 4, QTableWidgetItem(tarif["Arbeitspreis NT"]))
            self.tarif_table.setItem(row, 5, QTableWidgetItem(tarif["Grundpreis"]))
            self.tarif_table.setItem(row, 6, QTableWidgetItem(tarif["Zähler"]))

    def clear_form(self):
        self.von_datum.clear()
        self.bis_datum.clear()
        self.tarif_id.clear()
        self.arbeitspreis_ht.clear()
        self.arbeitspreis_nt.clear()
        self.grundpreis.clear()
        self.zähler.clear()

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()

    def show_context_menu(self, pos):
        selected_row = self.tarif_table.currentRow()
        if selected_row >= 0:
            menu = QMenu(self)
            edit_action = menu.addAction("Bearbeiten")
            delete_action = menu.addAction("Löschen")

            edit_action.triggered.connect(self.edit_tarif)
            delete_action.triggered.connect(self.delete_tarif)

            menu.exec_(self.tarif_table.viewport().mapToGlobal(pos))