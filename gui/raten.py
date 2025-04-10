import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QLabel, QMessageBox
from PyQt5.QtCore import Qt

class Raten(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Raten")
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

        input_frame = QGroupBox("Neue Rate hinzufügen")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        ratendatum_label = QLabel("Ratendatum:")
        ratendatum_label.setObjectName("form_label")
        self.ratendatum_input = QLineEdit()
        self.ratendatum_input.setPlaceholderText("DD.MM.YYYY")
        self.ratendatum_input.setFixedWidth(350)
        form_layout.addRow(ratendatum_label, self.ratendatum_input)

        ratenbetrag_label = QLabel("Ratenbetrag:")
        ratenbetrag_label.setObjectName("form_label")
        self.ratenbetrag_input = QLineEdit()
        self.ratenbetrag_input.setPlaceholderText("Betrag in €")
        self.ratenbetrag_input.setFixedWidth(350)
        form_layout.addRow(ratenbetrag_label, self.ratenbetrag_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_rate)
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

        table_frame = QGroupBox("Raten")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.raten_table = QTableWidget()
        self.raten_table.setColumnCount(3)
        self.raten_table.setHorizontalHeaderLabels(["Ratendatum", "Ratenbetrag", "Status"])
        self.raten_table.setColumnWidth(0, 300)
        self.raten_table.setColumnWidth(1, 300)
        self.raten_table.setColumnWidth(2, 300)
        self.raten_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.raten_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.raten_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.raten_table)
        table_frame.setLayout(table_layout)

        main_layout.addWidget(input_frame)
        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_data()

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
                cursor.execute("SELECT Ratendatum, Ratenbetrag, Status FROM Raten WHERE Vertragsnummer = ?", (self.vertragsnummer,))
                raten = cursor.fetchall()

            self.raten_table.setRowCount(len(raten))
            for row, rate in enumerate(raten):
                self.raten_table.setItem(row, 0, QTableWidgetItem(rate[0]))
                self.raten_table.setItem(row, 1, QTableWidgetItem(f"{rate[1]} (€)"))
                self.raten_table.setItem(row, 2, QTableWidgetItem(rate[2] if rate[2] else "Offen"))
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")
            self.raten_table.setRowCount(0)

    def save_rate(self):
        ratendatum = self.ratendatum_input.text()
        ratenbetrag = self.ratenbetrag_input.text()

        if not ratendatum or not ratenbetrag:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید!")
            return

        try:
            betrag = float(ratenbetrag)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Raten (Vertragsnummer, Ratendatum, Ratenbetrag, Status)
                    VALUES (?, ?, ?, ?)
                """, (self.vertragsnummer, ratendatum, betrag, "Offen"))
                conn.commit()
            self.ratendatum_input.clear()
            self.ratenbetrag_input.clear()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار رات باید عدد باشد!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()