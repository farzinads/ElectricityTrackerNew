from base import tk, ttk, messagebox, DateEntry, save_data
from datetime import datetime, timedelta

class AblesungManager:
    def __init__(self, app):
        self.root = app.root
        self.data = app.data
        self.current_contract = app.current_contract
        self.ablesung_tab = app.ablesung_tab
        self.verbrauchsmengen_tab = app.verbrauchsmengen_tab
        self.zahlung_manager = app
        self.setup_ablesung_tab()

    def setup_ablesung_tab(self):
        ablesung_frame = ttk.Frame(self.ablesung_tab)
        ablesung_frame.place(x=10, y=10)

        ttk.Label(ablesung_frame, text="Ablesungsdatum:").grid(row=0, column=0, pady=5, sticky="w")
        self.ablesungsdatum = DateEntry(ablesung_frame, date_pattern="dd.mm.yyyy")
        self.ablesungsdatum.grid(row=0, column=1, pady=5)

        ttk.Label(ablesung_frame, text="Zählerstand HT (1.8.0):").grid(row=1, column=0, pady=5, sticky="w")
        self.zählerstand_ht = ttk.Entry(ablesung_frame)
        self.zählerstand_ht.grid(row=1, column=1, pady=5)

        ttk.Label(ablesung_frame, text="Zählerstand NT (2.8.0):").grid(row=2, column=0, pady=5, sticky="w")
        self.zählerstand_nt = ttk.Entry(ablesung_frame)
        self.zählerstand_nt.grid(row=2, column=1, pady=5)

        ttk.Button(ablesung_frame, text="Speichern", command=self.save_ablesung).grid(row=3, column=0, columnspan=2, pady=10)

        table_frame_ablesung = ttk.Frame(self.ablesung_tab, relief="solid", borderwidth=2)
        table_frame_ablesung.place(x=10, y=145, width=960, height=505)

        self.ablesung_table = ttk.Treeview(table_frame_ablesung, columns=("Ablesungsdatum", "HT", "NT"), show="headings")
        self.ablesung_table.heading("Ablesungsdatum", text="Ablesungsdatum")
        self.ablesung_table.heading("HT", text="Zählerstand HT (1.8.0)")
        self.ablesung_table.heading("NT", text="Zählerstand NT (2.8.0)")
        self.ablesung_table.column("Ablesungsdatum", width=200, anchor="center")
        self.ablesung_table.column("HT", width=150, anchor="center")
        self.ablesung_table.column("NT", width=150, anchor="center")

        scrollbar_ablesung = ttk.Scrollbar(table_frame_ablesung, orient="vertical", command=self.ablesung_table.yview)
        self.ablesung_table.configure(yscrollcommand=scrollbar_ablesung.set)
        scrollbar_ablesung.pack(side="right", fill="y")
        self.ablesung_table.pack(fill="both", expand=True)

        self.context_menu_ablesung = tk.Menu(self.root, tearoff=0)
        self.context_menu_ablesung.add_command(label="Bearbeiten", command=self.edit_ablesung)
        self.context_menu_ablesung.add_command(label="Löschen", command=self.delete_ablesung)
        self.ablesung_table.bind("<Button-3>", self.show_context_menu_ablesung)

        table_frame_verbrauch = ttk.Frame(self.verbrauchsmengen_tab, relief="solid", borderwidth=2)
        table_frame_verbrauch.place(x=10, y=10, width=960, height=620)

        self.verbrauchsmengen_table = ttk.Treeview(table_frame_verbrauch, columns=("Zeitraum", "Tage", "Verbrauch HT", "Verbrauch NT"), show="headings")
        self.verbrauchsmengen_table.heading("Zeitraum", text="Zeitraum")
        self.verbrauchsmengen_table.heading("Tage", text="Tage")
        self.verbrauchsmengen_table.heading("Verbrauch HT", text="Verbrauch HT (kWh)")
        self.verbrauchsmengen_table.heading("Verbrauch NT", text="Verbrauch NT (kWh)")
        self.verbrauchsmengen_table.column("Zeitraum", width=200, anchor="center")
        self.verbrauchsmengen_table.column("Tage", width=100, anchor="center")
        self.verbrauchsmengen_table.column("Verbrauch HT", width=150, anchor="center")
        self.verbrauchsmengen_table.column("Verbrauch NT", width=150, anchor="center")

        scrollbar_verbrauch = ttk.Scrollbar(table_frame_verbrauch, orient="vertical", command=self.verbrauchsmengen_table.yview)
        self.verbrauchsmengen_table.configure(yscrollcommand=scrollbar_verbrauch.set)
        scrollbar_verbrauch.pack(side="right", fill="y")
        self.verbrauchsmengen_table.pack(fill="both", expand=True)

        self.update_ablesung_table()
        self.update_verbrauchsmengen_table()

    def save_ablesung(self):
        if not self.current_contract:
            messagebox.showerror("Fehler", "Kein Vertrag ausgewählt!")
            return
        ablesung = {
            "vertragskonto": self.current_contract,
            "ablesungsdatum": self.ablesungsdatum.get(),
            "zählerstand_ht": self.zählerstand_ht.get(),
            "zählerstand_nt": self.zählerstand_nt.get()
        }
        if not all([ablesung["ablesungsdatum"], ablesung["zählerstand_ht"], ablesung["zählerstand_nt"]]):
            messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllت sein!")
            return
        try:
            float(ablesung["zählerstand_ht"])
            float(ablesung["zählerstand_nt"])
        except ValueError:
            messagebox.showerror("Fehler", "Zählerstände müssen numerisch sein!")
            return
        self.data["ablesung"].append(ablesung)
        self.data["ablesung"] = sorted(self.data["ablesung"], key=lambda x: datetime.strptime(x["ablesungsdatum"], "%d.%m.%Y"))
        save_data(self.data)
        messagebox.showinfo("Erfolg", "Ablesung wurde gespeichert!")
        self.clear_ablesung_entries()
        self.update_ablesung_table()
        self.update_verbrauchsmengen_table()
        self.zahlung_manager.update_energiekosten_table()

    def update_ablesung_table(self):
        self.ablesung_table.delete(*self.ablesung_table.get_children())
        if self.current_contract:
            for item in self.data["ablesung"]:
                if item["vertragskonto"] == self.current_contract:
                    self.ablesung_table.insert("", "end", values=(item["ablesungsdatum"], item["zählerstand_ht"], item["zählerstand_nt"]))

    def update_verbrauchsmengen_table(self):
        self.verbrauchsmengen_table.delete(*self.verbrauchsmengen_table.get_children())
        if not self.current_contract:
            print("No current contract selected.")
            return
        ablesung_list = sorted(
            [item for item in self.data["ablesung"] if item["vertragskonto"] == self.current_contract],
            key=lambda x: datetime.strptime(x["ablesungsdatum"], "%d.%m.%Y")
        )
        print(f"Ablesung list length: {len(ablesung_list)}")
        print("Raw Ablesung dates:", [item["ablesungsdatum"] for item in ablesung_list])
        if len(ablesung_list) < 2:
            print("Less than 2 ablesung entries.")
            return

        for i in range(len(ablesung_list) - 1):
            if i == 0:
                # بازه اول: از تاریخ اول تا تاریخ دوم
                period_start = datetime.strptime(ablesung_list[i]["ablesungsdatum"], "%d.%m.%Y")
                period_end = datetime.strptime(ablesung_list[i + 1]["ablesungsdatum"], "%d.%m.%Y")
            else:
                # بازه‌های بعدی: از یک روز بعد از تاریخ قبلی تا تاریخ فعلی
                period_start = datetime.strptime(ablesung_list[i]["ablesungsdatum"], "%d.%m.%Y") + timedelta(days=1)
                period_end = datetime.strptime(ablesung_list[i + 1]["ablesungsdatum"], "%d.%m.%Y")
                
                # تنظیم شروع به اول ماه برای بازه‌های دوم و سوم
                if i in [1, 2]:
                    period_start = period_start.replace(day=1)

            days = (period_end - period_start).days + 1
            period_str = f"{period_start.strftime('%d.%m.%Y')} - {period_end.strftime('%d.%m.%Y')}"
            print(f"Period {i+1}: {period_str}, Days: {days}")

            verbrauch_ht = float(ablesung_list[i + 1]["zählerstand_ht"]) - float(ablesung_list[i]["zählerstand_ht"])
            verbrauch_nt = float(ablesung_list[i + 1]["zählerstand_nt"]) - float(ablesung_list[i]["zählerstand_nt"])

            self.verbrauchsmengen_table.insert("", "end", values=(
                period_str, days, f"{verbrauch_ht:.2f}", f"{verbrauch_nt:.2f}"
            ))

    def clear_ablesung_entries(self):
        self.ablesungsdatum.set_date("01.01.2025")
        self.zählerstand_ht.delete(0, tk.END)
        self.zählerstand_nt.delete(0, tk.END)

    def edit_ablesung(self):
        selected = self.ablesung_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.ablesung_table.item(selected[0], "values")
        for i, item in enumerate(self.data["ablesung"]):
            if item["vertragskonto"] == self.current_contract and item["ablesungsdatum"] == values[0]:
                self.ablesungsdatum.set_date(item["ablesungsdatum"])
                self.zählerstand_ht.delete(0, tk.END)
                self.zählerstand_ht.insert(0, item["zählerstand_ht"])
                self.zählerstand_nt.delete(0, tk.END)
                self.zählerstand_nt.insert(0, item["zählerstand_nt"])
                self.data["ablesung"].pop(i)
                self.ablesung_table.delete(selected[0])
                self.data["ablesung"] = sorted(self.data["ablesung"], key=lambda x: datetime.strptime(x["ablesungsdatum"], "%d.%m.%Y"))
                save_data(self.data)
                messagebox.showinfo("Info", "Ablesung zum Bearbeiten geladen. Ändern و erneut speichern!")
                self.update_ablesung_table()
                self.update_verbrauchsmengen_table()
                self.zahlung_manager.update_energiekosten_table()
                break

    def delete_ablesung(self):
        selected = self.ablesung_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.ablesung_table.item(selected[0], "values")
        for i, item in enumerate(self.data["ablesung"]):
            if item["vertragskonto"] == self.current_contract and item["ablesungsdatum"] == values[0]:
                self.data["ablesung"].pop(i)
                self.ablesung_table.delete(selected[0])
                save_data(self.data)
                messagebox.showinfo("Erfolg", "Ablesung wurde gelöscht!")
                break
        self.update_verbrauchsmengen_table()
        self.zahlung_manager.update_energiekosten_table()

    def show_context_menu_ablesung(self, event):
        row = self.ablesung_table.identify_row(event.y)
        if row:
            self.ablesung_table.selection_set(row)
            self.context_menu_ablesung.post(event.x_root, event.y_root)