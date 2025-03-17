import tkinter as tk
from app import ElectricityTrackerApp
from contract_manager import ContractManager
from details_tabs import DetailsTabs
from tarif_manager import TarifManager
from ablesung_manager import AblesungManager
from zahlung_manager import ZahlungManager
from rechnungen_manager import RechnungenManager

class MainApp(ElectricityTrackerApp, ContractManager, DetailsTabs, TarifManager, AblesungManager, ZahlungManager, RechnungenManager):
    def __init__(self, root):
        ElectricityTrackerApp.__init__(self, root)
        
        # راه‌اندازی صفحات و تب‌ها
        self.setup_contract_page()  # از ContractManager
        self.setup_contract_details_page()  # از DetailsTabs
        self.setup_tarifedaten_tab()  # از TarifManager
        self.setup_ablesung_tab()  # از AblesungManager
        self.setup_zahlungen_tab()  # از ZahlungManager
        self.setup_energiekosten_tab()  # از ZahlungManager
        self.setup_rechnungen_tab()  # از RechnungenManager
        
        self.switch_page(self.contract_frame)

    def setup_rechnungen_tab(self):
        RechnungenManager.setup_rechnungen_tab(self)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()