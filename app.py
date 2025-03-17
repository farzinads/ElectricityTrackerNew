import tkinter as tk
from tkinter import ttk
from base import load_data, save_data, PDF_DIR, os

class ElectricityTrackerApp:
    def __init__(self, root):
        self.data = load_data()
        self.root = root
        self.root.title("Stromverbrauchs-Tracker")
        self.root.geometry("1000x700")
        self.current_page = None
        self.current_contract = None
        self.current_pdf_path = None

        if not os.path.exists(PDF_DIR):
            os.makedirs(PDF_DIR)

        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.contract_frame = ttk.Frame(self.container, padding="10")
        self.contract_details_frame = ttk.Frame(self.container, padding="10")

        self.style = ttk.Style()
        self.style.configure("Custom.TButton", background="#A9A9A9", foreground="black")
        self.style.configure("TNotebook", background="#FFFFFF")
        self.style.configure("TNotebook.Tab", foreground="#FF0000", padding=[10, 5], font=("Arial", 10, "bold"))
        self.style.map("TNotebook.Tab", foreground=[("selected", "#008000")])
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def switch_page(self, frame):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = frame
        self.current_page.pack(fill="both", expand=True)