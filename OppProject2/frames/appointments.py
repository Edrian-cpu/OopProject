import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AppointmentsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Appointments Module", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_table()
        self.load_appointments()
        self.create_back_button()

    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10, fill="both", expand=True)

        columns = ("ID", "Client Name", "Pet Name", "Date", "Time", "Reason")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_appointments(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.controller.db.fetch_appointments()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white", 
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)
