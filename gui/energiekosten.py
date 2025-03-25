from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox
from PyQt5.QtCore import Qt
from datetime import datetime

class Energiekosten(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Energiekosten")
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
        table_frame = QGroupBox("Energiekosten")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.energiekosten_table = QTableWidget()
        self.energiekosten_table.setColumnCount(7)
        self.energiekosten_table.setHorizontalHeaderLabels([
            "", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag Brutto"
        ])
        self.energiekosten_table.setColumnWidth(0, 180)  # عرض ستون‌ها کمتر شد (از 240 به 180)
        self.energiekosten_table.setColumnWidth(1, 180)
        self.energiekosten_table.setColumnWidth(2, 180)
        self.energiekosten_table.setColumnWidth(3, 180)
        self.energiekosten_table.setColumnWidth(4, 180)
        self.energiekosten_table.setColumnWidth(5, 180)
        self.energiekosten_table.setColumnWidth(6, 180)
        self.energiekosten_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.energiekosten_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.energiekosten_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.energiekosten_table)
        table_frame.setLayout(table_layout)

        # دکمه بازگشت
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(100, 25)

        # چیدمان: جدول بالا و دکمه پایین
        main_layout.addWidget(table_frame)
        main_layout.addStretch()  # فاصله قبل از دکمه
        main_layout.addWidget(back_btn, alignment=Qt.AlignBottom | Qt.AlignLeft)  # دکمه پایین صفحه

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
                background-color: #F5F6F5; 
                color: #000000; 
                padding: 5px; 
            }
        """)

    def calculate_zeitraum(self, tariffs, key, value):
        # فیلتر کردن تعرفه‌ها برای مقدار مشخص (مثلاً Grundpreis = "50")
        relevant_tariffs = [t for t in tariffs if t[key] == value]
        if not relevant_tariffs:
            return None, None
        # مرتب‌سازی بر اساس تاریخ
        relevant_tariffs.sort(key=lambda x: datetime.strptime(x["Von"], "%d.%m.%Y"))
        # گرفتن اولین Von و آخرین Bis
        von_date = min(datetime.strptime(t["Von"], "%d.%m.%Y") for t in relevant_tariffs)
        bis_date = max(datetime.strptime(t["Bis"], "%d.%m.%Y") for t in relevant_tariffs)
        return von_date.strftime("%d.%m.%Y"), bis_date.strftime("%d.%m.%Y")

    def calculate_days(self, von, bis):
        von_date = datetime.strptime(von, "%d.%m.%Y")
        bis_date = datetime.strptime(bis, "%d.%m.%Y")
        return (bis_date - von_date).days + 1  # +1 چون روز آخر هم حساب می‌شه

    def load_data(self):
        # گرفتن داده‌ها از tarifdaten
        tariffs = self.db.get_all_tarifs()

        if not tariffs:
            self.energiekosten_table.setRowCount(1)
            self.energiekosten_table.setItem(0, 0, QTableWidgetItem("داده‌ای نیست"))
            return

        # گرفتن مقادیر منحصربه‌فرد
        unique_tarif_ids = sorted(set(tarif["Tarif-ID"] for tarif in tariffs))  # تعرفه‌های مختلف
        unique_grundpreis = sorted(set(tarif["Grundpreis"] for tarif in tariffs))  # مقادیر مختلف Grundpreis
        unique_zähler = sorted(set(tarif["Zähler"] for tarif in tariffs))  # مقادیر مختلف Zähler

        # تنظیم تعداد سطرها
        total_rows = (2 * len(unique_tarif_ids)) + len(unique_grundpreis) + len(unique_zähler) + 1
        self.energiekosten_table.setRowCount(total_rows)

        # پر کردن Arbeitspreis HT و NT
        row = 1  # از سطر دوم شروع می‌کنیم (سطر اول خالی)
        for tarif_id in unique_tarif_ids:
            tarif = next(t for t in tariffs if t["Tarif-ID"] == tarif_id)  # اولین تعرفه با این ID
            # Arbeitspreis HT
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem(f"Arbeitspreis HT ({tarif_id})"))
            self.energiekosten_table.setItem(row, 1, QTableWidgetItem(f"{tarif['Von']} - {tarif['Bis']}"))
            self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{tarif['Arbeitspreis HT']} (ct/kWh)"))
            row += 1
            # Arbeitspreis NT
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem(f"Arbeitspreis NT ({tarif_id})"))
            self.energiekosten_table.setItem(row, 1, QTableWidgetItem(f"{tarif['Von']} - {tarif['Bis']}"))
            self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{tarif['Arbeitspreis NT']} (ct/kWh)"))
            row += 1

        # پر کردن Grundpreis‌ها
        for grundpreis in unique_grundpreis:
            von, bis = self.calculate_zeitraum(tariffs, "Grundpreis", grundpreis)
            if von and bis:
                zeitraum = f"{von} - {bis}"
                days = self.calculate_days(von, bis)
                self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Grundpreis"))
                self.energiekosten_table.setItem(row, 1, QTableWidgetItem(zeitraum))
                self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{days} (days)"))
                self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{grundpreis} (€/jahr)"))
            row += 1

        # پر کردن Zähler‌ها
        for zähler in unique_zähler:
            von, bis = self.calculate_zeitraum(tariffs, "Zähler", zähler)
            if von and bis:
                zeitraum = f"{von} - {bis}"
                days = self.calculate_days(von, bis)
                self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Zähler"))
                self.energiekosten_table.setItem(row, 1, QTableWidgetItem(zeitraum))
                self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{days} (days)"))
                self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{zähler} (€/jahr)"))
            row += 1

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    from database.db_handler import DatabaseHandler
    app = QApplication(sys.argv)
    db = DatabaseHandler("electricity_tracker.db")
    window = Energiekosten(db)
    window.show()
    sys.exit(app.exec_())