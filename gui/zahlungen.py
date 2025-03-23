from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from database.db_handler import DatabaseHandler

class Zahlungen(QWidget):
    def __init__(self, db, parent=None, vertragsnummer=None):
        super().__init__()
        self.setWindowTitle("Zahlungen")
        self.db = db
        self.parent = parent
        self.vertragsnummer = vertragsnummer
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # نمایش Vertragsnummer
        vertragsnummer_label = QLabel(f"Vertragsnummer: {self.vertragsnummer if self.vertragsnummer else 'Nicht ausgewählt'}")
        vertragsnummer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(vertragsnummer_label)
        
        layout.addWidget(QLabel("Hier kommt später der Zahlungen-Inhalt"))
        
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.back_to_parent)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget { 
                font-size: 14px; 
                background-color: #434f5a; 
                color: #ffffff; 
            }
            QPushButton { 
                background-color: #676b6d; 
                color: white; 
                font-weight: bold; 
                padding: 5px; 
                border-radius: 10px; 
                border: 2px solid #676b6d; 
            }
        """)

    def back_to_parent(self):
        if self.parent:
            self.parent.show()
        self.close()