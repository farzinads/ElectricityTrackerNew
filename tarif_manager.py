from base import tk, ttk, messagebox, DateEntry, save_data
from datetime import datetime

class TarifManager:
    def __init__(self, app):
        self.root = app.root
        self.data = app.data
        self.current_contract = app.current_contract
        self.tarifedaten_tab = app.tarifedaten_tab
        self.zahlung_manager = app  # برای آپدیت جدول Energiekosten
        self.setup_tarifedaten_tab()

    def setup_tarifedaten_tab(self):
        tarifedaten_frame = ttk.Frame(self.tarifedaten_tab)
        tarifedaten_frame.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(tarifedaten_frame, text="Datum:").grid(row=0, column=0, pady=5, sticky="w")
        ttk.Label(tarifedaten_frame, text="Von:").grid(row=1, column=0, pady=5, sticky="w")
        self.tarif_von = DateEntry(tarifedaten_frame, date_pattern="dd.mm.yyyy")
        self.tarif_von.grid(row=1, column=1, pady=5)
        ttk.Label(tarifedaten_frame, text="Bis:").grid(row=2, column=0, pady=5, sticky="w")
        self.tarif_bis = DateEntry(tarifedaten_frame, date_pattern="dd.mm.yyyy")
        self.tarif_bis.grid(row=2, column=1, pady=5)

        ttk.Label(tarifedaten_frame, text="Arbeitspreis HT (ct/kWh):").grid(row=3, column=0, pady=5, sticky="w")
        self.tarif_arbeitspreis_ht = ttk.Entry(tarifedaten_frame)
        self.tarif_arbeitspreis_ht.grid(row=3, column=1, pady=5)

        ttk.Label(tarifedaten_frame, text="Arbeitspreis NT (ct/kWh):").grid(row=4, column=0, pady=5, sticky="w")
        self.tarif_arbeitspreis_nt = ttk.Entry(tarifedaten_frame)
        self.tarif_arbeitspreis_nt.grid(row=4, column=1, pady=5)

        ttk.Label(tarifedaten_frame, text="Grundpreis (€/Jahr):").grid(row=5, column=0, pady=5, sticky="w")
        self.tarif_grundpreis = ttk.Entry(tarifedaten_frame)
        self.tarif_grundpreis.grid(row=5, column=1, pady=5)
        ttk.Label(tarifedaten_frame, text="Kennung Grundpreis:").grid(row=5, column=2, pady=5, sticky="w")
        self.tarif_grundpreis_id = ttk.Entry(tarifedaten_frame)
        self.tarif_grundpreis_id.grid(row=5, column=3, pady=5)

        ttk.Label(tarifedaten_frame, text="Zählerkosten (€/Jahr):").grid(row=6, column=0, pady=5, sticky="w")
        self.tarif_zählerkosten = ttk.Entry(tarifedaten_frame)
        self.tarif_zählerkosten.grid(row=6, column=1, pady=5)
        ttk.Label(tarifedaten_frame, text="Kennung Zählerkosten:").grid(row=6, column=2, pady=5, sticky="w")
        self.tarif_zählerkosten_id = ttk.Entry(tarifedaten_frame)
        self.tarif_zählerkosten_id.grid(row=6, column=3, pady=5)

        ttk.Label(tarifedaten_frame, text="Zusatzkosten:").grid(row=7, column=0, pady=5, sticky="w")
        self.tarif_zusatzkosten = ttk.Entry(tarifedaten_frame)
        self.tarif_zusatzkosten.grid(row=7, column=1, pady=5)
        ttk.Label(tarifedaten_frame, text="Kennung Zusatzkosten:").grid(row=7, column=2, pady=5, sticky="w")
        self.tarif_zusatzkosten_id = ttk.Entry(tarifedaten_frame)
        self.tarif_zusatzkosten_id.grid(row=7, column=3, pady=5)

        ttk.Button(tarifedaten_frame, text="Speichern", command=self.save_tarifedaten).grid(row=8, column=1, pady=10, sticky="e")

        table_frame_tarif = ttk.Frame(self.tarifedaten_tab, relief="solid", borderwidth=2)
        table_frame_tarif.place(x=10, y=300, width=960, height=359)

        style = ttk.Style()
        style.configure("Tarif.Treeview.Heading", font=("Arial", 8), foreground="#00008B")

        self.tarifedaten_table = ttk.Treeview(table_frame_tarif, columns=("Von", "Bis", "Arbeitspreis HT", "Arbeitspreis NT", "Grundpreis", "Zählerkosten", "Zusatzkosten"), show="headings", style="Tarif.Treeview")
        self.tarifedaten_table.heading("Von", text="Von")
        self.tarifedaten_table.heading("Bis", text="Bis")
        self.tarifedaten_table.heading("Arbeitspreis HT", text="Arbeitspreis HT (ct/kWh)")
        self.tarifedaten_table.heading("Arbeitspreis NT", text="Arbeitspreis NT (ct/kWh)")
        self.tarifedaten_table.heading("Grundpreis", text="Grundpreis (€/Jahr)")
        self.tarifedaten_table.heading("Zählerkosten", text="Zählerkosten (€/Jahr)")
        self.tarifedaten_table.heading("Zusatzkosten", text="Zusatzkosten")
        self.tarifedaten_table.column("Von", width=100, anchor="center")
        self.tarifedaten_table.column("Bis", width=100, anchor="center")
        self.tarifedaten_table.column("Arbeitspreis HT", width=150, anchor="center")
        self.tarifedaten_table.column("Arbeitspreis NT", width=150, anchor="center")
        self.tarifedaten_table.column("Grundpreis", width=150, anchor="center")
        self.tarifedaten_table.column("Zählerkosten", width=150, anchor="center")
        self.tarifedaten_table.column("Zusatzkosten", width=150, anchor="center")

        scrollbar_tarif = ttk.Scrollbar(table_frame_tarif, orient="vertical", command=self.tarifedaten_table.yview)
        self.tarifedaten_table.configure(yscrollcommand=scrollbar_tarif.set)
        scrollbar_tarif.pack(side="right", fill="y")
        self.tarifedaten_table.pack(fill="both", expand=True)

        self.context_menu_tarifedaten = tk.Menu(self.root, tearoff=0)
        self.context_menu_tarifedaten.add_command(label="Bearbeiten", command=self.edit_tarifedaten)
        self.context_menu_tarifedaten.add_command(label="Löschen", command=self.delete_tarifedaten)
        self.tarifedaten_table.bind("<Button-3>", self.show_context_menu_tarifedaten)

        self.update_tarifedaten_table()

    def save_tarifedaten(self):
        if not self.current_contract:
            messagebox.showerror("Fehler", "Kein Vertrag ausgewählt!")
            return
        tarif = {
            "vertragskonto": self.current_contract,
            "von": self.tarif_von.get(),
            "bis": self.tarif_bis.get(),
            "arbeitspreis_ht": self.tarif_arbeitspreis_ht.get(),
            "arbeitspreis_nt": self.tarif_arbeitspreis_nt.get(),
            "grundpreis": self.tarif_grundpreis.get(),
            "grundpreis_id": self.tarif_grundpreis_id.get(),
            "zählerkosten": self.tarif_zählerkosten.get(),
            "zählerkosten_id": self.tarif_zählerkosten_id.get(),
            "zusatzkosten": self.tarif_zusatzkosten.get(),
            "zusatzkosten_id": self.tarif_zusatzkosten_id.get()
        }
        if not all([tarif["von"], tarif["bis"], tarif["arbeitspreis_ht"], tarif["arbeitspreis_nt"], tarif["grundpreis"]]):
            messagebox.showerror("Fehler", "Pflichtfelder müssen ausgefüllت sein!")
            return
        try:
            float(tarif["arbeitspreis_ht"])
            float(tarif["arbeitspreis_nt"])
            float(tarif["grundpreis"])
            if tarif["zählerkosten"]: float(tarif["zählerkosten"])
            if tarif["zusatzkosten"]: float(tarif["zusatzkosten"])
        except ValueError:
            messagebox.showerror("Fehler", "Numerische Werte erforderlich!")
            return
        self.data["tarifedaten"].append(tarif)
        self.data["tarifedaten"] = sorted(self.data["tarifedaten"], key=lambda x: datetime.strptime(x["von"], "%d.%m.%Y"))
        save_data(self.data)
        messagebox.showinfo("Erfolg", "Tarifdaten wurden gespeichert!")
        self.clear_tarif_entries()
        self.update_tarifedaten_table()
        self.zahlung_manager.update_energiekosten_table()

    def update_tarifedaten_table(self):
        self.tarifedaten_table.delete(*self.tarifedaten_table.get_children())
        if self.current_contract:
            for item in self.data["tarifedaten"]:
                if item["vertragskonto"] == self.current_contract:
                    grundpreis_str = f"{item['grundpreis']} ({item.get('grundpreis_id', '')})" if item.get("grundpreis_id") else item["grundpreis"]
                    zählerkosten_str = f"{item['zählerkosten']} ({item.get('zählerkosten_id', '')})" if item.get("zählerkosten_id") else item["zählerkosten"]
                    zusatzkosten_str = f"{item['zusatzkosten']} ({item.get('zusatzkosten_id', '')})" if item.get("zusatzkosten_id") else item["zusatzkosten"]
                    self.tarifedaten_table.insert("", "end", values=(
                        item["von"], item["bis"], item["arbeitspreis_ht"], item["arbeitspreis_nt"],
                        grundpreis_str, zählerkosten_str, zusatzkosten_str
                    ))

    def clear_tarif_entries(self):
        self.tarif_von.set_date("01.01.2024")
        self.tarif_bis.set_date("31.12.2024")
        self.tarif_arbeitspreis_ht.delete(0, tk.END)
        self.tarif_arbeitspreis_nt.delete(0, tk.END)
        self.tarif_grundpreis.delete(0, tk.END)
        self.tarif_grundpreis_id.delete(0, tk.END)
        self.tarif_zählerkosten.delete(0, tk.END)
        self.tarif_zählerkosten_id.delete(0, tk.END)
        self.tarif_zusatzkosten.delete(0, tk.END)
        self.tarif_zusatzkosten_id.delete(0, tk.END)

    def edit_tarifedaten(self):
        selected = self.tarifedaten_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.tarifedaten_table.item(selected[0], "values")
        for i, item in enumerate(self.data["tarifedaten"]):
            if (item["vertragskonto"] == self.current_contract and item["von"] == values[0] and item["bis"] == values[1]):
                self.tarif_von.set_date(item["von"])
                self.tarif_bis.set_date(item["bis"])
                self.tarif_arbeitspreis_ht.delete(0, tk.END)
                self.tarif_arbeitspreis_ht.insert(0, item["arbeitspreis_ht"])
                self.tarif_arbeitspreis_nt.delete(0, tk.END)
                self.tarif_arbeitspreis_nt.insert(0, item["arbeitspreis_nt"])
                self.tarif_grundpreis.delete(0, tk.END)
                self.tarif_grundpreis.insert(0, item["grundpreis"])
                self.tarif_grundpreis_id.delete(0, tk.END)
                self.tarif_grundpreis_id.insert(0, item.get("grundpreis_id", ""))
                self.tarif_zählerkosten.delete(0, tk.END)
                self.tarif_zählerkosten.insert(0, item["zählerkosten"])
                self.tarif_zählerkosten_id.delete(0, tk.END)
                self.tarif_zählerkosten_id.insert(0, item.get("zählerkosten_id", ""))
                self.tarif_zusatzkosten.delete(0, tk.END)
                self.tarif_zusatzkosten.insert(0, item["zusatzkosten"])
                self.tarif_zusatzkosten_id.delete(0, tk.END)
                self.tarif_zusatzkosten_id.insert(0, item.get("zusatzkosten_id", ""))
                self.data["tarifedaten"].pop(i)
                self.tarifedaten_table.delete(selected[0])
                self.data["tarifedaten"] = sorted(self.data["tarifedaten"], key=lambda x: datetime.strptime(x["von"], "%d.%m.%Y"))
                save_data(self.data)
                messagebox.showinfo("Info", "Tarifdaten zum Bearbeiten geladen. Ändern و erneut speichern!")
                self.update_tarifedaten_table()
                self.zahlung_manager.update_energiekosten_table()
                break

    def delete_tarifedaten(self):
        selected = self.tarifedaten_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.tarifedaten_table.item(selected[0], "values")
        for i, item in enumerate(self.data["tarifedaten"]):
            if (item["vertragskonto"] == self.current_contract and item["von"] == values[0] and item["bis"] == values[1]):
                self.data["tarifedaten"].pop(i)
                self.tarifedaten_table.delete(selected[0])
                save_data(self.data)
                messagebox.showinfo("Erfolg", "Tarifdaten wurden gelöscht!")
                break
        self.zahlung_manager.update_energiekosten_table()

    def show_context_menu_tarifedaten(self, event):
        row = self.tarifedaten_table.identify_row(event.y)
        if row:
            self.tarifedaten_table.selection_set(row)
            self.context_menu_tarifedaten.post(event.x_root, event.y_root)