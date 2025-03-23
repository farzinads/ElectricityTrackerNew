import sqlite3

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    Vertragsnummer TEXT PRIMARY KEY,
                    Stromanbieter TEXT,
                    Vertragstyp TEXT,
                    Startdatum TEXT,
                    Zählernummer TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tarifdaten (
                    "Tarif-ID" TEXT PRIMARY KEY,
                    "Von" TEXT,
                    "Bis" TEXT,
                    "Arbeitspreis HT" TEXT,
                    "Arbeitspreis NT" TEXT,
                    "Grundpreis" TEXT,
                    "Zähler" TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ablesungen (
                    "Ablesungsdatum" TEXT,
                    "Ablesungstyp" TEXT,
                    "Zählerstand HT" TEXT,
                    "Zählerstand NT" TEXT,
                    PRIMARY KEY ("Ablesungsdatum", "Ablesungstyp")
                )
            ''')
            conn.commit()

    def add_contract(self, contract):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contracts (Vertragsnummer, Stromanbieter, Vertragstyp, Startdatum, Zählernummer)
                VALUES (?, ?, ?, ?, ?)
            ''', (contract["Vertragsnummer"], contract["Stromanbieter"], contract["Vertragstyp"], 
                  contract["Startdatum"], contract["Zählernummer"]))
            conn.commit()

    def get_all_contracts(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contracts")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_contract(self, vertragsnummer):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contracts WHERE Vertragsnummer = ?", (vertragsnummer,))
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None

    def delete_contract(self, vertragsnummer):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contracts WHERE Vertragsnummer = ?", (vertragsnummer,))
            conn.commit()

    def add_tarif(self, tarif):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tarifdaten ("Tarif-ID", "Von", "Bis", "Arbeitspreis HT", "Arbeitspreis NT", "Grundpreis", "Zähler")
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tarif["Tarif-ID"], tarif["Von"], tarif["Bis"], tarif["Arbeitspreis HT"], 
                  tarif["Arbeitspreis NT"], tarif["Grundpreis"], tarif["Zähler"]))
            conn.commit()

    def get_all_tarifs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tarifdaten")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def delete_tarif(self, tarif_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarifdaten WHERE \"Tarif-ID\" = ?", (tarif_id,))
            conn.commit()

    def add_ablesung(self, ablesung):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ablesungen ("Ablesungsdatum", "Ablesungstyp", "Zählerstand HT", "Zählerstand NT")
                VALUES (?, ?, ?, ?)
            ''', (ablesung["Ablesungsdatum"], ablesung["Ablesungstyp"], 
                  ablesung["Zählerstand HT"], ablesung["Zählerstand NT"]))
            conn.commit()

    def get_all_ablesungen(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ablesungen")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def delete_ablesung(self, ablesungsdatum, ablesungstyp):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ablesungen WHERE \"Ablesungsdatum\" = ? AND \"Ablesungstyp\" = ?", 
                          (ablesungsdatum, ablesungstyp))
            conn.commit()