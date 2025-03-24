from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

class Energiekosten(QWidget):
    def __init__(self, db, parent=None):
        super().__init__()
        self.setWindowTitle("Energiekosten")
        self.resize(1200, 800)
        self.db = db  # دیتابیس برای محاسبات بعدی
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # جدول
        table_frame = QGroupBox("Energiekosten")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.energiekosten_table = QTableWidget()
        self.energiekosten_table.setColumnCount(7)
        self.energiekosten_table.setHorizontalHeaderLabels(["", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag Brutto"])
        self.energiekosten_table.setColumnWidth(0, 240)  # ستون اول بدون هدر
        self.energiekosten_table.setColumnWidth(1, 240)
        self.energiekosten_table.setColumnWidth(2, 240)
        self.energiekosten_table.setColumnWidth(3, 240)
        self.energiekosten_table.setColumnWidth(4, 240)
        self.energiekosten_table.setColumnWidth(5, 240)
        self.energiekosten_table.setColumnWidth(6, 240)
        self.energiekosten_table.setEditTriggers(QTableWidget.NoEditTriggers)  # غیرقابل ویرایش

        # استایل هدرها (مثل ablesung.py)
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

        main_layout.addWidget(table_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)
        
        # استایل کلی (مثل ablesung.py)
        self.setStyleSheet("""
            QWidget { 
                font-size: 14px; 
                background-color: #434f5a; 
                color: #ffffff; 
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
        """)

        # داده‌های اولیه (برای تست)
        self.load_sample_data()

    def load_sample_data(self):
        # نمونه داده برای تست جدول
        self.energiekosten_table.setRowCount(2)  # ۲ سطر برای شروع
        self.energiekosten_table.setItem(1, 0, QTableWidgetItem("Stromkosten"))  # تایتل توی ستون اول
        self.energiekosten_table.setItem(1, 1, QTableWidgetItem("01.01.2025 - 31.01.2025"))  # Zeitraum
        self.energiekosten_table.setItem(1, 2, QTableWidgetItem("100 kWh"))  # Menge
        self.energiekosten_table.setItem(1, 3, QTableWidgetItem("0.30 €/kWh"))  # Preis netto
        self.energiekosten_table.setItem(1, 4, QTableWidgetItem("30.00 €"))  # Betrag netto
        self.energiekosten_table.setItem(1, 5, QTableWidgetItem("19%"))  # MwSt.
        self.energiekosten_table.setItem(1, 6, QTableWidgetItem("35.70 €"))  # Betrag Brutto

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    from database.db_handler import DatabaseHandler  # فرض بر اینکه دیتابیس آماده‌ست
    app = QApplication(sys.argv)
    db = DatabaseHandler()  # دیتابیس رو وصل می‌کنیم
    window = Energiekosten(db)
    window.show()
    sys.exit(app.exec_())