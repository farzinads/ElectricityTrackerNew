from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

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

        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        table_frame = QGroupBox("Energiekosten")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.energiekosten_table = QTableWidget()
        self.energiekosten_table.setColumnCount(7)
        self.energiekosten_table.setHorizontalHeaderLabels([
            "", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag Brutto"
        ])
        self.energiekosten_table.setColumnWidth(0, 180)
        self.energiekosten_table.setColumnWidth(1, 180)
        self.energiekosten_table.setColumnWidth(2, 135)
        self.energiekosten_table.setColumnWidth(3, 135)
        self.energiekosten_table.setColumnWidth(4, 135)
        self.energiekosten_table.setColumnWidth(5, 135)
        self.energiekosten_table.setColumnWidth(6, 135)
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

        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(100, 25)

        main_layout.addWidget(table_frame)
        main_layout.addWidget(back_btn, alignment=Qt.AlignBottom | Qt.AlignLeft)
        main_layout.setStretch(1, 10)

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
        relevant_tariffs = [t for t in tariffs if t[key] == value]
        if not relevant_tariffs:
            return None, None
        relevant_tariffs.sort(key=lambda x: datetime.strptime(x["Von"], "%d.%m.%Y"))
        von_date = min(datetime.strptime(t["Von"], "%d.%m.%Y") for t in relevant_tariffs)
        bis_date = max(datetime.strptime(t["Bis"], "%d.%m.%Y") for t in relevant_tariffs)
        return von_date.strftime("%d.%m.%Y"), bis_date.strftime("%d.%m.%Y")

    def calculate_days(self, von, bis):
        von_date = datetime.strptime(von, "%d.%m.%Y")
        bis_date = datetime.strptime(bis, "%d.%m.%Y")
        return (bis_date - von_date).days + 1

    def calculate_verbrauch(self, von, bis, ht=True):
        ablesungen = self.db.get_all_ablesungen()
        if len(ablesungen) < 2:
            return 0.0
        ablesungen.sort(key=lambda x: datetime.strptime(x["Ablesungsdatum"], "%d.%m.%Y"))

        von_dt = datetime.strptime(von, "%d.%m.%Y")
        bis_dt = datetime.strptime(bis, "%d.%m.%Y")
        total_verbrauch = 0.0

        for i in range(len(ablesungen) - 1):
            start_date = datetime.strptime(ablesungen[i]["Ablesungsdatum"], "%d.%m.%Y")
            period_start = start_date + timedelta(days=1)
            end_date = datetime.strptime(ablesungen[i + 1]["Ablesungsdatum"], "%d.%m.%Y")

            if period_start >= von_dt and end_date <= bis_dt:
                start_ht = float(ablesungen[i]["Zählerstand HT"])
                end_ht = float(ablesungen[i + 1]["Zählerstand HT"])
                start_nt = float(ablesungen[i]["Zählerstand NT"])
                end_nt = float(ablesungen[i + 1]["Zählerstand NT"])
                verbrauch = (end_ht - start_ht) if ht else (end_nt - start_nt)
                total_verbrauch += max(verbrauch, 0)
            elif (end_date >= von_dt and period_start <= bis_dt):
                overlap_start = max(period_start, von_dt)
                overlap_end = min(end_date, bis_dt)
                if overlap_start <= overlap_end:
                    total_days = (end_date - period_start).days + 1
                    overlap_days = (overlap_end - overlap_start).days + 1
                    fraction = overlap_days / total_days

                    start_ht = float(ablesungen[i]["Zählerstand HT"])
                    end_ht = float(ablesungen[i + 1]["Zählerstand HT"])
                    start_nt = float(ablesungen[i]["Zählerstand NT"])
                    end_nt = float(ablesungen[i + 1]["Zählerstand NT"])
                    verbrauch = (end_ht - start_ht) if ht else (end_nt - start_nt)
                    total_verbrauch += max(verbrauch, 0) * fraction

        return total_verbrauch

    def load_data(self):
        tariffs = self.db.get_all_tarifs()

        if not tariffs:
            self.energiekosten_table.setRowCount(1)
            self.energiekosten_table.setItem(0, 0, QTableWidgetItem("داده‌ای نیست"))
            return

        unique_tarif_ids = sorted(set(tarif["Tarif-ID"] for tarif in tariffs))
        unique_grundpreis = sorted(set(tarif["Grundpreis"] for tarif in tariffs))
        unique_zähler = sorted(set(tarif["Zähler"] for tarif in tariffs))

        total_rows = (2 * len(unique_tarif_ids)) + len(unique_grundpreis) + len(unique_zähler) + 1
        self.energiekosten_table.setRowCount(total_rows)

        row = 0
        betrag_netto_sum = 0.0

        for tarif_id in unique_tarif_ids:
            tarif = next(t for t in tariffs if t["Tarif-ID"] == tarif_id)
            von, bis = tarif["Von"], tarif["Bis"]
            # Arbeitspreis HT
            verbrauch_ht = self.calculate_verbrauch(von, bis, ht=True)
            preis_ht = float(tarif["Arbeitspreis HT"])
            betrag_netto_ht = verbrauch_ht * preis_ht / 100
            betrag_netto_sum += betrag_netto_ht
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem(f"Arbeitspreis HT ({tarif_id})"))
            self.energiekosten_table.setItem(row, 1, QTableWidgetItem(f"{von} - {bis}"))
            self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{verbrauch_ht:.2f} (kWh)"))
            self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{tarif['Arbeitspreis HT']} (ct/kWh)"))
            self.energiekosten_table.setItem(row, 4, QTableWidgetItem(f"{betrag_netto_ht:.2f} (€)"))
            row += 1
            # Arbeitspreis NT
            verbrauch_nt = self.calculate_verbrauch(von, bis, ht=False)
            preis_nt = float(tarif["Arbeitspreis NT"])
            betrag_netto_nt = verbrauch_nt * preis_nt / 100
            betrag_netto_sum += betrag_netto_nt
            self.energiekosten_table.setItem(row, 0, QTableWidgetItem(f"Arbeitspreis NT ({tarif_id})"))
            self.energiekosten_table.setItem(row, 1, QTableWidgetItem(f"{von} - {bis}"))
            self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{verbrauch_nt:.2f} (kWh)"))
            self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{tarif['Arbeitspreis NT']} (ct/kWh)"))
            self.energiekosten_table.setItem(row, 4, QTableWidgetItem(f"{betrag_netto_nt:.2f} (€)"))
            row += 1

        for grundpreis in unique_grundpreis:
            von, bis = self.calculate_zeitraum(tariffs, "Grundpreis", grundpreis)
            if von and bis:
                zeitraum = f"{von} - {bis}"
                days = self.calculate_days(von, bis)
                preis_grund = float(grundpreis)
                betrag_netto_grund = preis_grund * (days / 365)
                betrag_netto_sum += betrag_netto_grund
                self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Grundpreis"))
                self.energiekosten_table.setItem(row, 1, QTableWidgetItem(zeitraum))
                self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{days} (days)"))
                self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{grundpreis} (€/jahr)"))
                self.energiekosten_table.setItem(row, 4, QTableWidgetItem(f"{betrag_netto_grund:.2f} (€)"))
            row += 1

        for zähler in unique_zähler:
            von, bis = self.calculate_zeitraum(tariffs, "Zähler", zähler)
            if von and bis:
                zeitraum = f"{von} - {bis}"
                days = self.calculate_days(von, bis)
                preis_zähler = float(zähler)
                betrag_netto_zähler = preis_zähler * (days / 365)
                betrag_netto_sum += betrag_netto_zähler
                self.energiekosten_table.setItem(row, 0, QTableWidgetItem("Zähler"))
                self.energiekosten_table.setItem(row, 1, QTableWidgetItem(zeitraum))
                self.energiekosten_table.setItem(row, 2, QTableWidgetItem(f"{days} (days)"))
                self.energiekosten_table.setItem(row, 3, QTableWidgetItem(f"{zähler} (€/jahr)"))
                self.energiekosten_table.setItem(row, 4, QTableWidgetItem(f"{betrag_netto_zähler:.2f} (€)"))
            row += 1

        # سطر Energiekosten (Summe)
        mwst = betrag_netto_sum * 0.19
        betrag_brutto = betrag_netto_sum + mwst

        # تنظیم فونت Bold و رنگ طوسی ملایم
        font = QFont()
        font.setBold(True)

        energiekosten_item = QTableWidgetItem("Energiekosten")
        energiekosten_item.setFont(font)
        energiekosten_item.setBackground(Qt.lightGray)  # طوسی ملایم (#D3D3D3)

        betrag_netto_item = QTableWidgetItem(f"{betrag_netto_sum:.2f} (€)")
        betrag_netto_item.setFont(font)
        betrag_netto_item.setBackground(Qt.lightGray)

        mwst_item = QTableWidgetItem(f"(19%) {mwst:.2f} (€)")
        mwst_item.setFont(font)
        mwst_item.setBackground(Qt.lightGray)

        betrag_brutto_item = QTableWidgetItem(f"{betrag_brutto:.2f} (€)")
        betrag_brutto_item.setFont(font)
        betrag_brutto_item.setBackground(Qt.lightGray)

        self.energiekosten_table.setItem(row, 0, energiekosten_item)
        self.energiekosten_table.setItem(row, 4, betrag_netto_item)
        self.energiekosten_table.setItem(row, 5, mwst_item)
        self.energiekosten_table.setItem(row, 6, betrag_brutto_item)

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