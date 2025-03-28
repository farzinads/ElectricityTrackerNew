from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QLabel, QMenu
from PyQt5.QtCore import Qt
import sqlite3

class Abschlagen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Abschlagen")
        self.resize(1200, 800)
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.is_editing = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(vertragsnummer_label)

        input_frame = QGroupBox("Neuen Abschlag hinzufügen")
        input_frame.setFixedHeight(350)
        input_layout = QVBoxLayout()

        form_layout = QFormLayout()

        # لیبل Zeitraum
        zeitraum_label = QLabel("Zeitraum:")
        zeitraum_label.setObjectName("form_label")

        # فیلدهای Von و Bis کنار هم
        zeitraum_fields_layout = QHBoxLayout()
        self.zeitraum_von_input = QLineEdit()
        self.zeitraum_von_input.setPlaceholderText("Von (DD.MM.YYYY)")
        self.zeitraum_von_input.setFixedWidth(170)
        self.zeitraum_bis_input = QLineEdit()
        self.zeitraum_bis_input.setPlaceholderText("Bis (DD.MM.YYYY)")
        self.zeitraum_bis_input.setFixedWidth(170)
        zeitraum_fields_layout.addWidget(self.zeitraum_von_input)
        zeitraum_fields_layout.addWidget(self.zeitraum_bis_input)

        form_layout.addRow(zeitraum_label, zeitraum_fields_layout)

        # فیلد Abschlag
        abschlag_label = QLabel("Abschlag:")
        abschlag_label.setObjectName("form_label")
        self.abschlag_input = QLineEdit()
        self.abschlag_input.setPlaceholderText("Betrag in €")
        self.abschlag_input.setFixedWidth(350)
        form_layout.addRow(abschlag_label, self.abschlag_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self.save_abschlag)
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setFixedSize(150, 37)
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        back_btn.setFixedSize(150, 37)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()

        input_layout.addLayout(form_layout)
        input_layout.addLayout(btn_layout)
        input_layout.addStretch()
        input_frame.setLayout(input_layout)

        table_frame = QGroupBox("Abschläge")
        table_frame.setObjectName("table_frame")
        table_layout = QVBoxLayout()

        self.abschlagen_table = QTableWidget()
        self.abschlagen_table.setColumnCount(2)  # فقط دو ستون
        self.abschlagen_table.setHorizontalHeaderLabels(["Zeitraum", "Abschlag"])
        self.abschlagen_table.setColumnWidth(0, 400)  # ستون Zeitraum عریض‌تر
        self.abschlagen_table.setColumnWidth(1, 200)
        self.abschlagen_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.abschlagen_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.abschlagen_table.customContextMenuRequested.connect(self.show_context_menu)

        self.abschlagen_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-bottom: 2px solid #000000;
            }
        """)
        self.abschlagen_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #D3D3D3;
                color: black;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #000000;
                border-right: 2px solid #000000;
            }
        """)

        table_layout.addWidget(self.abschlagen_table)
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
                cursor.execute("SELECT ZeitraumVon, ZeitraumBis, Abschlagsbetrag FROM Abschlagen WHERE Vertragsnummer = ?", (self.vertragsnummer,))
                abschlagen = cursor.fetchall()

            self.abschlagen_table.setRowCount(len(abschlagen))
            for row, abschlag in enumerate(abschlagen):
                zeitraum = f"{abschlag[0]} —— {abschlag[1]}"  # ترکیب Von و Bis با خط تیره
                self.abschlagen_table.setItem(row, 0, QTableWidgetItem(zeitraum))
                self.abschlagen_table.setItem(row, 1, QTableWidgetItem(f"{abschlag[2]:.2f} €"))
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "Fehler", f"Datenbankfehler: {str(e)}")
            self.abschlagen_table.setRowCount(0)

    def save_abschlag(self):
        zeitraum_von = self.zeitraum_von_input.text()
        zeitraum_bis = self.zeitraum_bis_input.text()
        abschlag = self.abschlag_input.text()

        if not zeitraum_von or not zeitraum_bis or not abschlag:
            QMessageBox.warning(self, "Fehler", "Bitte füllen Sie alle Felder aus!")
            return

        try:
            betrag = float(abschlag)
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                if self.is_editing:
                    cursor.execute("""
                        UPDATE Abschlagen 
                        SET ZeitraumVon = ?, ZeitraumBis = ?, Abschlagsbetrag = ?
                        WHERE Vertragsnummer = ? AND ZeitraumVon = ? AND ZeitraumBis = ?
                    """, (zeitraum_von, zeitraum_bis, betrag, self.vertragsnummer, self.edit_zeitraum_von, self.edit_zeitraum_bis))
                    self.is_editing = False
                    self.save_btn.setText("Speichern")
                else:
                    cursor.execute("""
                        INSERT INTO Abschlagen (Vertragsnummer, ZeitraumVon, ZeitraumBis, Abschlagsbetrag)
                        VALUES (?, ?, ?, ?)
                    """, (self.vertragsnummer, zeitraum_von, zeitraum_bis, betrag))
                conn.commit()
            self.zeitraum_von_input.clear()
            self.zeitraum_bis_input.clear()
            self.abschlag_input.clear()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Abschlag muss eine Zahl باشد!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Fehler", f"Datenbankfehler: {str(e)}")

    def edit_abschlag(self):
        selected_row = self.abschlagen_table.currentRow()
        if selected_row >= 0:
            zeitraum = self.abschlagen_table.item(selected_row, 0).text().split(" —— ")
            self.edit_zeitraum_von = zeitraum[0]
            self.edit_zeitraum_bis = zeitraum[1]
            self.zeitraum_von_input.setText(self.edit_zeitraum_von)
            self.zeitraum_bis_input.setText(self.edit_zeitraum_bis)
            self.abschlag_input.setText(self.abschlagen_table.item(selected_row, 1).text().replace(" €", ""))
            self.delete_abschlag()  # حذف موقت برای ویرایش
            self.is_editing = True
            self.save_btn.setText("Aktualisieren")
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Abschlag aus!")

    def delete_abschlag(self):
        selected_row = self.abschlagen_table.currentRow()
        if selected_row >= 0:
            zeitraum = self.abschlagen_table.item(selected_row, 0).text().split(" —— ")
            zeitraum_von = zeitraum[0]
            zeitraum_bis = zeitraum[1]
            if not self.is_editing:  # فقط در حالت غیر ویرایش هشدار بده
                reply = QMessageBox.question(self, "Warnung",
                                             f"Möchten Sie den Abschlag von {zeitraum_von} bis {zeitraum_bis} wirklich löschen?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM Abschlagen 
                        WHERE Vertragsnummer = ? AND ZeitraumVon = ? AND ZeitraumBis = ?
                    """, (self.vertragsnummer, zeitraum_von, zeitraum_bis))
                    conn.commit()
                self.load_data()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Fehler", f"Datenbankfehler: {str(e)}")
        else:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Abschlag aus!")

    def show_context_menu(self, pos):
        selected_row = self.abschlagen_table.currentRow()
        if selected_row >= 0:
            menu = QMenu(self)
            edit_action = menu.addAction("Bearbeiten")
            delete_action = menu.addAction("Löschen")

            edit_action.triggered.connect(self.edit_abschlag)
            delete_action.triggered.connect(self.delete_abschlag)

            menu.exec_(self.abschlagen_table.viewport().mapToGlobal(pos))

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()