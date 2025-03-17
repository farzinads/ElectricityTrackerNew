from base import tk, ttk, messagebox, DateEntry, save_data, PDF_DIR, os
import shutil
import subprocess
from datetime import datetime

class RechnungenManager:
    def __init__(self, app):
        self.root = app.root
        self.data = app.data
        self.current_contract = app.current_contract
        self.rechnungen_tab = app.rechnungen_tab
        self.setup_rechnungen_tab()

    def setup_rechnungen_tab(self):
        rechnungen_frame = ttk.Frame(self.rechnungen_tab)
        rechnungen_frame.place(x=10, y=10)

        # فرم ورودی
        ttk.Label(rechnungen_frame, text="Rechnungsnummer:").grid(row=0, column=0, pady=5, sticky="w")
        self.rechnungsnummer = ttk.Entry(rechnungen_frame)
        self.rechnungsnummer.grid(row=0, column=1, pady=5)

        ttk.Label(rechnungen_frame, text="Datum:").grid(row=1, column=0, pady=5, sticky="w")
        self.rechnungsdatum = DateEntry(rechnungen_frame, date_pattern="dd.mm.yyyy")
        self.rechnungsdatum.grid(row=1, column=1, pady=5)

        ttk.Label(rechnungen_frame, text="Betrag (€):").grid(row=2, column=0, pady=5, sticky="w")
        self.rechnung_betrag = ttk.Entry(rechnungen_frame)
        self.rechnung_betrag.grid(row=2, column=1, pady=5)

        ttk.Button(rechnungen_frame, text="PDF hochladen", command=self.upload_pdf).grid(row=3, column=0, pady=5)
        self.pdf_label = ttk.Label(rechnungen_frame, text="Kein PDF ausgewählt")
        self.pdf_label.grid(row=3, column=1, pady=5, sticky="w")

        ttk.Button(rechnungen_frame, text="Speichern", command=self.save_rechnung).grid(row=4, column=0, columnspan=2, pady=10)

        # جدول
        table_frame_rechnungen = ttk.Frame(self.rechnungen_tab, relief="solid", borderwidth=2)
        table_frame_rechnungen.place(x=10, y=165, width=960, height=485)

        self.rechnungen_table = ttk.Treeview(table_frame_rechnungen, columns=("Rechnungsnummer", "Datum", "Betrag", "PDF"), show="headings")
        self.rechnungen_table.heading("Rechnungsnummer", text="Rechnungsnummer")
        self.rechnungen_table.heading("Datum", text="Datum")
        self.rechnungen_table.heading("Betrag", text="Betrag (€)")
        self.rechnungen_table.heading("PDF", text="PDF")
        self.rechnungen_table.column("Rechnungsnummer", width=200, anchor="center")
        self.rechnungen_table.column("Datum", width=150, anchor="center")
        self.rechnungen_table.column("Betrag", width=150, anchor="center")
        self.rechnungen_table.column("PDF", width=150, anchor="center")

        scrollbar_rechnungen = ttk.Scrollbar(table_frame_rechnungen, orient="vertical", command=self.rechnungen_table.yview)
        self.rechnungen_table.configure(yscrollcommand=scrollbar_rechnungen.set)
        scrollbar_rechnungen.pack(side="right", fill="y")
        self.rechnungen_table.pack(fill="both", expand=True)

        # منوی راست‌کلیک
        self.context_menu_rechnungen = tk.Menu(self.root, tearoff=0)
        self.context_menu_rechnungen.add_command(label="Bearbeiten", command=self.edit_rechnung)
        self.context_menu_rechnungen.add_command(label="Löschen", command=self.delete_rechnung)
        self.rechnungen_table.bind("<Button-3>", self.show_context_menu_rechnungen)
        self.rechnungen_table.bind("<Double-1>", self.open_pdf_from_table)

        self.update_rechnungen_table()

    def upload_pdf(self):
        pdf_path = tk.filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            self.current_pdf_path = pdf_path
            self.pdf_label.config(text=os.path.basename(pdf_path))

    def save_rechnung(self):
        if not self.current_contract:
            messagebox.showerror("Fehler", "Kein Vertrag ausgewählt!")
            return
        rechnungsnummer = self.rechnungsnummer.get()
        datum = self.rechnungsdatum.get()
        betrag = self.rechnung_betrag.get()
        if not all([rechnungsnummer, datum, betrag]):
            messagebox.showerror("Fehler", "Rechnungsnummer, Datum und Betrag müssen ausgefüllت sein!")
            return
        try:
            float(betrag)
        except ValueError:
            messagebox.showerror("Fehler", "Betrag muss numerisch sein!")
            return
        pdf_path = None
        if hasattr(self, 'current_pdf_path') and self.current_pdf_path:
            pdf_filename = f"Rechnung_{self.current_contract}_{datum.replace('.', '_')}_{os.path.basename(self.current_pdf_path)}"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)
            shutil.copy(self.current_pdf_path, pdf_path)
        rechnung = {
            "vertragskonto": self.current_contract,
            "rechnungsnummer": rechnungsnummer,
            "datum": datum,
            "betrag": betrag,
            "pdf_path": pdf_path if pdf_path else "-"
        }
        if "rechnungen" not in self.data:
            self.data["rechnungen"] = []
        self.data["rechnungen"].append(rechnung)
        self.data["rechnungen"] = sorted(self.data["rechnungen"], key=lambda x: datetime.strptime(x["datum"], "%d.%m.%Y"))
        save_data(self.data)
        messagebox.showinfo("Erfolg", "Rechnung wurde gespeichert!")
        self.clear_rechnung_entries()
        self.update_rechnungen_table()

    def update_rechnungen_table(self):
        self.rechnungen_table.delete(*self.rechnungen_table.get_children())
        if self.current_contract and "rechnungen" in self.data:
            for item in self.data["rechnungen"]:
                if item["vertragskonto"] == self.current_contract:
                    pdf_button = "Anzeigen" if item["pdf_path"] != "-" else "-"
                    self.rechnungen_table.insert("", "end", values=(item["rechnungsnummer"], item["datum"], item["betrag"], pdf_button), tags=(item["pdf_path"],))

    def clear_rechnung_entries(self):
        self.rechnungsnummer.delete(0, tk.END)
        self.rechnungsdatum.set_date(datetime.now().strftime("%d.%m.%Y"))
        self.rechnung_betrag.delete(0, tk.END)
        self.current_pdf_path = None
        self.pdf_label.config(text="Kein PDF ausgewählt")

    def edit_rechnung(self):
        selected = self.rechnungen_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.rechnungen_table.item(selected[0], "values")
        for i, item in enumerate(self.data["rechnungen"]):
            if item["vertragskonto"] == self.current_contract and item["rechnungsnummer"] == values[0]:
                self.rechnungsnummer.delete(0, tk.END)
                self.rechnungsnummer.insert(0, item["rechnungsnummer"])
                self.rechnungsdatum.set_date(item["datum"])
                self.rechnung_betrag.delete(0, tk.END)
                self.rechnung_betrag.insert(0, item["betrag"])
                self.current_pdf_path = item["pdf_path"] if item["pdf_path"] != "-" else None
                self.pdf_label.config(text=os.path.basename(item["pdf_path"]) if item["pdf_path"] != "-" else "Kein PDF ausgewählt")
                self.data["rechnungen"].pop(i)
                self.rechnungen_table.delete(selected[0])
                self.data["rechnungen"] = sorted(self.data["rechnungen"], key=lambda x: datetime.strptime(x["datum"], "%d.%m.%Y"))
                save_data(self.data)
                messagebox.showinfo("Info", "Rechnung zum Bearbeiten geladen. Ändern و erneut speichern!")
                self.update_rechnungen_table()
                break

    def delete_rechnung(self):
        selected = self.rechnungen_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.rechnungen_table.item(selected[0], "values")
        for i, item in enumerate(self.data["rechnungen"]):
            if item["vertragskonto"] == self.current_contract and item["rechnungsnummer"] == values[0]:
                if item["pdf_path"] != "-" and os.path.exists(item["pdf_path"]):
                    os.remove(item["pdf_path"])
                self.data["rechnungen"].pop(i)
                self.rechnungen_table.delete(selected[0])
                save_data(self.data)
                messagebox.showinfo("Erfolg", "Rechnung wurde gelöscht!")
                break
        self.update_rechnungen_table()

    def open_pdf_from_table(self, event):
        item = self.rechnungen_table.identify_row(event.y)
        if not item:
            return
        pdf_path = self.rechnungen_table.item(item, "tags")[0]
        if pdf_path and pdf_path != "-":
            if os.name == "nt":  # Windows
                os.startfile(pdf_path)
            else:  # Linux/Mac
                subprocess.call(["xdg-open", pdf_path])

    def show_context_menu_rechnungen(self, event):
        row = self.rechnungen_table.identify_row(event.y)
        if row:
            self.rechnungen_table.selection_set(row)
            self.context_menu_rechnungen.post(event.x_root, event.y_root)