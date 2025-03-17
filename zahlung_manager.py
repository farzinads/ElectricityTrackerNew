from base import tk, ttk, messagebox, DateEntry, save_data, PDF_DIR, os
import shutil
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class ZahlungManager:
    def __init__(self, app):
        self.root = app.root
        self.data = app.data
        self.current_contract = app.current_contract
        self.zahlungen_tab = app.zahlungen_tab
        self.energiekosten_tab = app.energiekosten_tab
        self.setup_zahlungen_tab()
        self.setup_energiekosten_tab()

    def setup_zahlungen_tab(self):
        zahlungen_frame = ttk.Frame(self.zahlungen_tab)
        zahlungen_frame.place(x=10, y=10)

        ttk.Label(zahlungen_frame, text="Zahlungsdatum:").grid(row=0, column=0, pady=5, sticky="w")
        self.zahlungsdatum = DateEntry(zahlungen_frame, date_pattern="dd.mm.yyyy")
        self.zahlungsdatum.grid(row=0, column=1, pady=5)

        ttk.Label(zahlungen_frame, text="Betrag (€):").grid(row=1, column=0, pady=5, sticky="w")
        self.betrag = ttk.Entry(zahlungen_frame)
        self.betrag.grid(row=1, column=1, pady=5)

        ttk.Button(zahlungen_frame, text="PDF hochladen", command=self.upload_pdf).grid(row=2, column=0, pady=5)
        self.pdf_label = ttk.Label(zahlungen_frame, text="Kein PDF ausgewählt")
        self.pdf_label.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Button(zahlungen_frame, text="Speichern", command=self.save_zahlung).grid(row=3, column=0, columnspan=2, pady=10)

        table_frame_zahlungen = ttk.Frame(self.zahlungen_tab, relief="solid", borderwidth=2)
        table_frame_zahlungen.place(x=10, y=145, width=960, height=505)

        self.zahlungen_table = ttk.Treeview(table_frame_zahlungen, columns=("Zahlungsdatum", "Betrag", "PDF"), show="headings")
        self.zahlungen_table.heading("Zahlungsdatum", text="Zahlungsdatum")
        self.zahlungen_table.heading("Betrag", text="Betrag (€)")
        self.zahlungen_table.heading("PDF", text="PDF")
        self.zahlungen_table.column("Zahlungsdatum", width=200, anchor="center")
        self.zahlungen_table.column("Betrag", width=150, anchor="center")
        self.zahlungen_table.column("PDF", width=150, anchor="center")

        scrollbar_zahlungen = ttk.Scrollbar(table_frame_zahlungen, orient="vertical", command=self.zahlungen_table.yview)
        self.zahlungen_table.configure(yscrollcommand=scrollbar_zahlungen.set)
        scrollbar_zahlungen.pack(side="right", fill="y")
        self.zahlungen_table.pack(fill="both", expand=True)

        self.context_menu_zahlungen = tk.Menu(self.root, tearoff=0)
        self.context_menu_zahlungen.add_command(label="Bearbeiten", command=self.edit_zahlung)
        self.context_menu_zahlungen.add_command(label="Löschen", command=self.delete_zahlung)
        self.zahlungen_table.bind("<Button-3>", self.show_context_menu_zahlungen)
        self.zahlungen_table.bind("<Double-1>", self.open_pdf_from_table)

        self.update_zahlungen_table()

    def setup_energiekosten_tab(self):
        ttk.Button(self.energiekosten_tab, text="Export als PDF", command=self.export_energiekosten_to_pdf).place(x=850, y=5, width=120)

        table_frame_energie = ttk.Frame(self.energiekosten_tab, relief="solid", borderwidth=2)
        table_frame_energie.place(x=10, y=40, width=960, height=590)

        style = ttk.Style()
        style.configure("SmallFont.Treeview", font=("Arial", 8))
        style.configure("Treeview", font=("Arial", 10))
        style.configure("Red.Treeview", font=("Arial", 10), foreground="#FF4040")

        self.energiekosten_table = ttk.Treeview(table_frame_energie, columns=("", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag brutto"), show="headings", style="Treeview")
        self.energiekosten_table.heading("", text="")
        self.energiekosten_table.heading("Zeitraum", text="Zeitraum")
        self.energiekosten_table.heading("Menge", text="Menge")
        self.energiekosten_table.heading("Preis netto", text="Preis netto")
        self.energiekosten_table.heading("Betrag netto", text="Betrag netto")
        self.energiekosten_table.heading("MwSt.", text="MwSt.")
        self.energiekosten_table.heading("Betrag brutto", text="Betrag brutto")
        self.energiekosten_table.column("", width=200, anchor="center")
        self.energiekosten_table.column("Zeitraum", width=130, anchor="center")
        self.energiekosten_table.column("Menge", width=130, anchor="center")
        self.energiekosten_table.column("Preis netto", width=100, anchor="center")
        self.energiekosten_table.column("Betrag netto", width=100, anchor="center")
        self.energiekosten_table.column("MwSt.", width=100, anchor="center")
        self.energiekosten_table.column("Betrag brutto", width=100, anchor="center")

        self.energiekosten_table.tag_configure("smallfont", font=("Arial", 8))
        self.energiekosten_table.tag_configure("red", foreground="#FF4040")

        scrollbar_energie = ttk.Scrollbar(table_frame_energie, orient="vertical", command=self.energiekosten_table.yview)
        self.energiekosten_table.configure(yscrollcommand=scrollbar_energie.set)
        scrollbar_energie.pack(side="right", fill="y")
        self.energiekosten_table.pack(fill="both", expand=True)

        self.update_energiekosten_table()

    def upload_pdf(self):
        pdf_path = tk.filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            self.current_pdf_path = pdf_path
            self.pdf_label.config(text=os.path.basename(pdf_path))

    def save_zahlung(self):
        if not self.current_contract:
            messagebox.showerror("Fehler", "Kein Vertrag ausgewählt!")
            return
        zahlungsdatum = self.zahlungsdatum.get()
        betrag = self.betrag.get()
        if not all([zahlungsdatum, betrag]):
            messagebox.showerror("Fehler", "Zahlungsdatum und Betrag müssen ausgefüllت sein!")
            return
        try:
            float(betrag)
        except ValueError:
            messagebox.showerror("Fehler", "Betrag muss numerisch sein!")
            return
        pdf_path = None
        if hasattr(self, 'current_pdf_path') and self.current_pdf_path:
            pdf_filename = f"{self.current_contract}_{zahlungsdatum.replace('.', '_')}_{os.path.basename(self.current_pdf_path)}"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)
            shutil.copy(self.current_pdf_path, pdf_path)
        zahlung = {
            "vertragskonto": self.current_contract,
            "zahlungsdatum": zahlungsdatum,
            "betrag": betrag,
            "pdf_path": pdf_path if pdf_path else "-"
        }
        self.data["zahlungen"].append(zahlung)
        self.data["zahlungen"] = sorted(self.data["zahlungen"], key=lambda x: datetime.strptime(x["zahlungsdatum"], "%d.%m.%Y"))
        save_data(self.data)
        messagebox.showinfo("Erfolg", "Zahlung wurde gespeichert!")
        self.clear_zahlung_entries()
        self.update_zahlungen_table()

    def update_zahlungen_table(self):
        self.zahlungen_table.delete(*self.zahlungen_table.get_children())
        if self.current_contract:
            for item in self.data["zahlungen"]:
                if item["vertragskonto"] == self.current_contract:
                    pdf_button = "Anzeigen" if item["pdf_path"] != "-" else "-"
                    self.zahlungen_table.insert("", "end", values=(item["zahlungsdatum"], item["betrag"], pdf_button), tags=(item["pdf_path"],))

    def clear_zahlung_entries(self):
        self.zahlungsdatum.set_date("01.01.2025")
        self.betrag.delete(0, tk.END)
        self.current_pdf_path = None
        self.pdf_label.config(text="Kein PDF ausgewählt")

    def edit_zahlung(self):
        selected = self.zahlungen_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.zahlungen_table.item(selected[0], "values")
        for i, item in enumerate(self.data["zahlungen"]):
            if item["vertragskonto"] == self.current_contract and item["zahlungsdatum"] == values[0]:
                self.zahlungsdatum.set_date(item["zahlungsdatum"])
                self.betrag.delete(0, tk.END)
                self.betrag.insert(0, item["betrag"])
                self.current_pdf_path = item["pdf_path"] if item["pdf_path"] != "-" else None
                self.pdf_label.config(text=os.path.basename(item["pdf_path"]) if item["pdf_path"] != "-" else "Kein PDF ausgewählt")
                self.data["zahlungen"].pop(i)
                self.zahlungen_table.delete(selected[0])
                self.data["zahlungen"] = sorted(self.data["zahlungen"], key=lambda x: datetime.strptime(x["zahlungsdatum"], "%d.%m.%Y"))
                save_data(self.data)
                messagebox.showinfo("Info", "Zahlung zum Bearbeiten geladen. Ändern و erneut speichern!")
                self.update_zahlungen_table()
                break

    def delete_zahlung(self):
        selected = self.zahlungen_table.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        values = self.zahlungen_table.item(selected[0], "values")
        for i, item in enumerate(self.data["zahlungen"]):
            if item["vertragskonto"] == self.current_contract and item["zahlungsdatum"] == values[0]:
                if item["pdf_path"] != "-" and os.path.exists(item["pdf_path"]):
                    os.remove(item["pdf_path"])
                self.data["zahlungen"].pop(i)
                self.zahlungen_table.delete(selected[0])
                save_data(self.data)
                messagebox.showinfo("Erfolg", "Zahlung wurde gelöscht!")
                break

    def open_pdf_from_table(self, event):
        item = self.zahlungen_table.identify_row(event.y)
        if not item:
            return
        pdf_path = self.zahlungen_table.item(item, "tags")[0]
        if pdf_path and pdf_path != "-":
            if os.name == "nt":  # Windows
                os.startfile(pdf_path)
            else:  # Linux/Mac
                subprocess.call(["xdg-open", pdf_path])

    def update_energiekosten_table(self):
        self.energiekosten_table.delete(*self.energiekosten_table.get_children())
        if not self.current_contract:
            return

        tarif_periods = sorted(
            [item for item in self.data["tarifedaten"] if item["vertragskonto"] == self.current_contract],
            key=lambda x: datetime.strptime(x["von"], "%d.%m.%Y")
        )
        if not tarif_periods:
            ablesung_list = sorted(
                [item for item in self.data["ablesung"] if item["vertragskonto"] == self.current_contract],
                key=lambda x: datetime.strptime(x["ablesungsdatum"], "%d.%m.%Y")
            )
            if ablesung_list:
                default_tarif = {
                    "vertragskonto": self.current_contract,
                    "von": ablesung_list[0]["ablesungsdatum"],
                    "bis": ablesung_list[-1]["ablesungsdatum"],
                    "arbeitspreis_ht": "20.0",
                    "arbeitspreis_nt": "15.0",
                    "grundpreis": "100.0",
                    "zählerkosten": "0.0",
                    "zusatzkosten": "0.0",
                    "grundpreis_id": "default",
                    "zählerkosten_id": "default",
                    "zusatzkosten_id": "default"
                }
                tarif_periods = [default_tarif]
            else:
                messagebox.showwarning("Warnung", "Keine Tarifdaten oder Ablesungen vorhanden!")
                return

        ablesung_list = sorted(
            [item for item in self.data["ablesung"] if item["vertragskonto"] == self.current_contract],
            key=lambda x: datetime.strptime(x["ablesungsdatum"], "%d.%m.%Y")
        )

        superscript_map = {
            "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
            "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
            "T": "ᵀ", "t": "ᵗ", "A": "ᴬ", "a": "ᵃ", "B": "ᴮ", "b": "ᵇ",
            "C": "ᶜ", "c": "ᶜ", "D": "ᴰ", "d": "ᵈ", "E": "ᴱ", "e": "ᵉ"
        }

        rows = ["Arbeitspreis", "Grundpreis", "Zähler", "Zusatzkosten", "Energiekosten"]
        self.energiekosten_table.insert("", "end", values=("", "", "", "", "", "", ""))
        arbeitspreis_count = 0
        betrag_netto_sum = 0

        for i, row in enumerate(rows):
            if row == "Arbeitspreis" and tarif_periods:
                for j, tarif in enumerate(tarif_periods):
                    period = f"{tarif['von']} - {tarif['bis']}"
                    superscript_num = ''.join(superscript_map.get(digit, digit) for digit in f"{j+1:02d}")

                    verbrauch_ht = 0
                    verbrauch_nt = 0
                    if len(ablesung_list) >= 2:
                        start_date = datetime.strptime(tarif["von"], "%d.%m.%Y")
                        end_date = datetime.strptime(tarif["bis"], "%d.%m.%Y")
                        for k in range(len(ablesung_list) - 1):
                            ablesung_start = datetime.strptime(ablesung_list[k]["ablesungsdatum"], "%d.%m.%Y")
                            ablesung_end = datetime.strptime(ablesung_list[k + 1]["ablesungsdatum"], "%d.%m.%Y")
                            if ablesung_start < end_date and ablesung_end > start_date:
                                ht_diff = float(ablesung_list[k + 1]["zählerstand_ht"]) - float(ablesung_list[k]["zählerstand_ht"])
                                nt_diff = float(ablesung_list[k + 1]["zählerstand_nt"]) - float(ablesung_list[k]["zählerstand_nt"])
                                verbrauch_ht += ht_diff
                                verbrauch_nt += nt_diff

                    ht_label = f"Arbeitspreis HT{superscript_num}"
                    ht_menge = f"{verbrauch_ht:.2f} (kWh)"
                    ht_preis_netto = f"{tarif['arbeitspreis_ht']} (ct/kWh)"
                    ht_betrag_netto = (float(verbrauch_ht) * float(tarif["arbeitspreis_ht"])) / 100
                    betrag_netto_sum += ht_betrag_netto
                    self.energiekosten_table.insert("", i + arbeitspreis_count + 1, values=(ht_label, period, ht_menge, ht_preis_netto, f"{ht_betrag_netto:.2f} (€)", "", ""), tags=("smallfont",))
                    arbeitspreis_count += 1

                    nt_label = f"Arbeitspreis NT{superscript_num}"
                    nt_menge = f"{verbrauch_nt:.2f} (kWh)"
                    nt_preis_netto = f"{tarif['arbeitspreis_nt']} (ct/kWh)"
                    nt_betrag_netto = (float(verbrauch_nt) * float(tarif["arbeitspreis_nt"])) / 100
                    betrag_netto_sum += nt_betrag_netto
                    self.energiekosten_table.insert("", i + arbeitspreis_count + 1, values=(nt_label, period, nt_menge, nt_preis_netto, f"{nt_betrag_netto:.2f} (€)", "", ""), tags=("smallfont",))
                    arbeitspreis_count += 1

            elif row == "Grundpreis" and tarif_periods:
                for j, tarif in enumerate(tarif_periods):
                    period = f"{tarif['von']} - {tarif['bis']}"
                    start_date = datetime.strptime(tarif["von"], "%d.%m.%Y")
                    end_date = datetime.strptime(tarif["bis"], "%d.%m.%Y")
                    days = (end_date - start_date).days + 1
                    menge = f"{days} (Tags)"
                    preis_netto = float(tarif["grundpreis"])
                    betrag_netto = (days / 365) * preis_netto
                    betrag_netto_sum += betrag_netto
                    grundpreis_id = tarif.get("grundpreis_id", "")
                    grundpreis_label = f"Grundpreis{''.join(superscript_map.get(digit, digit) for digit in grundpreis_id)}" if grundpreis_id else "Grundpreis"
                    self.energiekosten_table.insert("", i + arbeitspreis_count + j, values=(grundpreis_label, period, menge, f"{preis_netto} (€)", f"{betrag_netto:.2f} (€)", "", ""), tags=("smallfont",))

            elif row == "Zähler" and tarif_periods:
                for j, tarif in enumerate(tarif_periods):
                    period = f"{tarif['von']} - {tarif['bis']}"
                    start_date = datetime.strptime(tarif["von"], "%d.%m.%Y")
                    end_date = datetime.strptime(tarif["bis"], "%d.%m.%Y")
                    days = (end_date - start_date).days + 1
                    menge = f"{days} (Tags)"
                    preis_netto = float(tarif["zählerkosten"]) if tarif["zählerkosten"] else 0
                    betrag_netto = (days / 365) * preis_netto
                    betrag_netto_sum += betrag_netto
                    zählerkosten_id = tarif.get("zählerkosten_id", "")
                    zählerkosten_label = f"Zähler{''.join(superscript_map.get(digit, digit) for digit in zählerkosten_id)}" if zählerkosten_id else "Zähler"
                    self.energiekosten_table.insert("", i + arbeitspreis_count + j, values=(zählerkosten_label, period, menge, f"{preis_netto} (€)", f"{betrag_netto:.2f} (€)", "", ""), tags=("smallfont",))

            elif row == "Zusatzkosten" and tarif_periods:
                for j, tarif in enumerate(tarif_periods):
                    period = f"{tarif['von']} - {tarif['bis']}"
                    start_date = datetime.strptime(tarif["von"], "%d.%m.%Y")
                    end_date = datetime.strptime(tarif["bis"], "%d.%m.%Y")
                    days = (end_date - start_date).days + 1
                    menge = f"{days} (Tags)"
                    preis_netto = float(tarif["zusatzkosten"]) if tarif["zusatzkosten"] else 0
                    betrag_netto = (days / 365) * preis_netto
                    betrag_netto_sum += betrag_netto
                    zusatzkosten_id = tarif.get("zusatzkosten_id", "")
                    zusatzkosten_label = f"Zusatzkosten{''.join(superscript_map.get(digit, digit) for digit in zusatzkosten_id)}" if zusatzkosten_id else "Zusatzkosten"
                    self.energiekosten_table.insert("", i + arbeitspreis_count + j, values=(zusatzkosten_label, period, menge, f"{preis_netto} (€)", f"{betrag_netto:.2f} (€)", "", ""), tags=("smallfont",))

            elif row == "Energiekosten":
                self.energiekosten_table.insert("", "end", values=("─" * 20, "─" * 20, "─" * 20, "─" * 20, "─" * 20, "─" * 20, "─" * 20), tags=("smallfont",))
                mwst = betrag_netto_sum * 0.19
                betrag_brutto = betrag_netto_sum + mwst
                self.energiekosten_table.insert("", "end", values=("Energiekosten", "", "", "", f"{betrag_netto_sum:.2f} (€)", f"{mwst:.2f} (€)", f"{betrag_brutto:.2f} (€)"), tags=("red",))

        for _ in range(4):
            self.energiekosten_table.insert("", "end", values=("", "", "", "", "", "", ""))

    def export_energiekosten_to_pdf(self):
        if not self.current_contract:
            messagebox.showerror("Fehler", "Kein Vertrag ausgewählt!")
            return

        pdf_path = os.path.join(PDF_DIR, f"Energiekosten_{self.current_contract}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph(f"Energiekosten - Vertragskonto: {self.current_contract}", styles["Heading1"])
        elements.append(title)
        elements.append(Paragraph("<br/><br/>", styles["Normal"]))

        data = [["", "Zeitraum", "Menge", "Preis netto", "Betrag netto", "MwSt.", "Betrag brutto"]]
        for item in self.energiekosten_table.get_children():
            values = self.energiekosten_table.item(item, "values")
            data.append(list(values))

        if len(data) <= 1:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden!")
            return

        table = Table(data, colWidths=[100, 100, 80, 80, 80, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, -1), (0, -1), colors.Color(1, 0.25, 0.25)),
            ('LINEABOVE', (0, -2), (-1, -2), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)
        messagebox.showinfo("Erfolg", f"PDF wurde gespeichert: {pdf_path}")
        if os.name == "nt":
            os.startfile(pdf_path)

    def show_context_menu_zahlungen(self, event):
        row = self.zahlungen_table.identify_row(event.y)
        if row:
            self.zahlungen_table.selection_set(row)
            self.context_menu_zahlungen.post(event.x_root, event.y_root)