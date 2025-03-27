from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QLabel
from PyQt5.QtCore import Qt
import sqlite3

class Analys(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Analysen")
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
        input_frame = QGroupBox("Neue Analyse hinzufügen")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        analysedatum_label = QLabel("Analyse Datum:")
        analysedatum_label.setObjectName("form_label")
        self.analysedatum_input = QLineEdit()
        self.analysedatum_input.setPlaceholderText("DD.MM.YYYY")
        self.analysedatum_input.setFixedWidth(350)
        form_layout.addRow(analysedatum_label, self.analysedatum_input)

        verbrauch_label = QLabel("Verbrauch:")
        verbrauch_label.setObjectName("form_label")
        self.verbrauch_input = QLineEdit()
        self.verbrauch_input.setPlaceholderText("Verbrauch in kWh")
        self.verbrauch_input.setFixedWidth(350)
        form_layout.addRow(verbrauch_label, self.verbrauch_input)

        kosten_label = QLabel("Kosten:")
        kosten_label.setObjectName("form_label")
        self.kosten_input = QLineEdit()
        self.kosten_input.setPlaceholderText("Kosten in €")
        self.kosten_input.setFixedWidth(350)
        form_layout.addRow(kosten_label, self.kosten_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_analyse)
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
        table_frame = QGroupBox("Analysen")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.analys_table = QTableWidget()
        self.analys_table.setColumnCount(3)
        self.analys_table.setHorizontalHeaderLabels(["Analyse Datum", "Verbrauch", "Kosten"])
        self.analys_table.setColumnWidth(0, 300)
        self.analys_table.setColumnWidth(1, 300)
        self.analys_table.setColumnWidth(2, 300)
        self.analys_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.analys_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.analys_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.analys_table)
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
                cursor.execute("SELECT AnalyseDatum, Verbrauch, Kosten FROM Analys WHERE Vertragsnummer = ?", (self.vertragsnummer,))
                analysen = cursor.fetchall()

            self.analys_table.setRowCount(len(analysen))
            for row, analyse in enumerate(analysen):
                self.analys_table.setItem(row, 0, QTableWidgetItem(analyse[0]))
                self.analys_table.setItem(row, 1, QTableWidgetItem(f"{analyse[1]:.2f} kWh"))
                self.analys_table.setItem(row, 2, QTableWidgetItem(f"{analyse[2]:.2f} (€)"))
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")
            self.analys_table.setRowCount(0)

    def save_analyse(self):
        analysedatum = self.analysedatum_input.text()
        verbrauch = self.verbrauch_input.text()
        kosten = self.kosten_input.text()

        if not analysedatum or not verbrauch or not kosten:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید!")
            return

        try:
            verbrauch_float = float(verbrauch)
            kosten_float = float(kosten)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Analys (Vertragsnummer, AnalyseDatum, Verbrauch, Kosten)
                    VALUES (?, ?, ?, ?)
                """, (self.vertragsnummer, analysedatum, verbrauch_float, kosten_float))
                conn.commit()
            self.analysedatum_input.clear()
            self.verbrauch_input.clear()
            self.kosten_input.clear()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار مصرف و هزینه باید عدد باشد!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "خطا", f"خطای دیتابیس: {str(e)}")

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()