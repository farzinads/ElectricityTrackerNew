import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

PDF_DIR = "zahlungen_pdfs"

def load_data():
    if os.path.exists("electricity_data.json"):
        with open("electricity_data.json", "r") as f:
            return json.load(f)
    return {"contracts": [], "tarifedaten": [], "ablesung": [], "zahlungen": []}

def save_data(data):
    with open("electricity_data.json", "w") as f:
        json.dump(data, f, indent=4)