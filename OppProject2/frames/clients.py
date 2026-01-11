import tkinter as tk
from tkinter import ttk, messagebox

class ClientsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Clients Module", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_table()
        self.load_clients()
        self.create_back_button()

    # ===== Table (readonly) =====
    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10, fill="both", expand=True)

        columns = ("ID", "Name", "Contact", "Address")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    # ===== Back to Dashboard button =====
    def create_back_button(self):
        tk.Button(
            self,
            text="Back to Dashboard",
            bg="#334155",
            fg="white",
            command=lambda: self.controller.show_frame("DashboardFrame")
        ).pack(pady=10)

    # ===== Load clients from database =====
    def load_clients(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.controller.db.fetch_clients()
        for row in rows:
            self.tree.insert("", "end", values=row)
