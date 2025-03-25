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
        self.energiekosten_table.setColumnWidth(0, 240)
        self.energiekosten_table.setColumnWidth(1, 240)
        self.energiekosten_table.setColumnWidth(2, 240)
        self.energiekosten_table.setColumnWidth(3, 240)
        self.energiekosten_table.setColumnWidth(4, 240)
        self.energiekosten_table.setColumnWidth(5, 240)
        self.energiekosten_table.setColumnWidth(6, 240)
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

        main_layout.addWidget(table_frame)
        main_layout.addWidget(back_btn)
        main_layout.addStretch()

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
        total_rows = len(unique_tarif_ids) + len(unique_grundpreis) + len(unique_zähler) + 1  # +1 برای فاصله‌ها
        self.energiekosten_table.setRowCount(total_rows)

        # پر کردن Arbeitspreis‌ها
        row = 1  # از سطر دوم شروع می‌کنیم (سطر اول خالی)
        for tarif_id in unique_tarif_ids:
            tarif = next(t for t in tariffs if t["Tarif-ID"] == tarif_id)  # اولین تعرفه با این ID
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem(f"Arbeitspreis ({tarif_id})"))
            self.energiekosten_table.setItem(row, 1, QTableWidgetItem(f"{tarif['Von']} - {tarif['Bis']}"))
            # بقیه ستون‌ها بعداً پر می‌شه
            row += 1

        # پر کردن Grundpreis‌ها
        for grundpreis in unique_grundpreis:
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Grundpreis"))
            # بقیه ستون‌ها بعداً پر می‌شه
            row += 1

        # پر کردن Zähler‌ها
        for zähler in unique_zähler:
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Zähler"))
            # بقیه ستون‌ها بعداً پر می‌شه
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