import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox, QMenu, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
import json
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import subprocess

class Rechnungen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Rechnungen")
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

        table_frame = QGroupBox("Rechnungen")
        table_layout = QVBoxLayout()

        self.rechnungen_table = QTableWidget()
        self.rechnungen_table.setColumnCount(4)
        self.rechnungen_table.setHorizontalHeaderLabels([
            "Rechnungsnummer", "Rechnungsdatum", "Betrag brutto", "Original Rechnung Upload"
        ])
        self.rechnungen_table.setColumnWidth(0, 200)
        self.rechnungen_table.setColumnWidth(1, 200)
        self.rechnungen_table.setColumnWidth(2, 200)
        self.rechnungen_table.setColumnWidth(3, 300)
        self.rechnungen_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rechnungen_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rechnungen_table.customContextMenuRequested.connect(self.show_context_menu)
        self.rechnungen_table.doubleClicked.connect(self.handle_double_click)  # اضافه کردن دابل‌کلیک

        self.rechnungen_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.rechnungen_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.rechnungen_table)
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
            QLabel { 
                background-color: #434f5a; 
                color: #ffffff; 
                padding: 5px; 
            }
        """)

    def load_data(self):
        rechnungen = self.db.get_all_rechnungen()
        self.rechnungen_table.setRowCount(len(rechnungen))
        for row, rechnung in enumerate(rechnungen):
            self.rechnungen_table.setItem(row, 0, QTableWidgetItem(rechnung["Rechnungsnummer"]))
            self.rechnungen_table.setItem(row, 1, QTableWidgetItem(rechnung["Rechnungsdatum"]))
            self.rechnungen_table.setItem(row, 2, QTableWidgetItem(f"{rechnung['Betrag_brutto']} (€)"))
            upload_item = QTableWidgetItem(self.uploaded_files.get(rechnung["Rechnungsnummer"], "No file uploaded"))
            self.rechnungen_table.setItem(row, 3, upload_item)

    def show_context_menu(self, pos):
        index = self.rechnungen_table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        column = index.column()

        if row < 0:
            return

        menu = QMenu(self)

        if column == 0:  # ستون Rechnungsnummer
            open_action = menu.addAction("Öffnen")
            edit_action = menu.addAction("Bearbeiten")
            delete_action = menu.addAction("Löschen")

            action = menu.exec_(self.rechnungen_table.viewport().mapToGlobal(pos))

            if action == open_action:
                self.open_pdf(row)
            elif action == edit_action:
                self.edit_rechnung(row)
            elif action == delete_action:
                self.delete_rechnung()

        elif column == 3:  # ستون Original Rechnung Upload
            current_file = self.rechnungen_table.item(row, 3).text()
            if current_file == "No file uploaded":
                upload_action = menu.addAction("Upload Original Rechnung")
                action = menu.exec_(self.rechnungen_table.viewport().mapToGlobal(pos))
                if action == upload_action:
                    self.upload_rechnung(row)
            else:
                edit_action = menu.addAction("Bearbeiten (Replace PDF)")
                delete_action = menu.addAction("Löschen (Remove PDF)")

                action = menu.exec_(self.rechnungen_table.viewport().mapToGlobal(pos))

                if action == edit_action:
                    self.upload_rechnung(row)  # جایگزین کردن فایل
                elif action == delete_action:
                    self.delete_uploaded_file(row)

        # ستون‌های 1 و 2 هیچ منویی ندارن
        else:
            return

    def handle_double_click(self, index):
        if index.column() == 3:  # فقط ستون Original Rechnung Upload
            row = index.row()
            rechnungsnummer = self.rechnungen_table.item(row, 0).text()
            file_path = self.uploaded_files.get(rechnungsnummer)
            if file_path and os.path.exists(file_path):
                subprocess.Popen([file_path], shell=True)
            else:
                QMessageBox.warning(self, "خطا", "فایل PDF پیدا نشد یا قبلاً حذف شده است.")

    def open_pdf(self, row):
        rechnungsnummer = self.rechnungen_table.item(row, 0).text()
        rechnungsdatum = self.rechnungen_table.item(row, 1).text()
        rechnungen = self.db.get_all_rechnungen()
        selected_rechnung = next(r for r in rechnungen if r["Rechnungsnummer"] == rechnungsnummer)

        print(f"Selected_rows for {rechnungsnummer}: {selected_rechnung['Selected_rows']}")

        if selected_rechnung["Selected_rows"] is None or selected_rechnung["Selected_rows"] == "":
            QMessageBox.warning(self, "خطا", f"هیچ داده‌ای برای {rechnungsnummer} انتخاب نشده است. PDF نمی‌تواند ساخته شود.")
            return

        selected_rows = json.loads(selected_rechnung["Selected_rows"])
        print(f"Parsed selected_rows: {selected_rows}")

        total_betrag_netto = sum(float(row["Betrag_netto"].split()[0]) for row in selected_rows)
        mwst = total_betrag_netto * 0.19
        betrag_brutto = total_betrag_netto + mwst

        invoice_dir = os.path.join(os.path.dirname(__file__), "..", "invoices")
        os.makedirs(invoice_dir, exist_ok=True)
        pdf_path = os.path.join(invoice_dir, f"Rechnung_{rechnungsnummer}.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()

        header_data = [
            ["Vertragsnummer:", self.vertragsnummer],
            ["Rechnungsnummer:", rechnungsnummer],
            ["Rechnungsdatum:", rechnungsdatum]
        ]
        header_table = Table(header_data, colWidths=[200, 500])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        data = [["", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag brutto"]]
        for row in selected_rows:
            betrag_netto = float(row["Betrag_netto"].split()[0])
            row_mwst = betrag_netto * 0.19
            row_brutto = betrag_netto + row_mwst
            data.append([
                row["Description"],
                row["Zeitraum"],
                row["Menge"],
                row["Preis_netto"],
                row["Betrag_netto"],
                f"{row_mwst:.2f} (€)",
                f"{row_brutto:.2f} (€)"
            ])
        
        data.append([
            "Energiekosten",
            "", "", "",
            f"{total_betrag_netto:.2f} (€)",
            f"{mwst:.2f} (€)",
            f"{betrag_brutto:.2f} (€)"
        ])

        table = Table(data, colWidths=[200, 120, 100, 100, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.827, 0.827, 0.827)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)

        doc.build(elements)
        subprocess.Popen([pdf_path], shell=True)

    def edit_rechnung(self, row):
        from gui.energiekosten import Energiekosten
        rechnungsnummer = self.rechnungen_table.item(row, 0).text()
        rechnungen = self.db.get_all_rechnungen()
        selected_rechnung = next(r for r in rechnungen if r["Rechnungsnummer"] == rechnungsnummer)
        selected_rows = json.loads(selected_rechnung["Selected_rows"]) if selected_rechnung["Selected_rows"] else []

        self.energiekosten_window = Energiekosten(self.db, self.parent, self.vertragsnummer, selected_rechnung=selected_rechnung)
        self.energiekosten_window.show()
        self.hide()

    def delete_rechnung(self):
        selected_row = self.rechnungen_table.currentRow()
        if selected_row >= 0:
            rechnungsnummer = self.rechnungen_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, "تأیید حذف", f"آیا مطمئن هستید که می‌خواهید {rechnungsnummer} را حذف کنید؟",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Rechnungen WHERE Rechnungsnummer = ?", (rechnungsnummer,))
                    conn.commit()
                self.load_data()

    def upload_rechnung(self, row):
        rechnungsnummer = self.rechnungen_table.item(row, 0).text()
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Original Rechnung", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.uploaded_files[rechnungsnummer] = file_path
            self.rechnungen_table.setItem(row, 3, QTableWidgetItem(file_path.split('/')[-1]))

    def delete_uploaded_file(self, row):
        rechnungsnummer = self.rechnungen_table.item(row, 0).text()
        if rechnungsnummer in self.uploaded_files:
            del self.uploaded_files[rechnungsnummer]
            self.rechnungen_table.setItem(row, 3, QTableWidgetItem("No file uploaded"))

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()