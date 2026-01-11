import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ConfineFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Confined Pets", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_table()
        self.create_actions()
        self.load_confined()
        self.create_back_button()

    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Pet", "Client", "Status", "Date", "Notes")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def create_actions(self):
        btn_frame = tk.Frame(self, bg="#f4f6f9")
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Refresh", bg="#2563eb", fg="white", width=14, command=self.load_confined).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Note", bg="#6b7280", fg="white", width=14, command=self.add_note_to_selected).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Daily Treatment", bg="#10b981", fg="white", width=14, command=lambda: self.update_selected_status("Daily Treatment")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Discharge", bg="#f59e0b", fg="white", width=14, command=lambda: self.update_selected_status("Discharged")).pack(side="left", padx=5)

    def load_confined(self):
        """Load pet_status rows where status == 'Confined'"""
        try:
            self.tree.delete(*self.tree.get_children())
            rows = self.controller.db.fetch_pet_status()
            for row in rows:
                # row: (id, pet, client, status, date, notes)
                if str(row[3]).lower() == "confined":
                    self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load confined pets: {e}")

    def on_select(self, event):
        pass  # reserved for future detail view

    def get_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a confined pet first.")
            return None
        item = self.tree.item(sel[0], "values")
        return item  # tuple matching displayed columns

    def add_note_to_selected(self):
        row = self.get_selected_row()
        if not row:
            return
        note_win = tk.Toplevel(self)
        note_win.title("Add Note")
        tk.Label(note_win, text=f"Pet: {row[1]}  Client: {row[2]}").pack(pady=6)
        txt = tk.Text(note_win, width=60, height=6)
        txt.pack(padx=10, pady=6)
        def save():
            note = txt.get(1.0, tk.END).strip()
            if not note:
                messagebox.showwarning("Note", "Note is empty.")
                return
            # Insert another pet_status record with same pet/client and appended notes
            try:
                date = datetime.now().strftime("%Y-%m-%d")
                self.controller.db.insert_pet_status([row[1], row[2], "Confined", date, note])
                messagebox.showinfo("Saved", "Note added.")
                note_win.destroy()
                self.load_confined()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save note: {e}")
        tk.Button(note_win, text="Save Note", bg="#2563eb", fg="white", command=save).pack(pady=6)

    def update_selected_status(self, new_status):
        row = self.get_selected_row()
        if not row:
            return
        pet, client = row[1], row[2]
        confirm = messagebox.askyesno("Confirm", f"Set status for {pet} ({client}) to '{new_status}'?")
        if not confirm:
            return
        try:
            date = datetime.now().strftime("%Y-%m-%d")
            self.controller.db.insert_pet_status([pet, client, new_status, date, ""])
            messagebox.showinfo("Updated", f"Status set to {new_status}.")

            # If discharged, auto-create invoice from treatments for this pet/client
            if new_status == "Discharged":
                self._create_discharge_invoice(client, pet)

            # refresh views
            self.load_confined()
            fn = getattr(self.controller.frames.get("PetStatusFrame"), "load_pet_status", None)
            if callable(fn):
                fn()
            fn2 = getattr(self.controller.frames.get("InvoicesFrame"), "load_invoices", None)
            if callable(fn2):
                fn2()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {e}")

    def _create_discharge_invoice(self, client, pet):
        try:
            treatments = self.controller.db.fetch_treatments()
            treatment_costs = {
                "Checkup": 50, "Vaccination": 75, "Surgery": 500,
                "Dental Cleaning": 150, "X-Ray": 100, "Blood Test": 80,
                "Grooming": 60, "Wound Care": 120, "Physical Therapy": 100,
                "Medication": 40
            }
            total = 0
            for t in treatments:
                # treatment format: (id, reason, pet, client, treatment_type, date, confined, notes)
                if t[3] == client and t[2] == pet:
                    total += treatment_costs.get(t[4], 50)
            invoice_no = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")
            date = datetime.now().strftime("%Y-%m-%d")
            self.controller.db.insert_invoice([invoice_no, client, pet, total, date, "Unpaid"])
            messagebox.showinfo("Invoice Created", f"Invoice {invoice_no} created for {pet}. Amount: ${total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create invoice: {e}")

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white",
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)