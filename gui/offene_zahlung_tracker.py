from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QLabel
from PyQt5.QtCore import Qt
import sqlite3

class OffeneZahlungTracker(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Offene Zahlung Tracker")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # برچسب Vertragsnummer بالای صفحه
        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        # فرم ورودی
        input_frame = QGroupBox("Neue offene Zahlung hinzufügen")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        rechnungsnummer_label = QLabel("Rechnungsnummer:")
        rechnungsnummer_label.setObjectName("form_label")
        self.rechnungsnummer_input = QLineEdit()
        self.rechnungsnummer_input.setPlaceholderText("Rechnungsnummer eingeben")
        self.rechnungsnummer_input.setFixedWidth(350)
        form_layout.addRow(rechnungsnummer_label, self.rechnungsnummer_input)

        rechnungsdatum_label = QLabel("Rechnungsdatum:")
        rechnungsdatum_label.setObjectName("form_label")
        self.rechnungsdatum_input = QLineEdit()
        self.rechnungsdatum_input.setPlaceholderText("DD.MM.YYYY")
        self.rechnungsdatum_input.setFixedWidth(350)
        form_layout.addRow(rechnungsdatum_label, self.rechnungsdatum_input)

        betrag_label = QLabel("Betrag:")
        betrag_label.setObjectName("form_label")
        self.betrag_input = QLineEdit()
        self.betrag_input.setPlaceholderText("Betrag in €")
        self.betrag_input.setFixedWidth(350)
        form_layout.addRow(betrag_label, self.betrag_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_offene_zahlung)
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
        table_frame = QGroupBox("Offene Zahlungen")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.tracker_table = QTableWidget()
        self.tracker_table.setColumnCount(4)
        self.tracker_table.setHorizontalHeaderLabels(["Rechnungsnummer", "Rechnungsdatum", "Betrag", "Zahlungsstatus"])
        self.tracker_table.setColumnWidth(0, 250)
        self.tracker_table.setColumnWidth(1, 250)
        self.tracker_table.setColumnWidth(2, 250)
        self.tracker_table.setColumnWidth(3, 250)
        self.tracker_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.tracker_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.tracker_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.tracker_table)
        table_frame.setLayout(table_layout)

        main_layout.addWidget(input_frame)
        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_data()

        # استایل مشابه Zahlungen
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
        """)

    def load_data(self):
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Rechnungsnummer, Rechnungsdatum, Betrag, Zahlungsstatus FROM OffeneZahlungTracker WHERE Vertragsnummer = ?", (self.vertragsnummer,))
                tracker_data = cursor.fetchall()

            self.tracker_table.setRowCount(len(tracker_data))
            for row, data in enumerate(tracker_data):
                self.tracker_table.setItem(row, 0, QTableWidgetItem(data[0]))
                self.tracker_table.setItem(row, 1, QTableWidgetItem(data[1]))
                self.tracker_table.setItem(row, 2, QTableWidgetItem(f"{data[2]:.2f} (€)"))
                self.tracker_table.setItem(row, 3, QTableWidgetItem(data[3] if data[3] else "Offen"))
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")
            self.tracker_table.setRowCount(0)

    def save_offene_zahlung(self):
        rechnungsnummer = self.rechnungsnummer_input.text()
        rechnungsdatum = self.rechnungsdatum_input.text()
        betrag = self.betrag_input.text()

        if not rechnungsnummer or not rechnungsdatum or not betrag:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید!")
            return

        try:
            betrag_float = float(betrag)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO OffeneZahlungTracker (Vertragsnummer, Rechnungsnummer, Rechnungsdatum, Betrag, Zahlungsstatus)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.vertragsnummer, rechnungsnummer, rechnungsdatum, betrag_float, "Offen"))
                conn.commit()
            self.rechnungsnummer_input.clear()
            self.rechnungsdatum_input.clear()
            self.betrag_input.clear()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار باید عدد باشد!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()