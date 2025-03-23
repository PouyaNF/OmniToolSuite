import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

class ExcelDuplicateRemoverTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=10)
        self.selected_file = None
        self.build_widgets()

    def build_widgets(self):
        self.browse_button = ttk.Button(self.frame, text="Browse Excel File", command=self.browse_file, width=25)
        self.browse_button.pack(pady=10)

        self.file_label = ttk.Label(self.frame, text="No file selected", wraplength=450)
        self.file_label.pack(pady=5)

        self.column_frame = ttk.Frame(self.frame)
        self.column_frame.pack(pady=10)
        self.column_label = ttk.Label(self.column_frame, text="Special Column Name:")
        self.column_label.pack(side=tk.LEFT, padx=5)
        self.column_entry = ttk.Entry(self.column_frame, width=30)
        self.column_entry.pack(side=tk.LEFT)

        self.process_button = ttk.Button(self.frame, text="Process File", command=self.process_file, width=25)
        self.process_button.pack(pady=20)

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filepath:
            self.file_label.config(text=filepath)
            self.selected_file = filepath

    def process_file(self):
        column_name = self.column_entry.get().strip()
        if not self.selected_file:
            messagebox.showerror("Error", "Please select an Excel file!")
            return
        if not column_name:
            messagebox.showerror("Error", "Please enter the column name to process!")
            return

        try:
            df = pd.read_excel(self.selected_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the Excel file:\n{e}")
            return

        if column_name not in df.columns:
            messagebox.showerror("Error", f"Column '{column_name}' not found in the Excel file.")
            return

        df = df.drop_duplicates(subset=[column_name], keep='first')

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx *.xls")],
            title="Save Edited File As"
        )
        if not save_path:
            return

        try:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Success", f"File saved successfully:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the file:\n{e}")
