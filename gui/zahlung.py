import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QMenu, QFileDialog, QMessageBox, QComboBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont  # اضافه شده برای بولد کردن
import os
import subprocess

class Zahlungen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Zahlungen")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.uploaded_files = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        input_frame = QGroupBox("Neue Zahlung hinzufügen")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        zahlungsdatum_label = QLabel("Zahlungsdatum:")
        zahlungsdatum_label.setObjectName("form_label")
        self.zahlungsdatum_input = QLineEdit()
        self.zahlungsdatum_input.setPlaceholderText("DD.MM.YYYY")
        self.zahlungsdatum_input.setFixedWidth(350)
        form_layout.addRow(zahlungsdatum_label, self.zahlungsdatum_input)

        zahlungstyp_label = QLabel("Zahlungstyp:")
        zahlungstyp_label.setObjectName("form_label")
        self.zahlungstyp_combo = QComboBox()
        self.zahlungstyp_combo.addItems(["Überweisung", "Abbuchung"])
        self.zahlungstyp_combo.setFixedWidth(350)
        form_layout.addRow(zahlungstyp_label, self.zahlungstyp_combo)

        zahlungsbetrag_label = QLabel("Zahlungsbetrag:")
        zahlungsbetrag_label.setObjectName("form_label")
        self.zahlungsbetrag_input = QLineEdit()
        self.zahlungsbetrag_input.setPlaceholderText("Betrag in €")
        self.zahlungsbetrag_input.setFixedWidth(350)
        form_layout.addRow(zahlungsbetrag_label, self.zahlungsbetrag_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_zahlung)
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

        table_frame = QGroupBox("Zahlungen")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.zahlungen_table = QTableWidget()
        self.zahlungen_table.setColumnCount(5)  # ستون جدید برای Zahlungssumme
        self.zahlungen_table.setHorizontalHeaderLabels([
            "Zahlungsdatum", "Zahlungstyp", "Zahlungsbetrag", "Upload Beleg", "Zahlungssumme"
        ])
        self.zahlungen_table.setColumnWidth(0, 200)
        self.zahlungen_table.setColumnWidth(1, 200)
        self.zahlungen_table.setColumnWidth(2, 200)
        self.zahlungen_table.setColumnWidth(3, 240)
        self.zahlungen_table.setColumnWidth(4, 200)  # عرض ستون Zahlungssumme
        self.zahlungen_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.zahlungen_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.zahlungen_table.customContextMenuRequested.connect(self.show_context_menu)
        self.zahlungen_table.doubleClicked.connect(self.handle_double_click)

        self.zahlungen_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.zahlungen_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.zahlungen_table)
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
            QComboBox { 
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
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Zahlungsdatum, Zahlungstyp, Zahlungsbetrag FROM Zahlungen WHERE Vertragsnummer = ?", (self.vertragsnummer,))
            zahlungen = cursor.fetchall()

        self.zahlungen_table.setRowCount(len(zahlungen) + 1)  # +1 برای ردیف جمع
        total_sum = 0
        for row, zahlung in enumerate(zahlungen):
            self.zahlungen_table.setItem(row, 0, QTableWidgetItem(zahlung[0]))
            self.zahlungen_table.setItem(row, 1, QTableWidgetItem(zahlung[1]))
            self.zahlungen_table.setItem(row, 2, QTableWidgetItem(f"{zahlung[2]} (€)"))
            upload_item = QTableWidgetItem(self.uploaded_files.get(f"{self.vertragsnummer}_{row}", "No file uploaded"))
            self.zahlungen_table.setItem(row, 3, upload_item)
            total_sum += float(zahlung[2])

        # ردیف آخر برای جمع
        sum_item = QTableWidgetItem(f"{total_sum:.2f} (€)")
        sum_font = QFont()  # ساخت فونت جدید
        sum_font.setBold(True)  # بولد کردن
        sum_item.setFont(sum_font)  # اعمال فونت به آیتم
        self.zahlungen_table.setItem(len(zahlungen), 4, sum_item)

        gesamt_item = QTableWidgetItem("Gesamt")
        gesamt_item.setFont(sum_font)  # بولد کردن "Gesamt"
        self.zahlungen_table.setItem(len(zahlungen), 0, gesamt_item)

    def save_zahlung(self):
        zahlungsdatum = self.zahlungsdatum_input.text()
        zahlungstyp = self.zahlungstyp_combo.currentText()
        zahlungsbetrag = self.zahlungsbetrag_input.text()

        if not zahlungsdatum or not zahlungsbetrag:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید!")
            return

        try:
            betrag = float(zahlungsbetrag)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Zahlungen (Vertragsnummer, Zahlungsdatum, Zahlungstyp, Zahlungsbetrag)
                    VALUES (?, ?, ?, ?)
                """, (self.vertragsnummer, zahlungsdatum, zahlungstyp, betrag))
                conn.commit()
            self.zahlungsdatum_input.clear()
            self.zahlungsbetrag_input.clear()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار پرداخت باید عدد باشد!")

    def show_context_menu(self, pos):
        index = self.zahlungen_table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        column = index.column()

        if row < 0 or row == self.zahlungen_table.rowCount() - 1:  # ردیف جمع قابل ویرایش نیست
            return

        menu = QMenu(self)

        if column == 3:
            current_file = self.zahlungen_table.item(row, 3).text()
            if current_file == "No file uploaded":
                upload_action = menu.addAction("Upload Beleg")
                action = menu.exec_(self.zahlungen_table.viewport().mapToGlobal(pos))
                if action == upload_action:
                    self.upload_beleg(row)
            else:
                edit_action = menu.addAction("Bearbeiten (Replace PDF)")
                delete_action = menu.addAction("Löschen (Remove PDF)")
                action = menu.exec_(self.zahlungen_table.viewport().mapToGlobal(pos))
                if action == edit_action:
                    self.upload_beleg(row)
                elif action == delete_action:
                    self.delete_uploaded_file(row)

    def handle_double_click(self, index):
        if index.column() == 3:
            row = index.row()
            if row == self.zahlungen_table.rowCount() - 1:  # ردیف جمع
                return
            file_key = f"{self.vertragsnummer}_{row}"
            file_path = self.uploaded_files.get(file_key)
            if file_path and os.path.exists(file_path):
                subprocess.Popen([file_path], shell=True)
            else:
                QMessageBox.warning(self, "خطا", "فایل PDF پیدا نشد یا قبلاً حذف شده است.")

    def upload_beleg(self, row):
        file_key = f"{self.vertragsnummer}_{row}"
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Beleg", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.uploaded_files[file_key] = file_path
            self.zahlungen_table.setItem(row, 3, QTableWidgetItem(file_path.split('/')[-1]))

    def delete_uploaded_file(self, row):
        file_key = f"{self.vertragsnummer}_{row}"
        if file_key in self.uploaded_files:
            del self.uploaded_files[file_key]
            self.zahlungen_table.setItem(row, 3, QTableWidgetItem("No file uploaded"))

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()