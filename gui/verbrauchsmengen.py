from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler
from datetime import datetime, timedelta

class Verbrauchsmengen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Verbrauchsmengen")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # نمایش Vertragsnummer
        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        # جدول
        table_frame = QGroupBox("Verbrauchsmengen")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.verbrauch_table = QTableWidget()
        self.verbrauch_table.setColumnCount(6)
        self.verbrauch_table.setHorizontalHeaderLabels([
            "Zeitraum", "Zählerstand HT", "Zählerstand NT", 
            "Verbrauch HT (kWh)", "Verbrauch NT (kWh)", "Verbrauch Total (kWh)"
        ])
        self.verbrauch_table.setColumnWidth(0, 240)
        self.verbrauch_table.setColumnWidth(1, 240)
        self.verbrauch_table.setColumnWidth(2, 240)
        self.verbrauch_table.setColumnWidth(3, 240)
        self.verbrauch_table.setColumnWidth(4, 240)
        self.verbrauch_table.setColumnWidth(5, 240)
        self.verbrauch_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.verbrauch_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.verbrauch_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.verbrauch_table)
        table_frame.setLayout(table_layout)

        # دکمه بازگشت
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(100, 25)

        main_layout.addWidget(table_frame)
        main_layout.addWidget(back_btn)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.load_verbrauchsmengen()

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
                background-color: #F5F6F5; 
                color: #000000; 
                padding: 5px; 
            }
        """)

    def load_verbrauchsmengen(self):
        # گرفتن داده‌ها از Ablesung
        ablesungen = self.db.get_all_ablesungen()
        if len(ablesungen) < 2:  # حداقل ۲ قرائت برای محاسبه نیازه
            self.verbrauch_table.setRowCount(0)
            return

        # مرتب‌سازی بر اساس تاریخ
        ablesungen.sort(key=lambda x: datetime.strptime(x["Ablesungsdatum"], "%d.%m.%Y"))

        # تنظیم تعداد سطرها (بازه‌ها + ۱ برای Summe)
        self.verbrauch_table.setRowCount(len(ablesungen) - 1 + 1)

        total_verbrauch = 0.0  # برای جمع کل Verbrauch Total

        for i in range(len(ablesungen) - 1):
            # تاریخ شروع و پایان بازه
            start_date = ablesungen[i]["Ablesungsdatum"]
            end_date = ablesungen[i + 1]["Ablesungsdatum"]

            # تبدیل تاریخ‌ها به datetime برای محاسبه
            start_dt = datetime.strptime(start_date, "%d.%m.%Y")
            end_dt = datetime.strptime(end_date, "%d.%m.%Y")

            # برای سطر اول، شروع از تاریخ اولین قرائت، برای بقیه از فردای تاریخ پایان قبلی
            if i == 0:
                zeitraum_start = start_dt
            else:
                zeitraum_start = datetime.strptime(ablesungen[i]["Ablesungsdatum"], "%d.%m.%Y") + timedelta(days=1)

            zeitraum = f"{zeitraum_start.strftime('%d.%m.%Y')} - {end_date}"

            # Zählerstand HT و NT با Ablesungstyp به صورت توان‌نما
            start_ht = float(ablesungen[i]["Zählerstand HT"])
            end_ht = float(ablesungen[i + 1]["Zählerstand HT"])
            start_nt = float(ablesungen[i]["Zählerstand NT"])
            end_nt = float(ablesungen[i + 1]["Zählerstand NT"])
            start_typ = ablesungen[i]["Ablesungstyp"]
            end_typ = ablesungen[i + 1]["Ablesungstyp"]

            zählerstand_ht_text = f"{int(start_ht)}<sup><font size='3'>{start_typ}</font></sup> —— {int(end_ht)}<sup><font size='3'>{end_typ}</font></sup>"
            zählerstand_nt_text = f"{int(start_nt)}<sup><font size='3'>{start_typ}</font></sup> —— {int(end_nt)}<sup><font size='3'>{end_typ}</font></sup>"

            # Verbrauch HT و NT
            verbrauch_ht = end_ht - start_ht
            verbrauch_nt = end_nt - start_nt

            # Verbrauch Total
            verbrauch_total = verbrauch_ht + verbrauch_nt
            total_verbrauch += verbrauch_total

            # پر کردن جدول
            self.verbrauch_table.setItem(i, 0, QTableWidgetItem(zeitraum))

            ht_label = QLabel()
            ht_label.setText(zählerstand_ht_text)
            ht_label.setAlignment(Qt.AlignCenter)
            self.verbrauch_table.setCellWidget(i, 1, ht_label)

            nt_label = QLabel()
            nt_label.setText(zählerstand_nt_text)
            nt_label.setAlignment(Qt.AlignCenter)
            self.verbrauch_table.setCellWidget(i, 2, nt_label)

            self.verbrauch_table.setItem(i, 3, QTableWidgetItem(f"{verbrauch_ht:.2f}"))
            self.verbrauch_table.setItem(i, 4, QTableWidgetItem(f"{verbrauch_nt:.2f}"))
            self.verbrauch_table.setItem(i, 5, QTableWidgetItem(f"{verbrauch_total:.2f}"))

            self.verbrauch_table.setRowHeight(i, 45)

        # اضافه کردن ردیف Summe
        summe_row = len(ablesungen) - 1
        self.verbrauch_table.setItem(summe_row, 0, QTableWidgetItem("Summe"))
        self.verbrauch_table.setItem(summe_row, 5, QTableWidgetItem(f"{total_verbrauch:.2f}"))
        self.verbrauch_table.setRowHeight(summe_row, 45)

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()